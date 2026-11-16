<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\GatewayController;
use App\Http\Middleware\JwtAuthMiddleware; 

Route::any('/{service}/{path?}', [GatewayController::class, 'handle'])
    ->where('path', '.*')
    ->middleware(JwtAuthMiddleware::class); 