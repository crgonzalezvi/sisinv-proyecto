<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class GatewayController extends Controller
{
    public function handle(Request $request, $service, $path = null)
    {
        // 1. Mapeamos el nombre de la ruta con la variable del .env
        $services = [
            'usuarios'   => env('MS_USUARIOS_URL'),
            'productos'  => env('MS_PRODUCTOS_URL'),
            'proveedores'=> env('MS_PROVEEDORES_URL'),
            'inventario' => env('MS_INVENTARIO_URL'),
            'ordenes'    => env('MS_ORDENES_URL'),
        ];

        // 2. Si el servicio no existe, bloqueamos de inmediato
        if (!array_key_exists($service, $services)) {
            return response()->json(['error' => 'Servicio o dominio no encontrado en el API Gateway'], 404);
        }

        // 3. Construimos la URL final hacia el microservicio
        $baseUrl = $services[$service];
        // Asumimos que los microservicios también tendrán prefijo /api/
        $url = $path ? "{$baseUrl}/api/{$path}" : "{$baseUrl}/api";

        // 4. Reenviamos la petición HTTP exacta al microservicio
        try {
            $response = Http::withHeaders($request->headers->all())
                ->send($request->method(), $url, [
                    'query' => $request->query(),
                    'body'  => $request->getContent(),
                ]);

            // 5. Devolvemos al cliente la respuesta tal cual la dio el microservicio
            return response($response->body(), $response->status())
                ->withHeaders($response->headers());
                
        } catch (\Exception $e) {
            return response()->json([
                'error' => 'El microservicio destino no responde.',
                'detalle' => $e->getMessage()
            ], 503); // 503 Service Unavailable
        }
    }
}