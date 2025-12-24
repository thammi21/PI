# Intelligent Invoice Analysis & Matching Service

This service acts as an intelligent automation layer for finance teams, seamlessly bridging the gap between external Agent Invoices (PDFs) and internal financial records (CRM Database). It utilizes advanced AI (Azure Document Intelligence , Custom neural model trained on azure & Google Gemini) to extract, validate, and reconcile invoice data.

## 🚀 Key Features

*   **Document Intelligence**: Utilizes **Azure Document Intelligence** to accurately extract structured data (Supplier, Invoice No, Line Items, etc.) from PDF invoices.
*   **Hybrid Matching Capability**:
    *   **Fuzzy Logic**: Pre-calculates similarity scores for line item descriptions to handle matching nomenclature.
    *   **LLM Reasoning**: Uses **Google Gemini 2.0 Flash** to perform semantic analysis and making final "MATCH/MISMATCH" decisions based on context, currency, dates, and amounts.
*   **Automated Verification**: Generates a "Verified Invoice" PDF automatically upon a successful match.
*   **Detailed Logging**: Maintains a comprehensive log of the entire pipeline for audit trails and debugging.

## 🛠️ Technology Stack

*   **Language**: Python 3.10+
*   **AI/ML**:
    *   **Extraction**: Azure Document Intelligence
    *   **Reasoning**: LangChain + Google Gemini (gemini-2.0-flash)
*   **Database**: SQLite (via SQLAlchemy)
*   **Utilities**: `pydantic` (Data Validation), `thefuzz` (Fuzzy Matching), `reportlab` (PDF Generation)

## ⚙️ Setup & Installation

1.  **Clone the Repository** (if applicable):
    ```bash
    git clone <repository-url>
    cd invoice-matcher-service/PI
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Configuration**:
    Create a `.env` file in the root directory (`PI/.env`) and add your API keys:
    ```env
    # Google Gemini API
    GOOGLE_API_KEY=your_google_api_key

    # Azure Document Intelligence
    AZURE_FORM_ENDPOINT=https://<your-resource-name>.cognitiveservices.azure.com/
    AZURE_FORM_KEY=your_azure_key
    ```

4.  **Initialize Database**:
    Before running the pipeline, ensure the CRM database is populated.
    ```bash
    python scripts/initialize_system.py
    ```

## 🏃 Usage

Run the main pipeline by pointing it to a specific invoice PDF.

```bash
python main.py "data/sample_invoices/target_invoice.pdf"
```

### Pipeline Flow

1.  **Extraction**: The system sends the PDF to Azure to extract header fields (Supplier, Date, Total) and line items.
2.  **CRM Lookup**: It interprets the Job Number and Supplier Invoice Number to fetch the corresponding record from the internal CRM database ('crm.db').
3.  **AI Comparison**:
    *   Calculates fuzzy match scores for line items.
    *   Constructs a prompt for Gemini with Extracted Data, CRM Data, and Fuzzy Scores.
    *   Gemini returns a structured `ComparisonResult`.
4.  **Result Handling**:
    *   **MATCH**: A stamped `verified_invoice.pdf` is generated in the `output/` folder.
    *   **MISMATCH**: Differences are logged and displayed in the console.

## 📂 Project Structure

```
PI/
├── data/                    # Data storage (DB, Sample Invoices)
├── output/                  # Generated Verified Invoices
├── scripts/                 # Utility scripts (Init DB, Tests)
├── src/                     # Core Source Code
│   ├── comparator.py        # Logic for Fuzzy + LLM Matching
│   ├── crm_tool.py          # Database interaction tools
│   ├── extractor_azure.py   # Azure extraction logic
│   ├── generator.py         # PDF generation logic
│   └── models.py            # Pydantic data models
├── main.py                  # Application Entry Point
├── requirements.txt         # Project Dependencies
└── README.md                # Project Documentation
```

## 📝 Logging

*   Execution logs are stored in `pipeline.log`.
*   Check this file for detailed error messages or trace information regarding the extraction and matching process.
