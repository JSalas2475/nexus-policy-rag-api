import pytest

from app import create_app
from app.rag.chunking import chunk_documents
from app.rag.ingestion import load_all_documents, parse_document
from app.config import settings


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "index_loaded" in data
    assert "model" in data


def test_index_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Policy Assistant" in response.data


def test_chat_requires_question(client):
    response = client.post("/chat", json={})
    assert response.status_code == 400


def test_chat_with_mock(client, mocker):
    mock_response = mocker.Mock()
    mock_response.answer = "New employees receive 15 PTO days annually. [pto-policy: PTO Accrual for New Employees]"
    mock_response.citations = [
        {
            "doc_id": "pto-policy",
            "title": "Pto Policy",
            "section": "PTO Accrual for New Employees",
            "snippet": "New full-time employees receive 15 PTO days annually",
            "source_path": "data/policies/pto-policy.md",
        }
    ]
    mock_response.latency_ms = 100.0
    mock_response.refused = False

    mocker.patch("app.routes.chat.get_rag_pipeline").return_value.is_index_loaded.return_value = True
    mocker.patch("app.routes.chat.get_rag_pipeline").return_value.answer.return_value = mock_response

    response = client.post("/chat", json={"question": "How many PTO days?"})
    assert response.status_code == 200
    data = response.get_json()
    assert "answer" in data
    assert "citations" in data
    assert len(data["citations"]) >= 1


def test_create_app_import():
    app = create_app()
    assert app is not None


def test_load_documents():
    sections = load_all_documents(settings.policies_dir)
    assert len(sections) >= 10


def test_chunk_documents():
    sections = load_all_documents(settings.policies_dir)
    chunks = chunk_documents(sections[:5], seed=42)
    assert len(chunks) >= 5
    assert all(chunk.metadata.get("doc_id") for chunk in chunks)


def test_parse_html():
    html_path = settings.policies_dir / "travel-policy.html"
    if html_path.exists():
        sections = parse_document(html_path)
        assert len(sections) >= 1

def test_parse_txt():
    txt_path = settings.policies_dir / "incident-reporting.txt"
    if txt_path.exists():
        sections = parse_document(txt_path)
        assert len(sections) >= 1
