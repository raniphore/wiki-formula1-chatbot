from src.retrieval.retriever import DocumentRetriever


def test_singleton_pattern():
    """Test that retriever implements singleton pattern correctly."""
    from src.retrieval.retriever import DocumentRetriever

    # Reset singleton
    DocumentRetriever._instance = None
    DocumentRetriever._vectorstore = None

    retriever1 = DocumentRetriever()
    retriever2 = DocumentRetriever()

    # Should be same instance
    assert retriever1 is retriever2


def test_retrieval_documents():
    retriever = DocumentRetriever(k=2)
    query = "When and where the first lombank trophy held"

    results = retriever.retrieve(query, k=2)
    assert len(results) == 2
    assert all(hasattr(doc, 'page_content') for doc in results)
    assert all(hasattr(doc, 'metadata') for doc in results)


def test_retrieval_deterministic():
    retriever = DocumentRetriever()
    query = "Who won the Formula 1 World Championship in 2021?"

    docs1 = retriever.retrieve(query, k=5)
    docs2 = retriever.retrieve(query, k=5)

    assert len(docs1) == len(docs2)
    assert [d.page_content for d in docs1] == [
        d.page_content for d in docs2
    ]


def test_retrieval_respects_k():
    retriever = DocumentRetriever()
    query = "Who is Lewis Hamilton?"

    docs = retriever.retrieve(query, k=3)
    assert len(docs) == 3

