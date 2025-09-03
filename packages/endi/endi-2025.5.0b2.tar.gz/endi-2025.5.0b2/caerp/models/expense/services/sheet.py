from typing import Union


class ExpenseSheetService:
    @classmethod
    def get_lines_justified_status(cls, instance) -> Union[None, bool]:
        """
        Get common lines justified status

        :return: True/False if all lines have same justified state. None else.
        """
        lines = instance.lines
        lines_count = len(lines)
        justified_lines_count = len([l for l in lines if l.justified])
        if justified_lines_count == 0:
            return False
        elif justified_lines_count == lines_count:
            return True
        else:
            return None
