def place(client, customer, product, qty):
    return client.post("/api/orders", json={
        "customer_id": customer["id"], "items": [{"product_id": product["id"], "quantity": qty}]})


def stock(client, product):
    return client.get(f"/api/products/{product['id']}").json()["stock"]


def test_create_order_decrements_stock_and_totals(client, customer, product):
    r = place(client, customer, product, 3)
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert float(body["total"]) == 3 * 49.99
    assert body["customer_name"] == "Ada Lovelace"
    assert body["items"][0]["product_name"] == "Runner"
    assert stock(client, product) == 17


def test_unit_price_is_snapshotted(client, customer, product):
    order = place(client, customer, product, 1).json()
    client.put(f"/api/products/{product['id']}", json={
        "name": "Runner", "sku": "SKU-1", "price": "99.00", "stock": 19,
        "category_id": product["category_id"]})
    again = client.get(f"/api/orders/{order['id']}").json()
    assert float(again["items"][0]["unit_price"]) == 49.99


def test_duplicate_lines_are_merged(client, customer, product):
    r = client.post("/api/orders", json={"customer_id": customer["id"], "items": [
        {"product_id": product["id"], "quantity": 2}, {"product_id": product["id"], "quantity": 3}]})
    assert r.status_code == 201
    assert len(r.json()["items"]) == 1 and r.json()["items"][0]["quantity"] == 5


def test_insufficient_stock(client, customer, product):
    r = place(client, customer, product, 21)
    assert r.status_code == 400
    assert stock(client, product) == 20
    assert client.get("/api/orders").json() == []


def test_order_validation(client, customer, product):
    assert place(client, customer, product, 0).status_code == 422
    assert client.post("/api/orders",
                       json={"customer_id": customer["id"], "items": []}).status_code == 422
    assert client.post("/api/orders", json={"customer_id": 999, "items": [
        {"product_id": product["id"], "quantity": 1}]}).status_code == 422
    assert client.post("/api/orders", json={"customer_id": customer["id"], "items": [
        {"product_id": 999, "quantity": 1}]}).status_code == 422


def test_inactive_product_rejected(client, customer, product):
    client.put(f"/api/products/{product['id']}", json={
        "name": "Runner", "sku": "SKU-1", "price": "49.99", "stock": 20, "is_active": False})
    assert place(client, customer, product, 1).status_code == 400


def test_status_flow_and_invalid_transition(client, customer, product):
    oid = place(client, customer, product, 1).json()["id"]
    for nxt in ("paid", "shipped", "delivered"):
        r = client.patch(f"/api/orders/{oid}/status", json={"status": nxt})
        assert r.status_code == 200 and r.json()["status"] == nxt
    r = client.patch(f"/api/orders/{oid}/status", json={"status": "cancelled"})
    assert r.status_code == 409
    assert client.patch(f"/api/orders/{oid}/status", json={"status": "bogus"}).status_code == 422


def test_cancel_restocks(client, customer, product):
    oid = place(client, customer, product, 4).json()["id"]
    assert stock(client, product) == 16
    client.patch(f"/api/orders/{oid}/status", json={"status": "cancelled"})
    assert stock(client, product) == 20


def test_delete_only_cancelled(client, customer, product):
    oid = place(client, customer, product, 1).json()["id"]
    assert client.delete(f"/api/orders/{oid}").status_code == 409
    client.patch(f"/api/orders/{oid}/status", json={"status": "cancelled"})
    assert client.delete(f"/api/orders/{oid}").status_code == 204
    assert client.get(f"/api/orders/{oid}").status_code == 404


def test_list_filters(client, customer, product):
    a = place(client, customer, product, 1).json()["id"]
    place(client, customer, product, 1)
    client.patch(f"/api/orders/{a}/status", json={"status": "paid"})
    assert len(client.get("/api/orders").json()) == 2
    assert [o["id"] for o in client.get("/api/orders", params={"status": "paid"}).json()] == [a]
    assert len(client.get("/api/orders", params={"customer_id": customer["id"]}).json()) == 2
    assert client.get("/api/orders", params={"customer_id": 999}).json() == []
