import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk  # For handling images
import sqlite3
import hashlib
import pygame
import csv
from database import init_db, add_admin_user, add_sample_users, authenticate_user, save_quiz_result, get_all_quiz_results

def init_db():
    """Initialize the database and create the users table if it doesn't exist."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_admin_user():
    """Add an admin user to the database if one doesn't already exist."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Check if admin user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", ('admin',))
    result = cursor.fetchone()
    if not result:
        # Hash the password
        password = 'admin123'  # Default password for admin
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('admin', hashed_password))
    conn.commit()
    conn.close()

def add_sample_users():
    """Add sample users to the database."""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    sample_users = [
        ('john_doe', 'password1'),
        ('jane_smith', 'password2'),
        ('alice_wonder', 'password3'),
    ]
    for username, password in sample_users:
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        except sqlite3.IntegrityError:
            pass  # User already exists
    conn.commit()
    conn.close()

def login():
    """Handle the login GUI and return login status and username."""

    def attempt_login():
        nonlocal login_successful, username
        username = username_entry.get()
        password = password_entry.get()
        if not username or not password:
            error_label.config(text="Please enter both username and password.")
            return
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
        result = cursor.fetchone()
        conn.close()
        if result:
            login_successful = True
            root.withdraw()  # Hide the login window on successful login
            if username == 'admin':
                open_admin_page(root, username)
            else:
                open_main_app(root, username)
        else:
            error_label.config(text="Invalid username or password.")

    def forgot_password():
        messagebox.showinfo("Forgot Password", "Please contact the administrator to reset your password.")

    def toggle_password_visibility():
        if password_entry.cget('show') == '':
            password_entry.config(show='*')
            eye_button.config(image=eye_closed_photo)
        else:
            password_entry.config(show='')
            eye_button.config(image=eye_open_photo)

    root = tk.Tk()
    root.title("Login System")
    root.geometry("400x500")
    root.resizable(False, False)

    # Set background color
    root.configure(bg='#f0f2f5')  # Light gray background

    # Define styles
    style = ttk.Style()
    style.configure('TLabel', font=('Helvetica', 12), background='#f0f2f5')
    style.configure('TEntry', font=('Helvetica', 12))
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.configure('Header.TLabel', font=('Helvetica', 20, 'bold'), background='#f0f2f5')
    style.configure('Error.TLabel', font=('Helvetica', 10), foreground='red', background='#f0f2f5')

    # Center frame
    login_frame = tk.Frame(root, bg='#ffffff', bd=0, relief='flat')
    login_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Heading
    heading_label = ttk.Label(login_frame, text="Welcome Back", style='Header.TLabel')
    heading_label.pack(pady=(20, 10))

    # Username Entry
    username_label = ttk.Label(login_frame, text="Username:")
    username_label.pack(pady=(10, 0), anchor='w', padx=20)
    username_entry = ttk.Entry(login_frame, width=30)
    username_entry.pack(pady=5, padx=20)

    # Password Entry
    password_label = ttk.Label(login_frame, text="Password:")
    password_label.pack(pady=(10, 0), anchor='w', padx=20)
    password_entry = ttk.Entry(login_frame, show="*", width=30)
    password_entry.pack(pady=5, padx=20)

    # Eye icon for password visibility
    try:
        eye_open_image = Image.open('eye_open.png')
        eye_closed_image = Image.open('eye_closed.png')
        eye_open_photo = ImageTk.PhotoImage(eye_open_image.resize((20, 20)))
        eye_closed_photo = ImageTk.PhotoImage(eye_closed_image.resize((20, 20)))
        eye_button = tk.Button(login_frame, image=eye_closed_photo, command=toggle_password_visibility, bg='white',
                               bd=0, activebackground='white', cursor='hand2')
        eye_button.image = eye_closed_photo  # Keep a reference
        eye_button.place(relx=0.85, rely=0.45)
    except FileNotFoundError:
        pass  # If icon images are not found, skip the eye icon

    # Remember Me checkbox
    remember_var = tk.IntVar()
    remember_check = ttk.Checkbutton(login_frame, text="Remember Me", variable=remember_var)
    remember_check.pack(pady=5, padx=20, anchor='w')

    # Error label
    error_label = ttk.Label(login_frame, text="", style='Error.TLabel')
    error_label.pack()

    # Login Button
    login_successful = False
    username = None
    login_button = ttk.Button(login_frame, text="Login", command=attempt_login)
    login_button.pack(pady=20, padx=20, fill='x')

    # Forgot Password link
    forgot_password_link = tk.Label(login_frame, text="Forgot Password?", font=('Helvetica', 10, 'underline'),
                                    fg='blue', bg='white', cursor="hand2")
    forgot_password_link.pack()
    forgot_password_link.bind("<Button-1>", lambda e: forgot_password())

    # Set focus to username entry
    username_entry.focus()

    root.mainloop()

def open_admin_page(root, username):
    """Open the admin page window."""
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Page")
    admin_window.geometry("400x500")
    admin_window.resizable(False, False)

    # Set background color
    admin_window.configure(bg='#f0f2f5')

    # Define styles
    style = ttk.Style()
    style.configure('TLabel', font=('Helvetica', 12), background='#f0f2f5')
    style.configure('TButton', font=('Helvetica', 12), padding=10)
    style.configure('Header.TLabel', font=('Helvetica', 20, 'bold'), background='#f0f2f5')

    # Center frame
    main_frame = tk.Frame(admin_window, bg='#ffffff', bd=0, relief='flat')
    main_frame.place(relx=0.5, rely=0.5, anchor='center')

    # Heading
    heading_label = ttk.Label(main_frame, text="Admin Dashboard", style='Header.TLabel')
    heading_label.pack(pady=(20, 20))

    # Buttons
    button_width = 30
    view_users_button = ttk.Button(main_frame, text="View Users", command=view_users, width=button_width)
    view_users_button.pack(pady=10)

    add_user_button = ttk.Button(main_frame, text="Add User", command=add_user, width=button_width)
    add_user_button.pack(pady=10)

    view_results_button = ttk.Button(main_frame, text="View Quiz Results", command=view_quiz_results, width=button_width)
    view_results_button.pack(pady=10)

    main_app_button = ttk.Button(
        main_frame,
        text="Go to Main App",
        command=lambda: open_main_app(admin_window, username),
        width=button_width
    )
    main_app_button.pack(pady=10)

def view_users():
    """Display a list of users with the ability to remove a user."""
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users")
    users = cursor.fetchall()
    conn.close()

    # Create a new window to display users
    users_window = tk.Toplevel()
    users_window.title("Registered Users")
    users_window.geometry("400x400")
    users_window.configure(bg='#f0f2f5')

    main_frame = tk.Frame(users_window, bg='#ffffff')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    heading_label = ttk.Label(main_frame, text="Registered Users", style='Header.TLabel')
    heading_label.pack(pady=10)

    # Create Treeview to display users
    columns = ('Username',)
    tree = ttk.Treeview(main_frame, columns=columns, show='headings')
    tree.heading('Username', text='Username')
    tree.column('Username', anchor='center', width=200)
    tree.pack(fill=tk.BOTH, expand=True)

    # Populate the treeview with user data
    for user in users:
        tree.insert('', tk.END, values=user)

    # Function to remove a user
    def remove_user():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a user to remove.")
            return
        username = tree.item(selected_item)['values'][0]
        if username == 'admin':
            messagebox.showerror("Error", "Cannot remove the admin user.")
            return
        confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove the user '{username}'?")
        if confirm:
            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            conn.commit()
            conn.close()
            # Remove the user from the treeview
            tree.delete(selected_item)
            messagebox.showinfo("Success", f"User '{username}' has been removed.")

    # Function to handle right-click event
    def on_right_click(event):
        # Select the item under the cursor
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            context_menu.post(event.x_root, event.y_root)

    # Create a context menu
    context_menu = tk.Menu(users_window, tearoff=0)
    context_menu.add_command(label="Remove User", command=remove_user)

    # Bind right-click event to the treeview
    tree.bind("<Button-3>", on_right_click)

def view_quiz_results():
    """Display quiz results with filtering and sorting options."""
    # Retrieve quiz results from the database
    conn = sqlite3.connect('quiz_results.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, score, timestamp FROM quiz_results")
    results = cursor.fetchall()
    conn.close()

    # Create a new window to display quiz results
    results_window = tk.Toplevel()
    results_window.title("Quiz Results")
    results_window.geometry("700x600")
    results_window.configure(bg='#f0f2f5')

    # Main frame
    main_frame = tk.Frame(results_window, bg='#ffffff')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    heading_label = ttk.Label(main_frame, text="Quiz Results", style='Header.TLabel')
    heading_label.pack(pady=10)

    # Filter Frame
    filter_frame = tk.Frame(main_frame, bg='#ffffff')
    filter_frame.pack(pady=5)

    filter_label = ttk.Label(filter_frame, text="Filter by Username:")
    filter_label.pack(side='left', padx=5)

    filter_entry = ttk.Entry(filter_frame, width=20)
    filter_entry.pack(side='left', padx=5)

    # Sort Options
    sort_label = ttk.Label(filter_frame, text="Sort by:")
    sort_label.pack(side='left', padx=5)

    sort_var = tk.StringVar(value="Date Descending")
    sort_options = ["Date Descending", "Date Ascending", "Score Descending", "Score Ascending"]
    sort_menu = ttk.Combobox(filter_frame, textvariable=sort_var, values=sort_options, state='readonly', width=18)
    sort_menu.pack(side='left', padx=5)

    # Apply Filter and Sort Button
    apply_button = ttk.Button(filter_frame, text="Apply", command=lambda: apply_filter_and_sort())
    apply_button.pack(side='left', padx=5)

    # Create Treeview to display results
    columns = ('Username', 'Score', 'Timestamp')
    tree = ttk.Treeview(main_frame, columns=columns, show='headings')
    tree.heading('Username', text='Username')
    tree.heading('Score', text='Score')
    tree.heading('Timestamp', text='Date Taken')
    tree.column('Username', anchor='center', width=200)
    tree.column('Score', anchor='center', width=100)
    tree.column('Timestamp', anchor='center', width=200)
    tree.pack(fill=tk.BOTH, expand=True)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

    # Function to populate the treeview with data
    def populate_treeview(data):
        # Clear existing data
        for row in tree.get_children():
            tree.delete(row)
        # Insert new data
        for result in data:
            tree.insert('', 'end', values=result)

    # Initially populate the treeview with all results
    populate_treeview(results)

    # Function to apply filter and sorting
    def apply_filter_and_sort():
        username_filter = filter_entry.get()
        sort_option = sort_var.get()

        query = "SELECT username, score, timestamp FROM quiz_results"
        params = []

        if username_filter:
            query += " WHERE username LIKE ?"
            params.append(f"%{username_filter}%")

        # Determine sorting
        if "Date" in sort_option:
            query += " ORDER BY timestamp"
            if "Descending" in sort_option:
                query += " DESC"
        elif "Score" in sort_option:
            query += " ORDER BY score"
            if "Descending" in sort_option:
                query += " DESC"

        conn = sqlite3.connect('quiz_results.db')
        cursor = conn.cursor()
        cursor.execute(query, params)
        filtered_results = cursor.fetchall()
        conn.close()

        populate_treeview(filtered_results)

    # Refresh Button to reset filters and sorting
    def refresh_results():
        filter_entry.delete(0, 'end')
        sort_var.set("Date Descending")
        populate_treeview(results)

    refresh_button = ttk.Button(main_frame, text="Refresh", command=refresh_results)
    refresh_button.pack(pady=5)

    # Export to CSV Button
    def export_to_csv():
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[("CSV files", '*.csv')])
        if file_path:
            # Get current data in treeview
            tree_data = [tree.item(item)['values'] for item in tree.get_children()]
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Username", "Score", "Date Taken"])
                writer.writerows(tree_data)
            messagebox.showinfo("Export Successful", f"Quiz results have been exported to {file_path}")

    export_button = ttk.Button(main_frame, text="Export to CSV", command=export_to_csv)
    export_button.pack(pady=5)

    # Close Button
    close_button = ttk.Button(main_frame, text="Close", command=results_window.destroy)
    close_button.pack(pady=10)

def add_user():
    """Open a window to add a new user."""
    def save_user():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()
        if not new_username or not new_password:
            messagebox.showerror("Error", "Username and password cannot be empty")
            return
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hashed_password))
            conn.commit()
            messagebox.showinfo("Success", f"User '{new_username}' added successfully")
            add_user_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"User '{new_username}' already exists")
        conn.close()

    add_user_window = tk.Toplevel()
    add_user_window.title("Add New User")
    add_user_window.geometry("400x300")
    add_user_window.configure(bg='#f0f2f5')

    main_frame = tk.Frame(add_user_window, bg='#ffffff')
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

    # Heading
    heading_label = ttk.Label(main_frame, text="Add New User", style='Header.TLabel')
    heading_label.pack(pady=10)

    # Username
    new_username_label = ttk.Label(main_frame, text="Username:")
    new_username_label.pack(pady=(10, 0), anchor='w')
    new_username_entry = ttk.Entry(main_frame, width=30)
    new_username_entry.pack(pady=5)

    # Password
    new_password_label = ttk.Label(main_frame, text="Password:")
    new_password_label.pack(pady=(10, 0), anchor='w')
    new_password_entry = ttk.Entry(main_frame, show="*", width=30)
    new_password_entry.pack(pady=5)

    # Save Button
    save_button = ttk.Button(main_frame, text="Save", command=save_user)
    save_button.pack(pady=20, fill='x')

def open_main_app(window, username):
    """Function to open the main application."""
    from menu import menu  # Assuming 'menu.py' is in the same directory

    # Initialize Pygame and open the menu from menu.py
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Main Application - Ideal Gas Simulation')

    window.destroy()
    params = menu(screen, username)  # Call the menu to get parameters

    # Check if the user clicked 'Start' and parameters were returned
    if params:
        num_particles, box_size, particle_radius, temperature, dt, total_steps = params
        # Initialize and run your simulation with these parameters
        from simulation import Simulation  # Import your simulation class
        simulation = Simulation(num_particles, box_size, particle_radius, temperature, dt, total_steps)
        simulation.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    init_db()
    add_admin_user()
    add_sample_users()
    login()
