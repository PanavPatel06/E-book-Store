# E-Book Store

A modern, full-stack web application and interactive database showcase based on a relational database design for a digital e-bookstore. This project features a Python FastAPI backend, a React frontend, and a self-seeding SQLite database engine, packaged with developer utilities like a SQL playground and a real-time query logger for presentation.

Link to website: [E-book Store]()

## Features

### 🛒 E-Commerce Storefront
- **User Authentication**: Register and log in securely. Supports customer, premium customer, and admin roles.
- **Book Catalog**: Browse a dynamic collection of books. Search books by Title, Author, or Category.
- **Shopping Cart**: Manage cart items, adjust quantities, and calculate subtotal/totals in real-time.
- **Checkout system**: Complete purchases via transactions that check book stock, record orders, save order details, and empty shopping carts atomically.

### 🛠️ Admin Dashboard
- **Inventory Management**: Add, update, and delete books in real-time.
- **Automatic Stock Tracking**: Visually inspect and manage inventory quantities.
- **Orders Log**: Access all customer order transactions.

### 📊 Interactive Database Showcase (Resume Feature)
- **Live SQL Query Playground**: Write custom `SELECT` queries directly in the web browser. The app runs the query on the SQLite database and displays the results in an interactive table.
- **Real-Time SQL Log Terminal**: A terminal panel that shows the exact SQL queries executed in the database as you click around the app, complete checkouts, or search books.
- **Database ER Visualizer**: Inspect the database schema and table relationships directly on the page.

---

## Technical Architecture

```
                                  +------------------+
                                  |  React Frontend  |
                                  |  (Vite + CSS)    |
                                  +--------+---------+
                                           |
                                           | HTTP API REST
                                           v
                                 +---------+----------+
                                 |  FastAPI Backend   |
                                 |  (Python 3.14)     |
                                 +---------+----------+
                                           |
                                           | sqlite3 (PRAGMA foreign_keys = ON)
                                           v
                                  +--------+---------+
                                  | SQLite Database  |
                                  |  (ebookstore.db) |
                                  +------------------+
```

---

## Database Schema (ER Diagram)

The system consists of 8 tables modeling a digital bookstore's operational database:

- **publishers**: Publisher details and website URLs.
- **categories**: E-book genre categories.
- **authors**: Author biographies.
- **books**: Book details, prices, stocks, and links to publishers.
- **book_authors**: Many-to-many relationship mapping books to authors.
- **book_categories**: Many-to-many relationship mapping books to categories.
- **customers**: User accounts, credentials, and roles (`customer`, `admin`, `premium`).
- **orders** / **order_details**: Relational transaction models representing customer purchase histories.
- **shopping_cart**: Cart state persistent database records.

---

## Local Setup

### Prerequisite
Ensure you have **Python 3.10+** and **Node.js v18+** installed.

### Setup Steps
1. **Clone the Repository**:
   ```bash
   git clone <your-repo-url>
   cd DBMS_e-book_system
   ```

2. **Run the Application (Single Command Development)**:
   You can run the full backend and frontend simultaneously.
   
   - **Backend**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     pip install -r backend/requirements.txt
     python backend/main.py
     ```
   - **Frontend**:
     ```bash
     cd frontend
     npm install
     npm run dev
     ```

3. **Production Build & Unified Run**:
   Compile the React app and let FastAPI serve it on `localhost:8000`:
   ```bash
   cd frontend
   npm run build
   cd ../
   python backend/main.py
   ```
