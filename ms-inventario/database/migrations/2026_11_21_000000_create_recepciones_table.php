<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('recepciones', function (Blueprint $table) {
            $table->uuid('orden_id')->primary();
            $table->foreignId('bodega_id')->constrained('bodegas');
            $table->string('huella', 64);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('recepciones');
    }
};
