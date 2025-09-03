from decimal import Decimal


def normalize_number(number: str | float | Decimal) -> str:
    if not isinstance(number, Decimal):
        number = Decimal(number)
    return str(number.quantize(Decimal('0.001')))