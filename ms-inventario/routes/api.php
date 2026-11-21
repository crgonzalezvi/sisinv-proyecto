<?php

use App\Http\Controllers\InventarioController;
use Illuminate\Support\Facades\Route;

Route::prefix('inventario')->controller(InventarioController::class)->group(function () {
    Route::post('bodegas', 'crearBodega');
    Route::post('recepciones', 'recibirOrden');
    Route::post('entradas', 'registrarEntrada');
    Route::get('bodegas/{bodega}/productos/{producto}/stock', 'stock')
        ->whereNumber('bodega')->whereUuid('producto');
});
