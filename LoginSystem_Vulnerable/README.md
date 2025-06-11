# LoginSystem Vulnerable

## Giới thiệu

Đây là một phiên bản cố tình dễ bị tấn công của hệ thống đăng nhập thông thường. Dự án này được tạo ra **CHỈ** cho mục đích học tập và nghiên cứu về bảo mật web, cụ thể là lỗ hổng SQL Injection.

**CẢNH BÁO**: Không sử dụng mã nguồn này trong môi trường sản xuất hoặc với dữ liệu thật!

## Lỗ hổng bảo mật

Hệ thống này cố ý chứa các lỗ hổng bảo mật sau:

1. **SQL Injection trong form đăng nhập**:
   - Tham số username được ghép trực tiếp vào câu truy vấn SQL
   - Không có lọc ký tự đặc biệt
   
2. **SQL Injection trong tìm kiếm người dùng**:
   - Tham số tìm kiếm được ghép trực tiếp vào câu truy vấn SQL
   - Không có giới hạn quyền truy cập đối với dữ liệu nhạy cảm

## Ví dụ tấn công

### SQL Injection trong đăng nhập:

- Đăng nhập với username: `' OR '1'='1` và mật khẩu bất kỳ
  - Kết quả: Đăng nhập thành công với tài khoản đầu tiên trong database

- Đăng nhập với username: `' OR 1=1 --` và mật khẩu bất kỳ
  - Kết quả: Đăng nhập thành công và bỏ qua kiểm tra mật khẩu

### SQL Injection trong tìm kiếm:

- Tìm kiếm với `' OR '1'='1`
  - Kết quả: Hiển thị tất cả người dùng

- Tìm kiếm với `' UNION SELECT 1, name, sql, 4, 5 FROM sqlite_master WHERE type='table' --`
  - Kết quả: Hiển thị cấu trúc bảng trong database

## Cách phòng chống SQL Injection

Trong môi trường thực tế, bạn nên:

1. Sử dụng tham số hóa truy vấn (parameterized query)
   ```python
   cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
   ```

2. Sử dụng ORM (Object-Relational Mapping) như SQLAlchemy

3. Áp dụng nguyên tắc "least privilege" - cấp quyền tối thiểu cho người dùng database

4. Lọc và xác thực dữ liệu đầu vào

5. Sử dụng prepared statements

## Cài đặt và sử dụng

1. Clone repository
2. Cài đặt các gói phụ thuộc:
   ```bash
   pip install -r requirements.txt
   ```
3. Chạy ứng dụng:
   ```bash
   python app.py
   ```

## Tài nguyên học tập

- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger SQL Injection Tutorial](https://portswigger.net/web-security/sql-injection)

## Disclaimer

Dự án này được tạo ra chỉ cho mục đích giáo dục. Tác giả không chịu trách nhiệm cho bất kỳ hành động nào sử dụng kiến thức này cho mục đích xấu hoặc bất hợp pháp.
