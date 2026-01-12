import pytest
from dotenv import load_dotenv

from src.api.app import app

load_dotenv()


@pytest.fixture(scope="session")
def client():
    client = app.test_client()
    return client


@pytest.fixture(scope="session")
def sample_documents():
    """Sample documents for testing."""
    from langchain_core.documents import Document

    return [
        Document(
            page_content="The Nürburgring is a motorsports complex in Germany. It was built in 1927.",
            metadata={"source": "docs/Nurburgring.html", "title": "Nürburgring - Wikipedia"}
        ),
        Document(
            page_content="The Mercedes-Benz M196 engine was a straight-8 Formula One engine used in 1954-1955.",
            metadata={"source": "docs/Mercedes-Benz M196 engine.html", "title": "Mercedes-Benz M196 engine - Wikipedia"}
        ),
        Document(
            page_content="Formula One is the highest class of international racing for open-wheel single-seater formula "
                         "racing cars.",
            metadata={"source": "docs/Formula One.html", "title": "Formula One - Wikipedia"}
        ),
    ]