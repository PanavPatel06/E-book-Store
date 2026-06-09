from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
import os
import re
import time
from typing import Optional, List
from duckduckgo_search import DDGS

from . import database as db

# Project Root Directory Setup
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)

app = FastAPI(
    title="E-Bookstore API",
    description="Backend API for E-Bookstore showing SQL operations, transactions, and live database showcase.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify front-end domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cover image cache
cover_cache = {}

# --- Pydantic Request Models ---

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None

class CartAddRequest(BaseModel):
    customer_id: int
    book_id: int
    quantity: int = 1

class CartUpdateRequest(BaseModel):
    quantity: int

class CheckoutRequest(BaseModel):
    customer_id: int
    shipping_address: str

class BookSaveRequest(BaseModel):
    title: str
    price: float
    stock_quantity: int
    isbn: str
    publication_year: int
    publisher_id: int
    description: Optional[str] = ""

class SQLPlaygroundRequest(BaseModel):
    query: str

# --- Authentication Endpoints ---

@app.post("/api/auth/login")
def login(req: LoginRequest):
    query = "SELECT customer_id, password, role, name, address FROM customers WHERE email = ?"
    try:
        users = db.execute_read(query, (req.email,))
        if not users or users[0]['password'] != req.password:
            raise HTTPException(status_code=401, detail="Invalid email or password.")
        
        user_info = users[0]
        # Remove password from response
        user_info.pop('password')
        return user_info
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Database login error: {str(e)}")

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    # Check if email exists
    check_query = "SELECT customer_id FROM customers WHERE email = ?"
    existing = db.execute_read(check_query, (req.email,))
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
        
    query = """
        INSERT INTO customers (name, email, password, phone, role, address)
        VALUES (?, ?, ?, ?, 'customer', ?)
    """
    success, err_or_id, _ = db.execute_write(query, (req.name, req.email, req.password, req.phone, req.address))
    if not success:
        raise HTTPException(status_code=500, detail=f"Registration failed: {err_or_id}")
    return {"message": "Registration successful!", "customer_id": err_or_id}

# --- Books Catalog Endpoints ---

@app.get("/api/books")
def list_books(search: str = "", search_by: str = "Title"):
    base_query = """
        SELECT DISTINCT b.book_id, b.isbn, b.title, b.price, b.stock_quantity, b.publication_year, b.description, b.publisher_id,
               GROUP_CONCAT(DISTINCT a.name) AS authors,
               GROUP_CONCAT(DISTINCT c.name) AS categories
        FROM books b
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        LEFT JOIN book_categories bc ON b.book_id = bc.book_id
        LEFT JOIN categories c ON bc.category_id = c.category_id
    """
    
    params = []
    where_clause = ""
    if search:
        search_like = f"%{search}%"
        params.append(search_like)
        if search_by == 'Title':
            where_clause = " WHERE b.title LIKE ?"
        elif search_by == 'Author':
            where_clause = " WHERE a.name LIKE ?"
        elif search_by == 'Category':
            where_clause = " WHERE c.name LIKE ?"
            
    full_query = base_query + where_clause + " GROUP BY b.book_id ORDER BY b.title"
    
    try:
        books = db.execute_read(full_query, params)
        # Format authors and categories as lists
        for book in books:
            book['authors'] = book['authors'].split(',') if book['authors'] else []
            book['categories'] = book['categories'].split(',') if book['categories'] else []
        return books
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch books: {str(e)}")

@app.get("/api/books/cover")
def get_book_cover(query: str):
    # Query is typically the book title
    if query in cover_cache:
        return {"url": cover_cache[query]}
        
    try:
        results = DDGS().images(keywords=f"{query} book cover", region="wt-wt", safesearch="moderate", max_results=1)
        if results:
            url = results[0]['image']
            cover_cache[query] = url
            return {"url": url}
    except Exception:
        pass
    
    # Fallback to UI-friendly SVG or gradient placeholder in frontend
    return {"url": None}

# --- Cart Endpoints ---

@app.get("/api/cart")
def view_cart(customer_id: int):
    query = """
        SELECT sc.cart_id, b.book_id, b.title, sc.quantity, b.price, (sc.quantity * b.price) AS subtotal
        FROM shopping_cart sc
        JOIN books b ON sc.book_id = b.book_id
        WHERE sc.customer_id = ?
    """
    try:
        items = db.execute_read(query, (customer_id,))
        total = sum(item['subtotal'] for item in items)
        return {"items": items, "total": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load cart: {str(e)}")

@app.post("/api/cart")
def add_to_cart(req: CartAddRequest):
    # Verify book exists and is in stock
    book = db.execute_read("SELECT stock_quantity FROM books WHERE book_id = ?", (req.book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    if book[0]['stock_quantity'] < req.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock available.")
        
    query = """
        INSERT INTO shopping_cart (customer_id, book_id, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(customer_id, book_id) DO UPDATE SET quantity = quantity + excluded.quantity
    """
    success, msg_or_id, _ = db.execute_write(query, (req.customer_id, req.book_id, req.quantity))
    if not success:
        raise HTTPException(status_code=500, detail=f"Could not add item to cart: {msg_or_id}")
    return {"message": "Added to cart successfully."}

@app.put("/api/cart/{book_id}")
def update_cart_quantity(book_id: int, customer_id: int, req: CartUpdateRequest):
    # Verify stock
    book = db.execute_read("SELECT stock_quantity FROM books WHERE book_id = ?", (book_id,))
    if not book:
        raise HTTPException(status_code=404, detail="Book not found.")
    if book[0]['stock_quantity'] < req.quantity:
        raise HTTPException(status_code=400, detail=f"Only {book[0]['stock_quantity']} items in stock.")
        
    if req.quantity <= 0:
        # Delete item
        query = "DELETE FROM shopping_cart WHERE customer_id = ? AND book_id = ?"
        success, err, _ = db.execute_write(query, (customer_id, book_id))
    else:
        query = "UPDATE shopping_cart SET quantity = ? WHERE customer_id = ? AND book_id = ?"
        success, err, _ = db.execute_write(query, (req.quantity, customer_id, book_id))
        
    if not success:
        raise HTTPException(status_code=500, detail=f"Cart update failed: {err}")
    return {"message": "Cart updated successfully."}

@app.delete("/api/cart/{book_id}")
def remove_from_cart(book_id: int, customer_id: int):
    query = "DELETE FROM shopping_cart WHERE customer_id = ? AND book_id = ?"
    success, err, _ = db.execute_write(query, (customer_id, book_id))
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to remove item: {err}")
    return {"message": "Item removed from cart."}

# --- Checkout Endpoint (DBMS Transactions Demo) ---

@app.post("/api/checkout")
def checkout(req: CheckoutRequest):
    # 1. Fetch cart items
    cart_items = db.execute_read("SELECT book_id, quantity FROM shopping_cart WHERE customer_id = ?", (req.customer_id,))
    if not cart_items:
        raise HTTPException(status_code=400, detail="Your shopping cart is empty.")
        
    # Start compiling our transaction operations
    operations = []
    total_amount = 0.0
    
    # 2. Verify stock & calculate totals inside loop
    for item in cart_items:
        book_id = item['book_id']
        qty = item['quantity']
        
        # Verify book stock and price
        book_info = db.execute_read("SELECT price, stock_quantity, title FROM books WHERE book_id = ?", (book_id,))
        if not book_info:
            raise HTTPException(status_code=404, detail=f"Book ID {book_id} not found.")
            
        book = book_info[0]
        if book['stock_quantity'] < qty:
            raise HTTPException(
                status_code=400, 
                detail=f"Checkout failed: '{book['title']}' is out of stock (Requested: {qty}, Available: {book['stock_quantity']})."
            )
            
        total_amount += book['price'] * qty
        
        # Decrement stock operation
        operations.append((
            "UPDATE books SET stock_quantity = stock_quantity - ? WHERE book_id = ?",
            (qty, book_id)
        ))
        
    # We must insert into 'orders' and 'order_details'. Since we need the generated order_id inside the sqlite transaction, 
    # we can construct a unified transaction manually in database.py or perform step-by-step transaction handling here:
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    start_time = time.time()
    try:
        conn.execute("BEGIN TRANSACTION;")
        
        # Insert main order
        cursor.execute(
            "INSERT INTO orders (customer_id, total_amount, status, shipping_address) VALUES (?, ?, 'pending', ?)",
            (req.customer_id, total_amount, req.shipping_address)
        )
        order_id = cursor.lastrowid
        
        # Insert details and apply stock updates
        for item in cart_items:
            book_id = item['book_id']
            qty = item['quantity']
            
            # Fetch book price
            cursor.execute("SELECT price FROM books WHERE book_id = ?", (book_id,))
            price = cursor.fetchone()[0]
            
            # Order details
            cursor.execute(
                "INSERT INTO order_details (order_id, book_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
                (order_id, book_id, qty, price)
            )
            
            # Stock deduct
            cursor.execute(
                "UPDATE books SET stock_quantity = stock_quantity - ? WHERE book_id = ?",
                (qty, book_id)
            )
            
        # Empty cart
        cursor.execute("DELETE FROM shopping_cart WHERE customer_id = ?", (req.customer_id,))
        
        conn.commit()
        duration = (time.time() - start_time) * 1000
        
        # Log SQL execution representation
        db.log_query(
            f"BEGIN TRANSACTION;\n"
            f"INSERT INTO orders (customer_id, total_amount, shipping_address) VALUES ({req.customer_id}, {total_amount}, '{req.shipping_address}');\n"
            f"-- (Loop for each book detail inserting order_details and updating books stock) --\n"
            f"DELETE FROM shopping_cart WHERE customer_id = {req.customer_id};\n"
            f"COMMIT;", 
            None, 
            duration
        )
        
        return {"message": "Order placed successfully!", "order_id": order_id}
        
    except Exception as e:
        conn.rollback()
        duration = (time.time() - start_time) * 1000
        db.log_query("BEGIN TRANSACTION; -- ROLLBACK DUE TO EXCEPTION --", None, duration, status=f"ROLLBACK ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Checkout database transaction failed: {str(e)}")
    finally:
        conn.close()

# --- Admin Operations Endpoints ---

@app.get("/api/admin/publishers")
def get_publishers():
    try:
        return db.execute_read("SELECT publisher_id, name FROM publishers ORDER BY name")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch publishers: {str(e)}")

@app.post("/api/admin/books")
def admin_add_book(req: BookSaveRequest):
    query = """
        INSERT INTO books (title, price, stock_quantity, isbn, publication_year, publisher_id, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    success, val, _ = db.execute_write(
        query, 
        (req.title, req.price, req.stock_quantity, req.isbn, req.publication_year, req.publisher_id, req.description)
    )
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to create book: {val}")
    return {"message": "Book created successfully.", "book_id": val}

@app.put("/api/admin/books/{book_id}")
def admin_update_book(book_id: int, req: BookSaveRequest):
    query = """
        UPDATE books 
        SET title = ?, price = ?, stock_quantity = ?, isbn = ?, publication_year = ?, publisher_id = ?, description = ?
        WHERE book_id = ?
    """
    success, val, count = db.execute_write(
        query, 
        (req.title, req.price, req.stock_quantity, req.isbn, req.publication_year, req.publisher_id, req.description, book_id)
    )
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to update book: {val}")
    if count == 0:
        raise HTTPException(status_code=404, detail="Book not found.")
    return {"message": "Book updated successfully."}

@app.delete("/api/admin/books/{book_id}")
def admin_delete_book(book_id: int):
    query = "DELETE FROM books WHERE book_id = ?"
    success, val, count = db.execute_write(query, (book_id,))
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to delete book: {val}")
    if count == 0:
        raise HTTPException(status_code=404, detail="Book not found.")
    return {"message": "Book deleted successfully."}

@app.get("/api/admin/orders")
def admin_list_orders():
    # Return list of all orders with customer names
    query = """
        SELECT o.order_id, o.customer_id, c.name as customer_name, o.order_date, o.total_amount, o.status, o.shipping_address
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY o.order_date DESC
    """
    try:
        orders = db.execute_read(query)
        # For each order, fetch items
        for order in orders:
            order['items'] = db.execute_read("""
                SELECT od.book_id, b.title, od.quantity, od.unit_price, (od.quantity * od.unit_price) as subtotal
                FROM order_details od
                JOIN books b ON od.book_id = b.book_id
                WHERE od.order_id = ?
            """, (order['order_id'],))
        return orders
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")

# --- DBMS Showcase/Playground Endpoints ---

@app.get("/api/db/logs")
def get_db_logs():
    return db.get_query_logs()

@app.get("/api/db/schema")
def get_db_schema():
    try:
        # Get list of tables (exclude sqlite system tables)
        tables = db.execute_read("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        schema = {}
        for row in tables:
            tbl_name = row['name']
            columns = db.execute_read(f"PRAGMA table_info({tbl_name});")
            schema[tbl_name] = [
                {
                    "cid": col["cid"],
                    "name": col["name"],
                    "type": col["type"],
                    "notnull": col["notnull"],
                    "dflt_value": col["dflt_value"],
                    "pk": col["pk"]
                } for col in columns
            ]
        return schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract schema: {str(e)}")

@app.post("/api/db/query")
def run_playground_query(req: SQLPlaygroundRequest):
    sql_stripped = req.query.strip()
    
    # Validation check: Ensure query starts with SELECT
    if not re.match(r"^\s*select\b", sql_stripped, re.IGNORECASE):
        return {
            "success": False,
            "error": "Security Restriction: Only SELECT queries are permitted in the public console for security reasons."
        }
        
    # Prevent destructive subqueries or side-effects (e.g. nested write statements, comment injections to execute stacked commands)
    destructive_keywords = ["insert", "update", "delete", "drop", "alter", "create", "replace", "truncate", "pragma", "reindex", "vacuum"]
    for kw in destructive_keywords:
        # Regex word boundary check
        if re.search(r"\b" + kw + r"\b", sql_stripped, re.IGNORECASE):
            return {
                "success": False,
                "error": f"Security Restriction: Keyword '{kw.upper()}' is forbidden to prevent modification of showcase database state."
            }
            
    # Execute query
    try:
        rows = db.execute_read(sql_stripped)
        return {
            "success": True,
            "data": rows,
            "count": len(rows),
            "columns": list(rows[0].keys()) if rows else []
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"SQL Error: {str(e)}"
        }

# --- Serve Static React Frontend ---

# Check if front-end production build exists
FRONTEND_DIST = os.path.join(ROOT_DIR, "frontend", "dist")

if os.path.exists(FRONTEND_DIST):
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="static")
    print(f"Mounted production React build from {FRONTEND_DIST}")
else:
    @app.get("/")
    def read_root():
        return {
            "message": "FastAPI is running! The React frontend was not found in frontend/dist. "
                       "Please run 'npm run build' inside the 'frontend' directory to build the UI."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
