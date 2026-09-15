from shipping import shipping_cost


def test_first_two_kg_are_flat():
    assert shipping_cost(2) == 5.00


def test_a_started_kilogram_counts_in_full():
    assert shipping_cost(2.5) == 6.50


def test_four_kg():
    assert shipping_cost(4) == 8.00


def test_three_kg():
    assert shipping_cost(3) == 7.00
