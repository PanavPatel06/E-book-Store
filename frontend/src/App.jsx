import React, { useState, useEffect, useRef } from 'react';

// Custom inline SVG components to avoid sandbox network blocks and external dependencies
const BookOpen = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" /><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
  </svg>
);
const ShoppingCart = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="8" cy="21" r="1" /><circle cx="19" cy="21" r="1" />
    <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12" />
  </svg>
);
const Settings = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.1a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z" />
    <circle cx="12" cy="12" r="3" />
  </svg>
);
const ShieldAlert = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M20 13c0 5-3.5 7.5-7.66 9.7a1 1 0 0 1-.68 0C7.5 20.5 4 18 4 13V6a1 1 0 0 1 .76-.97l8-2a1 1 0 0 1 .48 0l8 2A1 1 0 0 1 20 6z" />
    <line x1="12" x2="12" y1="9" y2="13" /><line x1="12" x2="12.01" y1="17" y2="17" />
  </svg>
);
const LogOut = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
    <polyline points="16 17 21 12 16 7" /><line x1="21" x2="9" y1="12" y2="12" />
  </svg>
);
const User = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2" />
    <circle cx="12" cy="7" r="4" />
  </svg>
);
const Search = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="11" cy="11" r="8" /><line x1="21" x2="16.65" y1="21" y2="16.65" />
  </svg>
);
const Trash2 = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" /><line x1="10" x2="10" y1="11" y2="17" /><line x1="14" x2="14" y1="11" y2="17" />
  </svg>
);
const Edit = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M12 20h9" /><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
  </svg>
);
const Check = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <polyline points="20 6 9 17 4 12" />
  </svg>
);
const AlertCircle = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <circle cx="12" cy="12" r="10" /><line x1="12" x2="12" y1="8" y2="12" /><line x1="12" x2="12.01" y1="16" y2="16" />
  </svg>
);
const Database = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <ellipse cx="12" cy="5" rx="9" ry="3" />
    <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" /><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3" />
  </svg>
);
const Terminal = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <polyline points="4 17 10 11 4 5" /><line x1="12" x2="20" y1="19" y2="19" />
  </svg>
);
const Play = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <polygon points="6 3 20 12 6 21 6 3" />
  </svg>
);
const ChevronDown = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <polyline points="6 9 12 15 18 9" />
  </svg>
);
const ChevronRight = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <polyline points="9 18 15 12 9 6" />
  </svg>
);
const ShoppingBag = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
    <line x1="3" x2="21" y1="6" y2="6" /><path d="M16 10a4 4 0 0 1-8 0" />
  </svg>
);
const ClipboardList = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2" />
    <rect x="8" y="2" width="8" height="4" rx="1" ry="1" />
    <line x1="8" x2="8" y1="11" y2="11" /><line x1="8" x2="8" y1="16" y2="16" />
    <line x1="12" x2="16" y1="11" y2="11" /><line x1="12" x2="16" y1="16" y2="16" />
  </svg>
);
const MapPin = ({ size = 24, ...props }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}>
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z" /><circle cx="12" cy="10" r="3" />
  </svg>
);

const API_BASE = import.meta.env.DEV ? 'http://localhost:8000' : '';

export default function App() {
  // Navigation & Session
  const [view, setView] = useState('home');
  const [user, setUser] = useState(null);
  const [authError, setAuthError] = useState('');
  
  // Forms state
  const [loginForm, setLoginForm] = useState({ email: '', password: '' });
  const [registerForm, setRegisterForm] = useState({ name: '', email: '', password: '', phone: '', address: '' });
  
  // Data lists
  const [books, setBooks] = useState([]);
  const [publishers, setPublishers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [covers, setCovers] = useState({}); // cached covers: {title: url}

  // Search
  const [search, setSearch] = useState('');
  const [searchBy, setSearchBy] = useState('Title');

  // Live DBMS Logs & Terminal
  const [sqlLogs, setSqlLogs] = useState([]);
  const [terminalOpen, setTerminalOpen] = useState(true);
  const [schema, setSchema] = useState({});
  const [playgroundQuery, setPlaygroundQuery] = useState('SELECT * FROM books WHERE price < 15.00;');
  const [playgroundResult, setPlaygroundResult] = useState(null);
  const [playgroundError, setPlaygroundError] = useState('');

  // Admin Manage Book Form
  const [adminBook, setAdminBook] = useState({
    book_id: null,
    title: '',
    price: '',
    stock_quantity: '',
    isbn: '',
    publication_year: new Date().getFullYear(),
    publisher_id: '',
    description: ''
  });

  // Load user from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('ebook_user');
    if (savedUser) {
      const parsed = JSON.parse(savedUser);
      setUser(parsed);
      fetchCart(parsed.customer_id);
      if (parsed.role === 'admin') {
        setView('admin');
      }
    }
    fetchBooks();
    fetchSchema();
  }, []);

  // Poll SQL Logs every 2 seconds
  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 2500);
    return () => clearInterval(interval);
  }, []);

  // Fetch admin-only resources or update checkout logs when user changes
  useEffect(() => {
    if (user) {
      fetchCart(user.customer_id);
      if (user.role === 'admin') {
        fetchAdminData();
      }
    } else {
      setCart({ items: [], total: 0 });
    }
  }, [user]);

  // --- API Fetch Helpers ---

  const fetchBooks = async (searchStr = '', searchByField = 'Title') => {
    try {
      const queryParams = new URLSearchParams();
      if (searchStr) {
        queryParams.append('search', searchStr);
        queryParams.append('search_by', searchByField);
      }
      const res = await fetch(`${API_BASE}/api/books?${queryParams.toString()}`);
      if (res.ok) {
        const data = await res.ok ? await res.json() : [];
        setBooks(data);
        // Load book covers asynchronously
        data.forEach(book => {
          if (!covers[book.title]) {
            fetchCover(book.title);
          }
        });
      }
    } catch (err) {
      console.error("Failed to load books:", err);
    }
  };

  const fetchCover = async (title) => {
    try {
      const res = await fetch(`${API_BASE}/api/books/cover?query=${encodeURIComponent(title)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.url) {
          setCovers(prev => ({ ...prev, [title]: data.url }));
        }
      }
    } catch (err) {
      console.color("Failed cover query", err);
    }
  };

  const fetchCart = async (customerId) => {
    if (!customerId) return;
    try {
      const res = await fetch(`${API_BASE}/api/cart?customer_id=${customerId}`);
      if (res.ok) {
        const data = await res.json();
        setCart(data);
      }
    } catch (err) {
      console.error("Cart error:", err);
    }
  };

  const fetchLogs = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/db/logs`);
      if (res.ok) {
        const data = await res.json();
        setSqlLogs(data);
      }
    } catch (err) {
      // Quiet fail to avoid polluting developer tools
    }
  };

  const fetchSchema = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/db/schema`);
      if (res.ok) {
        const data = await res.json();
        setSchema(data);
      }
    } catch (err) {
      console.error("Schema fetch error:", err);
    }
  };

  const fetchAdminData = async () => {
    try {
      const pRes = await fetch(`${API_BASE}/api/admin/publishers`);
      if (pRes.ok) {
        const pData = await pRes.json();
        setPublishers(pData);
        if (pData.length > 0 && !adminBook.publisher_id) {
          setAdminBook(prev => ({ ...prev, publisher_id: pData[0].publisher_id }));
        }
      }
      const oRes = await fetch(`${API_BASE}/api/admin/orders`);
      if (oRes.ok) {
        setOrders(await oRes.json());
      }
    } catch (err) {
      console.error("Admin data loading failed:", err);
    }
  };

  // --- Auth Handlers ---

  const handleLogin = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(loginForm)
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
        localStorage.setItem('ebook_user', JSON.stringify(data));
        setView(data.role === 'admin' ? 'admin' : 'home');
        setLoginForm({ email: '', password: '' });
      } else {
        const err = await res.json();
        setAuthError(err.detail || 'Login failed.');
      }
    } catch (err) {
      setAuthError('Server connection failed.');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      const res = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(registerForm)
      });
      if (res.ok) {
        alert("Account created successfully! Please log in.");
        setRegisterForm({ name: '', email: '', password: '', phone: '', address: '' });
        setView('login');
      } else {
        const err = await res.json();
        setAuthError(err.detail || 'Registration failed.');
      }
    } catch (err) {
      setAuthError('Server connection failed.');
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem('ebook_user');
    setView('home');
  };

  // --- Cart Handlers ---

  const addToCart = async (bookId) => {
    if (!user) {
      setView('login');
      return;
    }
    try {
      const res = await fetch(`${API_BASE}/api/cart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: user.customer_id, book_id: bookId, quantity: 1 })
      });
      if (res.ok) {
        fetchCart(user.customer_id);
        alert("Book added to cart!");
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to add book.");
      }
    } catch (err) {
      alert("Error adding item to cart.");
    }
  };

  const updateCartQty = async (bookId, currentQty, amount) => {
    const targetQty = currentQty + amount;
    try {
      const res = await fetch(`${API_BASE}/api/cart/${bookId}?customer_id=${user.customer_id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: targetQty })
      });
      if (res.ok) {
        fetchCart(user.customer_id);
        fetchBooks(); // refresh stock numbers
      } else {
        const err = await res.json();
        alert(err.detail || "Quantity update failed.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const removeFromCart = async (bookId) => {
    try {
      const res = await fetch(`${API_BASE}/api/cart/${bookId}?customer_id=${user.customer_id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        fetchCart(user.customer_id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleCheckout = async () => {
    if (!user.address) {
      const addr = prompt("Please confirm your shipping address:", user.address || "");
      if (!addr) return;
      user.address = addr;
      setUser({ ...user });
      localStorage.setItem('ebook_user', JSON.stringify(user));
    }
    
    try {
      const res = await fetch(`${API_BASE}/api/checkout`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customer_id: user.customer_id, shipping_address: user.address })
      });
      if (res.ok) {
        const data = await res.json();
        alert(`Order placed successfully! Order ID: #${data.order_id}`);
        fetchCart(user.customer_id);
        fetchBooks();
        setView('home');
      } else {
        const err = await res.json();
        alert(err.detail || "Checkout failed.");
      }
    } catch (err) {
      alert("Error processing transaction checkout.");
    }
  };

  // --- Admin Handlers ---

  const handleAdminSaveBook = async (e) => {
    e.preventDefault();
    const isEdit = !!adminBook.book_id;
    const url = isEdit 
      ? `${API_BASE}/api/admin/books/${adminBook.book_id}`
      : `${API_BASE}/api/admin/books`;
      
    try {
      const res = await fetch(url, {
        method: isEdit ? 'PUT' : 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: adminBook.title,
          price: parseFloat(adminBook.price),
          stock_quantity: parseInt(adminBook.stock_quantity),
          isbn: adminBook.isbn,
          publication_year: parseInt(adminBook.publication_year),
          publisher_id: parseInt(adminBook.publisher_id),
          description: adminBook.description
        })
      });
      
      if (res.ok) {
        alert(isEdit ? "Book updated successfully." : "Book added successfully.");
        fetchBooks();
        setAdminBook({
          book_id: null,
          title: '',
          price: '',
          stock_quantity: '',
          isbn: '',
          publication_year: new Date().getFullYear(),
          publisher_id: publishers[0]?.publisher_id || '',
          description: ''
        });
      } else {
        const err = await res.json();
        alert(err.detail || "Failed to save book settings.");
      }
    } catch (err) {
      alert("Error communicating with admin API.");
    }
  };

  const handleAdminDeleteBook = async (bookId) => {
    if (!confirm("Are you sure you want to delete this book? This will clear its constraints cascades.")) return;
    try {
      const res = await fetch(`${API_BASE}/api/admin/books/${bookId}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        alert("Book removed.");
        fetchBooks();
      } else {
        const err = await res.json();
        alert(err.detail || "Delete operation failed.");
      }
    } catch (err) {
      console.error(err);
    }
  };

  // --- SQL Playground handler ---

  const runPlaygroundQuery = async () => {
    setPlaygroundError('');
    setPlaygroundResult(null);
    try {
      const res = await fetch(`${API_BASE}/api/db/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: playgroundQuery })
      });
      if (res.ok) {
        const data = await res.json();
        if (data.success) {
          setPlaygroundResult(data);
        } else {
          setPlaygroundError(data.error);
        }
      }
    } catch (err) {
      setPlaygroundError("Database connection timed out.");
    }
  };

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <header className="navbar glass">
        <div className="nav-brand">
          <BookOpen size={24} color="#3b82f6" />
          <span>E-book Store</span>
        </div>
        <nav className="nav-links">
          <span className={`nav-link ${view === 'home' ? 'active' : ''}`} onClick={() => setView('home')}>
            Store
          </span>
          <span className={`nav-link ${view === 'showcase' ? 'active' : ''}`} onClick={() => setView('showcase')}>
            <Database size={16} /> Showcase DB
          </span>
          {user && user.role === 'admin' && (
            <span className={`nav-link ${view === 'admin' ? 'active' : ''}`} onClick={() => setView('admin')}>
              <Settings size={16} /> Admin Portal
            </span>
          )}
          {!user ? (
            <span className={`nav-link ${view === 'login' ? 'active' : ''}`} onClick={() => setView('login')}>
              <User size={16} /> Sign In
            </span>
          ) : (
            <>
              {user.role !== 'admin' && (
                <span className={`nav-link ${view === 'cart' ? 'active' : ''}`} onClick={() => setView('cart')}>
                  <ShoppingCart size={16} />
                  <span>Cart ({cart.items.reduce((acc, curr) => acc + curr.quantity, 0)})</span>
                </span>
              )}
              <span className="nav-link" onClick={handleLogout} title="Log Out">
                <LogOut size={16} />
              </span>
            </>
          )}
        </nav>
      </header>

      {/* Main Container */}
      <main className="main-content">
        
        {/* --- VIEW: Catalog Storefront --- */}
        {view === 'home' && (
          <div>
            <div className="catalog-header">
              <h1>Digital Inventory Catalog</h1>
              <div className="search-bar">
                <select 
                  className="search-select" 
                  value={searchBy} 
                  onChange={(e) => { setSearchBy(e.target.value); fetchBooks(search, e.target.value); }}
                >
                  <option value="Title">Search by Title</option>
                  <option value="Author">Search by Author</option>
                  <option value="Category">Search by Category</option>
                </select>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder="Type query terms..." 
                  value={search}
                  onChange={(e) => { setSearch(e.target.value); fetchBooks(e.target.value, searchBy); }}
                />
                <button className="btn btn-primary" onClick={() => fetchBooks(search, searchBy)}>
                  <Search size={16} />
                </button>
              </div>
            </div>

            <div className="books-grid">
              {books.map(book => (
                <div key={book.book_id} className="book-card glass">
                  <div className="book-cover-container">
                    {covers[book.title] ? (
                      <img src={covers[book.title]} alt={book.title} className="book-cover" />
                    ) : (
                      <div className="book-cover-fallback">
                        <span className="fallback-title">{book.title}</span>
                        <span className="fallback-author">{book.authors?.join(', ') || 'Unknown Author'}</span>
                      </div>
                    )}
                  </div>
                  <div className="book-details">
                    <h3 className="book-title" title={book.title}>{book.title}</h3>
                    <p className="book-author">by {book.authors?.join(', ') || 'N/A'}</p>
                    <div className="book-meta">
                      {book.categories?.map(cat => (
                        <span key={cat} className="badge badge-primary">{cat}</span>
                      ))}
                      {book.stock_quantity > 0 ? (
                        <span className="badge badge-success">In Stock ({book.stock_quantity})</span>
                      ) : (
                        <span className="badge badge-danger">Out of Stock</span>
                      )}
                    </div>
                    <p className="book-description">{book.description || 'No description provided.'}</p>
                    <div className="book-footer">
                      <span className="book-price">${book.price.toFixed(2)}</span>
                      {book.stock_quantity > 0 && user?.role !== 'admin' && (
                        <button className="btn btn-primary" onClick={() => addToCart(book.book_id)}>
                          <ShoppingCart size={14} /> Add
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
              {books.length === 0 && (
                <div className="glass text-center" style={{ gridColumn: '1 / -1', padding: '3rem' }}>
                  <p style={{ color: 'var(--text-secondary)' }}>No books match your selection query.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* --- VIEW: Login Screen --- */}
        {view === 'login' && (
          <div className="auth-wrapper">
            <div className="auth-card glass">
              <div className="auth-header">
                <h2 className="auth-title">Welcome Back</h2>
                <p className="auth-subtitle">Log in to manage your e-books shopping cart</p>
              </div>
              <form onSubmit={handleLogin}>
                {authError && (
                  <div className="form-group flex align-center gap-1" style={{ color: 'var(--danger)', fontSize: '0.875rem' }}>
                    <AlertCircle size={16} /> <span>{authError}</span>
                  </div>
                )}
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input 
                    type="email" 
                    className="form-input" 
                    required 
                    placeholder="amit.sharma@email.com"
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input 
                    type="password" 
                    className="form-input" 
                    required 
                    placeholder="••••••••"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  />
                </div>
                <button type="submit" className="btn btn-primary btn-block mb-4">Login</button>
                <p className="text-center" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  Don't have an account?{' '}
                  <span style={{ color: 'var(--accent-secondary)', cursor: 'pointer' }} onClick={() => setView('register')}>
                    Create registration
                  </span>
                </p>
              </form>
            </div>
          </div>
        )}

        {/* --- VIEW: Register Screen --- */}
        {view === 'register' && (
          <div className="auth-wrapper">
            <div className="auth-card glass">
              <div className="auth-header">
                <h2 className="auth-title">Create Account</h2>
                <p className="auth-subtitle">Register to shop online e-books</p>
              </div>
              <form onSubmit={handleRegister}>
                {authError && (
                  <div className="form-group flex align-center gap-1" style={{ color: 'var(--danger)', fontSize: '0.875rem' }}>
                    <AlertCircle size={16} /> <span>{authError}</span>
                  </div>
                )}
                <div className="form-group">
                  <label className="form-label">Full Name</label>
                  <input 
                    type="text" 
                    className="form-input" 
                    required 
                    placeholder="John Doe"
                    value={registerForm.name}
                    onChange={(e) => setRegisterForm({ ...registerForm, name: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Email Address</label>
                  <input 
                    type="email" 
                    className="form-input" 
                    required 
                    placeholder="john.doe@email.com"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Password</label>
                  <input 
                    type="password" 
                    className="form-input" 
                    required 
                    placeholder="••••••••"
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Phone</label>
                  <input 
                    type="text" 
                    className="form-input" 
                    placeholder="+91-9876543210"
                    value={registerForm.phone}
                    onChange={(e) => setRegisterForm({ ...registerForm, phone: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label className="form-label">Shipping Address</label>
                  <input 
                    type="text" 
                    className="form-input" 
                    placeholder="123 Street Name, City, State, Country"
                    value={registerForm.address}
                    onChange={(e) => setRegisterForm({ ...registerForm, address: e.target.value })}
                  />
                </div>
                <button type="submit" className="btn btn-primary btn-block mb-4">Register</button>
                <p className="text-center" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                  Already registered?{' '}
                  <span style={{ color: 'var(--accent-secondary)', cursor: 'pointer' }} onClick={() => setView('login')}>
                    Sign in here
                  </span>
                </p>
              </form>
            </div>
          </div>
        )}

        {/* --- VIEW: Shopping Cart Page --- */}
        {view === 'cart' && (
          <div>
            <h1 className="mb-4">Shopping Cart Drawer</h1>
            <div className="cart-layout">
              <div className="cart-items-card glass">
                {cart.items.map(item => (
                  <div key={item.book_id} className="cart-item">
                    <div className="cart-item-info">
                      <h3 className="cart-item-title">{item.title}</h3>
                      <p className="cart-item-price">${item.price.toFixed(2)} each</p>
                    </div>
                    <div className="cart-item-actions">
                      <div className="quantity-controls">
                        <button className="qty-btn" onClick={() => updateCartQty(item.book_id, item.quantity, -1)}>-</button>
                        <span className="qty-val">{item.quantity}</span>
                        <button className="qty-btn" onClick={() => updateCartQty(item.book_id, item.quantity, 1)}>+</button>
                      </div>
                      <span className="book-price" style={{ minWidth: '80px', textAlign: 'right' }}>
                        ${item.subtotal.toFixed(2)}
                      </span>
                      <button className="btn btn-secondary" onClick={() => removeFromCart(item.book_id)} style={{ padding: '0.5rem' }}>
                        <Trash2 size={16} color="var(--danger)" />
                      </button>
                    </div>
                  </div>
                ))}
                {cart.items.length === 0 && (
                  <div className="text-center" style={{ padding: '2rem' }}>
                    <ShoppingBag size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
                    <p style={{ color: 'var(--text-secondary)' }}>Your shopping cart is empty.</p>
                    <button className="btn btn-primary mt-4" onClick={() => setView('home')}>Shop E-Books</button>
                  </div>
                )}
              </div>

              {cart.items.length > 0 && (
                <div className="cart-summary-card glass">
                  <h2>Order Summary</h2>
                  <div className="summary-row mt-4">
                    <span style={{ color: 'var(--text-secondary)' }}>Items Subtotal</span>
                    <span>${cart.total.toFixed(2)}</span>
                  </div>
                  <div className="summary-row">
                    <span style={{ color: 'var(--text-secondary)' }}>Shipping Rate</span>
                    <span style={{ color: 'var(--success)' }}>FREE</span>
                  </div>
                  <div className="summary-row summary-total">
                    <span>Grand Total</span>
                    <span>${cart.total.toFixed(2)}</span>
                  </div>
                  
                  <div className="form-group mt-4">
                    <label className="form-label flex align-center gap-1">
                      <MapPin size={14} /> Shipping Address
                    </label>
                    <textarea 
                      className="form-input" 
                      rows={2} 
                      value={user?.address || ''} 
                      onChange={(e) => {
                        user.address = e.target.value;
                        setUser({ ...user });
                        localStorage.setItem('ebook_user', JSON.stringify(user));
                      }}
                    />
                  </div>

                  <button className="btn btn-primary btn-block mt-4" onClick={handleCheckout}>
                    Process Secure Checkout
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* --- VIEW: Admin Dashboard --- */}
        {user && user.role === 'admin' && view === 'admin' && (
          <div className="admin-layout">
            <h1 className="mb-4">Inventory Operations Dashboard</h1>
            
            <div className="stats-grid">
              <div className="stat-card glass">
                <div className="stat-icon"><BookOpen size={24} /></div>
                <div>
                  <div className="stat-value">{books.length}</div>
                  <div className="stat-label">Total E-Books</div>
                </div>
              </div>
              <div className="stat-card glass">
                <div className="stat-icon"><ClipboardList size={24} /></div>
                <div>
                  <div className="stat-value">{orders.length}</div>
                  <div className="stat-label">Orders Logged</div>
                </div>
              </div>
              <div className="stat-card glass">
                <div className="stat-icon"><ShoppingBag size={24} /></div>
                <div>
                  <div className="stat-value">
                    ${orders.reduce((acc, curr) => acc + curr.total_amount, 0).toFixed(2)}
                  </div>
                  <div className="stat-label">Total Turnover</div>
                </div>
              </div>
            </div>

            <div className="admin-grid">
              <div className="glass" style={{ padding: '1.5rem', borderRadius: '12px' }}>
                <h2>Configure Book Catalog</h2>
                <div className="table-wrapper mt-4">
                  <table className="admin-table">
                    <thead>
                      <tr>
                        <th>ISBN</th>
                        <th>Title</th>
                        <th>Price</th>
                        <th>Stock</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {books.map(book => (
                        <tr key={book.book_id}>
                          <td>{book.isbn}</td>
                          <td style={{ fontWeight: 600 }}>{book.title}</td>
                          <td>${book.price.toFixed(2)}</td>
                          <td>
                            <span className={`badge ${book.stock_quantity < 10 ? 'badge-danger' : 'badge-success'}`}>
                              {book.stock_quantity} units
                            </span>
                          </td>
                          <td>
                            <div className="flex gap-1">
                              <button className="btn btn-secondary" onClick={() => setAdminBook({ ...book })} style={{ padding: '0.4rem' }}>
                                <Edit size={14} />
                              </button>
                              <button className="btn btn-secondary" onClick={() => handleAdminDeleteBook(book.book_id)} style={{ padding: '0.4rem' }}>
                                <Trash2 size={14} color="var(--danger)" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="glass" style={{ padding: '1.5rem', borderRadius: '12px', height: 'fit-content' }}>
                <h2>{adminBook.book_id ? 'Modify Catalog Entry' : 'Add New E-Book'}</h2>
                <form onSubmit={handleAdminSaveBook} className="mt-4">
                  <div className="form-group">
                    <label className="form-label">Book Title</label>
                    <input 
                      type="text" 
                      className="form-input" 
                      required 
                      value={adminBook.title}
                      onChange={(e) => setAdminBook({ ...adminBook, title: e.target.value })}
                    />
                  </div>
                  <div className="form-group flex gap-2">
                    <div className="flex-1">
                      <label className="form-label">Price ($)</label>
                      <input 
                        type="number" 
                        step="0.01" 
                        className="form-input" 
                        required 
                        value={adminBook.price}
                        onChange={(e) => setAdminBook({ ...adminBook, price: e.target.value })}
                      />
                    </div>
                    <div className="flex-1">
                      <label className="form-label">Stock Quantity</label>
                      <input 
                        type="number" 
                        className="form-input" 
                        required 
                        value={adminBook.stock_quantity}
                        onChange={(e) => setAdminBook({ ...adminBook, stock_quantity: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="form-group flex gap-2">
                    <div className="flex-1">
                      <label className="form-label">ISBN</label>
                      <input 
                        type="text" 
                        className="form-input" 
                        required 
                        value={adminBook.isbn}
                        onChange={(e) => setAdminBook({ ...adminBook, isbn: e.target.value })}
                      />
                    </div>
                    <div className="flex-1">
                      <label className="form-label">Publication Year</label>
                      <input 
                        type="number" 
                        className="form-input" 
                        required 
                        value={adminBook.publication_year}
                        onChange={(e) => setAdminBook({ ...adminBook, publication_year: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Publisher Association</label>
                    <select 
                      className="search-select" 
                      style={{ width: '100%' }}
                      value={adminBook.publisher_id}
                      onChange={(e) => setAdminBook({ ...adminBook, publisher_id: e.target.value })}
                    >
                      {publishers.map(pub => (
                        <option key={pub.publisher_id} value={pub.publisher_id}>{pub.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label className="form-label">Catalog Description</label>
                    <textarea 
                      className="form-input" 
                      rows={3}
                      value={adminBook.description}
                      onChange={(e) => setAdminBook({ ...adminBook, description: e.target.value })}
                    />
                  </div>
                  <div className="flex gap-2">
                    <button type="submit" className="btn btn-primary flex-1">
                      <Check size={16} /> Save Book
                    </button>
                    {adminBook.book_id && (
                      <button 
                        type="button" 
                        className="btn btn-secondary" 
                        onClick={() => setAdminBook({
                          book_id: null,
                          title: '',
                          price: '',
                          stock_quantity: '',
                          isbn: '',
                          publication_year: new Date().getFullYear(),
                          publisher_id: publishers[0]?.publisher_id || '',
                          description: ''
                        })}
                      >
                        Cancel
                      </button>
                    )}
                  </div>
                </form>
              </div>
            </div>

            {/* Placed Orders List */}
            <div className="glass mt-4" style={{ padding: '1.5rem', borderRadius: '12px' }}>
              <h2>Transaction Audit Ledger (Customer Orders)</h2>
              <div className="table-wrapper mt-4">
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Order ID</th>
                      <th>Customer Name</th>
                      <th>Order Date</th>
                      <th>Shipping Address</th>
                      <th>Order Summary</th>
                      <th>Total Paid</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map(order => (
                      <tr key={order.order_id}>
                        <td>#{order.order_id}</td>
                        <td style={{ fontWeight: 600 }}>{order.customer_name}</td>
                        <td>{new Date(order.order_date).toLocaleString()}</td>
                        <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{order.shipping_address}</td>
                        <td>
                          <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                            {order.items?.map(it => (
                              <div key={it.book_id}>• {it.title} (Qty: {it.quantity})</div>
                            ))}
                          </div>
                        </td>
                        <td style={{ fontWeight: 700, color: 'var(--success)' }}>
                          ${order.total_amount.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                    {orders.length === 0 && (
                      <tr>
                        <td colSpan={6} className="text-center" style={{ color: 'var(--text-secondary)' }}>
                          No checkout transactions exist in DB history logs yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* --- VIEW: Showcase DB & SQL console --- */}
        {view === 'showcase' && (
          <div className="showcase-layout">
            <div>
              <div className="console-card glass">
                <h2>Interactive SQL Console</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                  Write custom SELECT queries to directly query the SQLite operational relational database:
                </p>
                <textarea 
                  className="sql-editor" 
                  value={playgroundQuery} 
                  onChange={(e) => setPlaygroundQuery(e.target.value)}
                />
                <button className="btn btn-primary" onClick={runPlaygroundQuery}>
                  <Play size={14} /> Execute Query
                </button>

                {playgroundError && (
                  <div className="query-result-wrapper">
                    <pre className="query-error">{playgroundError}</pre>
                  </div>
                )}

                {playgroundResult && (
                  <div className="query-result-wrapper">
                    <div className="query-success-info">
                      ✓ Execution successful: Query returned {playgroundResult.count} rows.
                    </div>
                    {playgroundResult.data && playgroundResult.data.length > 0 ? (
                      <table className="admin-table" style={{ fontSize: '0.8rem' }}>
                        <thead>
                          <tr>
                            {playgroundResult.columns.map(col => (
                              <th key={col} style={{ borderBottom: '2px solid var(--accent-primary)' }}>{col}</th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {playgroundResult.data.map((row, idx) => (
                            <tr key={idx}>
                              {playgroundResult.columns.map(col => (
                                <td key={col}>{row[col] !== null ? String(row[col]) : 'NULL'}</td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Empty set returned.</p>
                    )}
                  </div>
                )}
              </div>

              {/* Schema layout */}
              <div className="er-card glass mt-4">
                <h2>Relational Database Schema (ER Table Cards)</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  Inspect the physical constraints and SQLite column datatypes mapping active relational fields:
                </p>
                <div className="schema-grid">
                  {Object.entries(schema).map(([tableName, columns]) => (
                    <div key={tableName} className="table-card">
                      <div className="table-card-name">{tableName}</div>
                      {columns.map(col => (
                        <div key={col.name} className="column-item">
                          <span>
                            {col.pk === 1 && <span className="column-pk mr-2">🔑</span>}
                            {col.name}
                          </span>
                          <span style={{ color: 'var(--text-muted)' }}>{col.type}</span>
                        </div>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Explanation card for resume */}
            <div className="glass" style={{ padding: '1.5rem', borderRadius: '12px', height: 'fit-content' }}>
              <h2>Project Specifications</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', marginTop: '1rem' }}>
                This personal project models a complete online store management system. By using structured SQL design patterns, 
                the operational database enforces data integrity across e-commerce activities:
              </p>
              <ul style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.6', margin: '1rem 0 0 1.25rem' }}>
                <li style={{ marginBottom: '0.5rem' }}>
                  <strong style={{ color: 'var(--text-primary)' }}>Referential Integrity:</strong> Cascade deletions are set on mapping tables (`book_authors`, `book_categories`) and shopping carts. If an admin deletes a book, its mapping references clear automatically.
                </li>
                <li style={{ marginBottom: '0.5rem' }}>
                  <strong style={{ color: 'var(--text-primary)' }}>Relational Seeding:</strong> On the backend startup, Python reads `ebookstore_insert_command.txt` and inserts relational rows into primary key auto-increment indices.
                </li>
                <li style={{ marginBottom: '0.5rem' }}>
                  <strong style={{ color: 'var(--text-primary)' }}>Transactional Safety:</strong> The checkout operation utilizes **SQLite Transactions**. It reads quantities, deducts stocks, creates the invoice order ledger, and clears shopping carts as a atomic block. If any step fails (e.g. stock goes negative), the database automatically rolls back to prevent race conditions.
                </li>
              </ul>
              <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(59, 130, 246, 0.05)', borderRadius: '8px', borderLeft: '3px solid var(--accent-primary)' }}>
                <h4 style={{ color: 'var(--text-primary)' }}>Recruiter Verification Tip:</h4>
                <p style={{ fontSize: '0.8rem', marginTop: '0.25rem' }}>
                  Toggle the <strong>Live SQL Log Terminal</strong> at the bottom of the screen! Click around the site (e.g., perform a search, add a book, or register) and watch the raw SQL queries generate in real-time.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Live SQL Logs Terminal (Sticky Bottom Drawer) */}
      <div className="terminal-wrapper" style={{ position: 'sticky', bottom: 0, zIndex: 150 }}>
        <div className="terminal-header" onClick={() => setTerminalOpen(!terminalOpen)} style={{ cursor: 'pointer' }}>
          <div className="terminal-title">
            <span className="terminal-dot"></span>
            <Terminal size={14} color="#10b981" />
            <span>Live SQLite Query Log Terminal (Real-time Database Monitor)</span>
          </div>
          <div>
            {terminalOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
          </div>
        </div>
        
        {terminalOpen && (
          <div className="terminal-body">
            {sqlLogs.map((log, index) => (
              <div key={index} className="log-entry">
                <div className="log-meta">
                  <span>[{log.timestamp}]</span>
                  <span>Status: <span className={`log-status ${log.status.startsWith('ERROR') ? 'ERROR' : 'SUCCESS'}`}>{log.status}</span></span>
                  <span className="log-duration">Duration: {log.duration}ms</span>
                </div>
                <pre className="log-sql">{log.sql}</pre>
                {log.params && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Params: {log.params}</div>}
              </div>
            ))}
            {sqlLogs.length === 0 && (
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '2rem' }}>
                No database query operations logged yet. Click elements on the site to trigger backend transactions.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
