"""LLM-based answer generation with RAG."""
import os
from typing import List

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

# System prompt enforcing source-only responses
SYSTEM_PROMPT = """You are an assistant for question-answering tasks.

You must answer the question using ONLY the information provided in the SOURCES below.
Do NOT use prior knowledge.
Do NOT make up facts.

If the answer cannot be determined from the sources, say:
"I don't know based on the provided documents."

Provide a clear, concise answer followed by the list of source documents you used.

Format your response EXACTLY like this:

<your answer here>

Sources:
- <source_file_1>
- <source_file_2>

Only list sources that were actually used to answer the question. Use the actual document filenames from the metadata."""


class AnswerGenerator:
    """Generates answers using retrieved context and LLM."""

    def __init__(
            self,
            model: str = "gpt-4o-mini",
            temperature: float = 0.0
    ):
        """
        Initialize answer generator.

        Args:
            model: OpenAI model name
            temperature: LLM temperature (0 for deterministic)
        """
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.model = model
        self.temperature = temperature
        self.llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature
        )

    def _build_context(self, docs: List[Document]) -> str:
        """
        Format retrieved documents into context string.

        Args:
            docs: Retrieved documents

        Returns:
            Formatted context with source attribution
        """
        formatted_sources = []

        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "unknown")
            title = doc.metadata.get("title", "")

            # Extract just the filename from the path
            source_filename = source.split('/')[-1] if '/' in source else source

            formatted_sources.append(
                f"[SOURCE {i + 1}: {source_filename}]\n"
                f"Title: {title}\n"
                f"Content:\n{doc.page_content}\n"
            )

            # formatted_sources.append(
            #     f"SOURCE [{i + 1}]\n"
            #     f"Document: {source}\n"
            #     f"Title: {title}\n"
            #     f"Content:\n{doc.page_content}"
            # )

        return "\n\n".join(formatted_sources)

    def _build_prompt(self, query: str, docs: List[Document]) -> str:
        """
        Build the user prompt with query and context.

        Args:
            query: User's question
            docs: Retrieved documents

        Returns:
            Formatted prompt string
        """
        context = self._build_context(docs)

        return f"""QUESTION:
        {query}

        CONTEXT FROM DOCUMENTS:
        {context}

        Remember to cite sources using the actual document filenames provided above."""

    def generate(self, query: str, docs: List[Document]) -> str:
        """
        Generate answer using LLM with retrieved context.

        Args:
            query: User's question
            docs: Retrieved relevant documents

        Returns:
            Generated answer with source attribution
        """
        if not docs:
            return "I don't know based on the provided documents."

        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=self._build_prompt(query, docs))
        ]

        response = self.llm.invoke(messages)
        return response.content


if __name__ == "__main__":
    answer_generator = AnswerGenerator()
    from src.retrieval.retriever import DocumentRetriever
    retriever = DocumentRetriever()
    # query = "Who built the nuerburgring"
    query = "When and where the first lombank trophy held"
    docs = retriever.retrieve(query)
    results = answer_generator.generate(query, docs)
    print(results)