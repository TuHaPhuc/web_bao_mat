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

# Dictionary to store original passwords for password leak demo
# EDUCATIONAL PURPOSE ONLY: In a real system, NEVER store passwords in plaintext!
# This is deliberately vulnerable for demonstrating SQL injection attacks
# Contains default sample passwords but will be updated when new users register
ORIGINAL_PASSWORDS = {
    'admin': 'admin123456',
    'user1': 'password123',
    'john_doe': 'secret12345',
    'jane_smith': 'mysecret1234',
    'security_expert': 'ComplexP@ssw0rd!'
}

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
                
                if error is None:                    # Mã hóa mật khẩu và lưu vào database
                    hashed_password = generate_password_hash(password)
                    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(
                        'INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, ?)',
                        (username, email, hashed_password, created_at)
                    )
                    conn.commit()
                      # Store the original password in our global dictionary for the password leak demo
                    # NGUY HIỂM: Đây chỉ là code ví dụ cho mục đích giáo dục!
                    # Trong ứng dụng thực tế, KHÔNG BAO GIỜ lưu mật khẩu gốc!
                    global ORIGINAL_PASSWORDS
                    ORIGINAL_PASSWORDS[username] = password
                    
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
    show_debug_info = False
    debug_info = None
    sql_structure = None
    password_leak = None
      # Sử dụng global ORIGINAL_PASSWORDS dictionary đã được định nghĩa ở đầu file
    # Mục đích là để thể hiện cách thức lộ mật khẩu gốc khi bị SQL injection
    global ORIGINAL_PASSWORDS
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Người dùng bình thường: Chỉ thấy thông tin của chính họ
        if not search:
            # Nếu không có tìm kiếm, chỉ hiển thị người dùng hiện tại
            query = f"SELECT * FROM users WHERE id = {session['user_id']}"
            cursor.execute(query)
            users = cursor.fetchall()
        else:
            # Lỗ hổng SQL Injection: Ghép chuỗi trực tiếp vào câu truy vấn SQL
            query = f"SELECT * FROM users WHERE username LIKE '%{search}%' OR email LIKE '%{search}%'"
            
            # Phát hiện các loại tấn công SQL injection
            if "' OR " in search or " OR " in search or "1=1" in search:
                show_debug_info = True
                debug_info = "SQL Injection phát hiện: OR condition - Hiển thị tất cả người dùng"
                print(f"DEBUG - SQL Injection attempt detected: {search}")
                
            elif "UNION SELECT" in search.upper() and "sqlite_master" in search.lower():
                show_debug_info = True
                debug_info = "SQL Injection phát hiện: UNION SELECT từ sqlite_master - Hiển thị cấu trúc cơ sở dữ liệu"
                print(f"DEBUG - SQL Injection attempt detected: {search}")
                
                # Truy vấn trực tiếp để lấy cấu trúc bảng
                try:
                    schema_cursor = conn.cursor()
                    schema_cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
                    tables = schema_cursor.fetchall()
                    
                    sql_structure = []
                    for table in tables:
                        sql_structure.append({
                            "table_name": table[0] if table[0] else "Unknown",
                            "sql_def": table[1] if table[1] else "No definition"
                        })
                except Exception as e:
                    print(f"DEBUG - Error fetching schema: {e}")
                
            # Phát hiện tấn công lấy mật khẩu
            elif "UNION SELECT" in search.upper() and "password" in search.lower():
                show_debug_info = True
                debug_info = "SQL Injection phát hiện: UNION SELECT bao gồm mật khẩu - Tiết lộ cả mật khẩu đã mã hóa và mật khẩu gốc"
                print(f"DEBUG - SQL Injection attempt detected: {search}")
                
                # Truy vấn trực tiếp để lấy mật khẩu và thêm mật khẩu gốc
                try:
                    password_cursor = conn.cursor()
                    password_cursor.execute("SELECT id, username, password FROM users")
                    raw_password_leak = password_cursor.fetchall()
                    
                    # Tạo danh sách mới với mật khẩu gốc
                    password_leak = []
                    for user in raw_password_leak:                        # Chuyển đổi từ đối tượng Row sang dict
                        user_dict = dict(user)
                        # Thêm mật khẩu gốc nếu có
                        user_dict['plain_password'] = ORIGINAL_PASSWORDS.get(user['username'], '(unknown)')
                        password_leak.append(user_dict)
                        
                except Exception as e:
                    print(f"DEBUG - Error fetching passwords: {e}")
            # Ghi log câu truy vấn để debug và demo
            print(f"DEBUG - SQL Query: {query}")
            
            try:
                cursor.execute(query)
                users = cursor.fetchall()
            except sqlite3.OperationalError as e:
                # Nếu lỗi cú pháp SQL, hiển thị thông báo gỡ lỗi kèm truy vấn
                print(f"DEBUG - SQL Error: {e}")
                debug_info = f"SQL Syntax Error: {e}"
                show_debug_info = True
                users = []
        
        return render_template('admin_users.html', users=users, search=search, 
                              show_debug_info=show_debug_info, debug_info=debug_info,
                              sql_structure=sql_structure, password_leak=password_leak)
    
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
