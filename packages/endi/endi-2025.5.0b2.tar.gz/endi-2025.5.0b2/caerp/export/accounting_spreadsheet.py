import string
import logging
from collections import defaultdict
from typing import (
    Dict,
    List,
    Tuple,
)

from caerp.compute.parser import NumericStringParser
from caerp.models.accounting.base import BaseAccountingMeasureType
from caerp.utils.compat import Iterable


from openpyxl.utils import get_column_letter

logger = logging.getLogger(__name__)


class NumericStringSpreadsheetReducer:
    """
    Reduce a parsed numeric string to a spreadsheet formula

    By compiling it to Excel/Libreoffice formulas.

    As supported functions have same signature in .ods/.xlsx, this is a generic Reducer
    that can be used for both formats.

    Expects input in the format of NumericStringParser output.

    Does support brace vars : will keep them as-is.

    Eg: transforms ["{fu}", "2",  "+",  "ABS"] to "ABS({fu}+2)"
    """

    # Supported functions are unary operations
    functions = {
        "abs": "ABS",
        "trunc": "TRUNC",
        "round": "ROUND",
    }

    # Use same char in numeric string and spreadsheet formulas
    operators = "+-*/"

    @classmethod
    def reduce(cls, stack: List[str]) -> str:
        """

        :param stack: example : ["2", "{thing}", "+" "round"]
        :return: The xls/ods formula for this expression
        """

        op = stack.pop()
        if op == "unary -":
            op1 = cls.reduce(stack)
            return f"-1 * {op1}"
        if op in cls.operators:
            op2 = cls.reduce(stack)
            op1 = cls.reduce(stack)
            out = f"{op1} {op} {op2}"
            if op in "+-":
                # Keep correct operation priority
                # can lead to useless parenthesis
                return f"({out})"
            else:  # /*
                return out
        elif op in cls.functions:
            return f"{cls.functions[op]}({cls.reduce(stack)})"
        elif op.startswith("{"):
            return op  # brace vars, returned as is
        else:  # Number
            return op


class CellContent(str):
    """
    Represents a cell content with additional cell-related props

    A wrapper arround str including a style_variant property
    """

    STYLE_VARIANT_PERCENTAGE = "percentage"

    def __new__(cls, value, style_variant=None, *args, **kwargs):
        ret = super().__new__(cls, value, *args, **kwargs)
        ret.style_variant = style_variant
        return ret


class SpreadsheetFormula(CellContent):
    """
    Represents a spreadsheet formula

    Basically a wrapper arround str to do basic validation and to be able to differentiate
    scalar cell data (= a str/int/float…) from formula cell data (= the formula itself).
    """

    def __new__(cls, value, *args, **kwargs) -> "SpreadsheetFormula":
        if not value.startswith("="):
            raise ValueError(f'"{value}" does not look like a spreadsheet formula.')
        return super().__new__(cls, value, *args, **kwargs)


class CellsIndex:
    """
    Register the order of registration of Measure types

    To be able to get
    - the registration index of a given type label in the future
    - the indexes list that are related to a given category label
    """

    def __init__(self):
        self.types_index: Dict[str, int] = {}
        self.categories_index: Dict[str, List[int]] = defaultdict(list)
        self.types_counter = 0

    def category_lookup(self, label: str) -> List[int]:
        return self.categories_index[label]

    def type_lookup(self, label: str) -> int:
        return self.types_index[label]

    def register(self, measure_type: BaseAccountingMeasureType):
        self.types_index[measure_type.label] = self.types_counter
        if not measure_type.is_computed_total:
            self.categories_index[measure_type.category.label].append(
                self.types_counter
            )

        self.types_counter += 1


# Shortcut types:
# Point in a two-dimensional space (zero-indexed)
XYCoords = Tuple[int, int]
# Vector in two-dimensional space (zero-indexed)
XYRange = Tuple[XYCoords, XYCoords]


def to_ranges(coords: Iterable[XYCoords]) -> Iterable[XYRange]:
    """
    Transforms a bunch on unordered cell coords into optimized ranges

    Ranges are optimized on the y-axis only.
    >>> list(to_ranges([(0, 0)]))
    [((0, 0), (0, 0))]

    >>> list(to_ranges([(0, 0), (0, 1), (0, 2)]))  # optimize
    [((0, 0), (0, 2))]

    >>> list(to_ranges([(0, 0), (0, 1), (0, 2), (0, 4)]))  # optimize partialy
    [((0, 0), (0, 2)), ((0, 4), (0, 4))]
    """
    y_sorted_coords = sorted(coords, key=lambda x_y: x_y[1])
    ranges = (((x, y), (x, y)) for x, y in y_sorted_coords)
    return optimize_y_ranges(ranges)


def optimize_y_ranges(ranges: Iterable[XYRange]) -> Iterable[XYRange]:
    """
    Regroup vertically adjacent ranges.
    """
    # current_start, current_stop represent the range currently in preparation
    current_start, current_stop = None, None
    for start, stop in ranges:
        if current_start is None:
            current_start = start
            current_stop = stop
        else:
            current_next_cell_in_column = (current_stop[0] + 0, current_stop[1] + 1)
            if start == current_next_cell_in_column:
                # extend range:
                current_stop = stop
            else:
                # end range
                yield current_start, current_stop
                current_start, current_stop = start, stop

    if current_start is not None:
        # a range is pending, yield it.
        yield current_start, current_stop


SpreadsheetRange = Tuple[str, str]
SpreadsheetCoords = str


class SpreadsheetCoordinatesMapper:
    """
    Maps x, y numeric-style coords to spreadsheet-style coords

    - change coordinates notation (0,0) ➡ "A1"
    - apply an optional offset
    """

    def __init__(self, x_offset: int = 0, y_offset: int = 0):
        self.x_offset, self.y_offset = x_offset, y_offset

    def to_spreadsheet_coords(self, x: int, y: int) -> SpreadsheetCoords:
        # In enDI, indexes are from 0. In spreadsheets, they are from 1.
        return "{}{}".format(
            get_column_letter(self.x_offset + x + 1), self.y_offset + y + 1
        )

    def to_spreadsheet_ranges(
        self, ranges: Iterable[XYRange]
    ) -> Iterable[SpreadsheetRange]:
        """
        Given a list of XY ranges, transforrms them into a spreadsheet cells reference

        Eg: [((0,1),  (0,3)), ((0,5), (0,5)] ➡ [["A2":"A4"];["A6":"A6"]"]
        """
        return (
            (self.to_spreadsheet_coords(*start), self.to_spreadsheet_coords(*stop))
            for start, stop in ranges
        )


class SpreadSheetSyntax:
    ARGS_SEPARATOR = NotImplemented
    RANGE_SEPARATOR = NotImplemented


class ODSSyntax(SpreadSheetSyntax):
    ARGS_SEPARATOR = ";"
    RANGE_SEPARATOR = ":"


class XLSXSyntax(SpreadSheetSyntax):
    ARGS_SEPARATOR = ","
    RANGE_SEPARATOR = ":"


class SpreadSheetReferenceFormatter(string.Formatter):
    """
    Resolve category/types names as spreadsheet expressions

    Supports : excel / libreoffice.

    eg. "=ROUND({grand total}) + {others}"
      could become =ROUND(SUM(A1:A6)) + B12
    """

    def __init__(
        self,
        index: CellsIndex,
        mapper: SpreadsheetCoordinatesMapper,
        x_coordinate: int,
        syntax: SpreadSheetSyntax,
    ):
        self.index = index
        self.mapper = mapper
        self.x_coordinate = x_coordinate
        self.syntax = syntax

    def get_value(self, key, args, kwargs):
        try:
            y_coordinates = [self.index.type_lookup(label=key)]
        except KeyError:
            y_coordinates = self.index.category_lookup(label=key)

        # [(0, 1), (0, 2), (0, 3)]
        related_cell_coords = [(self.x_coordinate, y) for y in y_coordinates]
        # ((0,1),(0,3))
        related_cell_ranges = to_ranges(related_cell_coords)
        # (('A1', 'A3'),)
        spreadsheet_ranges = self.mapper.to_spreadsheet_ranges(related_cell_ranges)
        # 'A1:A3'
        spreadsheet_ranges_as_str = self.syntax.ARGS_SEPARATOR.join(
            f"{start}{self.syntax.RANGE_SEPARATOR}{stop}" if start != stop else start
            for start, stop in spreadsheet_ranges
        )

        if len(related_cell_coords) == 0:
            return "0"
        elif len(related_cell_coords) == 1:
            return spreadsheet_ranges_as_str  # EG: "A6"
        else:
            return f"SUM({spreadsheet_ranges_as_str})"  # eg: A6:A7


class SpreadSheetCompiler:
    """
    Given an identifiers index and an offset, generate formulas.

    Resolve computed measuure types into spreadsheet formulas.

    Supports : excel / libreoffice through syntax arg.
    """

    def __init__(
        self,
        syntax: SpreadSheetSyntax,
        index: CellsIndex,
        x_offset: int,
        y_offset: int,
    ):
        self.index = index
        self.mapper = SpreadsheetCoordinatesMapper(x_offset, y_offset)
        self.parser = NumericStringParser()
        self.syntax = syntax

    def get_column_formula(
        self, type_: BaseAccountingMeasureType, x_coordinate: int
    ) -> SpreadsheetFormula:
        """
        Given a BaseAccountingMeasureType, build a spreadsheet formula.

        :param x_coordinate: the formula column index
        """
        if type_.total_type == "categories":
            category_labels = type_.account_prefix.split(",")
            complex_formula = "+".join(f"{{{label}}}" for label in category_labels)
        elif type_.total_type == "complex_total":
            complex_formula = type_.account_prefix
        else:
            raise ValueError(f"Unsupported total_type: {type_.total_type}")

        parsed_stack = self.parser.parse(complex_formula)

        # Numeric string to spreadsheet formula with brace-variables
        templated_formula = NumericStringSpreadsheetReducer.reduce(parsed_stack)

        # Resolve brace-variables (category names)
        formatter = SpreadSheetReferenceFormatter(
            self.index, self.mapper, x_coordinate, self.syntax
        )
        final_formula = formatter.format(templated_formula)

        return SpreadsheetFormula(f"={final_formula}")

    def get_row_sum_formula(
        self, y_coordinate: int, cols_nb: int
    ) -> SpreadsheetFormula:
        start_cell = self.mapper.to_spreadsheet_coords(0, y_coordinate)
        stop_cell = self.mapper.to_spreadsheet_coords(cols_nb - 1, y_coordinate)
        return SpreadsheetFormula(
            f"=SUM({start_cell}{self.syntax.RANGE_SEPARATOR}{stop_cell})"
        )

    def get_row_percentage_formula(
        self, fraction_cell_coords: XYCoords, total: float
    ) -> SpreadsheetFormula:
        fraction_cell = self.mapper.to_spreadsheet_coords(*fraction_cell_coords)
        return SpreadsheetFormula(
            f"={fraction_cell}/{total}",
            style_variant=SpreadsheetFormula.STYLE_VARIANT_PERCENTAGE,
        )
