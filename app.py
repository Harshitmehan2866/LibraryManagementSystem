from flask import Flask, request, render_template, redirect, url_for, flash
import pyodbc
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Required for flash messages

# -------------------- Azure SQL Connection --------------------
server = 'ibrary-sql-server.database.windows.net'
database = 'librarydb'
username = 'harshitmehan'
password = 'harshit@9420'
driver = '{ODBC Driver 18 for SQL Server}'

def get_connection():
    return pyodbc.connect(
        f"DRIVER={driver};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )

# -------------------- Routes --------------------

# Home Page: Display all books and issued books
@app.route('/')
def home():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Fetch all books
    cursor.execute("SELECT * FROM Books")
    books = cursor.fetchall()

    # Fetch all issued books with book titles
    cursor.execute("""
        SELECT i.issue_id, b.title, i.borrower_name, i.issue_date
        FROM Issues i
        JOIN Books b ON i.book_id = b.book_id
    """)
    issued_books = cursor.fetchall()

    conn.close()
    return render_template("index.html", books=books, issued_books=issued_books)

# -------------------- Book Management --------------------

# Add a new book
@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    quantity = request.form['quantity']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Books (title, author, quantity) VALUES (?, ?, ?)",
        (title, author, quantity)
    )
    conn.commit()
    conn.close()
    
    flash(f"Book '{title}' added successfully!", "success")
    return redirect('/')

# Delete a book
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT title FROM Books WHERE book_id = ?", (book_id,))
    book_title = cursor.fetchone()[0]

    cursor.execute("DELETE FROM Books WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()

    flash(f"Book '{book_title}' deleted successfully!", "success")
    return redirect(url_for('home'))

# Show edit form for a book
@app.route('/edit/<int:book_id>', methods=['GET'])
def edit_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    return render_template("edit_book.html", book=book)

# Update book details
@app.route('/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    title = request.form['title']
    author = request.form['author']
    quantity = request.form['quantity']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Books SET title = ?, author = ?, quantity = ? WHERE book_id = ?",
        (title, author, quantity, book_id)
    )
    conn.commit()
    conn.close()

    flash(f"Book '{title}' updated successfully!", "success")
    return redirect('/')

# -------------------- Issue Book --------------------

@app.route('/issue', methods=['POST'])
def issue_book():
    book_id = request.form['book_id']
    borrower_name = request.form['borrower_name']

    conn = get_connection()
    cursor = conn.cursor()

    # Check if book is available
    cursor.execute("SELECT title, quantity FROM Books WHERE book_id = ?", (book_id,))
    book = cursor.fetchone()
    available = book[1]
    book_title = book[0]

    if available > 0:
        # Insert into Issues table
        cursor.execute(
            "INSERT INTO Issues (book_id, borrower_name, issue_date) VALUES (?, ?, ?)",
            (book_id, borrower_name, datetime.now())
        )
        # Reduce book quantity
        cursor.execute("UPDATE Books SET quantity = quantity - 1 WHERE book_id = ?", (book_id,))
        conn.commit()
        flash(f"Book '{book_title}' issued to {borrower_name}!", "success")
    else:
        flash(f"Book '{book_title}' is not available to issue.", "error")

    conn.close()
    return redirect('/')

# -------------------- Return Book --------------------

@app.route('/return/<int:issue_id>', methods=['POST'])
def return_book(issue_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get the book_id and title from the Issues table
    cursor.execute("""
        SELECT i.book_id, b.title 
        FROM Issues i 
        JOIN Books b ON i.book_id = b.book_id 
        WHERE i.issue_id = ?
    """, (issue_id,))
    book = cursor.fetchone()
    book_id = book[0]
    book_title = book[1]

    # Delete the issue record
    cursor.execute("DELETE FROM Issues WHERE issue_id = ?", (issue_id,))
    
    # Increment the book quantity
    cursor.execute("UPDATE Books SET quantity = quantity + 1 WHERE book_id = ?", (book_id,))
    
    conn.commit()
    conn.close()

    flash(f"Book '{book_title}' returned successfully!", "success")
    return redirect('/')

# -------------------- Run App --------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5500, debug=True)
