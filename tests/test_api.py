import json

from src.api.app import app


def test_health_endpoint(client):

    resp = client.get("/api/health")

    assert resp.status_code == 200
    assert resp.json["status"] == "healthy"


def test_chat_endpoint(monkeypatch, client):
    def fake_retrieve(*args, **kwargs):
        from langchain_core.documents import Document
        return [
            Document(
                page_content="Max Verstappen won the 2021 championship.",
                metadata={"source": "max_verstappen.html"}
            )
        ]

    def fake_generate(*args, **kwargs):
        return """
            Max Verstappen won the championship.
            
            Sources:
            - Max Verstappen.html
        """

    monkeypatch.setattr(
        "src.api.app.retriever",
        type("R", (), {"retrieve": fake_retrieve})()
    )

    monkeypatch.setattr(
        "src.api.app.generator",
        type("G", (), {"generate": fake_generate})()
    )

    client = app.test_client()
    resp = client.post(
        "/api/chat",
        json={"query": "Who won F1 2021?"}
    )

    assert resp.status_code == 200
    assert "Sources" in resp.json["answer"]


def test_chat_endpoint_missing_query(client):
    response = client.post(
        '/api/chat',
        data=json.dumps({}),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_chat_endpoint_empty_query(client):
    response = client.post(
        '/api/chat',
        data=json.dumps({'query': ''}),
        content_type='application/json'
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'empty' in data['error'].lower()


def test_404_endpoint(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')

    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
