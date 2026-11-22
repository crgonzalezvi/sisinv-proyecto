import express from 'express';
import jwt from 'jsonwebtoken';
import { randomUUID } from 'node:crypto';
import { DatabaseSync } from 'node:sqlite';

const app = express();
const db = new DatabaseSync(process.env.DB_PATH || 'ordenes.sqlite');
const productos = process.env.MS_PRODUCTOS_URL || 'http://127.0.0.1:8002';
const inventario = process.env.MS_INVENTARIO_URL || 'http://127.0.0.1:8003';
const proveedores = process.env.MS_PROVEEDORES_URL || 'http://127.0.0.1:8004';
const ruta = '/api/ordenes';
const uuid = /^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/i;

db.exec(`CREATE TABLE IF NOT EXISTS ordenes (
    id TEXT PRIMARY KEY, proveedor_id TEXT NOT NULL, usuario_id TEXT NOT NULL,
    detalles TEXT NOT NULL, estado TEXT NOT NULL DEFAULT 'PENDIENTE', bodega_id INTEGER
)`);
app.use(express.json());

app.use(ruta, (req, res, next) => {
    if (!process.env.JWT_SECRET) return res.status(503).json({ error: 'Falta configurar JWT_SECRET.' });
    try {
        const token = req.get('authorization')?.match(/^Bearer (.+)$/i)?.[1];
        req.usuario = jwt.verify(token, process.env.JWT_SECRET, { algorithms: ['HS256'] });
        if (!req.usuario.sub || !req.usuario.exp) throw new Error();
    } catch {
        return res.status(401).json({ error: 'Token inválido o vencido.' });
    }
    next();
});

function leerOrden(id) {
    const orden = db.prepare('SELECT * FROM ordenes WHERE id = ?').get(id);
    if (!orden) throw Object.assign(new Error('Orden no encontrada.'), { status: 404 });
    orden.detalles = JSON.parse(orden.detalles);
    return orden;
}

async function solicitar(url, req, cuerpo) {
    if (cuerpo && !process.env.ORDENES_INTERNAL_KEY) {
        throw Object.assign(new Error('Falta configurar la clave interna de Inventario.'), { status: 503 });
    }
    const respuesta = await fetch(url, {
        method: cuerpo ? 'POST' : 'GET',
        headers: { ...(cuerpo && { 'X-Ordenes-Key': process.env.ORDENES_INTERNAL_KEY }), Authorization: req.get('authorization'), Accept: 'application/json', 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000),
        body: cuerpo && JSON.stringify(cuerpo),
    });
    if (!respuesta.ok) {
        const status = respuesta.status === 404 ? 422 : respuesta.status;
        throw Object.assign(new Error('El servicio rechazó la operación: ' + new URL(url).pathname), { status });
    }
    return respuesta.json();
}

app.post(ruta, async (req, res) => {
    if (String(req.usuario.rol_id) !== '1') return res.status(403).json({ error: 'Se requiere administrador.' });
    const { proveedor_id, detalles } = req.body || {};
    if (!uuid.test(proveedor_id) || !Array.isArray(detalles) || !detalles.length) {
        return res.status(400).json({ error: 'Indica el proveedor y al menos un producto.' });
    }
    const ids = new Set();
    const lineas = [];
    for (const detalle of detalles) {
        const { producto_id, cantidad_solicitada, precio_unitario } = detalle || {};
        if (!uuid.test(producto_id) || ids.has(producto_id.toLowerCase()) ||
            !Number.isInteger(cantidad_solicitada) || cantidad_solicitada < 1 || cantidad_solicitada > 2147483647 ||
            !Number.isFinite(precio_unitario) || precio_unitario < 0) {
            return res.status(400).json({ error: 'Revisa el producto, la cantidad y el precio de cada línea.' });
        }
        ids.add(producto_id.toLowerCase());
        lineas.push({ producto_id: producto_id.toLowerCase(), cantidad_solicitada, precio_unitario });
    }
    const proveedor = await solicitar(proveedores + '/api/proveedores/' + proveedor_id, req);
    if (!proveedor.activo) return res.status(422).json({ error: 'Proveedor inactivo.' });
    for (const id of ids) await solicitar(productos + '/api/productos/' + id, req);

    const id = randomUUID();
    db.prepare('INSERT INTO ordenes (id, proveedor_id, usuario_id, detalles) VALUES (?, ?, ?, ?)')
        .run(id, proveedor_id, String(req.usuario.sub), JSON.stringify(lineas));
    res.status(201).json(leerOrden(id));
});

app.get(ruta + '/:id', (req, res) => res.json(leerOrden(req.params.id)));

app.post(ruta + '/:id/recepciones', async (req, res) => {
    const orden = leerOrden(req.params.id);
    const bodega = req.body?.bodega_id;
    if (!Number.isSafeInteger(bodega) || bodega < 1) return res.status(400).json({ error: 'Bodega inválida.' });
    if (orden.estado === 'RECIBIDA') {
        if (orden.bodega_id !== bodega) return res.status(409).json({ error: 'Orden recibida en otra bodega.' });
        return res.json(orden);
    }
    await solicitar(inventario + '/api/inventario/recepciones', req, {
        orden_id: orden.id, bodega_id: bodega,
        detalles: orden.detalles.map(d => ({ producto_id: d.producto_id, cantidad: d.cantidad_solicitada })),
    });
    db.prepare("UPDATE ordenes SET estado = 'RECIBIDA', bodega_id = ? WHERE id = ?").run(bodega, orden.id);
    res.json(leerOrden(orden.id));
});

app.use((error, req, res, next) => {
    const status = error.status || (['TypeError', 'TimeoutError'].includes(error.name) ? 503 : 500);
    res.status(status).json({ error: status >= 500 ? 'No se pudo completar la operación.' : error.message });
});

app.listen(process.env.PORT || 8005, process.env.HOST || '0.0.0.0', () => {
    console.log(`ms-ordenes escuchando en puerto ${process.env.PORT || 8005}`);
});