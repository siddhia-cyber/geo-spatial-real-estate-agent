# from fastapi import APIRouter, HTTPException
# from services.auth_service import hash_password, verify_password, create_access_token
# import sqlite3

# router = APIRouter(prefix="/auth")

# conn = sqlite3.connect("db/users.db", check_same_thread=False)
# cursor = conn.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     email TEXT UNIQUE,
#     password TEXT
# )
# """)
# conn.commit()


# @router.post("/signup")
# def signup(email: str, password: str):
#     try:
#         cursor.execute(
#             "INSERT INTO users (email, password) VALUES (?, ?)",
#             (email, hash_password(password))
#         )
#         conn.commit()
#         return {"message": "User created"}
#     except:
#         raise HTTPException(status_code=400, detail="User already exists")


# @router.post("/login")
# def login(email: str, password: str):
#     cursor.execute("SELECT password FROM users WHERE email=?", (email,))
#     row = cursor.fetchone()

#     if not row or not verify_password(password, row[0]):
#         raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": email})
#     return {"access_token": token}
