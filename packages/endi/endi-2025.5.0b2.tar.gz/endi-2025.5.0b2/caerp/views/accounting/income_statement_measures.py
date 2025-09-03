from collections import OrderedDict
import logging

import colander
from sqlalchemy import or_, and_
from sqlalchemy.orm import (
    joinedload,
)

from caerp.consts.permissions import PERMISSIONS
from caerp.export.accounting_spreadsheet import (
    CellsIndex,
    SpreadSheetCompiler,
    SpreadSheetSyntax,
    XLSXSyntax,
    ODSSyntax,
)
from caerp.export.utils import write_file_to_request
from caerp.export.excel import XlsExporter
from caerp.export.ods import OdsExporter
from caerp.compute import math_utils
from caerp.utils.widgets import Link
from caerp.utils.strings import (
    short_month_name,
    format_float,
)
from caerp.models.company import Company
from caerp.models.accounting.income_statement_measures import (
    IncomeStatementMeasureGrid,
    IncomeStatementMeasure,
    IncomeStatementMeasureTypeCategory,
)
from caerp.forms.accounting import (
    get_income_statement_measures_list_schema,
    get_upload_treasury_list_schema,
)
from caerp.utils.accounting import (
    get_current_financial_year_value,
    get_current_financial_year_data,
    get_financial_year_data,
)
from caerp.views import BaseListView
from caerp.views.accounting.routes import (
    UPLOAD_ITEM_ROUTE,
    UPLOAD_ITEM_INCOME_STATEMENT_ROUTE,
    INCOME_STATEMENT_GRIDS_ROUTE_EXPORT,
    INCOME_STATEMENT_GRIDS_ROUTE,
)

logger = logging.getLogger(__name__)


class IncomeStatementMeasureGridListView(BaseListView):
    """
    List companies having IncomeStatementMeasureGrid generated with the current
    context (AccountingOperationUpload)
    """

    sort_columns = {
        "company": "name",
    }
    add_template_vars = ("stream_actions",)
    default_sort = "company"
    default_direction = "asc"
    schema = get_upload_treasury_list_schema()
    title = "Liste des comptes de résultat"

    def populate_actionmenu(self, appstruct):
        self.request.navigation.breadcrumb.append(
            Link(
                self.request.route_path(UPLOAD_ITEM_ROUTE, id=self.context.id),
                "Revenir à la liste des écritures",
            )
        )
        self.request.navigation.breadcrumb.append(Link("", self.title))

    def query(self):
        query = Company.query().filter(
            Company.id.in_(
                self.dbsession.query(IncomeStatementMeasureGrid.company_id).filter_by(
                    upload_id=self.context.id
                )
            )
        )
        return query

    def filter_company_id(self, query, appstruct):
        company_id = appstruct.get("company_id")
        if company_id not in (colander.null, None):
            query = query.filter_by(id=company_id)
        return query

    def stream_actions(self, company):
        url = self.request.route_path(INCOME_STATEMENT_GRIDS_ROUTE, id=company.id)
        return (
            Link(
                url,
                "Voir ce compte de résultat",
                title="Voir le détail de ce compte de résultats",
                icon="euro-circle",
                css="icon",
            ),
        )


class YearGlobalGrid:
    """
    Abstract class used to modelize the income statement and group all stuff
    """

    def __init__(self, year, grids, turnover):
        self.financial_year = get_financial_year_data(year)
        if not grids:
            self.is_void = True
        else:
            self.is_void = False

        if not self.is_void:
            self.categories = IncomeStatementMeasureTypeCategory.get_categories()

            self.turnover = turnover
            self.build_indexes(grids)
            self.rows = list(self.compile_rows())

    def build_indexes(self, grids):
        # Build columns index
        self.columns_index = self._build_columns_index()

        # Month grids stored by month number
        self.grids = self._grid_by_month(grids, self.columns_index)

        # Types by category id
        self.types = self._type_by_category()

    def _build_columns_index(self):
        """
        Compute columns index based on financial year

        :returns: An OrderedDict with a tuple `(index, (year,month))` for each column
        """
        columns_index = OrderedDict((month, (None, None)) for month in range(1, 13))
        year = self.financial_year["start_year"]
        month = self.financial_year["start_month"]
        for index in range(1, 13):
            columns_index[index] = (year, month)
            month += 1
            if month > 12:
                year += 1
                month = 1
        return columns_index

    def get_column_index_by_month(self, month, from_zero=False):
        """
        Return grid index of the given month
        """
        for col in self.columns_index:
            col_year, col_month = self.columns_index[col]
            if col_month == month:
                return col - 1 if from_zero else col
        raise ValueError(f"Month {month} can not be found in grid, should not append")

    @staticmethod
    def _grid_by_month(month_grids, columns_index):
        """
        Store month grids by month
        """
        result = OrderedDict((month, None) for month in range(1, 13))
        logger.debug("Building income statement grids by month")
        for col in columns_index:
            col_year, col_month = columns_index[col]
            col_grid = month_grids
            col_grid = col_grid.filter(IncomeStatementMeasureGrid.year == col_year)
            col_grid = col_grid.filter(IncomeStatementMeasureGrid.month == col_month)
            grid = col_grid.scalar()
            logger.debug(
                " > Column {} ({} {}) : Grid id = {}".format(
                    col,
                    col_year,
                    col_month,
                    grid.id if grid else None,
                )
            )
            result[col] = grid
        return result

    def _get_last_filled_grid(self):
        """
        Return the last grid (month) where datas were filled
        In fact if we pass here, there should be almost one

        :returns: An IncomeStatementMeasureGrid
        """
        result = None
        grids = list(self.grids.values())
        grids.reverse()
        for grid in grids:
            if grid is not None:
                result = grid
                break
        return result

    def _type_by_category(self):
        """
        Stores IncomeStatementMeasureType by category (to keep the display
        order)

        :returns: A dict {'category.id': [IncomeStatementMeasureType]}
        :rtype: dict
        """
        result = dict((category.id, []) for category in self.categories)
        # On  est sûr d'avoir au moins une grille
        last_grid = self._get_last_filled_grid()
        if not last_grid:
            logger.error("All grids are void")
            return result
        types = IncomeStatementMeasure.get_measure_types(last_grid.id)

        for type_ in types:
            # Les types donc la catégorie a été désactivé entre temps doit
            # toujours apparaitre
            if type_.category not in self.categories:
                self.categories.append(type_.category)
                result[type_.category.id] = []
            result[type_.category.id].append(type_)
        return result

    def _get_month_cell(self, grid, type_id):
        """
        Return the value to display in month related cells
        """
        result = 0

        if grid is not None:
            measure = grid.get_measure_by_type(type_id)
            if measure is not None:
                result = measure.get_value()

        return result

    def compile_rows(self):
        """
        Collect the output grid corresponding to the current grid list

        Stores all datas in rows (each row matches a measure_type)
        Compute totals and ratio per line, and an indicator to tell if a line is full of zeroes.

        :returns: generator yielding 3-uples (type, row, contains_only_zeroes) where type is a
        IncomeStatementMeasureType instance and row contains the datas of the
        grid row for the given type (15 columns).
        :rtype: tuple
        """
        for category in self.categories:
            for type_ in self.types[category.id]:
                row = []
                sum = 0
                contains_only_zeroes = True
                for month, grid in list(self.grids.items()):
                    value = self._get_month_cell(grid, type_.id)
                    if value != 0:
                        contains_only_zeroes = False
                    sum += value
                    row.append(value)

                row.append(sum)
                percent = math_utils.percent(sum, self.turnover, 0)
                row.append(percent)

                yield type_, contains_only_zeroes, row

    def format_datas(self):
        """
        Format all numeric datas to strings in localized formats
        """
        for row in self.rows:
            for index, data in enumerate(row[2]):
                row[2][index] = format_float(data, precision=2, wrap_decimals=True)

    def get_updated_at(self):
        """
        Return the last date of the data after a celery update
        """
        dates_updated_at = []
        for month, grid in self.grids.items():
            if grid is not None:
                dates_updated_at.append(grid.updated_at)

        logger.debug(dates_updated_at)

        # Get rid of None values
        dates_updated_at = list(filter(None, dates_updated_at))

        if not dates_updated_at:
            return None
        else:
            return max(dates_updated_at)


class YearGlobalGridWithFormulas(YearGlobalGrid):
    """
    Like YearGlobalGrid, but will generate totals as spreadsheet formulas instead of numbers.

    Internaly, passes `SpreadsheetFormula` instances instead of `str` to allow exporter to distinguish a formula from an str.
    """

    def __init__(self, syntax: SpreadSheetSyntax, *args, **kwargs):
        self.syntax = syntax
        super().__init__(*args, **kwargs)

    def format_datas(self):
        pass

    def build_indexes(self, grids):
        super().build_indexes(grids)

        # Index of indicator and category members rows.
        self.cells_index = CellsIndex()

        # Use this same iteration despite the 1st level of iteration being useless to
        # keep the same order
        for category, types in self.types.items():
            for type_ in types:
                self.cells_index.register(type_)

    def compile_rows(self):
        """
        Collect the output grid corresponding to the current grid list

        Stores all datas in rows (each row matches a measure_type)
        Compute totals and ratio per line

        :returns: generator yielding 2-uple (type, row) where type is a
        IncomeStatementMeasureType instance and row contains the datas of the
        grid row for the given type (15 columns).
        :rtype: tuple
        """

        compiler = SpreadSheetCompiler(
            self.syntax,
            self.cells_index,
            x_offset=1,  # skip: label col
            y_offset=3,  # skip: Title col, blank col, month name col
        )

        # Flattens the list of types that are stored by category
        types = (
            type_ for category in self.categories for type_ in self.types[category.id]
        )

        for type_index, type_ in enumerate(types):
            row = []
            contains_only_zeroes = True
            last_nonempty_grid = None

            for month, grid in list(self.grids.items()):
                # Make an exception for formulas cells with no data (future month) :
                # copy the data from prev month, re-using grid from prev month (if any)
                # allowing formula to be generated and thus spreadsheet hand-filled
                if (
                    grid is None
                    and last_nonempty_grid is not None
                    and type_.is_computed_total
                ):
                    x_offset = month - last_nonempty_grid.month
                    value = self._get_month_cell(
                        last_nonempty_grid, type_.id, compiler, x_offset
                    )
                else:
                    value = self._get_month_cell(grid, type_.id, compiler)
                    last_nonempty_grid = grid

                row.append(value)
                if value != 0:
                    contains_only_zeroes = False

            sum_formula = compiler.get_row_sum_formula(type_index, len(row))
            sum_xy_coordinates = len(row), type_index

            percentage_formula = compiler.get_row_percentage_formula(
                sum_xy_coordinates, self.turnover
            )

            row.append(sum_formula)
            row.append(percentage_formula)

            yield type_, contains_only_zeroes, row

    def _get_month_cell(
        self,
        grid: IncomeStatementMeasureGrid,
        type_id,
        compiler: SpreadSheetCompiler,
        formula_x_offset: int = 0,
    ):
        """
        :formula_x_offset: force the formula to be shifted to right by a given number of column

        Return the value to display in month related cells
        """
        result = 0
        if grid is not None:
            measure = grid.get_measure_by_type(type_id)
            if measure is not None:
                if measure.measure_type.is_computed_total:
                    x_coordinate = (
                        self.get_column_index_by_month(grid.month, from_zero=True)
                        + formula_x_offset
                    )
                    result = compiler.get_column_formula(
                        measure.measure_type, x_coordinate
                    )
                else:
                    result = measure.get_value()

        return result


class CompanyIncomeStatementMeasuresListView(BaseListView):
    use_paginate = False
    default_sort = "month"
    sort_columns = {"month": "month"}
    filter_button_label = "Changer"
    filter_button_icon = False
    filter_button_css = "btn btn-primary"
    year = get_current_financial_year_value()
    financial_year = get_current_financial_year_data()

    def get_schema(self):
        return get_income_statement_measures_list_schema(self.get_company_id())

    @property
    def title(self):
        return f"Comptes de résultat"

    @property
    def title_detail(self):
        return f"(enseigne {self.context.name})"

    def get_company_id(self):
        """
        Return the company_id from which to fetch the grids. If there is multiple
        companies with the same analytical account we use the oldest company.
        """
        return Company.get_id_by_analytical_account(self.context.code_compta)

    def query(self):
        """
        Collect the grids we present in the output
        """
        query = self.request.dbsession.query(IncomeStatementMeasureGrid)
        query = query.options(
            joinedload(IncomeStatementMeasureGrid.measures, innerjoin=True)
        )
        query = query.filter(
            IncomeStatementMeasureGrid.company_id == self.get_company_id()
        )
        return query

    def filter_year(self, query, appstruct):
        """
        Filter the current query by a given year
        """
        year = appstruct.get("year")
        if year not in (None, colander.null):
            self.year = int(year)
            self.financial_year = get_financial_year_data(year)

        logger.debug("Filtering by year : %s" % year)
        query = query.filter(
            or_(
                and_(
                    IncomeStatementMeasureGrid.year
                    == self.financial_year["start_year"],
                    IncomeStatementMeasureGrid.month
                    >= self.financial_year["start_month"],
                ),
                and_(
                    IncomeStatementMeasureGrid.year == self.financial_year["end_year"],
                    IncomeStatementMeasureGrid.month <= self.financial_year["end_year"],
                ),
            )
        )
        query = query.order_by(
            IncomeStatementMeasureGrid.year, IncomeStatementMeasureGrid.month
        )
        return query

    def _display_years_in_headers(self):
        return self.financial_year["start_year"] != self.financial_year["end_year"]

    def more_template_vars(self, response_dict):
        """
        Add template datas in the response dictionnary
        """
        month_grids = response_dict["records"]
        logger.debug("MONTH : {}".format(month_grids.count()))
        year_turnover = self.context.get_turnover(
            self.financial_year["start_date"],
            self.financial_year["end_date"],
        )

        grid = YearGlobalGrid(self.year, month_grids, year_turnover)
        grid.format_datas()
        response_dict["grid"] = grid
        response_dict["current_year"] = get_current_financial_year_value()
        response_dict["selected_year"] = self.year
        response_dict["display_years_in_headers"] = self._display_years_in_headers()
        response_dict["show_zero_rows"] = self.appstruct.get("show_zero_rows")
        response_dict["show_decimals"] = self.appstruct.get("show_decimals")
        response_dict["export_xls_url"] = self.request.route_path(
            INCOME_STATEMENT_GRIDS_ROUTE_EXPORT,
            id=self.context.id,
            extension="xls",
            _query=self.request.GET,
        )
        response_dict["export_ods_url"] = self.request.route_path(
            INCOME_STATEMENT_GRIDS_ROUTE_EXPORT,
            id=self.context.id,
            extension="ods",
            _query=self.request.GET,
        )
        return response_dict


class IncomeStatementMeasureGridXlsView(CompanyIncomeStatementMeasuresListView):
    """
    Xls output
    """

    _factory = XlsExporter
    syntax = XLSXSyntax()
    grid = None

    @property
    def filename(self):
        return "compte_de_resultat_{}.{}".format(
            self.year,
            self.request.matchdict["extension"],
        )

    def _init_grid(self, query):
        year_turnover = self.context.get_turnover(
            self.financial_year["start_date"],
            self.financial_year["end_date"],
        )
        self.grid = YearGlobalGridWithFormulas(
            self.syntax, self.year, query, year_turnover
        )

    def _init_writer(self, writer_options=None):
        writer = self._factory(options=writer_options)
        writer.add_title(
            "Compte de résultat de {} pour l’année {}".format(
                self.context.name,
                self.year,
            ),
            width=15,
        )
        writer.add_breakline()
        headers = [""]
        display_years = self._display_years_in_headers()
        for i in range(1, 13):
            year, month = self.grid.columns_index[i]
            month_label = short_month_name(month).capitalize()
            if display_years:
                month_label += " {}".format(str(year)[2:])
            headers.append(month_label)
        headers.append("TOTAL")
        headers.append("% CA")
        writer.add_headers(headers)
        return writer

    def _mk_writer_options(self, appstruct):
        if appstruct.get("show_decimals", False):
            decimal_places = "2"
        else:
            decimal_places = "0"
        return {"decimal_places": decimal_places}

    def _build_return_value(self, schema, appstruct, query):
        self._init_grid(query)
        writer = self._init_writer(self._mk_writer_options(appstruct))
        writer._datas = []
        for type_, contains_only_zeroes, row in self.grid.rows:
            row_options = {
                "hidden": not appstruct.get("show_zero_rows") and contains_only_zeroes,
                "highlight": type_.is_total,
            }
            row_datas = [type_.label]
            row_datas.extend(row)
            writer.add_row(row_datas, options=row_options)
        writer.set_column_options(column_index=0, column_style_name="wide_column")
        write_file_to_request(self.request, self.filename, writer.render())
        return self.request.response


class IncomeStatementMeasureGridOdsView(IncomeStatementMeasureGridXlsView):
    _factory = OdsExporter
    syntax = ODSSyntax()


def includeme(config):
    config.add_view(
        IncomeStatementMeasureGridListView,
        route_name=UPLOAD_ITEM_INCOME_STATEMENT_ROUTE,
        permission=PERMISSIONS["global.generate_accounting_measures"],
        renderer="/accounting/income_statement_grids.mako",
    )
    config.add_view(
        CompanyIncomeStatementMeasuresListView,
        route_name=INCOME_STATEMENT_GRIDS_ROUTE,
        permission=PERMISSIONS["company.view_accounting"],
        renderer="/accounting/income_statement_measures.mako",
    )
    config.add_view(
        IncomeStatementMeasureGridXlsView,
        route_name=INCOME_STATEMENT_GRIDS_ROUTE_EXPORT,
        permission=PERMISSIONS["company.view_accounting"],
        match_param="extension=xls",
    )
    config.add_view(
        IncomeStatementMeasureGridOdsView,
        route_name=INCOME_STATEMENT_GRIDS_ROUTE_EXPORT,
        permission=PERMISSIONS["company.view_accounting"],
        match_param="extension=ods",
    )

    config.add_company_menu(
        parent="accounting",
        order=1,
        label="Comptes de résultat",
        route_name=INCOME_STATEMENT_GRIDS_ROUTE,
        route_id_key="company_id",
    )
