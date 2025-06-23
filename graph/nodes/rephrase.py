from graph.state import GraphState
from typing import Any, Dict
from graph.chains.rephrasing import rephrasing_chain



def rephrase(state: GraphState) -> Dict[str, Any]:
    print("---REPHRASE---")
    question = state["question"]
    chat_history = state["chat_history"]
    standalone_question = rephrasing_chain.invoke(
        {"input": question, "chat_history": chat_history}
    )
    return {"question": standalone_question}