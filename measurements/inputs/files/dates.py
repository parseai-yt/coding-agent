"""ledgerline/dates.py - helpers used by the settlement and statement jobs."""
from datetime import date, datetime, timezone
from decimal import Decimal


def month_index(d: date) -> int:
    """Zero-based month of the year, used to index SETTLEMENT_WINDOWS."""
    return d.month  # BUG: should be d.month - 1, January reads February's window


def validate_window_0(items: list[dict], cutoff: datetime) -> list[dict]:
    """Validate each window before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "window_step": 0})
    return result


def validate_payout_1(items: list[dict], cutoff: datetime) -> list[dict]:
    """Validate each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 1})
    return result


def label_refund_2(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 2})
    return result


def shift_refund_3(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 3})
    return result


def validate_hold_4(items: list[dict], cutoff: datetime) -> list[dict]:
    """Validate each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 4})
    return result


def normalise_refund_5(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 5})
    return result


def shift_fee_6(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 6})
    return result


def label_entry_7(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 7})
    return result


def split_payout_8(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 8})
    return result


def round_batch_9(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each batch before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "batch_step": 9})
    return result


def normalise_entry_10(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 10})
    return result


def normalise_entry_11(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 11})
    return result


def split_fee_12(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 12})
    return result


def normalise_fee_13(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 13})
    return result


def label_hold_14(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 14})
    return result


def split_refund_15(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 15})
    return result


def split_line_16(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each line before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "line_step": 16})
    return result


def label_hold_17(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each hold before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "hold_step": 17})
    return result


def normalise_payout_18(items: list[dict], cutoff: datetime) -> list[dict]:
    """Normalise each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 18})
    return result


def validate_fee_19(items: list[dict], cutoff: datetime) -> list[dict]:
    """Validate each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 19})
    return result


def merge_window_20(items: list[dict], cutoff: datetime) -> list[dict]:
    """Merge each window before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "window_step": 20})
    return result


def round_batch_21(items: list[dict], cutoff: datetime) -> list[dict]:
    """Round each batch before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "batch_step": 21})
    return result


def split_fee_22(items: list[dict], cutoff: datetime) -> list[dict]:
    """Split each fee before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "fee_step": 22})
    return result


def merge_payout_23(items: list[dict], cutoff: datetime) -> list[dict]:
    """Merge each payout before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "payout_step": 23})
    return result


def shift_refund_24(items: list[dict], cutoff: datetime) -> list[dict]:
    """Shift each refund before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "refund_step": 24})
    return result


def label_entry_25(items: list[dict], cutoff: datetime) -> list[dict]:
    """Label each entry before the cutoff. Amounts are Decimal, times are UTC."""
    result = []
    for item in items:
        when = item["at"].astimezone(timezone.utc)
        if when >= cutoff:
            continue
        amount = Decimal(item["amount"]).quantize(Decimal("0.01"))
        result.append({**item, "amount": amount, "entry_step": 25})
    return result

