from datamodel_code_generator.format import CustomCodeFormatter

EXTRA_LINES = [
    "from decimal import Decimal",
    "from pydantic import PlainSerializer",
    "from typing import Annotated",
    '',
    "DecimalValue = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used='json')]"
]


class CodeFormatter(CustomCodeFormatter):
    def apply(self, code: str) -> str:
        # Example transformation:
        code = code.replace(": float", ": DecimalValue")
        return '\n'.join(EXTRA_LINES + ['', code])
