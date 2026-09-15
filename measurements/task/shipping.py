def shipping_cost(weight_kg: float) -> float:
    """Price of posting one parcel, in euros.

    5.00 covers the first 2 kg.
    Every started kilogram above 2 kg adds 1.50.
    So 2.5 kg costs 6.50, and 4 kg costs 8.00.
    """
    if weight_kg <= 2:
        return 5.00
    return 5.00 + (weight_kg - 2) * 1.50
