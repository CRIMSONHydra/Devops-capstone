def test_empty_dashboard(client):
    body = client.get("/api/dashboard/stats").json()
    assert float(body["total_revenue"]) == 0
    assert body["total_orders"] == 0
    assert body["orders_by_status"]["pending"] == 0
    assert body["top_products"] == [] and body["recent_orders"] == []


def test_dashboard_aggregates(client, customer, product):
    def order(qty):
        return client.post("/api/orders", json={
            "customer_id": customer["id"],
            "items": [{"product_id": product["id"], "quantity": qty}]}).json()["id"]

    o1, o2 = order(2), order(5)
    client.patch(f"/api/orders/{o2}/status", json={"status": "cancelled"})

    body = client.get("/api/dashboard/stats").json()
    assert float(body["total_revenue"]) == 2 * 49.99  # cancelled excluded
    assert body["total_orders"] == 2
    assert body["orders_by_status"]["pending"] == 1 and body["orders_by_status"]["cancelled"] == 1
    assert body["total_customers"] == 1 and body["total_products"] == 1
    assert body["top_products"] == [
        {"product_id": product["id"], "name": "Runner", "units_sold": 2}]
    assert body["recent_orders"][0]["id"] == o2
    assert body["low_stock"] == []  # stock 18 > threshold


def test_low_stock_listed(client, category):
    client.post("/api/products", json={"name": "Scarce", "sku": "S", "price": "1", "stock": 2})
    assert [p["sku"] for p in client.get("/api/dashboard/stats").json()["low_stock"]] == ["S"]


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/api/health").json() == {"status": "ok"}
