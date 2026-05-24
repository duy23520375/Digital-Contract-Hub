# Digital Contract Hub (POC)

Hệ thống Hỏi đáp (RAG) độ chính xác cao dành cho Tài liệu Pháp lý, tích hợp Agentic OCR và Dịch thuật Truy vấn Xuyên ngôn ngữ. Được thiết kế đặc biệt để xử lý các file PDF dạng ảnh quét (Scanned PDFs) và bảng biểu phức tạp mà các hệ thống RAG truyền thống không thể giải quyết.

## Tính năng cốt lõi
- Agentic OCR (unstructured): Quét hình ảnh trực quan và trích xuất văn bản cùng bảng biểu HTML từ các file ảnh chụp.
- Stateful Title Tracking: Giải quyết vấn đề "bảng biểu mồ côi" (orphan table) bằng cách ghi nhớ và kế thừa các tiêu đề vật lý của tài liệu vào siêu dữ liệu (metadata) của các đoạn cắt (chunk).
- AI Table Summarization: Sử dụng Gemini 2.5 Flash để tạo bản tóm tắt ngữ nghĩa từ các bảng HTML thô trước khi đưa vào cơ sở dữ liệu vector, giúp các điều khoản về giá cả và SLA hoàn toàn có thể tìm kiếm được.
- Cross-lingual Query Translation: Người dùng có thể đặt câu hỏi bằng Tiếng Việt. Hệ thống tự động dịch câu hỏi sang Tiếng Anh để tra cứu trong VectorDB, sau đó dịch câu trả lời về lại Tiếng Việt kèm theo trích dẫn chính xác (Nguồn, Trang, Tên điều khoản).

## Cài đặt và Khởi chạy

### 1. Yêu cầu hệ thống
- Python 3.10+
- Tesseract OCR: Bắt buộc để quét hình ảnh.
  - Windows: Tải và cài đặt từ UB-Mannheim/tesseract (https://github.com/UB-Mannheim/tesseract/wiki).
  - Thêm đường dẫn cài đặt (thường là C:\Program Files\Tesseract-OCR) vào biến môi trường PATH của Windows.

### 2. Cài đặt thư viện
Clone repository và cài đặt các thư viện Python cần thiết:

```bash
git clone <your-repo-url>
cd OnPoint
python -m venv venv
venv\Scripts\activate
pip install -r streamlit_app/requirements.txt
```

### 3. Biến môi trường
Tạo một file `.env` ở thư mục gốc (`OnPoint/`) và cấu hình API Key của Gemini:
```env
GEMINI_API_KEY=your_google_api_key_here
```

## Hướng dẫn sử dụng

1. Kích hoạt môi trường ảo (nếu chưa kích hoạt).
2. Khởi động ứng dụng Streamlit:
```bash
cd streamlit_app
streamlit run app.py
```
3. Mở trình duyệt web tại `http://localhost:8501`.
4. Ở thanh bên trái, tải lên một hợp đồng (định dạng PDF) và nhấn "Phân tích & Số hóa".
5. Chờ hệ thống xử lý (khoảng 1-2 phút đối với PDF dạng ảnh quét).
6. Bắt đầu đặt câu hỏi bằng Tiếng Việt trong khung chat để tra cứu.

## Hạn chế và Đánh đổi (Trade-offs)
- Độ trễ (Latency): Bản POC này sử dụng Tesseract OCR chạy cục bộ, tiêu tốn nhiều tài nguyên CPU và khá chậm. Trong môi trường thực tế (Production), module này nên được thay thế bằng các dịch vụ Cloud OCR (như AWS Textract hoặc Google Cloud Vision).
- QA Đơn lượt (Single-turn QA): Hiện tại, trợ lý ảo chỉ trả lời các câu hỏi đơn lẻ. Tính năng bộ nhớ (Memory) cho các cuộc hội thoại đa lượt có thể được tích hợp trong các bản cập nhật sau.

## Kiến trúc Lõi (Dành cho Developer)
Để xem chi tiết về luồng thiết kế thuật toán (Chunking, Prompts, Stateful Logic) mà không cần giao diện người dùng, vui lòng tham khảo file Jupyter Notebook: `Digital_Contract_Hub_Full.ipynb`.
