# Digital Contract Hub (POC)

A High-Precision RAG Assistant for Legal Documents featuring Agentic OCR and Cross-lingual Query Translation. Built specifically to handle complex Scanned PDFs and structured tables that traditional RAG systems fail to process.

## 🌟 Key Features
- **Agentic OCR (`unstructured`)**: Visually scans and extracts text + HTML tables from scanned images.
- **Stateful Title Tracking**: Solves the "orphan table" problem by remembering and passing down physical document headings into chunk metadata.
- **AI Table Summarization**: Uses Gemini 2.5 Flash to generate semantic text summaries of raw HTML tables before embedding, making pricing and SLA clauses fully searchable.
- **Cross-lingual Query Translation**: Users can chat in Vietnamese. The system translates the query to English for Vector Search, and translates the answer back to Vietnamese with exact citations (Source, Page, Clause).

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.10+**
- **Tesseract OCR**: Required for scanning images.
  - **Windows**: Download and install from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
  - Add the installation path (usually `C:\Program Files\Tesseract-OCR`) to your system's `PATH` environment variable.

### 2. Install Dependencies
Clone the repository and install the required Python packages:

```bash
git clone <your-repo-url>
cd OnPoint
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
*(Note: If you don't have a `requirements.txt`, you can install manually: `pip install streamlit langchain langchain-google-genai langchain-chroma unstructured[pdf] sentence-transformers python-dotenv`)*

### 3. Environment Variables
Create a `.env` file in the root directory (`OnPoint/`) and add your Gemini API Key:
```env
GEMINI_API_KEY=your_google_api_key_here
```

## 💻 How to Run the App

1. Activate your virtual environment (if not already active).
2. Start the Streamlit app:
```bash
cd streamlit_app
streamlit run app.py
```
3. Open your browser at `http://localhost:8501`.
4. Upload a contract (PDF) on the sidebar and click **"Phân tích & Số hóa"**.
5. Wait for the processing to finish (1-2 minutes for scanned PDFs).
6. Start asking questions in Vietnamese in the chat box!

## ⚠️ Limitations & Trade-offs
- **Latency**: This POC uses a local Tesseract OCR engine which is highly CPU-intensive and slow. In a production environment, this should be replaced with a managed Cloud OCR (like AWS Textract).
- **Single-turn QA**: Currently, the assistant answers one-off questions. Memory can be added for multi-turn conversations in future iterations.

## 🧠 Core Logic (For Developers)
If you want to see the algorithmic design (Chunking, Prompts, Stateful Logic) without the UI, please refer to the Jupyter Notebook: `Digital_Contract_Hub_Full.ipynb`.
