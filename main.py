
from langgraph.graph import StateGraph, START, END
from invoice_po_agents import extract_node, invoice_schema_node, po_schema_node, validation_node
from typing import TypedDict, Optional

# Shared Memory for the graph
class InvoiceState(TypedDict):

    # Input paths
    invoice_path: str
    po_path: str

    # Output from your existing extract_node
    invoice_text: str
    po_text: str

    # Structured data
    invoice: Optional[dict]
    po: Optional[dict]

    # Final validation
    validation: Optional[dict]




# Create graph
graph = StateGraph(InvoiceState)


# Add nodes
graph.add_node("extract", extract_node)
graph.add_node("invoice_schema", invoice_schema_node)
graph.add_node("po_schema", po_schema_node)
graph.add_node("validation", validation_node)


# Connect nodes

graph.add_edge(START, "extract")
graph.add_edge("extract", "invoice_schema")
graph.add_edge("invoice_schema", "po_schema")
graph.add_edge("po_schema", "validation")
graph.add_edge("validation", END)

# Compile
app = graph.compile()

