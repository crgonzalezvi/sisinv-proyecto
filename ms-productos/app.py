import os
import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

db_user = os.getenv('DB_USERNAME', 'root')
db_pass = os.getenv('DB_PASSWORD', '')
db_host = os.getenv('DB_HOST', '127.0.0.1')
db_port = os.getenv('DB_PORT', '3306')
db_name = os.getenv('DB_DATABASE', 'db_productos')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo Producto
class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sku = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    categoria = db.Column(db.String(100), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'sku': self.sku,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': float(self.precio),
            'categoria': self.categoria,
            'activo': self.activo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Crear tablas automáticamente al arrancar
with app.app_context():
    db.create_all()

# --- RUTAS ---

@app.route('/api/productos', methods=['GET'])
def listar_productos():
    productos = Producto.query.all()
    return jsonify([p.to_dict() for p in productos]), 200

@app.route('/api/productos', methods=['POST'])
def crear_producto():
    data = request.get_json()

    if not data or not data.get('sku') or not data.get('nombre') or data.get('precio') is None:
        return jsonify({'error': 'Los campos sku, nombre y precio son obligatorios'}), 400

    if Producto.query.filter_by(sku=data['sku']).first():
        return jsonify({'error': 'Ya existe un producto con ese SKU'}), 409

    nuevo = Producto(
        sku=data['sku'],
        nombre=data['nombre'],
        descripcion=data.get('descripcion', ''),
        precio=data['precio'],
        categoria=data.get('categoria', 'General')
    )

    db.session.add(nuevo)
    db.session.commit()

    return jsonify({
        'mensaje': 'Producto creado exitosamente',
        'producto': nuevo.to_dict()
    }), 201

@app.route('/api/productos/<string:producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    producto = Producto.query.get(producto_id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify(producto.to_dict()), 200

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8002, debug=True)