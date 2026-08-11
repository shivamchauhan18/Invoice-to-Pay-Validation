
from docling.document_converter import DocumentConverter
from langchain_core.output_parsers import PydanticOutputParser
from config import llm
from schema import *



# --------------------------------------------------
# 2. Docling Node
# --------------------------------------------------
def extract_node(state):

    invoice_path = state["invoice_path"]
    po_path = state["po_path"]

    converter = DocumentConverter()

    invoice_result = converter.convert(invoice_path)
    po_result = converter.convert(po_path)

    invoice_markdown = invoice_result.document.export_to_markdown()
    po_markdown = po_result.document.export_to_markdown()

    return {
        "invoice_text": invoice_markdown,
        "po_text": po_markdown
    }


def invoice_schema_node(state):

    parser = PydanticOutputParser(
        pydantic_object=Invoice
    )

    prompt = f"""
Extract the invoice information from the following document.

{parser.get_format_instructions()}

STRICT RULES:

1. Extract only information explicitly present in the document.
2. Do not invent, infer, assume, or calculate information.
3. If a field is missing, return null.
4. Every extracted value must be a string.
5. Quantity, unit price, amount, subtotal, tax, and total
   must also be strings.
6. Preserve the original value and formatting.
7. Return ONLY valid JSON.
8. Do not return explanations, Markdown, headings, or plain text.

DOCUMENT:

{state["invoice_text"]}
"""

    response = llm.invoke(prompt)

    result = parser.parse(response.content)

    return {
        "invoice": result.model_dump()
    }


def po_schema_node(state):

    parser = PydanticOutputParser(
        pydantic_object=PurchaseOrder
    )

    prompt = f"""
Extract the Purchase Order information from the following document.

{parser.get_format_instructions()}

STRICT RULES:

1. Extract only information explicitly present in the document.
2. Do not invent, infer, assume, or calculate information.
3. If a field is missing, return null.
4. Every extracted value must be a string.
5. Quantity, unit price, amount, subtotal, tax, and total
   must also be strings.
6. Preserve the original value and formatting.
7. Return ONLY valid JSON.
8. Do not return explanations, Markdown, headings, or plain text.
9. If the document is not a Purchase Order, return null
   for fields that cannot be identified.

DOCUMENT:

{state["po_text"]}
"""

    response = llm.invoke(prompt)

    result = parser.parse(response.content)

    return {
        "po": result.model_dump()
    }


def validation_node(state):

    parser = PydanticOutputParser(
        pydantic_object=ValidationResult
    )

    invoice = state["invoice"]
    po = state["po"]

    prompt = f"""
You are an Invoice-to-Pay validation agent.

Compare the Invoice with the Purchase Order.

Check every item for:
- Product
- Quantity
- Unit price
- Line amount

Rules:
- All fields match → MATCH.
- Any clear difference → MISMATCH.
- Important information missing → REVIEW.
- Compare every item.
- Show actual Invoice and PO values.
- Do not invent values.
- Ignore formatting and OCR currency differences.

The `html_table` field MUST contain a complete HTML table.

Table columns:
Item | Field | Invoice | PO | Result

Create 4 rows for every item:
Product, Quantity, Unit Price, Line Amount.

Example:

<table>
<thead>
<tr>
<th>Item</th>
<th>Field</th>
<th>Invoice</th>
<th>PO</th>
<th>Result</th>
</tr>
</thead>
<tbody>
<tr>
<td>Laptop</td>
<td>Product</td>
<td>Laptop</td>
<td>Laptop</td>
<td>MATCH</td>
</tr>
<tr>
<td>Laptop</td>
<td>Quantity</td>
<td>10</td>
<td>10</td>
<td>MATCH</td>
</tr>
<tr>
<td>Laptop</td>
<td>Unit Price</td>
<td>₹50,000</td>
<td>₹50,000</td>
<td>MATCH</td>
</tr>
<tr>
<td>Laptop</td>
<td>Line Amount</td>
<td>₹5,90,000</td>
<td>₹5,00,000</td>
<td>MISMATCH</td>
</tr>
</tbody>
</table>

IMPORTANT:
- Return the actual values in Invoice and PO columns.
- Do not return a summary instead of the table.
- Do not return Markdown.
- Do not return ```html.
- `html_table` must contain ONLY the HTML table.

INVOICE:
{invoice}

PURCHASE ORDER:
{po}

{parser.get_format_instructions()}
"""

    response = llm.invoke(prompt)

    result = parser.parse(response.content)

    return {
        "validation": result.model_dump()
    }