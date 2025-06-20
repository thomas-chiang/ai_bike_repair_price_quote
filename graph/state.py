from typing import Dict, List, TypedDict, Any


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
        can_answer_question: whether document can confidently answer question
    """

    question: str
    chat_history: List[Dict[str, Any]]
    generation: str
    documents: List[str]
    can_answer_question: bool