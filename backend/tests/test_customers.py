def test_customer_crud(client):
    r = client.post("/api/customers",
                    json={"name": "Bob", "email": "bob@example.com", "phone": "123"})
    assert r.status_code == 201
    cid = r.json()["id"]

    assert client.get(f"/api/customers/{cid}").json()["email"] == "bob@example.com"
    r = client.put(f"/api/customers/{cid}", json={"name": "Bobby", "email": "bob@example.com"})
    assert r.json()["name"] == "Bobby"
    assert client.get("/api/customers", params={"q": "bobb"}).json()[0]["id"] == cid
    assert client.delete(f"/api/customers/{cid}").status_code == 204
    assert client.get(f"/api/customers/{cid}").status_code == 404


def test_duplicate_email(client, customer):
    r = client.post("/api/customers", json={"name": "Other", "email": "ada@example.com"})
    assert r.status_code == 409


def test_invalid_email(client):
    r = client.post("/api/customers", json={"name": "X", "email": "not-an-email"})
    assert r.status_code == 422


def test_cannot_delete_customer_with_orders(client, product, customer):
    client.post("/api/orders", json={"customer_id": customer["id"],
                                     "items": [{"product_id": product["id"], "quantity": 1}]})
    assert client.delete(f"/api/customers/{customer['id']}").status_code == 409
