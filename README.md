# LoginSystem Vulnerable

# Link demo: https://phucdemo.hmp.it.com/

## 🚨 Chỉ Dành Cho Mục Đích Học Tập | Educational Purpose Only
Đây là một phiên bản cố tình dễ bị tấn công của hệ thống đăng nhập thông thường. Dự án này được tạo ra **CHỈ** cho mục đích học tập và nghiên cứu về bảo mật web, cụ thể là lỗ hổng SQL Injection.

**CẢNH BÁO**: Không sử dụng mã nguồn này trong môi trường sản xuất hoặc với dữ liệu thật!

## 📝 Mô Tả | Description
Một hệ thống đăng nhập được thiết kế có chủ ý với các lỗ hổng bảo mật để demo:
- Cách thức hoạt động của tấn công SQL Injection
- Các mẫu lỗ hổng phổ biến
- Best practices cho lập trình bảo mật
- Tầm quan trọng của việc validate đầu vào và parameterized queries

## 🛠 Features
- Basic authentication system (login/register)
- Password hashing demonstration
- SQL Injection vulnerabilities
- Admin panel with search functionality
- User profile management
- Password reset simulation

## 🔥 Vulnerabilities Demonstrated
1. **SQL Injection in Login Form**
   - Direct string concatenation in queries
   - No input sanitization
   
2. **SQL Injection in User Search**
   - Vulnerable search functionality
   - Exposure of sensitive data

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package installer)
- Virtual environment (recommended)

### Installation
1. Clone the repository
```bash
git clone https://github.com/YourUsername/LoginSystem_Vulnerable.git
cd LoginSystem_Vulnerable
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Initialize the database
```bash
python seed_database.py
```

5. Run the application
```bash
python app.py
```

## 🎯 Testing SQL Injection

### Login Form
Try these examples:
- Username: `' OR '1'='1`
- Username: `' OR 1=1 --`
- Password: (anything)

### User Search
Example queries:
- `' OR '1'='1`
- `' UNION SELECT 1, name, sql FROM sqlite_master WHERE type='table' --`

## 🛡️ Security Best Practices
Learn how to prevent these vulnerabilities:
1. Use parameterized queries
2. Implement input validation
3. Apply the principle of least privilege
4. Use ORM when possible
5. Regular security audits

## 📚 Learning Resources
- [OWASP SQL Injection](https://owasp.org/www-community/attacks/SQL_Injection)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger SQL Injection Tutorial](https://portswigger.net/web-security/sql-injection)

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer
This project contains intentional security vulnerabilities for educational purposes. The author is not responsible for any misuse or damage caused by this code. DO NOT use this code in production environments!
