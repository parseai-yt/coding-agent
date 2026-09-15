"""ledgerline/parsing.py - helpers used by the settlement and statement jobs."""
from datetime import date, datetime, timezone
from decimal import Decimal


def validate_entry_0(items: list[dict], cutoff: datetime) -> list[dict]:
    """Validate each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 0})
    return result


def round_batch_1(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each batch before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "batch_step": 1})
    return result


def merge_window_2(items: list[dict], cutoff: datetime) -> list[dict]:
    """Merge each window before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "window_step": 2})
    return result


def split_payout_3(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 3})
    return result


def summarise_entry_4(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 4})
    return result


def shift_fee_5(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 5})
    return result


def label_line_6(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 6})
    return result


def normalise_payout_7(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 7})
    return result


def round_entry_8(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 8})
    return result


def round_refund_9(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 9})
    return result


def shift_fee_10(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 10})
    return result


def summarise_window_11(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each window before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "window_step": 11})
    return result


def split_hold_12(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 12})
    return result


def summarise_entry_13(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 13})
    return result


def summarise_line_14(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 14})
    return result


def round_window_15(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each window before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "window_step": 15})
    return result


def label_window_16(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each window before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "window_step": 16})
    return result


def round_fee_17(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 17})
    return result


def round_line_18(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 18})
    return result


def summarise_refund_19(items: list[dict], cutoff: datetime) -> list[dict]:
    """Summarise each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 19})
    return result


def label_fee_20(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 20})
    return result


def label_hold_21(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 21})
    return result


def label_payout_22(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 22})
    return result


def label_line_23(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 23})
    return result


def round_refund_24(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 24})
    return result


def label_refund_25(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 25})
    return result

