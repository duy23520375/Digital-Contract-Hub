import json
import os
import re
from dotenv import load_dotenv
from unstructured.partition.pdf import partition_pdf
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../../.env'), override=True)
llm_flash = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.1
)

def extract_elements(pdf_path):
    print(f"Partitioning documents from {pdf_path}...")
    elements = partition_pdf(
        filename=pdf_path,
        strategy='hi_res',
        infer_table_structure=True, 
        extract_image_block_types=['Image'], 
        extract_image_block_to_payload=True 
    )
    print(f"Extracted {len(elements)} elements")
    return elements

def parse_contract_info(elements):
    full_text = "\n\n".join([str(el) for el in elements])
    
    prompt = f"""
    Bạn là một trợ lý pháp lý AI. Hãy đọc văn bản hợp đồng sau và trích xuất thông tin dưới dạng JSON CHUẨN XÁC theo cấu trúc:
    {{
      "parties": ["Tên bên A", "Tên bên B"],
      "effective_date": "Ngày hiệu lực",
      "amount": "Tóm tắt về tiền tệ, phí dịch vụ",
      "key_clauses": [
        {{"clause_name": "Tên điều khoản 1", "summary": "Tóm tắt ngắn"}}
      ]
    }}
    Tuyệt đối KHÔNG xuất ra markdown. Chỉ xuất JSON thuần.
    
    Văn bản:
    {full_text}
    """
    try:
        response = llm_flash.invoke([HumanMessage(content=prompt)])
        text_content = response.content
        
        match = re.search(r'\{.*\}', text_content, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            return json.loads(text_content.strip())
    except Exception as e:
        print(f"Lỗi trích xuất JSON OCR: {e}")
        try:
            return {"Thông báo": "Gemini không trả về định dạng JSON chuẩn", "Nội dung gốc": text_content}
        except:
            return {"error": "Lỗi không xác định"}
