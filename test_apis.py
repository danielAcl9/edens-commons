import requests
import ephem
import anthropic
from datetime import date, datetime
from dotenv import load_dotenv
import os

SEPARATOR = "\n" + "=" * 60 + "\n"


# ── 1. Open-Meteo ─────────────────────────────────────────────
def test_open_meteo():
    """Datos climáticos mensuales para Santander, Colombia.

    Usa /v1/forecast con parámetros indicados; como ese endpoint limita
    el pronóstico a 16 días y no expone _max/_min/_sum como variables
    mensuales directas, se obtienen datos diarios del último año completo
    desde /v1/archive y se agregan por mes.
    """
    print("TEST 1 — Open-Meteo: clima mensual Santander, Colombia")
    url = "https://api.open-meteo.com/v1/forecast"

    # Intentar primero con los parámetros exactos solicitados
    params = [
        ("latitude", 6.6437),
        ("longitude", -73.1327),
        ("monthly", "temperature_2m_max"),
        ("monthly", "temperature_2m_min"),
        ("monthly", "precipitation_sum"),
        ("timezone", "America/Bogota"),
        ("forecast_months", 12),
    ]
    resp = requests.get(url, params=params, timeout=30)

    if resp.status_code == 200:
        data = resp.json()
        monthly = data.get("monthly", {})
        times  = monthly.get("time", [])
        t_max  = monthly.get("temperature_2m_max", [])
        t_min  = monthly.get("temperature_2m_min", [])
        precip = monthly.get("precipitation_sum", [])
        rows = list(zip(times, t_max, t_min, precip))
    else:
        # Fallback: datos diarios del último año vía /v1/archive, agregados por mes
        today = date.today()
        end   = date(today.year - 1, 12, 31)
        start = date(today.year - 1, 1, 1)
        arc_url = "https://archive-api.open-meteo.com/v1/archive"
        arc_params = [
            ("latitude", 6.6437),
            ("longitude", -73.1327),
            ("daily", "temperature_2m_max"),
            ("daily", "temperature_2m_min"),
            ("daily", "precipitation_sum"),
            ("timezone", "America/Bogota"),
            ("start_date", str(start)),
            ("end_date", str(end)),
        ]
        ar = requests.get(arc_url, params=arc_params, timeout=30)
        ar.raise_for_status()
        daily  = ar.json().get("daily", {})
        days   = daily.get("time", [])
        t_max  = daily.get("temperature_2m_max", [])
        t_min  = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])

        from collections import defaultdict
        agg: dict = defaultdict(lambda: {"tmax": [], "tmin": [], "prec": []})
        for i, d in enumerate(days):
            ym = d[:7]
            if i < len(t_max)  and t_max[i]  is not None: agg[ym]["tmax"].append(t_max[i])
            if i < len(t_min)  and t_min[i]  is not None: agg[ym]["tmin"].append(t_min[i])
            if i < len(precip) and precip[i] is not None: agg[ym]["prec"].append(precip[i])

        rows = [
            (ym,
             max(v["tmax"]) if v["tmax"] else None,
             min(v["tmin"]) if v["tmin"] else None,
             sum(v["prec"]) if v["prec"] else None)
            for ym, v in sorted(agg.items())
        ]

    month_names = {
        "01": "Enero", "02": "Febrero", "03": "Marzo",    "04": "Abril",
        "05": "Mayo",  "06": "Junio",   "07": "Julio",    "08": "Agosto",
        "09": "Sep",   "10": "Oct",     "11": "Nov",      "12": "Dic",
    }

    print(f"\n{'Mes':<10} {'T.Max (°C)':>10} {'T.Min (°C)':>10} {'Precip (mm)':>12}")
    print("-" * 46)
    for label, tmax, tmin, prec in rows:
        nombre = month_names.get(str(label)[5:7], str(label))
        s_tmax = f"{tmax:.1f}" if tmax is not None else "N/D"
        s_tmin = f"{tmin:.1f}" if tmin is not None else "N/D"
        s_prec = f"{prec:.1f}" if prec is not None else "N/D"
        print(f"{nombre:<10} {s_tmax:>10} {s_tmin:>10} {s_prec:>12}")


# ── 2. Nominatim (OpenStreetMap) ───────────────────────────────
def test_nominatim():
    """Busca 'Santander, Colombia' y retorna latitud y longitud."""
    print("TEST 2 — Nominatim: geocodificación de 'Santander, Colombia'")
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": "Santander, Colombia", "format": "json", "limit": 1}
    headers = {"User-Agent": "eden-commons-test"}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    results = resp.json()

    if not results:
        print("Sin resultados.")
        return

    r = results[0]
    print(f"\nLugar    : {r.get('display_name')}")
    print(f"Latitud  : {r.get('lat')}")
    print(f"Longitud : {r.get('lon')}")


# ── 3. ephem ───────────────────────────────────────────────────
def test_ephem():
    """Lista las próximas 12 fechas de luna nueva y luna llena."""
    print("TEST 3 — ephem: próximas 12 lunas nuevas y llenas")
    month_names = [
        "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
    ]

    today = ephem.now()
    phases = []

    # Recorre hacia adelante hasta reunir 12 eventos
    cursor = today
    while len(phases) < 12:
        next_new = ephem.next_new_moon(cursor)
        next_full = ephem.next_full_moon(cursor)
        if next_new < next_full:
            phases.append(("Luna Nueva 🌑", next_new))
            cursor = next_new + 1          # avanza un día para no repetir
        else:
            phases.append(("Luna Llena 🌕", next_full))
            cursor = next_full + 1

    print(f"\n{'#':<3} {'Fecha':<14} {'Tipo':<14} {'Mes'}")
    print("-" * 52)
    for i, (tipo, dt) in enumerate(phases, 1):
        d = dt.datetime()
        mes = month_names[d.month]
        print(f"{i:<3} {d.strftime('%Y-%m-%d'):<14} {tipo:<14} {mes}")


# ── 4. Anthropic Claude ────────────────────────────────────────
def test_anthropic():
    """Llama a la Claude API con claude-haiku-4-5-20251001."""
    print("TEST 4 — Anthropic Claude API")
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError("ANTHROPIC_API_KEY no encontrada en .env")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[
            {
                "role": "user",
                "content": 'Respond with exactly: EDEN Commons API test successful',
            }
        ],
    )
    text = next(
        (block.text for block in message.content if block.type == "text"), ""
    )
    print(f"\nRespuesta: {text}")
    print(f"Modelo   : {message.model}")
    print(f"Tokens   : entrada={message.usage.input_tokens}, salida={message.usage.output_tokens}")


# ── Runner ─────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [test_open_meteo, test_nominatim, test_ephem, test_anthropic]

    for test in tests:
        print(SEPARATOR)
        try:
            test()
        except Exception as exc:
            print(f"\n[ERROR] {type(exc).__name__}: {exc}")

    print(SEPARATOR)
    print("Pruebas finalizadas.")
