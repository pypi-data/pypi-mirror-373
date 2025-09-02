from datamodel_code_generator.format import CustomCodeFormatter

EXTRA_LINES = [
    "import datetime",
    "from pydantic import BeforeValidator, PlainSerializer",
    "from typing import Annotated",
    '',
    "DateYear = Annotated[datetime.date, BeforeValidator(lambda x: datetime.datetime.strptime(x, '%Y')), PlainSerializer(lambda x: x.strftime('%Y'))]"
]

_NEW_FORMAT = 'Union[datetime.date, DateYear]'


class CodeFormatter(CustomCodeFormatter):
    def apply(self, code: str) -> str:
        # Example transformation:
        code = code.replace("startDate: Optional[str]", f"startDate: Optional[{_NEW_FORMAT}]")
        code = code.replace("startDate: str", f"startDate: {_NEW_FORMAT}")

        code = code.replace("endDate: Optional[str]", f"endDate: Optional[{_NEW_FORMAT}]")
        code = code.replace("endDate: str", f"endDate: {_NEW_FORMAT}")

        code = code.replace("date: Optional[str]", f"date: Optional[{_NEW_FORMAT}]")

        code = code.replace("dates: Optional[List[str]]", f"dates: Optional[List[{_NEW_FORMAT}]]")

        return '\n'.join(EXTRA_LINES + ['', code])
