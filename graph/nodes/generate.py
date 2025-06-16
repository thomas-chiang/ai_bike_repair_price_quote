from typing import Any, Dict

from graph.chains.generation import generation_chain
from graph.state import GraphState


def generate(state: GraphState) -> Dict[str, Any]:
    print("---GENERATE---")
    question = state["question"]
    documents = state["documents"]
    can_answer_question = state["can_answer_question"]
    if can_answer_question:
        generation = generation_chain.invoke({"context": documents, "question": question})
    else:
        generation = 'I cannot answer your question. Will escalate to a human agent'
    return {"documents": documents, "question": question, "generation": generation}