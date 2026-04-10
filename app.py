from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from google import genai
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True) # Tải biến môi trường từ file .env (ghi đè nếu có thay đổi)

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24).hex() # Khóa bảo mật ngẫu nhiên nếu không cấu hình

def load_users():
    try:
        with open('users.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Thay vì dùng mật khẩu mặc định "admin123", chỉ cho đăng nhập nếu cố tình gán qua biến môi trường
        admin_pass = os.getenv("ADMIN_PASSWORD")
        if admin_pass:
            return {"admin": admin_pass}
        return {} # Từ chối đăng nhập nếu không có file hoặc cấu hình an toàn

def save_users(users_db):
    try:
        with open('users.json', 'w', encoding='utf-8') as f:
            json.dump(users_db, f, indent=4)
    except Exception as e:
        print(f"Lỗi khi lưu người dùng: {e}")

def load_stats():
    try:
        if os.path.exists('usage_stats.json'):
            with open('usage_stats.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading stats: {e}")
    
    return {
        "total_requests": 0,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "history": [] # Lưu theo ngày [{date: '2024-04-10', requests: 5, tokens: 100}, ...]
    }

def save_stats(prompt_tokens, completion_tokens):
    stats = load_stats()
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Cập nhật tổng số
    stats["total_requests"] += 1
    stats["total_prompt_tokens"] += prompt_tokens
    stats["total_completion_tokens"] += completion_tokens
    
    # Cập nhật lịch sử theo ngày
    found_today = False
    for entry in stats["history"]:
        if entry["date"] == today:
            entry["requests"] += 1
            entry["prompt_tokens"] += prompt_tokens
            entry["completion_tokens"] += completion_tokens
            found_today = True
            break
    
    if not found_today:
        stats["history"].append({
            "date": today,
            "requests": 1,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens
        })
    
    # Chỉ giữ lại 30 ngày gần nhất để file không quá lớn
    if len(stats["history"]) > 30:
        stats["history"] = stats["history"][-30:]
        
    with open('usage_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=4)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        users_db = load_users()
        
        if username in users_db and users_db[username] == password:
            session['logged_in'] = True
            session['username'] = username # (Tùy chọn ghi nhớ ai đang đăng nhập)
            return redirect(url_for('home'))
        else:
            error = 'Tài khoản hoặc mật khẩu không chính xác!'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    error = None
    success = None
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        username = session.get('username')
        
        users_db = load_users()
        
        if not username or username not in users_db:
            error = "Lỗi xác thực. Vui lòng đăng nhập lại."
        elif users_db[username] != current_password:
            error = "Mật khẩu hiện tại không đúng!"
        elif new_password != confirm_password:
            error = "Mật khẩu xác nhận không khớp!"
        elif not re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[\W_]).{8,}$", new_password):
            error = "Mật khẩu mới không đạt yêu cầu. Tối thiểu 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt."
        else:
            users_db[username] = new_password
            save_users(users_db)
            success = "Đổi mật khẩu thành công!"
            
    return render_template('change_password.html', error=error, success=success)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    api_key = os.getenv("GEMINI_API_KEY")
    
    grade = data.get('grade', '1')
    semester = data.get('semester', '1')
    chapter = data.get('chapter', '')
    lesson = data.get('lesson', '')
    test_type = data.get('test_type', 'lesson') # lesson, chapter, semester
    count = data.get('count', 5)
    
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        return jsonify({'error': 'Chưa cấu hình API Key trong file .env!'}), 400
        
    try:
        client = genai.Client(api_key=api_key)
        
        # Xây dựng ngữ cảnh cụ thể cho prompt
        context = f"Toán lớp {grade}, Học kỳ {semester}"
        if test_type == 'lesson':
            topic_str = f"bài học '{lesson}' thuộc chương '{chapter}'"
        elif test_type == 'chapter':
            topic_str = f"toàn bộ chương '{chapter}' (Luyện tập chung)"
        else:
            topic_str = f"tổng hợp kiến thức toàn bộ học kỳ {semester} (Đề ôn tập học kỳ)"
            
        prompt = f"""Bạn là chuyên gia soạn đề thi tiểu học tại Việt Nam. Hãy tạo một đề kiểm tra {context} cho {topic_str}.

Yêu cầu chi tiết:
1. Số lượng câu hỏi: ĐÚNG {count} câu.
2. Cấu trúc đề: 
   - Phần 1: Trắc nghiệm khách quan (khoanh tròn đáp án đúng A, B, C, D). Chiếm khoảng 60-70% số câu.
   - Phần 2: Tự luận (Giải toán có lời văn, đặt tính rồi tính). Chiếm khoảng 30-40% số câu.
3. Nội dung: Bám sát chương trình GDPT 2018. Câu hỏi sinh động, gần gũi với học sinh lớp {grade}.
4. Định dạng đầu ra: Trả về mã HTML sạch (không có thẻ ```html hay ```).
   - Tuyệt đối KHÔNG sử dụng thẻ <img> hoặc chèn các đường dẫn ảnh ảo. Nếu cần minh họa con vật, đồ vật, BẮT BUỘC sử dụng biểu tượng Emoji (ví dụ: 🐟, 🍎, ⏰).
   - Sử dụng các thẻ <h3> cho tiêu đề đề thi.
   - Sử dụng thẻ <div class="question"> cho mỗi câu hỏi.
   - Trình bày bảng biểu hoặc công thức toán học rõ ràng (nếu có).
   - Cuối đề thi có một phần <div class="answer-key" style="display:none;"> chứa đáp án chi tiết cho tất cả các câu.
5. Ngôn ngữ: Tiếng Việt hoàn toàn.
"""
        
        response = client.models.generate_content(
            model='gemini-2.0-flash', # Sửa lại model đúng định dạng nếu cần
            contents=prompt
        )
        
        # Lưu thống kê sử dụng
        usage = response.usage_metadata
        save_stats(usage.prompt_token_count, usage.candidates_token_count)
        
        # Làm sạch kết quả trả về (loại bỏ markdown blocks nếu có)
        clean_html = response.text.strip()
        if clean_html.startswith("```html"):
            clean_html = clean_html[7:]
        if clean_html.endswith("```"):
            clean_html = clean_html[:-3]
            
        return jsonify({
            'html': clean_html.strip(),
            'usage': {
                'prompt_tokens': usage.prompt_token_count,
                'completion_tokens': usage.candidates_token_count,
                'total_tokens': usage.total_token_count
            }
        })
    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        if "429" in error_msg:
            error_msg = "Lỗi: Đã hết hạn mức sử dụng API (Quota Exceeded). Vui lòng thử lại sau vài phút."
        return jsonify({'error': error_msg}), 500

@app.route('/admin')
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/api/stats')
def get_stats():
    if not session.get('logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(load_stats())

if __name__ == '__main__':
    # host='0.0.0.0' cho phép các máy tính khác trong mạng LAN truy cập vào
    app.run(host='0.0.0.0', debug=True, port=5000)
