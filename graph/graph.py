from dotenv import load_dotenv

from langgraph.graph import END, StateGraph

from graph.consts import RETRIEVE, GRADE_DOCUMENTS, GENERATE
from graph.nodes import generate, grade_documents, retrieve
from graph.state import GraphState

load_dotenv()


# def decide_to_generate(state):
#     print("---ASSESS GRADED DOCUMENTS---")

#     if state["web_search"]:
#         print(
#             "---DECISION: NOT ALL DOCUMENTS ARE NOT RELEVANT TO QUESTION, INCLUDE WEB SEARCH---"
#         )
#         return WEBSEARCH
#     else:
#         print("---DECISION: GENERATE---")
#         return GENERATE


workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)

workflow.set_entry_point(RETRIEVE)
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)
workflow.add_edge(GRADE_DOCUMENTS, GENERATE)
workflow.add_edge(GENERATE, END)

app = workflow.compile()

app.get_graph().draw_mermaid_png(output_file_path="graph.png")