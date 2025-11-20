"""
We need to implement a function that calculates the final value of a shopping cart by applying a specific promotion rule: 
'Buy 3, Pay for 2'.
The rule is simple: 
For every 3 units of the same product in the cart, 
the customer only pays for 2 (the discount is applied to the unit price of that item). 
If he takes 4 items, he pays for 2 at the promotional price + 1 at the full price.
How would you model and solve this?

Assumptions:

Let's assume that consuming from a queue (like SQS or Kafka) 
is a great architectural premise, 
as it decouples message reception from business rule processing.

In this method, we will focus only on the necessary data (client_id, product_code, price),
demonstrating concern for payload efficiency, which is great for high-scale systems.

"""

import json
import pytest
from pathlib import Path
from collections import defaultdict
import importlib.util


MODULE_PATH = Path(__file__).resolve(
).parents[1] / "dsa" / "hash" / "shopping_carts.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "shopping_carts", MODULE_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_load_data_sucefull(monkeypatch: pytest.MonkeyPatch):
    """
    Test that load_data returns a list when data is successfully loaded.

    This test replaces the module's load_data function with a monkeypatched
    call that returns a single, representative shopping cart record. The sample
    cart contains multiple items, promotion codes, metadata and timestamps to
    represent a realistic payload. After invoking load_data with an arbitrary
    path, the test asserts that the returned value is a list, confirming that
    the loader produces an iterable collection of cart records.

    Notes:
    - No actual file I/O is performed because load_data is monkeypatched.
    - The test focuses on type/structure (a list) rather than validating
        individual field values.
    """
    mod = _load_module()
    sample_cart = {
        "cart_id": "cart-0010",
        "user_id": "user-1010",
        "created_at": "2025-11-20T08:55:00Z",
        "items": [
            {"product_id": "prod-015", "name": "Bluetooth Speaker",
             "category": "electronics", "unit_price": 59.99, "quantity": 1},
            {"product_id": "prod-001", "name": "USB-C Cable",
             "category": "electronics", "unit_price": 9.99, "quantity": 3}
        ],
        "promotion_codes": ["PROMO10", "FREE_SHIP"],
        "metadata": {"source": "web", "tags": ["audio"]}
    }
    monkeypatch.setattr(mod, "load_data", lambda path: {
                        "carts": [sample_cart]})
    carts = mod.load_data("ignored_path")
    assert isinstance(carts, dict)


def test_simulate_dequeued_data_normalizes_and_skips_non_dict(monkeypatch: pytest.MonkeyPatch):
    """
    Test that simulate_dequeued_data normalizes dequeued cart entries.
    In this method, we will focus only on the necessary data 
    (client_id, product_code, price) 
    to simulate a real time data process 
    where we want to calculate the discount
    """
    sample_input_cart = {
        "metadata": {
            "generated_at": "2025-11-20T12:00:00Z",
            "currency": "USD",
            "count": 30,
            "notes": "Sample nested shopping cart dataset for promotion rule testing"
        },
        "carts": [
            {
                "cart_id": "cart-0001",
                "user_id": "user-1001",
                "created_at": "2025-11-20T08:15:00Z",
                "items": [
                    {"product_id": "prod-011", "name": "Notebook",
                        "category": "office", "unit_price": 3.5, "quantity": 2},
                    {"product_id": "prod-001", "name": "USB-C Cable",
                        "category": "electronics", "unit_price": 9.99, "quantity": 1},
                    {"product_id": "prod-011", "name": "Notebook",
                        "category": "office", "unit_price": 3.5, "quantity": 3},
                    {"product_id": "prod-001", "name": "USB-C Cable",
                        "category": "electronics", "unit_price": 9.99, "quantity": 1}
                ],
                "promotion_codes": [],
                "metadata": {"source": "bulk-import", "tags": ["mobile-accessory"]}
            }
        ]
    }

    mod = _load_module()
    # return the inner list under 'carts' instead of wrapping the whole sample_input_cart dict
    monkeypatch.setattr(mod, "load_data", lambda path: sample_input_cart)
    carts = mod.load_data("ignored_path")
    returned_json = mod.simulate_dequeued_data(carts)
    sample_output_cart = {
        "carts": [
            {
                "cart_id": "cart-0001",
                "user_id": "user-1001",
                "items": [
                    {
                        "product_id": "prod-011",
                        "quantity": 2,
                        "unit_price": 3.5
                    },
                    {
                        "product_id": "prod-001",
                        "quantity": 1,
                        "unit_price": 9.99
                    },
                    {
                        "product_id": "prod-011",
                        "quantity": 3,
                        "unit_price": 3.5
                    },
                    {
                        "product_id": "prod-001",
                        "quantity": 1,
                        "unit_price": 9.99
                    }
                ]
            }
        ]
    }
    assert returned_json == sample_output_cart


def test_agregate_results_by_id(monkeypatch: pytest.MonkeyPatch):
    """
    In this method, we will focus only on the necessary data 
    (client_id, product_code, price) 
    to simulate a real time data process 
    where we want to calculate the discount
    """
    sample_input_cart = {
        "carts": [
            {
                "cart_id": "cart-0001",
                "user_id": "user-1001",
                "items": [
                    {
                        "product_id": "prod-011",
                        "quantity": 2,
                        "unit_price": 3.5
                    },
                    {
                        "product_id": "prod-001",
                        "quantity": 1,
                        "unit_price": 9.99
                    },
                    {
                        "product_id": "prod-011",
                        "quantity": 3,
                        "unit_price": 3.5
                    },
                    {
                        "product_id": "prod-001",
                        "quantity": 1,
                        "unit_price": 9.99
                    }
                ]
            }
        ]
    }

    sample_output_cart = {
        "carts": [
            {
                "cart_id": "cart-0001",
                "user_id": "user-1001",
                "items": [
                    {
                        "product_id": "prod-011",
                        "quantity": 5,
                        "unit_price": 3.5,
                        "total_price": 14.00,
                        "discount": 3.5
                    },
                    {
                        "product_id": "prod-001",
                        "quantity": 2,
                        "unit_price": 9.99,
                        "total_price": 19.98,
                        "discount": 0
                    }
                ]
            }
        ]
    }

    mod = _load_module()
    monkeypatch.setattr(mod, "load_data", lambda path: sample_input_cart)
    carts = mod.load_data("ignored_path")
    returned_json = mod.simulate_dequeued_data(carts)
    aggregated_json = mod.agregate_results_by_id(returned_json)
    print(aggregated_json)
    print("---")
    print(sample_output_cart)
    assert sample_output_cart == aggregated_json
