# Invoice-to-Pay Validation Agent

An AI-powered **Invoice-to-Pay Validation Agent** that automatically extracts information from an Invoice and Purchase Order, converts the extracted information into structured Pydantic models, and validates both documents using an LLM-based validation agent.

The application uses **LangGraph** to orchestrate the complete workflow and provides a web-based frontend for uploading documents, monitoring the workflow, viewing extracted information, and reviewing validation results.

---

## 🚀 Features

- Upload Invoice PDF
- Upload Purchase Order PDF
- Extract document information
- Convert extracted information into structured Pydantic models
- Validate Invoice against Purchase Order
- Compare:
  - Product
  - Quantity
  - Unit Price
  - Line Amount
- Handle missing information using `REVIEW`
- Detect mismatches using `MISMATCH`
- Return `MATCH` when all required information matches
- Display validation results in an HTML table
- Highlight mismatched cells

---

# 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │     User Upload     │
                         │                     │
                         │   Invoice PDF       │
                         │   Purchase Order    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Extract Node     │
                         │                     │
                         │ Extract Invoice &   │
                         │ Purchase Order Text │
                         └──────────┬──────────┘
                                    │
                   ┌────────────────┴────────────────┐
                   │                                 │
                   ▼                                 ▼
        ┌─────────────────────┐           ┌─────────────────────┐
        │  Invoice Schema     │           │ Purchase Order      │
        │       Node          │           │    Schema Node      │
        │                     │           │                     │
        │ Extract structured  │           │ Extract structured  │
        │ Invoice information │           │ Purchase Order data │
        └──────────┬──────────┘           └──────────┬──────────┘
                   │                                 │
                   └────────────────┬────────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Validation Node   │
                         │                     │
                         │ Compare Invoice &   │
                         │ Purchase Order      │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │  Validation Result  │
                         │                     │
                         │ MATCH               │
                         │ MISMATCH            │
                         │ REVIEW              │
                         └─────────────────────┘

```
# Install Dependencies
```python
pip install -r requirements.txt
```

# Start Application
```python
python app.py

```text
MIT License

```
