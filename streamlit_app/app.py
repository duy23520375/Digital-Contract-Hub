import streamlit as st
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

from src.ocr_extractor import extract_elements, parse_contract_info
from src.indexer import index_contract, get_retriever

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'), override=True)
api_key = os.getenv("GEMINI_API_KEY")
print(api_key)
# Khởi tạo mô hình
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=api_key,
    temperature=0.1
)

st.set_page_config(page_title="Digital Contract Hub", layout="wide", page_icon="📜")
st.title("OnPoint Digital Contract Hub")
st.markdown("*A High-Precision RAG Assistant with Agentic OCR & Query Translation*")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📁 Quản lý hợp đồng")
    uploaded_file = st.file_uploader("Upload file hợp đồng (PDF)", type="pdf")
    
    if uploaded_file:
        # KIỂM TRA XEM FILE ĐÃ ĐƯỢC XỬ LÝ CHƯA
        is_processed = st.session_state.get('processed_file') == uploaded_file.name
        
        if not is_processed:
            if st.button("Phân tích & Số hóa"):
                with st.status("Đang xử lý tài liệu...", expanded=True) as status:
                    pdf_path = os.path.join("temp_contract.pdf")
                    with open(pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 1. Trích xuất Elements (Hỗ trợ Scanned PDF qua Tesseract)
                    st.write("1. Phân tích tài liệu với Unstructured.io (Hỗ trợ Scanned PDF)...")
                    elements = extract_elements(pdf_path)
                    
                    # 2. JSON Parsing
                    st.write("2. Trích xuất Key Fields (Gemini 2.5 Flash)...")
                    extracted_data = parse_contract_info(elements)
                    if extracted_data:
                        st.session_state.extracted_data = extracted_data
                    
                    # 3. Indexing với AI Table Summary
                    st.write("3. Nhận diện Điều khoản, Xử lý Bảng biểu & Indexing...")
                    index_contract(elements, filename=uploaded_file.name)
                    
                    status.update(label="✅ Đã hoàn tất Số hóa!", state="complete", expanded=False)
                    st.success("Hệ thống đã sẵn sàng để truy vấn.")
                    
                    # Lưu lại trạng thái đã xử lý cho file này
                    st.session_state.processed_file = uploaded_file.name
                    st.rerun() # Refresh lại để khóa nút
        else:
            st.success(f"✅ Đã số hóa thành công: {uploaded_file.name}")
            st.info("💡 Bạn có thể xem kết quả cấu trúc ở bảng bên phải hoặc bắt đầu đặt câu hỏi.")
                
    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử Chat"):
        st.session_state.chat_history = []
        st.rerun()

# --- KHU VỰC HIỂN THỊ DỮ LIỆU CÓ CẤU TRÚC (JSON) ---
if 'extracted_data' in st.session_state:
    with st.expander("📊 Structured records — searchable by party, date, clause type, or free-text", expanded=True):
        st.json(st.session_state.extracted_data)

st.markdown("---")
st.subheader("💬 Trợ lý Pháp lý Đa ngôn ngữ (QA)")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Tìm kiếm điều khoản hợp đồng (Ví dụ: Chi phí lưu kho là bao nhiêu?)..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    retriever = get_retriever()
    if retriever is None:
        st.error("Vui lòng upload hợp đồng ở Sidebar trước khi chat.")
    else:
        with st.chat_message("assistant"):
            status_container = st.container()
            with status_container:
                st.info("🌐 Đang dịch câu hỏi (Query Translation) & Tra cứu VectorDB...")
            
            # --- QUERY TRANSLATION ---
            # Dịch câu hỏi sang Tiếng Anh để tra cứu hiệu quả với Embedding tiếng Anh
            translation_prompt = f"Translate the following question into English. Return ONLY the English translation.\\nQuestion: {user_input}"
            search_query = llm.invoke([HumanMessage(content=translation_prompt)]).content.strip()
            
            # --- RETRIEVAL ---
            docs = retriever.invoke(search_query)
            
            # --- CHUẨN BỊ CONTEXT ---
            context_text = ""
            for idx, doc in enumerate(docs):
                source = doc.metadata.get('source', 'Unknown')
                page = doc.metadata.get('page', 'Unknown')
                clause = doc.metadata.get('clause', 'Unknown')
                
                context_text += f"\\n--- Trích đoạn {idx+1} [Nguồn: {source} | Trang: {page} | Điều khoản: {clause}] ---\\n"
                context_text += doc.page_content + "\\n"
                    
            # --- GENERATION ---
            prompt = f"""
            Bạn là một trợ lý pháp lý AI. 
            Dựa TRỰC TIẾP vào các đoạn trích hợp đồng dưới đây, hãy trả lời câu hỏi của người dùng.
            NẾU KHÔNG TÌM THẤY THÔNG TIN, HÃY TRẢ LỜI LÀ "Không có thông tin", TUYỆT ĐỐI KHÔNG BỊA ĐẶT.
            BẮT BUỘC: Trích dẫn chính xác Nguồn, Số Trang và Tên Điều khoản ở cuối câu trả lời (Ví dụ: Nguồn: Hợp đồng ABC | Trang: 2 | Điều khoản: Bảo mật).
            QUAN TRỌNG: Trả lời bằng TIẾNG VIỆT, ngắn gọn, súc tích.
            
            ĐOẠN TRÍCH:
            {context_text}
            
            CÂU HỎI CỦA NGƯỜI DÙNG: {user_input}
            """
            
            try:
                response = llm.invoke([HumanMessage(content=prompt)])
                st.markdown(response.content)
                st.session_state.chat_history.append({"role": "assistant", "content": response.content})
            except Exception as e:
                st.error(f"Lỗi: {e}")
                
            status_container.empty()
