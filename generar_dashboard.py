import csv
import glob
import json
import os

ARCHIVOS = sorted(glob.glob("resultados/*_stats.csv"))
PERFILES = ["carga", "estres", "capacidad"]
ORDEN_PERFIL = {p: i for i, p in enumerate(PERFILES)}

datos = []

for ruta in ARCHIVOS:
    nombre_base = os.path.basename(ruta).replace("_stats.csv", "")
    partes = nombre_base.rsplit("_", 1)
    if len(partes) != 2:
        continue
    endpoint_tag, perfil = partes[0], partes[1].lower()

    with open(ruta, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    # Prioriza la fila del endpoint real (excluyendo setup: login y Aggregated)
    fila = next(
        (r for r in filas if r.get("Name") not in ("Aggregated", "setup: login")),
        None,
    ) or next((r for r in filas if r.get("Name") == "Aggregated"), None)

    if not fila:
        continue

    reqs = int(float(fila.get("Request Count", 0) or 0))
    fails = int(float(fila.get("Failure Count", 0) or 0))
    pct_fail = round((fails / reqs * 100), 2) if reqs else 0.0

    datos.append({
        "tag": endpoint_tag,
        "endpoint": fila.get("Name", endpoint_tag),
        "perfil": perfil,
        "reqs": reqs,
        "fails": fails,
        "pct_fail": pct_fail,
        "rps": round(float(fila.get("Requests/s", 0) or 0), 2),
        "avg_ms": round(float(fila.get("Average Response Time", 0) or 0), 1),
        "p95_ms": round(float(fila.get("95%", 0) or 0), 1),
        "max_ms": round(float(fila.get("Max Response Time", 0) or 0), 1),
    })

datos.sort(key=lambda x: (x["tag"], ORDEN_PERFIL.get(x["perfil"], 99)))

# Exporta también un CSV consolidado (útil para Excel o Power BI)
if datos:
    with open("resultados/resumen_consolidado.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=datos[0].keys())
        writer.writeheader()
        writer.writerows(datos)

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Dashboard de Rendimiento - SisInv</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  body {{ font-family: system-ui, -apple-system, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
  h1 {{ margin: 0 0 4px; font-size: 1.6rem; }}
  .sub {{ color: #94a3b8; margin-bottom: 24px; font-size: 0.95rem; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .card {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; }}
  .kpi-label {{ color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; }}
  .kpi-val {{ font-size: 1.7rem; font-weight: 700; margin-top: 6px; }}
  .charts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(380px, 1fr)); gap: 20px; margin-bottom: 24px; }}
  .chart-box {{ background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 16px; }}
  .chart-box h3 {{ margin: 0 0 12px; font-size: 1rem; color: #e2e8f0; }}
  table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 10px; overflow: hidden; }}
  th, td {{ padding: 10px 12px; text-align: left; border-bottom: 1px solid #334155; font-size: 0.9rem; }}
  th {{ background: #0b1220; color: #94a3b8; font-weight: 600; }}
  .badge {{ padding: 3px 8px; border-radius: 999px; font-size: 0.78rem; font-weight: 600; }}
  .ok {{ background: #14532d; color: #86efac; }}
  .warn {{ background: #713f12; color: #fde047; }}
  .err {{ background: #7f1d1d; color: #fca5a5; }}
</style>
</head>
<body>
  <h1>SisInv — Dashboard de Pruebas de Rendimiento</h1>
  <div class="sub">Comparativa consolidada de Carga, Estrés y Capacidad vía API Gateway</div>

  <div class="kpis" id="kpis"></div>

  <div class="charts">
    <div class="chart-box"><h3>Rendimiento (Requests / segundo)</h3><canvas id="cRps"></canvas></div>
    <div class="chart-box"><h3>Latencia p95 (ms) — menor es mejor</h3><canvas id="cP95"></canvas></div>
    <div class="chart-box"><h3>Tasa de Fallos (%)</h3><canvas id="cFail"></canvas></div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Endpoint</th><th>Perfil</th><th>Peticiones</th><th>RPS</th>
        <th>Prom (ms)</th><th>p95 (ms)</th><th>Máx (ms)</th><th>Fallos</th><th>Estado</th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>

<script>
const datos = {json.dumps(datos, ensure_ascii=False)};
const tags = [...new Set(datos.map(d => d.tag))];
const perfiles = ["carga", "estres", "capacidad"];
const colores = {{ carga: "#22c55e", estres: "#f59e0b", capacidad: "#ef4444" }};

const totalReqs = datos.reduce((s, d) => s + d.reqs, 0);
const totalFails = datos.reduce((s, d) => s + d.fails, 0);
const avgRps = datos.length ? (datos.reduce((s, d) => s + d.rps, 0) / datos.length).toFixed(1) : 0;
const avgP95 = datos.length ? (datos.reduce((s, d) => s + d.p95_ms, 0) / datos.length).toFixed(0) : 0;
const failPct = totalReqs ? ((totalFails / totalReqs) * 100).toFixed(2) : 0;

document.getElementById("kpis").innerHTML = `
  <div class="card"><div class="kpi-label">Pruebas Ejecutadas</div><div class="kpi-val">${{datos.length}}</div></div>
  <div class="card"><div class="kpi-label">Total Peticiones</div><div class="kpi-val">${{totalReqs.toLocaleString()}}</div></div>
  <div class="card"><div class="kpi-label">RPS Promedio</div><div class="kpi-val">${{avgRps}}</div></div>
  <div class="card"><div class="kpi-label">p95 Promedio</div><div class="kpi-val">${{avgP95}} ms</div></div>
  <div class="card"><div class="kpi-label">Fallos Globales</div><div class="kpi-val">${{failPct}}%</div></div>
`;

function hacerGrafica(canvasId, campo) {{
  const datasets = perfiles.map(p => ({{
    label: p.toUpperCase(),
    backgroundColor: colores[p],
    data: tags.map(t => {{
      const item = datos.find(d => d.tag === t && d.perfil === p);
      return item ? item[campo] : 0;
    }})
  }}));
  new Chart(document.getElementById(canvasId), {{
    type: "bar",
    data: {{ labels: tags, datasets }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ labels: {{ color: "#cbd5e1" }} }} }},
      scales: {{
        x: {{ ticks: {{ color: "#cbd5e1" }}, grid: {{ color: "#334155" }} }},
        y: {{ ticks: {{ color: "#cbd5e1" }}, grid: {{ color: "#334155" }} }}
      }}
    }}
  }});
}}

hacerGrafica("cRps", "rps");
hacerGrafica("cP95", "p95_ms");
hacerGrafica("cFail", "pct_fail");

document.getElementById("tbody").innerHTML = datos.map(d => {{
  let cls = "ok", txt = "Estable";
  if (d.pct_fail > 5 || d.p95_ms > 2000) {{ cls = "err"; txt = "Saturado"; }}
  else if (d.pct_fail > 0 || d.p95_ms > 800) {{ cls = "warn"; txt = "Degradado"; }}
  return `<tr>
    <td>${{d.endpoint}}</td>
    <td>${{d.perfil.toUpperCase()}}</td>
    <td>${{d.reqs.toLocaleString()}}</td>
    <td>${{d.rps}}</td>
    <td>${{d.avg_ms}}</td>
    <td>${{d.p95_ms}}</td>
    <td>${{d.max_ms}}</td>
    <td>${{d.fails}} (${{d.pct_fail}}%)</td>
    <td><span class="badge ${{cls}}">${{txt}}</span></td>
  </tr>`;
}}).join("");
</script>
</body>
</html>"""

with open("resultados/dashboard_rendimiento.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Listo: {len(datos)} pruebas consolidadas.")
print("-> Abre: resultados/dashboard_rendimiento.html")
print("-> CSV consolidado: resultados/resumen_consolidado.csv")