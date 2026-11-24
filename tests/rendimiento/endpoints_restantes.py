"""Escenarios por etiqueta. Las solicitudes de preparación quedan fuera de las métricas."""
import os
from uuid import uuid4

import requests
from locust import HttpUser, between, tag, task

PRODUCTOS = "/api/productos"
PROVEEDORES = "/api/proveedores"
ORDENES = "/api/ordenes"


def proveedor_nuevo():
    return {"identificacion_tributaria": uuid4().hex, "razon_social": "Proveedor de prueba"}


class Operaciones(HttpUser):
    wait_time = between(0.5, 1.5)

    def on_start(self):
        self.setup = requests.Session()
        token = os.environ["TEST_TOKEN"]
        self.client.headers["Authorization"] = f"Bearer {token}"
        self.setup.headers["Authorization"] = f"Bearer {token}"
        self.proveedor = None
        self.orden = None

    def on_stop(self):
        self.setup.close()

    def preparar(self, ruta, datos):
        respuesta = self.setup.post(self.host.rstrip("/") + ruta, json=datos, timeout=15)
        respuesta.raise_for_status()
        return respuesta.json()["id"]

    def proveedor_activo(self):
        if self.proveedor is None:
            self.proveedor = self.preparar(PROVEEDORES, proveedor_nuevo())
        return self.proveedor

    def datos_orden(self):
        return {"proveedor_id": self.proveedor_activo(), "detalles": [{
            "producto_id": os.environ["TEST_PRODUCTO_ID"], "cantidad_solicitada": 1, "precio_unitario": 10
        }]}

    @tag("registro")
    @task
    def registro(self):
        self.client.post("/api/usuarios/registro", json={
            "nombre_completo": "Prueba", "email": f"{uuid4().hex}@example.org", "password": uuid4().hex
        })

    @tag("producto_crear")
    @task
    def producto_crear(self):
        self.client.post(PRODUCTOS, json={"sku": uuid4().hex, "nombre": "Prueba", "precio": 10})

    @tag("producto_consultar")
    @task
    def producto_consultar(self):
        self.client.get(f"{PRODUCTOS}/{os.environ['TEST_PRODUCTO_ID']}", name="GET /productos/{id}")

    @tag("bodega_crear")
    @task
    def bodega_crear(self):
        self.client.post("/api/inventario/bodegas", json={"nombre": uuid4().hex})

    @tag("proveedores_listar")
    @task
    def proveedores_listar(self):
        self.client.get(PROVEEDORES)

    @tag("proveedor_crear")
    @task
    def proveedor_crear(self):
        self.client.post(PROVEEDORES, json=proveedor_nuevo())

    @tag("proveedor_consultar")
    @task
    def proveedor_consultar(self):
        self.client.get(f"{PROVEEDORES}/{self.proveedor_activo()}", name="GET /proveedores/{id}")

    @tag("proveedor_editar")
    @task
    def proveedor_editar(self):
        self.client.patch(f"{PROVEEDORES}/{self.proveedor_activo()}", json={"contacto": "Prueba"},
                          name="PATCH /proveedores/{id}")

    @tag("proveedor_baja")
    @task
    def proveedor_baja(self):
        identificador = self.preparar(PROVEEDORES, proveedor_nuevo())
        self.client.delete(f"{PROVEEDORES}/{identificador}", name="DELETE /proveedores/{id}")

    @tag("orden_crear")
    @task
    def orden_crear(self):
        self.client.post(ORDENES, json=self.datos_orden())

    @tag("orden_consultar")
    @task
    def orden_consultar(self):
        if self.orden is None:
            self.orden = self.preparar(ORDENES, self.datos_orden())
        self.client.get(f"{ORDENES}/{self.orden}", name="GET /ordenes/{id}")

    @tag("orden_recibir")
    @task
    def orden_recibir(self):
        orden = self.preparar(ORDENES, self.datos_orden())
        self.client.post(f"{ORDENES}/{orden}/recepciones", json={"bodega_id": int(os.environ["TEST_BODEGA_ID"])},
                         name="POST /ordenes/{id}/recepciones")
