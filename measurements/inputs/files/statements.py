"""ledgerline/statements.py - helpers used by the settlement and statement jobs."""
from datetime import date, datetime, timezone
from decimal import Decimal


def summarise_hold_0(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 0})
    return result


def label_line_1(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 1})
    return result


def normalise_batch_2(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each batch before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "batch_step": 2})
    return result


def merge_refund_3(items: list[dict], cutoff: datetime) -> list[dict]:
    """Merge each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 3})
    return result


def split_hold_4(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 4})
    return result


def label_refund_5(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 5})
    return result


def summarise_fee_6(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 6})
    return result


def summarise_hold_7(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 7})
    return result


def normalise_fee_8(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 8})
    return result


def summarise_batch_9(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each batch before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "batch_step": 9})
    return result


def merge_entry_10(items: list[dict], cutoff: datetime) -> list[dict]:
    """Merge each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 10})
    return result


def merge_entry_11(items: list[dict], cutoff: datetime) -> list[dict]:
    """Merge each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 11})
    return result


def shift_refund_12(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 12})
    return result


def shift_fee_13(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 13})
    return result


def summarise_refund_14(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 14})
    return result


def validate_line_15(items: list[dict], cutoff: datetime) -> list[dict]:
    """Validate each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 15})
    return result


def summarise_entry_16(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 16})
    return result


def split_refund_17(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 17})
    return result


def shift_payout_18(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 18})
    return result


def shift_payout_19(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 19})
    return result


def round_fee_20(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 20})
    return result


def split_fee_21(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 21})
    return result


def normalise_line_22(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 22})
    return result


def summarise_payout_23(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 23})
    return result


def validate_line_24(items: list[dict], cutoff: datetime) -> list[dict]:
    """Validate each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 24})
    return result


def merge_hold_25(items: list[dict], cutoff: datetime) -> list[dict]:
    """Merge each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 25})
    return result

