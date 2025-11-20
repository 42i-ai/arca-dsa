import json
from typing import Any, List, Dict, Tuple


def load_data(file_path: str) -> Any:
    """Load JSON data from a file and return a Python object.

    This function supports three common formats:
    - a single JSON object (returns dict)
    - a JSON array (returns list)
    - newline-delimited JSON (NDJSON) where each line is a JSON object (returns list)

    If the file is empty, returns an empty list.

    Args:
        file_path: path to the input file

    Returns:
        Parsed JSON as Python data structures (dict, list, etc.)

    Raises:
        json.JSONDecodeError: when the file contains invalid JSON and cannot be parsed as NDJSON.
    """
    p = file_path
    with open(p, "r", encoding="utf-8") as f:
        text = f.read()

    if not text.strip():
        return []

    # First, try to parse whole-file JSON (object or array)
    try:
        parsed = json.loads(text)
        return parsed
    except json.JSONDecodeError:
        # Fallback: try NDJSON (one JSON object per non-empty line)
        objs: List[Any] = []
        for ln in text.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            objs.append(json.loads(ln))
        return objs


def simulate_dequeued_data(carts) -> List:
    """
    Simple normalizer for an iterable of carts.

    Returns a list of dicts with keys: cart_id, user_id, items.
    - Accepts lists/iterables of dict-like carts.
    - Tolerates missing fields and non-list items (wraps into list).
    - Skips non-dict entries.
    Designed to be small and explicit for interview/code-challenge use.
    """
    result: List[Dict[str, Any]] = []
    carts = carts["carts"]

    try:
        iterator = iter(carts)
    except TypeError:
        return result

    for cart in iterator:
        if not isinstance(cart, dict):
            pass
        else:
            raw_items = cart.get("items", []) or []
            wrapped_items = raw_items if isinstance(
                raw_items, list) else [raw_items]
            normalized_items: List[Dict[str, Any]] = []
            items = cart.get("items", []) or []
            for it in wrapped_items:
                if isinstance(it, dict):
                    product_id = it.get("product_id")
                    if product_id is not None:
                        try:
                            quantity = int(it.get("quantity") or 0)
                        except (TypeError, ValueError):
                            quantity = 0
                        try:
                            unit_price = float(it.get("unit_price") or 0)
                        except (TypeError, ValueError):
                            unit_price = 0.0
                        if quantity != 0:
                            normalized_items.append({
                                "product_id": product_id,
                                "quantity": quantity,
                                "unit_price": unit_price
                            })

            result.append({
                "cart_id": cart.get("cart_id") or cart.get("id"),
                "user_id": cart.get("user_id") or cart.get("user"),
                "items": normalized_items,
            })

    return {"carts": result}


def discount_rule(quantity: int, unity_price: float) -> float:
    """
      Function which the discount is applyed. 
      To calculate the rule we will use the mod
      # integer modulo
      a = 17
      b = 3
      r = a % b          # 2
      q, r = divmod(a, b)  # q==5, r==2
      discount = unity_price * 5 
      TODO:
      we can get rule from an api.
    """
    discount = 0.00
    r = quantity % 3          # 2
    q, r = divmod(quantity, 3)  # q==5, r==2
    discount = unity_price * q
    return discount


def agregate_results_by_id(cart: List[dict]) -> Dict[str, dict]:
    """
      Agregate product by cart, item and sku
      using hash solve the problem in O(1) for search 
      and O(n) when need to aggregate keys
    """

    carts = cart.get("carts", [])
    result = {"carts": []}

    for cart in carts:
        aggregated = {}
        for item in cart.get("items", []):
            sku = item.get("product_id")
            qty = int(item.get("quantity") or 0)
            unit_price = float(item.get("unit_price") or 0.00)
            key = (sku, unit_price)
            if key not in aggregated:
                aggregated[key] = {"product_id": sku,
                                   "quantity": 0, "unit_price": unit_price}
            aggregated[key]["quantity"] += qty
        items_out = []
        for (pid, up), info in aggregated.items():
            qty = info["quantity"]
            upf = info["unit_price"]
            discount = discount_rule(quantity=qty, unity_price=upf)
            total_price = round((qty * upf) - discount, 2)
            items_out.append({
                "product_id": pid,
                "quantity": qty,
                "unit_price": upf,
                "total_price": total_price,
                "discount": round(discount, 2)
            })

        result["carts"].append({
            "cart_id": cart.get("cart_id"),
            "user_id": cart.get("user_id"),
            "items": items_out
        })
    return result


if __name__ == "__main__":
    # red-green implementation for the code
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

    agrregation_result = agregate_results_by_id(sample_input_cart)
    assert agrregation_result == sample_output_cart
