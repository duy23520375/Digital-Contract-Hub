import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'streamlit_app'))
from src.ocr_extractor import llm_flash
from langchain_core.messages import HumanMessage

try:
    print("Testing LLM...")
    res = llm_flash.invoke([HumanMessage(content="Hello")])
    print("Success:", res.content)
except Exception as e:
    print("Exception occurred:", type(e).__name__)
    print("Details:", e)
