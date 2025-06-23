from typing import Any, Dict

from graph.chains.retrieval_grader import retrieval_grader
from graph.state import GraphState


def grade_documents(state: GraphState) -> Dict[str, Any]:
    """
    Determines whether the retrieved documents are relevant to the question
    If any document is not relevant, we will set a flag can_answer_question 

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Filtered out irrelevant documents and updated can_answer_question state
    """

    print("---GRADE DOCUMENTS'S RELEVANCE TO THE QUESTION---")
    question = state["question"]
    documents = state["documents"]

    filtered_docs = []
    can_answer_question = True
    for d in documents:
        score = retrieval_grader.invoke(
            {"question": question, "document": d.page_content}
        )
        grade = score.binary_score
        if grade.lower() == "yes":
            filtered_docs.append(d)
    
    if len(filtered_docs) == 0:
        can_answer_question = False
    return {"documents": filtered_docs, "question": question, "can_answer_question": can_answer_question}