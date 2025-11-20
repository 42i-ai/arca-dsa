"""
Problem Definition: Você trabalha no time de Logística da VTEX. Recebemos um pedido com vários itens, e temos múltiplos estoques (warehouses) espalhados pelo país. Sua missão é escrever um algoritmo que decida **de qual estoque** retirar cada item para atender o pedido."

"""
import json
from typing import Tuple, Dict, List, Any


def simulate_sqs_dequeue(order: dict) -> Dict:
    return order


def simulate_redis_cache(inventory: List[dict]) -> Dict:
    inventory_map: dict = {item["warehouse_id"]: item["stock"] for item in inventory}
    return inventory_map


def check_warehouse_stock(order: dict, inventory: dict) -> Any:
    """
      Complexidade o(n) se tivermos todos os item em um warehouse o for item sempre vai sair quando não tiver um item.
    """
    id = order["id"]
    items = order["items"]
    order_with_warehouse = {}
    for warehouse_id, stock in inventory.items():
        order_with_warehouse = {
            "id": id, "items": []
        }
        for item in items:
            if stock.get(item.get("sku", None)) >= int(item.get("qty", 0)):
                order_with_warehouse["items"].append({
                    "sku": item.get("sku"), "qty": item.get("qty"), "warehouse_id": warehouse_id})
                if len(order_with_warehouse["items"]) == len(order["items"]):
                    return order_with_warehouse
            else:
                pass
    if len(order_with_warehouse["items"]) != len(order["items"]):
        return None
    return order_with_warehouse


def split_order(order: dict, inventory: dict) -> Any:
    """
     Ao pegar grandes blocos de estoque de quem tem mais, você evita "picotar" o pedido em 10 armazéns diferentes com 1 unidade cada. Isso reduz custo de manuseio (picking).Análise de Complexidade: Você está certíssimo.Iterar pelos itens: $O(I)$Ordenar armazéns: $O(W \log W)$Total: $O(I \times W \log W)$.Como o número de armazéns ($W$) raramente passa de algumas centenas, isso é muito rápido na prática.
    """
    id = order["id"]
    items_order = order["items"]
    order_with_warehouse = {
        "id": id, "items": []
    }

    for item_order in items_order:
        sku = item_order.get("sku", 0)
        sorted_wh = sorted(
            inventory.items(),
            key=lambda kv: kv[1].get(sku, 0),
            reverse=True
        )
        # 10
        # 7
        quantity_need = item_order.get("qty")
        for warehouse in sorted_wh:
            quantity_shipment = 0
            if warehouse[1].get(sku, 0) >= 0:
                # 3
                # 8
                avaliable = warehouse[1].get(sku, 0)
                # 3 > 10
                # 7 < 8
                if avaliable >= quantity_need:
                    quantity_shipment = quantity_need
                    quantity_need -= quantity_need
                else:
                    # 10 - 3 = 7
                    quantity_need -= avaliable
                    quantity_shipment = avaliable
                order_with_warehouse["items"].append({
                    "sku": sku, "qty": quantity_shipment, "warehouse_id": warehouse[0]})
                if (quantity_need == 0):
                    # quando os itens já estão completos vai para o próximo item
                    break
        if quantity_need > 0:
            raise Exception(
                f"Estoque insuficiente para o item {sku}. Faltam {quantity_need} unidades.")
    return order_with_warehouse


# Caso 1 (Green) temos todos os pedido no mesmo warehouse
order_green: dict = {
    "id": "order-123",
    "items": [
        {"sku": "IPHONE", "qty": 5},
        {"sku": "CASE",   "qty": 3}
    ]
}


inventory: List[dict] = [
    {"warehouse_id": "SP", "stock": {"IPHONE": 3, "CASE": 5}},
    {"warehouse_id": "RJ", "stock": {"IPHONE": 10, "CASE": 0}},
    {"warehouse_id": "MG", "stock": {"IPHONE": 5, "CASE": 5}}  # <- MG tem tudo!
]

order_with_warehouse = check_warehouse_stock(order=simulate_sqs_dequeue(
    order=order_green), inventory=simulate_redis_cache(inventory=inventory))
print(order_with_warehouse)

# Caso 1 (RED) temos todos os pedido no mesmo warehouse
order_red: dict = {
    "id": "order-123",
    "items": [
        {"sku": "IPHONE", "qty": 15},
        {"sku": "CASE",   "qty": 3}
    ]
}

order_with_warehouse = check_warehouse_stock(order=simulate_sqs_dequeue(
    order=order_red), inventory=simulate_redis_cache(inventory=inventory))
print(order_with_warehouse)

# Case 2 Green quando não temos todos os pedidos no warehouse
order_green_case2 = {"id": "o-2", "items": [{"sku": "IPHONE", "qty": 10}]}
inventory: List[dict] = [
    {"warehouse_id": "SP", "stock": {"IPHONE": 3, "CASE": 5}},
    {"warehouse_id": "RJ", "stock": {"IPHONE": 4, "CASE": 100}},
    {"warehouse_id": "MG", "stock": {"IPHONE": 3, "CASE": 5}}  # <- MG tem tudo!
]

order_with_warehouse = split_order(order=simulate_sqs_dequeue(
    order=order_green_case2), inventory=simulate_redis_cache(inventory=inventory))
print(order_with_warehouse)


# Case 2 Green quando não temos todos os pedidos no warehouse e temos 0 em uma warehouse
order_green_case21 = {"id": "o-2", "items": [{"sku": "IPHONE", "qty": 10}]}
inventory: List[dict] = [
    {"warehouse_id": "SP", "stock": {"IPHONE": 3, "CASE": 5}},
    {"warehouse_id": "RJ", "stock": {"IPHONE": 0, "CASE": 100}},
    {"warehouse_id": "MG", "stock": {"IPHONE": 7, "CASE": 5}}  # <- MG tem tudo!
]

order_with_warehouse = split_order(order=simulate_sqs_dequeue(
    order=order_green_case21), inventory=simulate_redis_cache(inventory=inventory))
print(order_with_warehouse)
