<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;

Route::post('/usuarios/registro', [AuthController::class, 'register']);
Route::post('/usuarios/login', [AuthController::class, 'login']);