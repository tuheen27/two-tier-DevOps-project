from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

# Database configuration
DB_PATH = 'database.db'

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_table():
    """Create users table if it doesn't exist"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    phone TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()
            print("Table created successfully")
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            connection.close()

@app.route('/')
def index():
    """Render the index.html page"""
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit_data():
    """Receive data from frontend and store in database"""
    try:
        data = request.get_json() if request.is_json else request.form
        
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        
        if not name or not email:
            return jsonify({'success': False, 'message': 'Name and email are required'}), 400
        
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            query = "INSERT INTO users (name, email, phone) VALUES (?, ?, ?)"
            cursor.execute(query, (name, email, phone))
            connection.commit()
            
            return jsonify({
                'success': True,
                'message': 'Data saved successfully',
                'id': cursor.lastrowid
            }), 201
        else:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
            
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email already exists'}), 409
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/users', methods=['GET'])
def get_users():
    """Retrieve all users from database"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
            users = [dict(row) for row in cursor.fetchall()]
            return jsonify({'success': True, 'data': users}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    create_table()
    app.run(debug=True, host='0.0.0.0', port=5000)