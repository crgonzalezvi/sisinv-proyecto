<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('bodegas', function (Blueprint $table) {
            $table->id();
            $table->string('nombre')->unique();
        });

        Schema::create('entradas', function (Blueprint $table) {
            $table->id();
            $table->foreignId('bodega_id')->constrained('bodegas');
            $table->uuid('producto_id');
            $table->unsignedInteger('cantidad');
            $table->timestamp('created_at')->useCurrent();
            $table->index(['bodega_id', 'producto_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('entradas');
        Schema::dropIfExists('bodegas');
    }
};
