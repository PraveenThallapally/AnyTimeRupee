from flask import Flask, render_template, request, jsonify
from config import Config
from database import get_db_connection, init_database
 
app = Flask(__name__)
app.config.from_object(Config)
 
# Initialize database on startup
with app.app_context():
    init_database()
 
# ==================== ROUTES ====================
 
@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')
 
@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "Application is running"}), 200
 
# ==================== CREATE ====================
@app.route('/api/persons', methods=['POST'])
def create_person():
    """Create a new person"""
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        with connection.cursor(dictionary=True) as cursor:
            query = """
            INSERT INTO persons (name, email, phone, address, age)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                data['name'],
                data['email'],
                data.get('phone', ''),
                data.get('address', ''),
                data.get('age', None)
            ))
            connection.commit()
            person_id = cursor.lastrowid
        
        connection.close()
        return jsonify({
            "message": "Person created successfully",
            "id": person_id
        }), 201
        
    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": str(e)}), 500
 
# ==================== READ ====================
@app.route('/api/persons', methods=['GET'])
def get_all_persons():
    """Get all persons"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM persons ORDER BY created_at DESC")
            persons = cursor.fetchall()
        
        connection.close()
        return jsonify(persons), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
@app.route('/api/persons/<int:person_id>', methods=['GET'])
def get_person(person_id):
    """Get a single person by ID"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM persons WHERE id = %s", (person_id,))
            person = cursor.fetchone()
        
        connection.close()
        
        if person:
            return jsonify(person), 200
        else:
            return jsonify({"error": "Person not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# ==================== UPDATE ====================
@app.route('/api/persons/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    """Update a person"""
    try:
        data = request.get_json()
        
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        with connection.cursor(dictionary=True) as cursor:
            # Check if person exists
            cursor.execute("SELECT id FROM persons WHERE id = %s", (person_id,))
            if not cursor.fetchone():
                connection.close()
                return jsonify({"error": "Person not found"}), 404
            
            # Update person
            query = """
            UPDATE persons
            SET name = %s, email = %s, phone = %s, address = %s, age = %s
            WHERE id = %s
            """
            cursor.execute(query, (
                data.get('name'),
                data.get('email'),
                data.get('phone', ''),
                data.get('address', ''),
                data.get('age', None),
                person_id
            ))
            connection.commit()
        
        connection.close()
        return jsonify({"message": "Person updated successfully"}), 200
        
    except Exception as e:
        if 'Duplicate entry' in str(e):
            return jsonify({"error": "Email already exists"}), 409
        return jsonify({"error": str(e)}), 500
 
# ==================== DELETE ====================
@app.route('/api/persons/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a person"""
    try:
        connection = get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        with connection.cursor(dictionary=True) as cursor:
            # Check if person exists
            cursor.execute("SELECT id FROM persons WHERE id = %s", (person_id,))
            if not cursor.fetchone():
                connection.close()
                return jsonify({"error": "Person not found"}), 404
            
            # Delete person
            cursor.execute("DELETE FROM persons WHERE id = %s", (person_id,))
            connection.commit()
        
        connection.close()
        return jsonify({"message": "Person deleted successfully"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
 
# ==================== RUN APPLICATION ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
