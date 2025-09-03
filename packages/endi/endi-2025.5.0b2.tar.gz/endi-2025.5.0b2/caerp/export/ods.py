import logging
import io
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

from odf.number import (
    Number,
    NumberStyle,
    PercentageStyle,
    Text,
)
from odf.opendocument import OpenDocumentSpreadsheet
from odf.style import (
    Style,
    TextProperties,
    TableCellProperties,
    TableColumnProperties,
)
from odf.namespaces import (
    OFFICENS,
    TABLENS,
)
from odf.table import (
    TableCell,
    TableRow,
    Table,
    TableColumn,
)
from odf.text import P
from pyexcel_io import service as converter
from zope.interface import (
    implementer,
)

from caerp.export.accounting_spreadsheet import (
    SpreadsheetFormula,
    CellContent,
)
from caerp.interfaces import IExporter


WIDE_COLUMN_WIDTH = "10cm"

STYLE_VARIANTS = {
    CellContent.STYLE_VARIANT_PERCENTAGE: dict(
        family="table-cell",
        datastylename="_percentage",
    )
}


def _mk_styles(options: dict) -> List[Style]:
    decimal_places = str(options.get("decimal_places", "2"))

    formatted_number_style = NumberStyle(name="currency")
    formatted_number_style.addElement(
        Number(
            decimalplaces=decimal_places,
            minintegerdigits="1",
            grouping="true",
        )
    )

    default_cell_style = Style(
        name="default",
        family="table-cell",
        datastylename=formatted_number_style,
    )

    title_cell_style = Style(name="title", family="table-cell")
    title_cell_style.addElement(TextProperties(fontweight="bold", fontsize="16pt"))

    header_cell_style = Style(name="header", family="table-cell")
    header_cell_style.addElement(TableCellProperties(backgroundcolor="#D9EDF7"))
    header_cell_style.addElement(TextProperties(fontweight="bold"))

    highlight_cell_style = Style(
        name="highlight",
        family="table-cell",
        parentstylename=default_cell_style,
    )
    highlight_cell_style.addElement(TableCellProperties(backgroundcolor="#efffef"))
    highlight_cell_style.addElement(TextProperties(fontweight="bold"))

    # Used in "percentage" style variant
    formatted_percentage_style = PercentageStyle(name="_percentage")
    formatted_percentage_style.addElement(
        Number(decimalplaces=decimal_places, minintegerdigits="1")
    )
    formatted_percentage_style.addElement(Text(text="%"))

    return [
        formatted_percentage_style,
        formatted_number_style,
        default_cell_style,
        title_cell_style,
        header_cell_style,
        highlight_cell_style,
    ]


def _mk_auto_styles():
    # Column style can *only* be automatic styles, not user-facing styles
    wide_column_style = Style(
        name="wide_column",
        family="table-column",
    )
    TableColumnProperties(parent=wide_column_style, columnwidth=WIDE_COLUMN_WIDTH)

    return [
        wide_column_style,
    ]


logger = logging.getLogger(__name__)


@implementer(IExporter)
class OdsExporter:
    """
    Those options are implemented :

    row-level : highlight, hidden
    document-level: decimal_places
    """

    title = "Export"

    def __init__(self, options: dict = None):
        if not options:
            options = {}

        self.book = OpenDocumentSpreadsheet()
        for style in _mk_styles(options):
            self.book.styles.addElement(style)

        for style in _mk_auto_styles():
            self.book.automaticstyles.addElement(style)

        self.sheet = Table(name=self.title)
        self.book.spreadsheet.addElement(self.sheet)

        self.column_props: List[Tuple[int, dict]] = []
        self.column_counter = 0
        self.columns_options: Dict[int, dict] = {}
        self.style_variants = {}

    def add_title(self, title, width):
        row = TableRow()
        cell = TableCell(stylename="title")
        cell.setAttrNS(TABLENS, "number-columns-spanned", width)
        cell.addElement(P(text=title))
        row.addElement(cell)
        self.sheet.addElement(row)

    def set_column_options(
        self, column_index: int, column_style_name=Optional[str]
    ) -> None:
        """Sets column options/styles"""
        self.columns_options[column_index] = {"column_style_name": column_style_name}

    def _apply_column_options(self):
        """
        Apply the options to columns

        This is deferred to render-time as columns cannot be handled easily by reference, but need to
        be "stacked" once.
        """
        columns_options = list(self.columns_options.items())
        columns_options.sort(key=lambda x: x[0])
        column_counter = 0

        for column_index, column_options in columns_options:
            spacer_width = column_index - column_counter - 1
            column_style_name = column_options.get("column_style_name")
            if column_style_name:
                if spacer_width > 0:
                    # Insert column properties up to our column
                    TableColumn(parent=self.sheet, numbercolumnsrepeated=spacer_width)
                # Insert our column property
                TableColumn(parent=self.sheet, stylename=column_style_name)
                column_counter = column_index

    def add_breakline(self):
        self._add_row(["\n"])

    def _get_style_variant(self, style_name: str, variant_name: str) -> str:
        """
        Create the variant on the fly if necessary

        A variant inherits a named style, adding additional properties.

        Similar to what you do in spreadsheet UX when you tweak style of an individual cell/range
        """
        identifier = f"{style_name}+{variant_name}"
        if not identifier in self.style_variants:
            try:
                variant_def = STYLE_VARIANTS[variant_name]
            except KeyError:
                raise ValueError(f'Unknown style variant: "{variant_name}"')
            else:
                style_variant = Style(
                    name=identifier,
                    parentstylename=style_name,
                    **variant_def,
                )
                self.style_variants[identifier] = style_variant
                self.book.automaticstyles.addElement(style_variant)

        return identifier

    def _get_cell(self, label, stylename=None):
        """
        Build a TableCell and adapt the format to the provided label format

        :param label: The data to write (int/float/bool/date/str)
        :param str stylename: One of the stylenames added in the __init__
        :returns: A TableCell instance
        """
        if isinstance(label, CellContent):
            # Switch if necessary to a variant of our style
            if label.style_variant:
                stylename = self._get_style_variant(stylename, label.style_variant)

        if stylename is not None:
            cell_to_be_written = TableCell(stylename=stylename)
        else:
            cell_to_be_written = TableCell()
        cell_type = type(label)
        cell_odf_type = converter.ODS_WRITE_FORMAT_COVERSION.get(cell_type, "string")
        cell_to_be_written.setAttrNS(OFFICENS, "value-type", cell_odf_type)
        cell_odf_value_token = converter.VALUE_TOKEN.get(
            cell_odf_type,
            "value",
        )
        converter_func = converter.ODS_VALUE_CONVERTERS.get(cell_odf_type, None)
        if converter_func:
            label = converter_func(label)
        if cell_odf_type != "string":
            cell_to_be_written.setAttrNS(OFFICENS, cell_odf_value_token, label)
            cell_to_be_written.addElement(P(text=label))
        else:
            if isinstance(label, SpreadsheetFormula):
                cell_to_be_written.setAttribute("formula", label)
            else:
                lines = label.split("\n")
                for line in lines:
                    cell_to_be_written.addElement(P(text=line))

        return cell_to_be_written

    def _add_row(self, labels, cell_style_name=None, row_attributes=None):
        row = TableRow(attributes=row_attributes)
        for label in labels:
            cell = self._get_cell(label, cell_style_name)
            row.addElement(cell)
        self.sheet.addElement(row)

    def add_headers(self, datas):
        self._add_row(datas, "header")

    def add_row(self, datas, options=None):
        row_attributes = {}
        options = options or {}

        if options.get("highlight", False):
            cell_style_name = "highlight"
        else:
            cell_style_name = "default"

        if options.get("hidden", False):
            # <table:table-row table:style-name="ro1" table:visibility="collapse">
            row_attributes["visibility"] = "collapse"

        self._add_row(datas, cell_style_name, row_attributes)

    def render(self, f_buf=None):
        self._apply_column_options()
        if f_buf is None:
            f_buf = io.BytesIO()
        self.book.write(f_buf)
        return f_buf
