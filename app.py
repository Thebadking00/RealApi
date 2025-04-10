from flask import Flask, jsonify, request, send_from_directory
from flask_mysqldb import MySQL
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import config

app = Flask(__name__)
CORS(app)

# Configuración de conexión a MySQL
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DATABASE
mysql = MySQL(app)

# Rutas existentes de tu API
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()
    resultado = [{'id': u[0], 'name': u[1], 'email': u[2], 'password': u[3]} for u in usuarios]
    return jsonify(resultado)

@app.route('/usuarios/<int:id>', methods=['GET'])
def get_user(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cur.fetchone()
    cur.close()
    if usuario:
        return jsonify({'id': usuario[0], 'name': usuario[1], 'email': usuario[2], 'password': usuario[3]})
    else:
        return jsonify({'message': 'User not found'}), 404

@app.route('/usuarios', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO usuarios (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/usuarios/<int:id>', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    cur = mysql.connection.cursor()
    cur.execute("UPDATE usuarios SET name = %s, email = %s, password = %s WHERE id = %s", (name, email, password, id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'User updated successfully'})

@app.route('/usuarios/<int:id>', methods=['DELETE'])
def delete_user(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': 'User deleted successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios WHERE email = %s AND password = %s", (email, password))
    user = cur.fetchone()
    cur.close()
    if user:
        return jsonify({'message': 'Login successful', 'user': {'id': user[0], 'name': user[1]}})
    else:
        return jsonify({'message': 'Invalid email or password'}), 401

# Configuración de Swagger
SWAGGER_URL = '/docs'  # URL donde estará disponible la documentación
API_URL = '/swagger.yaml'  # Ruta al archivo YAML

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # URL de Swagger UI
    API_URL,      # Ruta de la documentación YAML
    config={      # Configuraciones opcionales
        'app_name': "CRUD API de Usuarios"
    }
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Ruta para servir el archivo YAML
@app.route('/swagger.yaml')
def swagger_file():
    return send_from_directory('.', 'swagger.yaml')  # El archivo debe estar en el directorio raíz

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)