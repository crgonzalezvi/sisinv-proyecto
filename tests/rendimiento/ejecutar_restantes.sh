#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../.."
: "${TEST_HOST:?Indica el gateway de pruebas}" "${TEST_TOKEN:?Usa un JWT de administrador}" "${TEST_PRODUCTO_ID:?Indica un producto existente}" "${TEST_BODEGA_ID:?Indica una bodega existente}"
mkdir -p resultados
for escenario in registro producto_crear producto_consultar bodega_crear proveedores_listar proveedor_crear proveedor_consultar proveedor_editar proveedor_baja orden_crear orden_consultar orden_recibir; do
    for perfil in carga estres capacidad; do
        case "$perfil" in
            carga) usuarios=5 ;;
            estres) usuarios=20 ;;
            capacidad) usuarios=40 ;;
        esac
        prefijo="resultados/${escenario}_${perfil}"
        locust -f tests/rendimiento/endpoints_restantes.py --headless --host "$TEST_HOST" \
            --tags "$escenario" -u "$usuarios" -r 5 -t "${TEST_DURATION:-60s}" --csv "$prefijo" --html "$prefijo.html"
    done
done
python3 generar_dashboard.py
