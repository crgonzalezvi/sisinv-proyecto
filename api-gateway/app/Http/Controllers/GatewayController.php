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

        // 3. Construimos la URL final incluyendo {$service}
        $baseUrl = rtrim($services[$service], '/');
        $url = $path 
            ? "{$baseUrl}/api/{$service}/{$path}" 
            : "{$baseUrl}/api/{$service}";

        // 4. Reenviamos la petición filtrando solo las cabeceras necesarias
        try {
            $headers = [
                'Accept'       => 'application/json',
                'Content-Type' => $request->header('Content-Type', 'application/json'),
            ];

            if ($request->hasHeader('Authorization')) {
                $headers['Authorization'] = $request->header('Authorization');
            }

            $response = Http::withHeaders($headers)
                ->send($request->method(), $url, [
                    'query' => $request->query(),
                    'body'  => $request->getContent(),
                ]);

            // 5. Devolvemos la respuesta limpia
            return response($response->body(), $response->status())
                ->header('Content-Type', $response->header('Content-Type', 'application/json'));
                
        } catch (\Exception $e) {
            return response()->json([
                'error'   => 'El microservicio destino no responde.',
                'detalle' => $e->getMessage()
            ], 503);
        }
    }
}