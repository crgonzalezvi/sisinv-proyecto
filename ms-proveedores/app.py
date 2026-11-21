import os
import re
from uuid import uuid4

import jwt
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///proveedores.sqlite")
db = SQLAlchemy(app)
RUTA = "/api/proveedores"
CAMPOS = ("identificacion_tributaria", "razon_social", "contacto", "correo", "telefono", "direccion")


class Proveedor(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    identificacion_tributaria = db.Column(db.String, nullable=False, unique=True)
    razon_social = db.Column(db.String, nullable=False)
    contacto = db.Column(db.String)
    correo = db.Column(db.String)
    telefono = db.Column(db.String)
    direccion = db.Column(db.String)
    activo = db.Column(db.Boolean, nullable=False, default=True)

    def json(self):
        return {campo: getattr(self, campo) for campo in ("id", *CAMPOS, "activo")}


with app.app_context():
    db.create_all()


def error(codigo, mensaje, estado):
    return {"codigo": codigo, "mensaje": mensaje}, estado


@app.before_request
def verificar_acceso():
    clave = os.getenv("JWT_SECRET")
    if not clave:
        return error("CONFIGURACION", "Falta configurar JWT_SECRET.", 503)
    auth = request.authorization
    if not auth or auth.type.lower() != "bearer" or not auth.token:
        return error("NO_AUTENTICADO", "Se requiere un token.", 401)
    try:
        datos = jwt.decode(auth.token, clave, algorithms=["HS256"], options={"require": ["exp", "sub"]})
    except jwt.InvalidTokenError:
        return error("NO_AUTENTICADO", "Token inválido o vencido.", 401)
    if request.method in {"POST", "PATCH", "DELETE"} and str(datos.get("rol_id")) != "1":
        return error("SIN_PERMISO", "Se requiere el rol de administrador.", 403)


@app.errorhandler(404)
def no_encontrado(_):
    return error("RECURSO_NO_ENCONTRADO", "Recurso no encontrado.", 404)


@app.get(RUTA)
def listar():
    buscar = request.args.get("buscar", "").strip()
    consulta = db.select(Proveedor).where(Proveedor.activo.is_(True))
    if buscar:
        consulta = consulta.where(
            Proveedor.razon_social.contains(buscar, autoescape=True)
            | Proveedor.identificacion_tributaria.contains(buscar, autoescape=True)
        )
    return [p.json() for p in db.session.scalars(consulta.order_by(Proveedor.razon_social))]


@app.get(RUTA + "/<identificador>")
def consultar(identificador):
    return db.get_or_404(Proveedor, identificador).json()


@app.post(RUTA)
@app.patch(RUTA + "/<identificador>")
def guardar(identificador=None):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or not datos or datos.keys() - set(CAMPOS):
        return error("DATOS_INVALIDOS", "Revisa los campos del proveedor.", 400)
    for campo, valor in datos.items():
        if not isinstance(valor, str) or not valor.strip():
            return error("DATOS_INVALIDOS", f"Revisa el campo {campo}.", 400)
        datos[campo] = valor.strip()
    if "correo" in datos and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", datos["correo"]):
        return error("DATOS_INVALIDOS", "Correo inválido.", 400)
    if identificador is None:
        if not {"razon_social", "identificacion_tributaria"} <= datos.keys():
            return error("DATOS_INVALIDOS", "Faltan la razón social o la identificación tributaria.", 400)
        proveedor = Proveedor(**datos)
        db.session.add(proveedor)
    else:
        proveedor = db.get_or_404(Proveedor, identificador)
        for campo, valor in datos.items():
            setattr(proveedor, campo, valor)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("DUPLICADO", "La identificación tributaria ya existe.", 409)
    return proveedor.json(), 201 if identificador is None else 200


@app.delete(RUTA + "/<identificador>")
def dar_de_baja(identificador):
    proveedor = db.get_or_404(Proveedor, identificador)
    proveedor.activo = False
    db.session.commit()
    return "", 204


if __name__ == "__main__":
    app.run(port=8004)
