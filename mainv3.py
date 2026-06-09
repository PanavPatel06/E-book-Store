import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from PIL import Image
import requests
from io import BytesIO
import threading
from duckduckgo_search import DDGS

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Panav@960",
            database="ebookstore"
        )
        return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect to database: {e}")
        return None

def db_write_operation(query, params=None):
    conn = get_db_connection()
    if not conn: return False, "Database connection failed."
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return True, "Operation successful."
    except Error as e:
        return False, f"An error occurred: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def db_fetch_all(query, params=None):
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        return cursor.fetchall()
    except Error as e:
        messagebox.showerror("Fetch Error", f"Could not retrieve data: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def register_customer(name, email, password, address, phone):
    return db_write_operation("INSERT INTO customers (name, email, password, address, phone) VALUES (%s, %s, %s, %s, %s)", (name, email, password, address, phone))

def authenticate_user(email, password):
    users = db_fetch_all("SELECT customer_id, password, role, name, address FROM customers WHERE email = %s", (email,))
    if users and users[0]['password'] == password:
        return users[0]
    return None

def search_books(search_term, search_by='Title'):
    base_query = """
        SELECT DISTINCT b.book_id, b.title, b.price, b.stock_quantity, b.description, b.isbn, b.publication_year,
               GROUP_CONCAT(DISTINCT a.name SEPARATOR ', ') AS authors
        FROM books b
        LEFT JOIN book_authors ba ON b.book_id = ba.book_id
        LEFT JOIN authors a ON ba.author_id = a.author_id
        LEFT JOIN book_categories bc ON b.book_id = bc.book_id
        LEFT JOIN categories c ON bc.category_id = c.category_id
    """
    search_term_like = f"%{search_term}%"
    params = (search_term_like,)
    if search_by == 'Title': where_clause = " WHERE b.title LIKE %s"
    elif search_by == 'Author': where_clause = " WHERE a.name LIKE %s"
    elif search_by == 'Category': where_clause = " WHERE c.name LIKE %s"
    else: return []
    return db_fetch_all(base_query + where_clause + " GROUP BY b.book_id ORDER BY b.title;", params)

def add_book_to_cart(customer_id, book_id):
    query = "INSERT INTO shopping_cart (customer_id, book_id, quantity) VALUES (%s, %s, 1) ON DUPLICATE KEY UPDATE quantity = quantity + 1;"
    return db_write_operation(query, (customer_id, book_id))

def get_cart_items(customer_id):
    return db_fetch_all("SELECT sc.cart_id, b.book_id, b.title, sc.quantity, b.price, (sc.quantity * b.price) AS subtotal FROM shopping_cart sc JOIN books b ON sc.book_id = b.book_id WHERE sc.customer_id = %s", (customer_id,))

def process_checkout(customer_id, shipping_address):
    conn = get_db_connection()
    if not conn: return False, "Database connection failed."
    cursor = conn.cursor()
    try:
        conn.start_transaction()
        
        cart_items_raw = db_fetch_all("SELECT * FROM shopping_cart WHERE customer_id = %s", (customer_id,))
        if not cart_items_raw: return False, "Your cart is empty."
        
        total_amount = 0
        for item in cart_items_raw:
            book_info_list = db_fetch_all("SELECT price, stock_quantity FROM books WHERE book_id = %s FOR UPDATE", (item['book_id'],))
            book_info = book_info_list[0]
            if book_info['stock_quantity'] < item['quantity']:
                conn.rollback(); return False, f"Not enough stock for {item['book_id']}."
            total_amount += book_info['price'] * item['quantity']

        cursor.execute("INSERT INTO orders (customer_id, total_amount, shipping_address) VALUES (%s, %s, %s)", (customer_id, total_amount, shipping_address))
        order_id = cursor.lastrowid
        
        for item in cart_items_raw:
            book_price_list = db_fetch_all("SELECT price FROM books WHERE book_id = %s", (item['book_id'],))
            book_price = book_price_list[0]['price']
            cursor.execute("INSERT INTO order_details (order_id, book_id, quantity, unit_price) VALUES (%s, %s, %s, %s)", (order_id, item['book_id'], item['quantity'], book_price))
            cursor.execute("UPDATE books SET stock_quantity = stock_quantity - %s WHERE book_id = %s", (item['quantity'], item['book_id']))

        cursor.execute("DELETE FROM shopping_cart WHERE customer_id = %s", (customer_id,))
        conn.commit()
        return True, "Order placed successfully!"
    except Error as e:
        conn.rollback()
        return False, f"Checkout error: {e}"
    finally:
        if conn and conn.is_connected(): cursor.close(); conn.close()

def get_image_url(query):
    try:
        results = DDGS().images(keywords=query, region="wt-wt", safesearch="moderate", max_results=1)
        if results: return results[0]['image']
    except Exception: pass
    return None

def add_new_book(details):
    query = "INSERT INTO books (title, price, stock_quantity, isbn, publication_year, publisher_id) VALUES (%s, %s, %s, %s, %s, %s)"
    params = (details['title'], details['price'], details['stock'], details['isbn'], details['year'], details['publisher_id'])
    return db_write_operation(query, params)

def update_book(book_id, details):
    query = "UPDATE books SET title=%s, price=%s, stock_quantity=%s WHERE book_id=%s"
    params = (details['title'], details['price'], details['stock'], book_id)
    return db_write_operation(query, params)

def delete_book(book_id):
    return db_write_operation("DELETE FROM books WHERE book_id = %s", (book_id,))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("E-Bookstore")
        self.geometry("1200x800")
        self.current_user = None
        
        self._container = ctk.CTkFrame(self)
        self._container.pack(fill="both", expand=True)
        self._container.grid_rowconfigure(0, weight=1)
        self._container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # This is the FIX: Start by using the frame switching system immediately
        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame_class = globals().get(page_name)
        if frame_class:
            if page_name in self.frames:
                 self.frames[page_name].destroy()
            frame = frame_class(self._container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        login_frame = ctk.CTkFrame(self, fg_color="transparent")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(login_frame, text="E-Bookstore Login", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=12)
        self.email_entry = ctk.CTkEntry(login_frame, placeholder_text="Email", width=250, height=40)
        self.email_entry.pack(pady=12)
        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=250, height=40)
        self.password_entry.pack(pady=12)
        ctk.CTkButton(login_frame, text="Login", command=self.handle_login, height=40).pack(pady=12)
        ctk.CTkButton(login_frame, text="Register New Account", command=self.show_registration_window, height=40, fg_color="gray").pack(pady=12)

    def handle_login(self):
        user = authenticate_user(self.email_entry.get(), self.password_entry.get())
        if user:
            self.controller.current_user = user
            messagebox.showinfo("Success", f"Welcome, {user['name']}!")
            self.controller.show_frame("AdminDashboard" if user['role'] == 'admin' else "HomePage")
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    def show_registration_window(self):
        reg = ctk.CTkToplevel(self); reg.title("Register"); reg.geometry("400x450"); reg.transient(self); reg.grab_set()
        frame = ctk.CTkFrame(reg); frame.pack(fill="both", expand=True, padx=20, pady=20)
        entries = { "Full Name": ctk.CTkEntry(frame, placeholder_text="Full Name"), "Email": ctk.CTkEntry(frame, placeholder_text="Email"), "Password": ctk.CTkEntry(frame, placeholder_text="Password", show="*"), "Address": ctk.CTkEntry(frame, placeholder_text="Address"), "Phone": ctk.CTkEntry(frame, placeholder_text="Phone") }
        for e in entries.values(): e.pack(pady=10, padx=20, fill="x")
        
        def on_register():
            vals = {k: e.get() for k, e in entries.items()};
            if not all(vals.values()): messagebox.showerror("Error", "Please fill all fields.", parent=reg); return
            success, msg = register_customer(vals["Full Name"], vals["Email"], vals["Password"], vals["Address"], vals["Phone"])
            if success: messagebox.showinfo("Success", msg, parent=reg); reg.destroy()
            else: messagebox.showerror("Failed", msg, parent=reg)
        ctk.CTkButton(frame, text="Submit", command=on_register).pack(pady=20)

class TopBar(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#1a1a1a", corner_radius=0, height=60)
        self.pack(side="top", fill="x")
        ctk.CTkLabel(self, text=f"Welcome, {controller.current_user['name']}", font=ctk.CTkFont(size=16)).pack(side="left", padx=20)
        ctk.CTkButton(self, text="Logout", fg_color="gray", command=lambda: controller.show_frame("LoginPage")).pack(side="right", padx=10, pady=10)
        if controller.current_user['role'] != 'admin':
            ctk.CTkButton(self, text="View Cart", command=lambda: controller.show_frame("CartPage")).pack(side="right", padx=10, pady=10)

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller; TopBar(self, controller)
        search_frame = ctk.CTkFrame(self, fg_color="transparent"); search_frame.pack(fill="x", padx=20, pady=10)
        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Search for books...", width=400, height=35); self.search_entry.pack(side="left", padx=(0, 10))
        self.search_by_var = ctk.StringVar(value="Title"); ctk.CTkOptionMenu(search_frame, variable=self.search_by_var, values=["Title", "Author", "Category"], height=35).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Search", command=self.perform_search, height=35).pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="Clear", command=self.clear_search, height=35, fg_color="gray").pack(side="left", padx=10)
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Bestsellers"); self.scrollable_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.scrollable_frame.grid_columnconfigure(tuple(range(4)), weight=1)
        self.load_books()

    def perform_search(self): self.load_books(search_books(self.search_entry.get(), self.search_by_var.get()))
    def clear_search(self): self.search_entry.delete(0, 'end'); self.load_books()

    def load_books(self, books=None):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()
        book_list = books if books is not None else search_books("", "Title")
        if not book_list: ctk.CTkLabel(self.scrollable_frame, text="No books found.", font=ctk.CTkFont(size=16)).grid(pady=20); return
        for i, book in enumerate(book_list): threading.Thread(target=self.create_book_card, args=(book, i), daemon=True).start()

    def create_book_card(self, book, index):
        card = ctk.CTkFrame(self.scrollable_frame, border_width=1, border_color="gray")
        placeholder = Image.new('RGB', (150, 220), color = '#565656'); ctk_placeholder = ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=(150, 220))
        image_label = ctk.CTkLabel(card, text="", image=ctk_placeholder); image_label.pack(pady=10, padx=10)
        
        image_url = get_image_url(f"{book['title']} book cover")
        if image_url:
            try:
                img_data = Image.open(BytesIO(requests.get(image_url, timeout=10).content)); img_data.thumbnail((150, 220))
                ctk_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(img_data.width, img_data.height))
                self.after(0, lambda: image_label.configure(image=ctk_image))
            except Exception as e: print(f"Image load failed for {book['title']}: {e}")

        ctk.CTkLabel(card, text=book['title'], font=ctk.CTkFont(weight="bold"), wraplength=180).pack(pady=(0, 5), padx=10)
        ctk.CTkLabel(card, text=f"by {book.get('authors', 'N/A')}", wraplength=180).pack(pady=5, padx=10)
        ctk.CTkLabel(card, text=f"${book['price']:.2f}", font=ctk.CTkFont(size=16)).pack(pady=5, padx=10)
        ctk.CTkButton(card, text="Add to Cart", command=lambda b=book: messagebox.showinfo("Cart", f"'{b['title']}' added." if add_book_to_cart(self.controller.current_user['customer_id'], b['book_id'])[0] else "Failed to add.")).pack(pady=10)
        card.grid(row=index//4, column=index%4, padx=10, pady=10, sticky="nsew")

class CartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller; TopBar(self, controller)
        ctk.CTkButton(self, text="< Back to Shopping", command=lambda: controller.show_frame("HomePage")).pack(pady=10, padx=20, anchor="w")
        main = ctk.CTkFrame(self, fg_color="transparent"); main.pack(fill="both", expand=True, padx=20, pady=10)
        main.grid_columnconfigure(0, weight=3); main.grid_columnconfigure(1, weight=1); main.grid_rowconfigure(0, weight=1)
        self.cart_frame = ctk.CTkScrollableFrame(main, label_text="Shopping Cart"); self.cart_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.summary = ctk.CTkFrame(main, border_width=1); self.summary.grid(row=0, column=1, padx=(10, 0), sticky="nsew")
        self.load_cart()

    def load_cart(self):
        for w in self.cart_frame.winfo_children(): w.destroy()
        items = get_cart_items(self.controller.current_user['customer_id']); total = sum(i['subtotal'] for i in items)
        if not items: ctk.CTkLabel(self.cart_frame, text="Your cart is empty.").pack(pady=20)
        for i in items:
            f = ctk.CTkFrame(self.cart_frame); f.pack(fill="x", pady=5, padx=5)
            ctk.CTkLabel(f, text=f"{i['title']} (Qty: {i['quantity']})", wraplength=400, justify="left").pack(side="left", padx=10)
            ctk.CTkLabel(f, text=f"${i['subtotal']:.2f}", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10)
        for w in self.summary.winfo_children(): w.destroy()
        ctk.CTkLabel(self.summary, text="Order Summary", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)
        ctk.CTkLabel(self.summary, text=f"Total: ${total:.2f}", font=ctk.CTkFont(size=16)).pack(pady=10)
        if items: ctk.CTkButton(self.summary, text="Proceed to Checkout", height=40, command=self.checkout).pack(pady=20, padx=20, fill="x")

    def checkout(self):
        addr = self.controller.current_user.get('address', 'N/A'); total = sum(i['subtotal'] for i in get_cart_items(self.controller.current_user['customer_id']))
        if messagebox.askyesno("Confirm Checkout", f"Confirm order total of ${total:.2f}?\nShipping to: {addr}"):
            success, msg = process_checkout(self.controller.current_user['customer_id'], addr)
            messagebox.showinfo("Success", msg) if success else messagebox.showerror("Failed", msg)
            if success: self.controller.show_frame("HomePage")

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent); self.controller = controller; self.selected_book_id = None; TopBar(self, controller)
        main_frame = ctk.CTkFrame(self); main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=2); main_frame.grid_columnconfigure(1, weight=1); main_frame.grid_rowconfigure(0, weight=1)
        self.book_list_frame = ctk.CTkScrollableFrame(main_frame, label_text="Manage Books"); self.book_list_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        self.form_frame = ctk.CTkFrame(main_frame); self.form_frame.grid(row=0, column=1, padx=(10, 0), sticky="n")
        
        self.entries = { "title": ctk.CTkEntry(self.form_frame, placeholder_text="Title"), "price": ctk.CTkEntry(self.form_frame, placeholder_text="Price"), "stock": ctk.CTkEntry(self.form_frame, placeholder_text="Stock Quantity"), "isbn": ctk.CTkEntry(self.form_frame, placeholder_text="ISBN"), "year": ctk.CTkEntry(self.form_frame, placeholder_text="Publication Year") }
        for e in self.entries.values(): e.pack(pady=10, padx=20, fill="x")
        
        self.publishers = {p['name']: p['publisher_id'] for p in db_fetch_all("SELECT publisher_id, name FROM publishers")}; self.pub_var = ctk.StringVar(value=next(iter(self.publishers)) if self.publishers else "")
        ctk.CTkOptionMenu(self.form_frame, variable=self.pub_var, values=list(self.publishers.keys())).pack(pady=10, padx=20, fill="x")
        btn_frame = ctk.CTkFrame(self.form_frame, fg_color="transparent"); btn_frame.pack(pady=10, fill="x")
        ctk.CTkButton(btn_frame, text="Save Changes", command=self.save_book).pack(side="left", expand=True, padx=10)
        ctk.CTkButton(btn_frame, text="Clear Form", command=self.clear_form).pack(side="right", expand=True, padx=10)
        self.load_book_list()

    def load_book_list(self):
        for w in self.book_list_frame.winfo_children(): w.destroy()
        for book in search_books("", "Title"):
            f = ctk.CTkFrame(self.book_list_frame); f.pack(fill="x", pady=5)
            ctk.CTkLabel(f, text=f"{book['title']} (Stock: {book['stock_quantity']})", wraplength=400).pack(side="left", padx=10, expand=True, anchor="w")
            ctk.CTkButton(f, text="Delete", fg_color="red", width=60, command=lambda b_id=book['book_id']: self.delete_book_confirm(b_id)).pack(side="right", padx=5)
            ctk.CTkButton(f, text="Edit", width=60, command=lambda b=book: self.populate_form(b)).pack(side="right", padx=5)

    def populate_form(self, book):
        self.clear_form(); self.selected_book_id = book.get('book_id')
        self.entries['title'].insert(0, book.get('title', '')); self.entries['price'].insert(0, str(book.get('price', ''))); self.entries['stock'].insert(0, str(book.get('stock_quantity', ''))); self.entries['isbn'].insert(0, book.get('isbn', '')); self.entries['year'].insert(0, str(book.get('publication_year', '')))
    
    def clear_form(self):
        self.selected_book_id = None
        for e in self.entries.values(): e.delete(0, 'end')

    def save_book(self):
        details = {k: e.get() for k, e in self.entries.items()}; details['publisher_id'] = self.publishers.get(self.pub_var.get())
        if not all(v for k, v in details.items() if k != 'publisher_id'): messagebox.showerror("Error", "Please fill all fields."); return
        success, msg = update_book(self.selected_book_id, details) if self.selected_book_id else add_new_book(details)
        if success: messagebox.showinfo("Success", "Book saved."); self.load_book_list(); self.clear_form()
        else: messagebox.showerror("Error", msg)

    def delete_book_confirm(self, book_id):
        if messagebox.askyesno("Confirm Delete", "Are you sure? This cannot be undone."):
            success, msg = delete_book(book_id)
            if success: messagebox.showinfo("Success", "Book deleted."); self.load_book_list()
            else: messagebox.showerror("Error", msg)

if __name__ == "__main__":
    app = App()
    app.mainloop()