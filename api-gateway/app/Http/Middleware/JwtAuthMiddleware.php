<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class JwtAuthMiddleware
{
    public function handle(Request $request, Closure $next): Response
    {
        // Definimos las rutas públicas que NO exigen token
        $publicRoutes = [
            'usuarios/login',
            'usuarios/registro'
        ];

        $currentPath = $request->path();

        // Si la petición va a una ruta pública, pasa directo
        foreach ($publicRoutes as $route) {
            if (str_contains($currentPath, $route)) {
                return $next($request);
            }
        }

        // Para las demás rutas (Inventario, Productos, etc.), exigimos el token para la correcta autenticación
        $token = $request->bearerToken();

        if (!$token) {
            return response()->json([
                'error' => 'Acceso denegado. Se requiere un Token JWT válido.'
            ], 401);
        }

        // Aquí más adelante validaremos que la firma del token sea correcta
        // Por ahora, si trae cualquier token, lo dejamos pasar al microservicio
        return $next($request);
    }
}