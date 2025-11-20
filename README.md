# AI Invoice Processing Pipeline

This project implements an end-to-end invoice processing pipeline using LangChain, Google Gemini, and Python. It features AI-based reasoning for data comparison (no fuzzy matching) and generates verified invoices upon successful matching.

## Features

1.  **PDF Loading**: Extracts text from PDF invoices.
2.  **Structured Extraction**: Uses LLMs to extract structured data (Pydantic models).
3.  **CRM Lookup**: Fetches reference data from a SQL database.
4.  **AI Comparison**: Performs deep semantic comparison using an LLM chain.
5.  **Verified Output**: Generates a new PDF if the data matches.

## Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Environment Variables**:
    Create a `.env` file in the root directory and add your Google API key:
    ```
    GOOGLE_API_KEY=AIza...
    ```

3.  **Initialize Database**:
    Run the setup script to create the mock CRM database:
    ```bash
    python setup_db.py
    ```

4.  **Create Sample Invoice**:
    Generate a sample PDF for testing:
    ```bash
    python create_sample_pdf.py
    ```

## Usage

Run the main pipeline with the path to your invoice PDF:

```bash
python main.py data/sample_invoice.pdf
```

## Output

- **Logs**: Check `pipeline.log` for detailed execution logs.
- **Verified Invoice**: If matched, the new PDF is saved to `output/verified_invoice.pdf`.
- **Console**: JSON output of the processing result.

## Project Structure

- `main.py`: Entry point.
- `src/`: Core logic modules.
- `data/`: Database and sample files.
- `output/`: Generated results.
