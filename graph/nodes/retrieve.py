from typing import Any, Dict

from graph.state import GraphState
from ingestion import retriever
from langchain_core.documents import Document


def retrieve(state: GraphState) -> Dict[str, Any]:
    print("---RETRIEVE---")
    question = state["question"]

    documents = retriever.invoke(question)

    for chat in state["chat_history"]:
        if chat[0] == "ai" and chat[1] != "I cannot answer your question. Will escalate to a human agent":
            documents.append(Document(chat[1]))

    return {"documents": documents, "question": question}