# 🚀 Secure Flask Auth Backend

A robust, hackathon-ready Flask authentication system! 🔒✨ Built for students & production – secure by default. 😎

**Key Features** 💥
- User registration with strong password rules ✅
- Login w/ account lockout (5 fails = 10min ban) ⏰
- Session-based auth via secure cookies 🍪
- Protected routes & auto-expiring sessions 🛡️
- SQL injection-proof & bcrypt hashing 🔐

## 🛠️ Tech Stack
- Python 3 🐍
- Flask ⚗️
- SQLAlchemy Core 📊
- SQLite 💾
- bcrypt & UUID tokens 🛠️

## 🚀 Quick Start
````markdown
## 🚀 Getting Started

### 1️⃣ Install Dependencies 📦

```bash
pip install flask sqlalchemy bcrypt
````

### 2️⃣ Run Server ▶️

```bash
python app.py
```

Server live at:

```
http://127.0.0.1:5000
```

---

## 🗄️ Database Setup

SQLite auto-creates tables on first run.
Schema reference below 👇

### 👤 Users Table

| Column          | Type    | Description            |
| --------------- | ------- | ---------------------- |
| id              | INTEGER | Primary key            |
| username        | TEXT    | Unique username        |
| password        | TEXT    | bcrypt hashed password |
| failed_attempts | INTEGER | Failed login counter   |
| lock_until      | TEXT    | Lock expiry timestamp  |

---

### 🎫 Sessions Table

| Column        | Type    | Description       |
| ------------- | ------- | ----------------- |
| id            | INTEGER | Primary key       |
| user_id       | INTEGER | Linked user ID    |
| session_token | TEXT    | Unique UUID token |
| expires_at    | TEXT    | Expiry timestamp  |

---

## 📡 API Endpoints

All endpoints use JSON and cookie-based authentication.

---


## 📡 API Endpoints

---

### 1️⃣ POST `/register` 🆕

#### Request Body


        {
        "username": "string",
        "password": "string"
        }

#### 🔐 Password Requirements
    
    * Minimum 8 characters
    * At least 1 uppercase letter
    * At least 1 lowercase letter
    * At least 1 number
    * At least 1 special character

#### ✅ Success — 200 OK
    
    
    { "message": "Registration successful" }
    
    
#### ❌ Errors — 400 Bad Request
    
    * Username already exists
    * Weak password
    * Invalid input
    
    ---
    
### 2️⃣ POST `/login` 🔑
    
#### Request Body
    

    {
      "username": "string",
        "password": "string"
        }
        
#### ✅ Success — 200 OK
        
        
        { "message": "Login successful" }
        
        
 ✔ Secure session cookie is set
        
#### ❌ Errors
        
        * `401 Unauthorized` — Invalid credentials
        * `403 Forbidden` — Account locked
        
        ---
        
 ### 3️⃣ POST `/logout` 🚪
        
#### Requires
        
        * Valid session cookie
        
#### ✅ Success — 200 OK
        
        
        { "message": "Logged out" }
        
        
✔ Session deleted from database
✔ Cookie removed from browser

        
### 4️⃣ GET `/dashboard` 📊
        
#### Requires
        
        * Valid session cookie
        
#### ✅ Success — 200 OK
        
        
        { "message": "Welcome to dashboard!" }

        
#### ❌ Errors
        
        * `401 Unauthorized` — Unauthorized
        * `401 Unauthorized` — Invalid or expired session
        
## 🔒 Security Highlights
        
        * bcrypt password hashing
        * Parameterized SQL queries (SQL injection safe)
        * Account lockout: 5 failed attempts → 10 minute lock
        * UUID session tokens with database expiry
        * Secure cookies (`HttpOnly`, `SameSite=Strict`)
        * Input validation and login attempt logging
        
        > ⚠️ Suitable for hackathons and student production projects.
        > For full production systems, add rate limiting and CSRF protection.
        
                              
## 📁 Project Structure
                              
                              project/
                              ├── app.py
                              ├── auth.py
                              ├── login.db
                              └── templates/
                                  └── index.html
                                  
## ⚙️ Production Recommendations
                                  
                                  * Enable HTTPS
                                  * Set cookie `secure=True`
                                  * Use environment variables for secrets
                                  * Add rate limiting
                                  * Add CSRF protection
                                  * Consider Redis for scalable session storage
                        