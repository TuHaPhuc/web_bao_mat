# Secure vs. Vulnerable Code Comparison

This document highlights the key differences between the secure implementation (LoginSystem) and the vulnerable implementation (LoginSystem_Vulnerable).

## 1. Login Function

### Secure Version:
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        
        # Validation...
        
        if error is None:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Parameterized query - SECURE
                cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
                user = cursor.fetchone()
                
                # Rest of login logic...
```

### Vulnerable Version:
```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']  # No strip() - allows special characters
        password = request.form['password']
        
        # Validation...
        
        if error is None:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # String concatenation - VULNERABLE to SQL Injection
                query = f"SELECT * FROM users WHERE username = '{username}'"
                print(f"DEBUG - SQL Query: {query}")
                
                cursor.execute(query)
                user = cursor.fetchone()
                
                # Rest of login logic...
```

## 2. User Search Function

### Secure Version:
Not implemented in the secure version. If implemented, it would use parameterized queries:

```python
@app.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    search = request.args.get('search', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Parameterized query - SECURE
        if search:
            cursor.execute(
                "SELECT * FROM users WHERE username LIKE ? OR email LIKE ?", 
                (f"%{search}%", f"%{search}%")
            )
        else:
            cursor.execute("SELECT * FROM users")
            
        users = cursor.fetchall()
        
        return render_template('admin_users.html', users=users, search=search)
```

### Vulnerable Version:
```python
@app.route('/admin/users', methods=['GET'])
@login_required
def admin_users():
    search = request.args.get('search', '')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # String concatenation - VULNERABLE to SQL Injection
        if search:
            query = f"SELECT * FROM users WHERE username LIKE '%{search}%' OR email LIKE '%{search}%'"
        else:
            query = "SELECT * FROM users"
            
        print(f"DEBUG - SQL Query: {query}")
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        return render_template('admin_users.html', users=users, search=search)
```

## 3. Key Security Concerns

1. **Direct String Concatenation**:  
   The vulnerable version directly inserts user input into SQL queries, allowing attackers to modify the query structure.

2. **Lack of Input Sanitization**:  
   The vulnerable version doesn't sanitize input or remove special characters that could be used for injection.

3. **Overly Verbose Error Messages**:  
   The vulnerable version includes debugging information that could help attackers understand the database structure.

4. **Parameterized Queries**:  
   The secure version uses parameterized queries where user input is never directly incorporated into the SQL string.

## 4. Recommended Security Measures

1. **Always Use Parameterized Queries**:  
   Use `?` placeholders and pass parameters separately.

2. **Validate and Sanitize Inputs**:  
   Validate input format and sanitize special characters.

3. **Apply Principle of Least Privilege**:  
   Database users should have minimal permissions needed for the application.

4. **Implement Proper Error Handling**:  
   Don't expose internal errors to users.

5. **Use ORM Libraries**:  
   Libraries like SQLAlchemy provide built-in protection against SQL injection.

6. **Regular Security Audits**:  
   Regularly review code for security vulnerabilities.

7. **Use Prepared Statements**:  
   Separates SQL logic from data.
