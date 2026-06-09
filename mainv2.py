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

def register_customer(name, email, password, address, phone):
    conn = get_db_connection()
    if not conn: return False, "Database connection failed."
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id FROM customers WHERE email = %s", (email,))
        if cursor.fetchone():
            return False, "An account with this email already exists."
        query = "INSERT INTO customers (name, email, password, address, phone) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (name, email, password, address, phone))
        conn.commit()
        return True, "Registration successful! You can now log in."
    except Error as e:
        return False, f"An error occurred: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def authenticate_user(email, password):
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT customer_id, password, role, name, address FROM customers WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        if user and user['password'] == password:
            return user
        return None
    except Error as e:
        messagebox.showerror("Authentication Error", f"An error occurred: {e}")
        return None
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_all_books():
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT b.book_id, b.title, b.price, b.stock_quantity, b.description,
                   GROUP_CONCAT(a.name SEPARATOR ', ') AS authors
            FROM books b
            LEFT JOIN book_authors ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            GROUP BY b.book_id ORDER BY b.title;
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        messagebox.showerror("Fetch Error", f"Could not retrieve books: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def add_book_to_cart(customer_id, book_id):
    conn = get_db_connection()
    if not conn: return False, "Database connection failed."
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO shopping_cart (customer_id, book_id, quantity)
            VALUES (%s, %s, 1)
            ON DUPLICATE KEY UPDATE quantity = quantity + 1;
        """
        cursor.execute(query, (customer_id, book_id))
        conn.commit()
        return True, f"Added to cart."
    except Error as e:
        return False, f"Error: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_cart_items(customer_id):
    conn = get_db_connection()
    if not conn: return []
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT sc.cart_id, b.book_id, b.title, sc.quantity, b.price, (sc.quantity * b.price) AS subtotal
            FROM shopping_cart sc
            JOIN books b ON sc.book_id = b.book_id
            WHERE sc.customer_id = %s
        """
        cursor.execute(query, (customer_id,))
        return cursor.fetchall()
    except Error as e:
        messagebox.showerror("Cart Error", f"Could not fetch cart items: {e}")
        return []
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def process_checkout(customer_id, shipping_address):
    conn = get_db_connection()
    if not conn: return False, "Database connection failed."
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()
        cursor.execute("SELECT * FROM shopping_cart WHERE customer_id = %s", (customer_id,))
        cart_items_raw = cursor.fetchall()
        if not cart_items_raw:
            return False, "Your cart is empty."
        
        cart_items = []
        total_amount = 0
        for item in cart_items_raw:
            cursor.execute("SELECT price, stock_quantity FROM books WHERE book_id = %s", (item['book_id'],))
            book_info = cursor.fetchone()
            if book_info['stock_quantity'] < item['quantity']:
                conn.rollback()
                return False, f"Not enough stock for book ID {item['book_id']}."
            total_amount += book_info['price'] * item['quantity']
            cart_items.append({**item, 'unit_price': book_info['price']})

        query_order = "INSERT INTO orders (customer_id, total_amount, shipping_address) VALUES (%s, %s, %s)"
        cursor.execute(query_order, (customer_id, total_amount, shipping_address))
        order_id = cursor.lastrowid

        query_details = "INSERT INTO order_details (order_id, book_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"
        for item in cart_items:
            cursor.execute(query_details, (order_id, item['book_id'], item['quantity'], item['unit_price']))
            cursor.execute("UPDATE books SET stock_quantity = stock_quantity - %s WHERE book_id = %s", (item['quantity'], item['book_id']))

        cursor.execute("DELETE FROM shopping_cart WHERE customer_id = %s", (customer_id,))
        
        conn.commit()
        return True, "Order placed successfully!"
    except Error as e:
        conn.rollback()
        return False, f"An error occurred during checkout: {e}"
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

def get_image_url(query):
    try:
        results = DDGS().images(keywords=query, region="wt-wt", safesearch="moderate", max_results=1)
        if results:
            return results[0]['image']
    except Exception as e:
        print(f"Image search failed: {e}")
    return None

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
        self.show_frame("LoginPage")

    def show_frame(self, page_name, **kwargs):
        if page_name in self.frames:
            self.frames[page_name].destroy()
        
        if page_name == "LoginPage":
            frame = LoginPage(self._container, self)
        elif page_name == "HomePage":
            frame = HomePage(self._container, self)
        elif page_name == "CartPage":
            frame = CartPage(self._container, self)
        elif page_name == "AdminDashboard":
            frame = AdminDashboard(self._container, self)
        else:
            raise ValueError(f"Page {page_name} not found.")

        self.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        login_frame = ctk.CTkFrame(self, fg_color="transparent")
        login_frame.place(relx=0.5, rely=0.5, anchor="center")

        label = ctk.CTkLabel(login_frame, text="E-Bookstore Login", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=12, padx=10)

        self.email_entry = ctk.CTkEntry(login_frame, placeholder_text="Email", width=250, height=40)
        self.email_entry.pack(pady=12, padx=10)

        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=250, height=40)
        self.password_entry.pack(pady=12, padx=10)

        ctk.CTkButton(login_frame, text="Login", command=self.handle_login, height=40).pack(pady=12, padx=10)
        ctk.CTkButton(login_frame, text="Register New Account", command=self.show_registration_window, height=40, fg_color="gray").pack(pady=12, padx=10)

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        user = authenticate_user(email, password)
        if user:
            self.controller.current_user = user
            messagebox.showinfo("Success", f"Welcome, {user['name']}!")
            if user['role'] == 'admin':
                self.controller.show_frame("AdminDashboard")
            else:
                self.controller.show_frame("HomePage")
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    def show_registration_window(self):
        reg_window = ctk.CTkToplevel(self)
        reg_window.title("Register New Account")
        reg_window.geometry("400x450")
        reg_window.transient(self)
        reg_window.grab_set()

        frame = ctk.CTkFrame(reg_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(frame, text="Create a New Account", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        entries = {
            "Full Name": ctk.CTkEntry(frame, placeholder_text="Full Name", width=250),
            "Email": ctk.CTkEntry(frame, placeholder_text="Email", width=250),
            "Password": ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250),
            "Address": ctk.CTkEntry(frame, placeholder_text="Address", width=250),
            "Phone Number": ctk.CTkEntry(frame, placeholder_text="Phone Number", width=250)
        }
        for entry in entries.values():
            entry.pack(pady=10, padx=20)
        
        def perform_registration():
            values = {name: entry.get() for name, entry in entries.items()}
            if not all(values.values()):
                messagebox.showerror("Input Error", "Please fill in all fields.", parent=reg_window)
                return
            success, message = register_customer(values["Full Name"], values["Email"], values["Password"], values["Address"], values["Phone Number"])
            if success:
                messagebox.showinfo("Success", message, parent=reg_window)
                reg_window.destroy()
            else:
                messagebox.showerror("Registration Failed", message, parent=reg_window)

        ctk.CTkButton(frame, text="Submit Registration", command=perform_registration).pack(pady=20)

class TopBar(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#1a1a1a", corner_radius=0, height=60)
        self.controller = controller
        
        self.pack(side="top", fill="x")

        welcome_text = f"Welcome, {self.controller.current_user['name']}"
        welcome_label = ctk.CTkLabel(self, text=welcome_text, font=ctk.CTkFont(size=16))
        welcome_label.pack(side="left", padx=20)

        logout_button = ctk.CTkButton(self, text="Logout", fg_color="gray", command=self.logout)
        logout_button.pack(side="right", padx=10, pady=10)

        cart_button = ctk.CTkButton(self, text="View Cart", command=lambda: self.controller.show_frame("CartPage"))
        cart_button.pack(side="right", padx=10, pady=10)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("LoginPage")

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        TopBar(self, controller)
        
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Bestsellers")
        self.scrollable_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.scrollable_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.load_books()

    def load_books(self):
        books = get_all_books()
        for i, book in enumerate(books):
            threading.Thread(target=self.create_book_card, args=(book, i), daemon=True).start()

    def create_book_card(self, book, index):
        card = ctk.CTkFrame(self.scrollable_frame, border_width=1, border_color="gray")
        
        placeholder = Image.new('RGB', (150, 220), color = '#565656')
        ctk_placeholder = ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=(150, 220))
        image_label = ctk.CTkLabel(card, text="", image=ctk_placeholder)
        image_label.pack(pady=10, padx=10)
        
        image_url = get_image_url(f"{book['title']} book cover")
        if image_url:
            try:
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    img_data = Image.open(BytesIO(response.content))
                    img_data.thumbnail((150, 220))
                    ctk_image = ctk.CTkImage(light_image=img_data, dark_image=img_data, size=(img_data.width, img_data.height))
                    self.after(0, lambda: image_label.configure(image=ctk_image))
            except Exception as e:
                print(f"Failed to load image for {book['title']}: {e}")

        title_label = ctk.CTkLabel(card, text=book['title'], font=ctk.CTkFont(weight="bold"), wraplength=180)
        title_label.pack(pady=(0, 5), padx=10)

        author_label = ctk.CTkLabel(card, text=f"by {book.get('authors', 'N/A')}", wraplength=180)
        author_label.pack(pady=5, padx=10)

        price_label = ctk.CTkLabel(card, text=f"${book['price']:.2f}", font=ctk.CTkFont(size=16))
        price_label.pack(pady=5, padx=10)
        
        def add_to_cart_command(b=book):
            success, message = add_book_to_cart(self.controller.current_user['customer_id'], b['book_id'])
            if success:
                messagebox.showinfo("Cart", f"'{b['title']}' added to your cart.")
            else:
                messagebox.showerror("Error", message)

        cart_button = ctk.CTkButton(card, text="Add to Cart", command=add_to_cart_command)
        cart_button.pack(pady=10, padx=10)

        row, col = divmod(index, 4)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

class CartPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        TopBar(self, controller)
        
        ctk.CTkButton(self, text="< Back to Shopping", command=lambda: controller.show_frame("HomePage")).pack(pady=10, padx=20, anchor="w")

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        main_frame.grid_columnconfigure(0, weight=3)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        self.cart_frame = ctk.CTkScrollableFrame(main_frame, label_text="Your Shopping Cart")
        self.cart_frame.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.summary_frame = ctk.CTkFrame(main_frame, border_width=1)
        self.summary_frame.grid(row=0, column=1, padx=(10, 0), sticky="nsew")

        self.load_cart()

    def load_cart(self):
        for widget in self.cart_frame.winfo_children():
            widget.destroy()

        items = get_cart_items(self.controller.current_user['customer_id'])
        total = sum(item['subtotal'] for item in items)
        
        if not items:
            ctk.CTkLabel(self.cart_frame, text="Your cart is empty.", font=ctk.CTkFont(size=16)).pack(pady=20)
        
        for item in items:
            item_frame = ctk.CTkFrame(self.cart_frame)
            item_frame.pack(fill="x", pady=5, padx=5)
            
            info_text = f"{item['title']} (Qty: {item['quantity']})"
            ctk.CTkLabel(item_frame, text=info_text, wraplength=400, justify="left").pack(side="left", padx=10, pady=5)
            ctk.CTkLabel(item_frame, text=f"${item['subtotal']:.2f}", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=10, pady=5)
        
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.summary_frame, text="Order Summary", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10, padx=10)
        ctk.CTkLabel(self.summary_frame, text=f"Total: ${total:.2f}", font=ctk.CTkFont(size=16)).pack(pady=10, padx=10)
        
        if items:
            ctk.CTkButton(self.summary_frame, text="Proceed to Checkout", height=40, command=self.checkout).pack(pady=20, padx=20, fill="x")

    def checkout(self):
        shipping_address = self.controller.current_user.get('address', 'N/A')
        confirm = messagebox.askyesno("Confirm Checkout", f"Confirm order with a total of ${sum(item['subtotal'] for item in get_cart_items(self.controller.current_user['customer_id'])):.2f}?\n\nShipping to: {shipping_address}")
        
        if confirm:
            success, message = process_checkout(self.controller.current_user['customer_id'], shipping_address)
            if success:
                messagebox.showinfo("Success", message)
                self.controller.show_frame("HomePage")
            else:
                messagebox.showerror("Checkout Failed", message)

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        TopBar(self, controller)
        label = ctk.CTkLabel(self, text="Admin Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20, padx=20)
        info_label = ctk.CTkLabel(self, text="Management features for books, authors, and orders would be implemented here.")
        info_label.pack(pady=10, padx=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()