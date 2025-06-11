# Login System - Demo SQL Injection và Cách Phòng Chống

Ứng dụng demo này được thiết kế để minh họa cách tấn công SQL Injection hoạt động và cách phòng chống chúng. Ứng dụng này cung cấp hai chế độ:

1. **Chế độ dễ bị tấn công**: Cho phép thực hiện các cuộc tấn công SQL Injection để hiểu cách chúng hoạt động
2. **Chế độ bảo mật**: Triển khai các biện pháp bảo mật để ngăn chặn SQL Injection

## Tính năng

- Đăng ký, đăng nhập và quản lý tài khoản
- Demo SQL Injection trong trang đăng nhập và tìm kiếm người dùng
- Hiển thị mã nguồn bị tấn công và mã nguồn đã được bảo vệ
- Dễ dàng chuyển đổi giữa chế độ bảo mật và dễ bị tấn công
- Hiển thị tác động của SQL Injection (tiết lộ cấu trúc DB, mật khẩu, v.v.)

## Cài đặt

1. Clone repository:
```bash
git clone <repository-url>
cd LoginSystem_Vulnerable
```

2. Cài đặt các thư viện phụ thuộc:
```bash
pip install -r requirements.txt
```

3. Khởi tạo cơ sở dữ liệu với dữ liệu mẫu:
```bash
python seed_database.py
```

4. Chạy ứng dụng:
```bash
python app_switchable.py
```

5. Truy cập ứng dụng tại: [http://localhost:5000](http://localhost:5000)

## Cách sử dụng

### Chuyển đổi chế độ bảo mật

Bạn có thể dễ dàng chuyển đổi giữa chế độ bảo mật và chế độ dễ bị tấn công bằng nút chuyển đổi ở góc phải dưới màn hình:
- Nhấn "Switch to Vulnerable Mode" để tắt các biện pháp bảo mật
- Nhấn "Switch to Secure Mode" để bật các biện pháp bảo mật

### Demo SQL Injection

#### Chế độ dễ bị tấn công:

1. **Trang đăng nhập**:
   - Thử đăng nhập với tên đăng nhập: `' OR '1'='1` và mật khẩu bất kỳ
   - Kết quả: Đăng nhập thành công vào tài khoản đầu tiên (thường là admin)

2. **Trang tìm kiếm người dùng** (sau khi đăng nhập):
   - Thử tìm kiếm với: `' OR '1'='1`
   - Kết quả: Hiển thị tất cả người dùng
   - Thử tìm kiếm với: `' UNION SELECT 1, name, sql, '4', '5' FROM sqlite_master WHERE type='table' --`
   - Kết quả: Tiết lộ cấu trúc cơ sở dữ liệu
   - Thử tìm kiếm với: `' UNION SELECT 1, username, password FROM users --`
   - Kết quả: Tiết lộ mật khẩu đã được mã hóa và mật khẩu gốc

#### Chế độ bảo mật:

- Tất cả các mẫu SQL Injection kể trên sẽ không hoạt động, và ứng dụng sẽ xử lý tham số hóa để ngăn chặn các cuộc tấn công.

## Các biện pháp bảo mật

Ứng dụng triển khai các biện pháp bảo mật sau trong chế độ an toàn:

1. **Tham số hóa truy vấn (Parameterized Queries)**: Sử dụng placeholders (?) thay vì nối chuỗi SQL trực tiếp
2. **Xác thực đầu vào**: Kiểm tra và lọc đầu vào từ người dùng
3. **Mã hóa mật khẩu**: Lưu trữ mật khẩu dưới dạng mã hóa một chiều
4. **Xác thực người dùng chặt chẽ**: Kiểm tra đúng mật khẩu thay vì bỏ qua kiểm tra

## Dành cho mục đích giáo dục

**LƯU Ý QUAN TRỌNG**: Ứng dụng này được thiết kế CHỈ để giáo dục về lỗ hổng bảo mật. Đừng bao giờ sử dụng mã nguồn có lỗ hổng này trong môi trường thực tế. Các kỹ thuật tấn công SQL Injection chỉ được sử dụng với ứng dụng này và KHÔNG được áp dụng cho các trang web hoặc ứng dụng khác nếu không được phép.

## Hướng dẫn chi tiết

Để biết thêm chi tiết về các cuộc tấn công SQL Injection có sẵn trong ứng dụng này, hãy xem file [SQL_INJECTION_GUIDE.md](SQL_INJECTION_GUIDE.md).

## Các tài khoản mẫu

- Username: `admin`, Password: `admin123456`
- Username: `user1`, Password: `password123`
- Username: `john_doe`, Password: `secret12345`
- Username: `jane_smith`, Password: `mysecret1234`
- Username: `security_expert`, Password: `ComplexP@ssw0rd!`

Bạn cũng có thể tạo tài khoản mới thông qua trang đăng ký.
