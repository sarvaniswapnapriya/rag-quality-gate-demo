# src/rag/rag_pipeline.py
"""
Minimal RAG pipeline: retriever (Chroma) + generator (Gemini).
This is the system under test.
"""

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

from src.rag.prompts import ACTIVE_PROMPT


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline."""

    def __init__(self, model: str = "gemini-pro", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.embeddings = GoogleGenerativeAIEmbeddings()
        self.llm = ChatGoogleGenerativeAI(model=model, temperature=temperature)
        self.vector_store = None
        self.retriever = None

    def load_documents(self, documents: list[str]) -> None:
        """Chunk and embed documents into the vector store."""
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = []
        for doc in documents:
            chunks.extend(splitter.split_text(doc))

        self.vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=self.embeddings,
            collection_name="rag_collection",
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})

    def query(self, user_query: str) -> dict:
        """Run retrieval + generation for a single query."""
        retrieved_docs = self.retriever.get_relevant_documents(user_query)
        retrieved_context = [doc.page_content for doc in retrieved_docs]

        prompt = ChatPromptTemplate.from_template(ACTIVE_PROMPT)

        chain = (
            {
                "context": lambda x: "\n".join(retrieved_context),
                "question": RunnablePassthrough(),
            }
            | prompt
            | self.llm
        )
        response = chain.invoke(user_query)

        return {
            "query": user_query,
            "answer": response.content,
            "retrieved_context": retrieved_context,
        }


# Singleton
_pipeline: RAGPipeline | None = None


def get_pipeline(model: str = "gemini-pro", temperature: float = 0.7) -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline(model=model, temperature=temperature)
        _pipeline.load_documents(_load_knowledge_base())
    return _pipeline


def _load_knowledge_base() -> list[str]:
    """Load your company's knowledge base. Replace with your actual docs."""
    return [
        "Refund Policy: All customers are eligible for a 30-day full refund on any purchase. Returns must be initiated within 30 days of the original purchase date.",
        "Shipping: Standard shipping takes 5-7 business days. Express shipping takes 2-3 business days. Overnight options are available in most regions.",
        "Payment Methods: We accept Visa, MasterCard, American Express, PayPal, Apple Pay, and Google Pay.",
        "Order Tracking: Orders can be tracked in Account Dashboard under Order History. Customers receive automatic email updates when orders ship and arrive.",
        "Password Reset: Click 'Forgot Password' on the login page. Reset links are sent to your registered email and expire after 24 hours.",
        "Bulk Orders: Discounts are available for purchases exceeding 50 units. Contact sales@company.com for enterprise pricing.",
    ]
