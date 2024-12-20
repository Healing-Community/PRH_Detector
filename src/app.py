from flask import Flask, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')    

app = Flask(__name__)

CORS(app)

# Cấu hình Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def check_content(text):
    try:
        # Prompt cụ thể và rõ ràng
        prompt = f"""Bạn là hệ thống kiểm duyệt văn bản. 
        Với đoạn văn: "{text}"
        
        Hãy trả lời CHÍNH XÁC:
        1. Nếu KHÔNG có từ ngữ tục tĩu, xúc phạm, tiêu cực: Trả lời "SAFE"
        2. Nếu CÓ từ ngữ tục tĩu, xúc phạm: Trả lời "DANGER"
        
        Chỉ trả lời NGẮN GỌN một trong hai từ trên."""
        
        response = model.generate_content(
            prompt, 
            safety_settings={
                'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
            }
        )
        
        # Lấy text và xử lý
        result_text = response.text.strip().upper()
        
        print(result_text)
        
        # Kiểm tra kết quả
        if "SAFE" in result_text:
            return {"is_safe": True, "message": "Nội dung an toàn"}
        elif "DANGER" in result_text:
            return {"is_safe": False, "message": "Phát hiện từ ngữ không phù hợp"}
        else:
            return {"is_safe": False, "message": "Không thể xác định nội dung"}
    
    except Exception as e:
        return {"is_safe": False, "message": f"Lỗi: {str(e)}"}

@app.route('/check-content', methods=['POST'])
def api_check_content():
    # Kiểm tra dữ liệu đầu vào
    if not request.json or 'text' not in request.json:
        return jsonify({
            "error": True,
            "message": "Vui lòng cung cấp nội dung văn bản để kiểm tra"
        }), 400
    
    # Lấy nội dung từ request
    text = request.json['text']
    
    # Kiểm tra nội dung
    result = check_content(text)
    
    # Trả về kết quả
    return jsonify(result)

# Route test đơn giản
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "API kiểm tra nội dung đang hoạt động",
        "endpoints": ["/check-content"]
    })

# Cài đặt debug và port
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)