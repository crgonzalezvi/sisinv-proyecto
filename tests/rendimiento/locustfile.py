import os
import requests
from locust import HttpUser, task, between, tag, events

EMAIL = os.getenv("TEST_EMAIL", "crgonzalezvi@unal.edu.co")
PASSWORD = os.getenv("TEST_PASSWORD", "password123")
PRODUCTO_ID = os.getenv("TEST_PRODUCTO_ID", "a5ee7415-57bf-4c6a-bcdb-ec6d2b848826")
BODEGA_ID = os.getenv("TEST_BODEGA_ID", "1")
LOGIN_PATH = os.getenv("TEST_LOGIN_PATH", "/api/usuarios/login")

SHARED_HEADERS = {}


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    global SHARED_HEADERS
    url = f"{environment.host}{LOGIN_PATH}"
    try:
        res = requests.post(url, json={"email": EMAIL, "password": PASSWORD}, timeout=10)
        if res.status_code == 200:
            data = res.json()
            token = data.get("access_token") or data.get("token")
            if token:
                SHARED_HEADERS = {"Authorization": f"Bearer {token}"}
                print("Token JWT obtenido correctamente para la prueba.")
    except Exception as e:
        print(f"No se pudo obtener el token inicial: {e}")


class SisInvUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @tag("login")
    @task
    def test_login(self):
        self.client.post(
            LOGIN_PATH,
            json={"email": EMAIL, "password": PASSWORD},
            name="POST /login",
        )

    @tag("productos")
    @task
    def test_listar_productos(self):
        self.client.get("/api/productos", headers=SHARED_HEADERS, name="GET /productos")

    @tag("stock")
    @task
    def test_consultar_stock(self):
        self.client.get(
            f"/api/inventario/bodegas/{BODEGA_ID}/productos/{PRODUCTO_ID}/stock",
            headers=SHARED_HEADERS,
            name="GET /inventario/stock",
        )

    @tag("kardex")
    @task
    def test_consultar_kardex(self):
        self.client.get(
            f"/api/inventario/bodegas/{BODEGA_ID}/productos/{PRODUCTO_ID}/kardex",
            headers=SHARED_HEADERS,
            name="GET /inventario/kardex",
        )

    @tag("entradas")
    @task
    def test_registrar_entrada(self):
        self.client.post(
            "/api/inventario/entradas",
            json={
                "bodega_id": int(BODEGA_ID),
                "producto_id": PRODUCTO_ID,
                "cantidad": 1,
            },
            headers=SHARED_HEADERS,
            name="POST /inventario/entradas",
        )