def test_category_crud(client):
    r = client.post("/api/categories", json={"name": "Books", "description": "Paper"})
    assert r.status_code == 201
    cid = r.json()["id"]

    assert client.get(f"/api/categories/{cid}").json()["name"] == "Books"
    assert len(client.get("/api/categories").json()) == 1

    r = client.put(f"/api/categories/{cid}", json={"name": "Novels"})
    assert r.status_code == 200 and r.json()["name"] == "Novels"

    assert client.delete(f"/api/categories/{cid}").status_code == 204
    assert client.get(f"/api/categories/{cid}").status_code == 404


def test_duplicate_name_conflict(client, category):
    assert client.post("/api/categories", json={"name": "Shoes"}).status_code == 409


def test_validation_error(client):
    assert client.post("/api/categories", json={"name": ""}).status_code == 422


def test_delete_category_with_products_conflicts(client, category, product):
    assert client.delete(f"/api/categories/{category['id']}").status_code == 409


def test_missing_category_404(client):
    assert client.put("/api/categories/99", json={"name": "x"}).status_code == 404
    assert client.delete("/api/categories/99").status_code == 404
