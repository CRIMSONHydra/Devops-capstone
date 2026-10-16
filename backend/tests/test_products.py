def test_product_crud(client, category):
    payload = {"name": "Boot", "sku": "B-1", "price": "10.50", "stock": 3,
               "category_id": category["id"]}
    r = client.post("/api/products", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["category"]["name"] == "Shoes" and body["is_active"] is True

    pid = body["id"]
    payload["price"] = "12.00"
    r = client.put(f"/api/products/{pid}", json=payload)
    assert r.status_code == 200 and float(r.json()["price"]) == 12.0

    assert client.delete(f"/api/products/{pid}").status_code == 204
    assert client.get(f"/api/products/{pid}").status_code == 404


def test_duplicate_sku(client, product):
    r = client.post("/api/products", json={"name": "X", "sku": "SKU-1", "price": "1"})
    assert r.status_code == 409


def test_invalid_values(client):
    assert client.post("/api/products",
                       json={"name": "X", "sku": "S", "price": "-1"}).status_code == 422
    assert client.post("/api/products",
                       json={"name": "X", "sku": "S", "price": "1", "stock": -1}).status_code == 422


def test_unknown_category_rejected(client):
    r = client.post("/api/products",
                    json={"name": "X", "sku": "S", "price": "1", "category_id": 999})
    assert r.status_code == 422


def test_search_filter_pagination(client, category):
    for i in range(5):
        client.post("/api/products", json={
            "name": f"Item {i}", "sku": f"SK-{i}", "price": "5", "stock": i * 10,
            "category_id": category["id"]})
    client.post("/api/products", json={"name": "Lamp", "sku": "LMP", "price": "9", "stock": 50})

    page = client.get("/api/products", params={"limit": 2}).json()
    assert page["total"] == 6 and len(page["items"]) == 2

    assert client.get("/api/products", params={"q": "lamp"}).json()["total"] == 1
    assert client.get("/api/products", params={"category_id": category["id"]}).json()["total"] == 5
    low = client.get("/api/products", params={"low_stock": True}).json()
    assert {p["sku"] for p in low["items"]} == {"SK-0", "SK-1"}  # stock 0 and 10 (<= threshold)


def test_delete_product_in_order_conflicts(client, product, customer):
    client.post("/api/orders", json={"customer_id": customer["id"],
                                     "items": [{"product_id": product["id"], "quantity": 1}]})
    assert client.delete(f"/api/products/{product['id']}").status_code == 409
