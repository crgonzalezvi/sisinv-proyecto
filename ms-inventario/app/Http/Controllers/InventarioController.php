<?php

namespace App\Http\Controllers;

use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;

class InventarioController extends Controller
{
    public function crearBodega(Request $request): JsonResponse
    {
        $datos = $request->validate(['nombre' => 'required|string|max:255|unique:bodegas']);
        $id = DB::table('bodegas')->insertGetId($datos);

        return response()->json(['id' => $id, 'nombre' => $datos['nombre']], 201);
    }

    public function registrarEntrada(Request $request): JsonResponse
    {
        $datos = $request->validate([
            'bodega_id' => 'required|integer|exists:bodegas,id',
            'producto_id' => 'required|uuid',
            'cantidad' => 'required|integer|min:1|max:2147483647',
        ]);

        try {
            $producto = Http::baseUrl(config('services.productos.url'))->timeout(3)
                ->get('/api/productos/'.$datos['producto_id']);
        } catch (ConnectionException) {
            return response()->json(['error' => 'Productos no responde.'], 503);
        }

        if ($producto->notFound()) {
            return response()->json(['error' => 'El producto no existe.'], 422);
        }
        if (! $producto->successful()) {
            return response()->json(['error' => 'No se pudo verificar el producto.'], 502);
        }

        $id = DB::table('entradas')->insertGetId($datos);

        return response()->json(['id' => $id] + $datos, 201);
    }

    public function recibirOrden(Request $request): JsonResponse
    {
        $clave = config('services.ordenes.clave');
        abort_unless($clave && hash_equals($clave, $request->header('X-Ordenes-Key', '')), 403);

        $datos = $request->validate([
            'orden_id' => 'required|uuid',
            'bodega_id' => 'required|integer|exists:bodegas,id',
            'detalles' => 'required|array|min:1',
            'detalles.*.producto_id' => 'required|uuid|distinct',
            'detalles.*.cantidad' => 'required|integer|min:1|max:2147483647',
        ]);

        return DB::transaction(function () use ($datos) {
            $recepcion = [
                'orden_id' => $datos['orden_id'],
                'bodega_id' => $datos['bodega_id'],
                'huella' => hash('sha256', json_encode($datos['detalles'])),
            ];
            if (! DB::table('recepciones')->insertOrIgnore($recepcion)) {
                abort_unless(DB::table('recepciones')->where($recepcion)->exists(), 409, 'La recepción ya tiene otros datos.');
                return response()->json(['orden_id' => $datos['orden_id']]);
            }

            foreach ($datos['detalles'] as $detalle) {
                DB::table('entradas')->insert([
                    'bodega_id' => $datos['bodega_id'],
                    'producto_id' => $detalle['producto_id'],
                    'cantidad' => $detalle['cantidad'],
                ]);
            }

            return response()->json(['orden_id' => $datos['orden_id']], 201);
        });
    }

    public function stock(int $bodega, string $producto): JsonResponse
    {
        abort_unless(DB::table('bodegas')->where('id', $bodega)->exists(), 404, 'Bodega no encontrada.');

        $cantidad = DB::table('entradas')->where('bodega_id', $bodega)
            ->where('producto_id', $producto)->sum('cantidad');

        return response()->json(['bodega_id' => $bodega, 'producto_id' => $producto, 'stock' => (int) $cantidad]);
    }

    public function kardex(int $bodega, string $producto): JsonResponse
    {
        abort_unless(DB::table('bodegas')->where('id', $bodega)->exists(), 404, 'Bodega no encontrada.');

        $entradas = DB::table('entradas')
            ->where('bodega_id', $bodega)
            ->where('producto_id', $producto)
            ->orderBy('id')
            ->get();

        $saldo = 0;
        $movimientos = $entradas->map(function ($e) use (&$saldo) {
            $saldo += (int) $e->cantidad;
            return [
                'id' => $e->id,
                'bodega_id' => $e->bodega_id,
                'producto_id' => $e->producto_id,
                'tipo_movimiento' => 'ENTRADA',
                'cantidad_delta' => (int) $e->cantidad,
                'saldo_posterior' => $saldo,
            ];
        });

        return response()->json([
            'bodega_id' => $bodega,
            'producto_id' => $producto,
            'saldo_actual' => $saldo,
            'movimientos' => $movimientos,
        ]);
    }
}
