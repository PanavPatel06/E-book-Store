import customtkinter as ctk
import mysql.connector
from mysql.connector import Error
from tkinter import messagebox

# --- DATABASE FUNCTIONS ---

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    Update the user and password fields to match your MySQL setup.
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # <-- IMPORTANT: Make sure this is your MySQL username
            password="Panav@960",  # <-- IMPORTANT: Change this to your MySQL password
            database="ebookstore"
        )
        return connection
    except Error as e:
        messagebox.showerror("Database Error", f"Could not connect to database: {e}")
        return None

def register_customer(name, email, password, address, phone):
    """Registers a new customer with a plain text password."""
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
    """Authenticates a user by directly comparing the plain text password."""
    conn = get_db_connection()
    if not conn: return None

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT customer_id, password, role, name FROM customers WHERE email = %s"
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
    """Retrieves all available books with author names."""
    conn = get_db_connection()
    if not conn: return []

    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT b.book_id, b.title, b.price, b.stock_quantity,
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


# --- GUI CLASSES ---

class AdminDashboard(ctk.CTkFrame):
    """Placeholder frame for the Admin Dashboard."""
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(self, text="Admin Dashboard", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20, padx=20)

        info_label = ctk.CTkLabel(self, text="Management features for books, authors, and orders would be implemented here.")
        info_label.pack(pady=10, padx=20)

class UserDashboard(ctk.CTkFrame):
    """Dashboard for the regular customer to view and interact with books."""
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.user_info = user_info

        label = ctk.CTkLabel(self, text=f"Welcome, {self.user_info['name']}!", font=ctk.CTkFont(size=24, weight="bold"))
        label.pack(pady=20, padx=20)

        books_frame = ctk.CTkScrollableFrame(self, label_text="Available Books")
        books_frame.pack(pady=10, padx=20, fill="both", expand=True)

        books = get_all_books()
        if not books:
            ctk.CTkLabel(books_frame, text="No books available.").pack(pady=10)
        else:
            for book in books:
                text = f"'{book['title']}' by {book.get('authors', 'N/A')} - ${book['price']}"
                ctk.CTkLabel(books_frame, text=text, anchor="w").pack(fill="x", padx=10, pady=5)

class LoginPage(ctk.CTkFrame):
    """The initial login and registration page."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        login_frame = ctk.CTkFrame(self)
        login_frame.pack(pady=20, padx=60, fill="both", expand=True)

        label = ctk.CTkLabel(login_frame, text="Login", font=ctk.CTkFont(size=20, weight="bold"))
        label.pack(pady=12, padx=10)

        self.email_entry = ctk.CTkEntry(login_frame, placeholder_text="Email", width=200)
        self.email_entry.pack(pady=12, padx=10)

        self.password_entry = ctk.CTkEntry(login_frame, placeholder_text="Password", show="*", width=200)
        self.password_entry.pack(pady=12, padx=10)

        ctk.CTkButton(login_frame, text="Login", command=self.handle_login).pack(pady=12, padx=10)

        ctk.CTkLabel(login_frame, text="--- OR ---").pack(pady=5)
        ctk.CTkLabel(login_frame, text="Don't have an account?").pack()

        ctk.CTkButton(login_frame, text="Register New Account", command=self.show_registration_window).pack(pady=12, padx=10)

    def handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        if not email or not password:
            messagebox.showerror("Error", "Please enter both email and password.")
            return

        user = authenticate_user(email, password)
        if user:
            messagebox.showinfo("Success", f"Welcome, {user['name']}!")
            self.pack_forget() # Hide login page
            if user['role'] == 'admin':
                dashboard = AdminDashboard(self.master)
            else:
                dashboard = UserDashboard(self.master, user)
            dashboard.pack(fill="both", expand=True)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")

    def show_registration_window(self):
        # Create a new top-level window for registration
        reg_window = ctk.CTkToplevel(self)
        reg_window.title("Register New Account")
        reg_window.geometry("400x450")
        reg_window.transient(self) # Keep this window on top
        reg_window.grab_set()      # Modal behavior

        frame = ctk.CTkFrame(reg_window)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Create a New Account", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        name_entry = ctk.CTkEntry(frame, placeholder_text="Full Name", width=250)
        name_entry.pack(pady=10, padx=20)

        email_entry = ctk.CTkEntry(frame, placeholder_text="Email", width=250)
        email_entry.pack(pady=10, padx=20)

        password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250)
        password_entry.pack(pady=10, padx=20)

        address_entry = ctk.CTkEntry(frame, placeholder_text="Address", width=250)
        address_entry.pack(pady=10, padx=20)

        phone_entry = ctk.CTkEntry(frame, placeholder_text="Phone Number", width=250)
        phone_entry.pack(pady=10, padx=20)

        def perform_registration():
            # Get values from all fields
            name = name_entry.get()
            email = email_entry.get()
            password = password_entry.get()
            address = address_entry.get()
            phone = phone_entry.get()
            
            # Basic validation
            if not all([name, email, password, address, phone]):
                messagebox.showerror("Input Error", "Please fill in all fields.", parent=reg_window)
                return

            # Call the database function with all the required data
            success, message = register_customer(name, email, password, address, phone)
            
            if success:
                messagebox.showinfo("Success", message, parent=reg_window)
                reg_window.destroy() # Close the registration window on success
            else:
                messagebox.showerror("Registration Failed", message, parent=reg_window)

        ctk.CTkButton(frame, text="Submit Registration", command=perform_registration).pack(pady=20)


class App(ctk.CTk):
    """The main application window."""
    def __init__(self):
        super().__init__()
        self.title("E-Bookstore Management System")
        self.geometry("800x600")
        
        LoginPage(self, self).pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()