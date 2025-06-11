import os
import sqlite3
import re
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()  # Tạo secret key ngẫu nhiên
app.config['DATABASE'] = os.path.join(app.instance_path, 'users.db')

# Đảm bảo thư mục instance tồn tại
os.makedirs(app.instance_path, exist_ok=True)

# Context processor để thêm biến now vào tất cả các template
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Hàm để kết nối database
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# Tạo bảng users nếu chưa tồn tại
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login TEXT
            )
        ''')
        conn.commit()

# Gọi hàm khởi tạo database
init_db()

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Bạn cần đăng nhập để truy cập trang này!', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Hàm kiểm tra email hợp lệ
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Trang chủ
@app.route('/')
def index():
    return render_template('index.html')

# Đăng ký
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Kiểm tra validate
        error = None
        
        if not username:
            error = 'Tên đăng nhập không được để trống'
        elif not email:
            error = 'Email không được để trống'
        elif not is_valid_email(email):
            error = 'Email không hợp lệ'
        elif not password:
            error = 'Mật khẩu không được để trống'
        elif password != confirm_password:
            error = 'Mật khẩu không khớp'
        elif len(password) < 8:
            error = 'Mật khẩu phải có ít nhất 8 ký tự'
        
        # Kiểm tra username và email đã tồn tại chưa
        if error is None:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Kiểm tra username
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                if cursor.fetchone() is not None:
                    error = f'Tên đăng nhập "{username}" đã được sử dụng'
                
                # Kiểm tra email
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                if cursor.fetchone() is not None:
                    error = f'Email "{email}" đã được sử dụng'
                
                if error is None:
                    # Mã hóa mật khẩu và lưu vào database
                    hashed_password = generate_password_hash(password)
                    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    cursor.execute(
                        'INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)',
                        (username, email, hashed_password, created_at)
                    )
                    conn.commit()
                    
                    flash('Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.', 'success')
                    return redirect(url_for('login'))
            
            except sqlite3.Error as e:
                error = f"Database error: {e}"
            finally:
                conn.close()
        
        flash(error, 'danger')
    
    return render_template('register.html')

# Đăng nhập có lỗ hổng SQL injection
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # Không dùng strip() để cho phép các ký tự đặc biệt
        password = request.form['password']
        
        error = None
        user = None
        
        if not username:
            error = 'Tên đăng nhập không được để trống'
        elif not password:
            error = 'Mật khẩu không được để trống'
        
        if error is None:
            conn = None
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Lỗ hổng SQL Injection: Tạo câu truy vấn bằng cách nối chuỗi thay vì tham số hóa
                query = f"SELECT * FROM users WHERE username = '{username}'"
                
                # Debug: in câu truy vấn để xem SQL injection có hoạt động không
                print(f"DEBUG - SQL Query: {query}")
                
                cursor.execute(query)  # Dễ bị tấn công SQL Injection
                user = cursor.fetchone()
                
                if user is None:
                    error = 'Tên đăng nhập không tồn tại'
                # Với SQL Injection thành công, chúng ta muốn bỏ qua kiểm tra mật khẩu
                elif "' OR " in username.upper() or " OR " in username.upper() or "--" in username:
                    print("DEBUG - SQL Injection detected! Bypassing password check")
                    # Bỏ qua kiểm tra mật khẩu nếu phát hiện SQL injection
                elif not check_password_hash(user['password'], password):
                    error = 'Mật khẩu không chính xác'
                
                if user is not None and error is None:
                    # Xóa thông tin phiên đăng nhập cũ
                    session.clear()
                    # Lưu thông tin user vào session
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    
                    if conn:
                        # Cập nhật thời gian đăng nhập gần nhất
                        last_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (last_login, user['id']))
                        conn.commit()
                    
                    flash('Đăng nhập thành công!', 'success')
                    
                    # Nếu có tham số next, chuyển hướng đến trang đó
                    next_page = request.args.get('next')
                    if next_page:
                        return redirect(next_page)
                    return redirect(url_for('dashboard'))
            
            except sqlite3.Error as e:
                error = f"Database error: {e}"
                print(f"DEBUG - SQL Error: {e}")
            finally:
                if conn:
                    conn.close()
        
        if error:
            flash(error, 'danger')
    
    return render_template('login.html')

# Dashboard - trang riêng tư sau khi đăng nhập
@app.route('/dashboard')
@login_required
def dashboard():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        return render_template('dashboard.html', user=user)
    
    except sqlite3.Error as e:
        flash(f"Database error: {e}", 'danger')
        return redirect(url_for('login'))
    finally:
        conn.close()

# Đăng xuất
@app.route('/logout')
def logout():
    session.clear()
    flash('Bạn đã đăng xuất thành công!', 'success')
    return redirect(url_for('index'))

# Trang profile
@app.route('/profile')
@login_required
def profile():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        
        return render_template('profile.html', user=user)
    
    except sqlite3.Error as e:
        flash(f"Database error: {e}", 'danger')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

# Thay đổi mật khẩu
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        error = None
        
        if not current_password:
            error = 'Vui lòng nhập mật khẩu hiện tại'
        elif not new_password:
            error = 'Vui lòng nhập mật khẩu mới'
        elif new_password != confirm_password:
            error = 'Mật khẩu mới không khớp'
        elif len(new_password) < 8:
            error = 'Mật khẩu phải có ít nhất 8 ký tự'
        
        if error is None:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
                user = cursor.fetchone()
                
                if not check_password_hash(user['password'], current_password):
                    error = 'Mật khẩu hiện tại không chính xác'
                else:
                    hashed_password = generate_password_hash(new_password)
                    cursor.execute('UPDATE users SET password = ? WHERE id = ?', 
                                  (hashed_password, session['user_id']))
                    conn.commit()
                    
                    flash('Thay đổi mật khẩu thành công!', 'success')
                    return redirect(url_for('profile'))
            
            except sqlite3.Error as e:
                error = f"Database error: {e}"
            finally:
                conn.close()
        
        flash(error, 'danger')
    
    return render_template('change_password.html')

# Trang quên mật khẩu
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()
        
        if not email:
            flash('Email không được để trống', 'danger')
        elif not is_valid_email(email):
            flash('Email không hợp lệ', 'danger')
        else:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
                user = cursor.fetchone()
                
                if user is None:
                    flash('Không tìm thấy tài khoản với email này', 'danger')
                else:
                    # Trong ứng dụng thực tế, tại đây sẽ gửi email reset mật khẩu
                    # Nhưng trong ví dụ này, chúng ta chỉ giả lập việc đó
                    flash('Nếu email đã được đăng ký, bạn sẽ nhận được hướng dẫn để đặt lại mật khẩu.', 'info')
                    return redirect(url_for('login'))
            
            except sqlite3.Error as e:
                flash(f"Database error: {e}", 'danger')
            finally:
                conn.close()
    
    return render_template('forgot_password.html')

# Trang quản trị (Admin) - Có lỗ hổng SQL Injection
@app.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    search = request.args.get('search', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Lỗ hổng SQL Injection: Ghép chuỗi trực tiếp vào câu truy vấn SQL
        if search:
            query = f"SELECT * FROM users WHERE username LIKE '%{search}%' OR email LIKE '%{search}%'"
        else:
            query = "SELECT * FROM users"
            
        # Ghi log câu truy vấn để debug và demo
        print(f"DEBUG - SQL Query: {query}")
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        return render_template('admin_users.html', users=users, search=search)
    
    except sqlite3.Error as e:
        flash(f"Database error: {e}", 'danger')
        return redirect(url_for('dashboard'))
    finally:
        conn.close()

# Trang 404 Not Found
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
