from src.generation.generator import AnswerGenerator


def test_generate_with_no_documents():
    generator = AnswerGenerator()

    answer = generator.generate("Unanswerable question", [])

    assert answer == "I don't know based on the provided documents."


def test_build_context(sample_documents):
    """Test context building from documents."""

    generator = AnswerGenerator()
    context = generator._build_context(sample_documents)

    # Check that context contains source information
    assert "Nurburgring.html" in context
    assert "Mercedes-Benz M196 engine.html" in context


def test_build_prompt(sample_documents):
    generator = AnswerGenerator()
    query = "What is the Nurburgring?"
    prompt = generator._build_prompt(query, sample_documents)

    # Check query is in prompt
    assert "What is the Nurburgring?" in prompt

    # Check context is included
    assert "motorsports complex" in prompt

    # Check instructions about source citation
    assert "document filenames" in prompt.lower()


def test_generate_with_documents(sample_documents):
    # Mock LLM response
    class FakeLLM:
        def invoke(self, messages):
            class R:
                content = "The Nürburgring is a motorsports complex.\n\nSources:\n- Nurburgring.html"
            return R()

    generator = AnswerGenerator()
    generator.llm = FakeLLM()
    result = generator.generate("What is the Nurburgring?", sample_documents)

    # Check result
    assert "motorsports complex" in result
    assert "Nurburgring.html" in result
