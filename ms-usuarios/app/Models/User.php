<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Concerns\HasUuids;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Tymon\JWTAuth\Contracts\JWTSubject; 

class User extends Authenticatable implements JWTSubject
{
    use HasFactory, Notifiable, HasUuids; 

    protected $fillable = [
        'nombre_completo',
        'email',
        'password',
        'rol_id',
        'activo'
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected function casts(): array
    {
        return [
            'password' => 'hashed',
            'activo' => 'boolean',
        ];
    }

    
    public function getJWTIdentifier()
    {
        return $this->getKey();
    }

    public function getJWTCustomClaims()
    {
        return [
            'rol_id' => $this->rol_id,
            'nombre' => $this->nombre_completo
        ];
    }
}