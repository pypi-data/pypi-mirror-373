import os
import requests
import plotly.graph_objects as go
import plotly.io as pio
from datetime import datetime

def fetch_noaa():
    url = "https://services.swpc.noaa.gov/json/solar-wind.json"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return [float(d.get("density", 0)) for d in data[-50:]], [d.get("time_tag") for d in data[-50:]]
    except Exception as e:
        print("NOAA fetch failed, fallback:", e)
        return [0.1], [datetime.utcnow().isoformat()]

def fetch_usgs():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        mags = [f["properties"]["mag"] for f in data["features"] if f["properties"]["mag"]]
        times = [datetime.utcfromtimestamp(f["properties"]["time"]/1000).isoformat()
                 for f in data["features"] if f["properties"]["time"]]
        return mags, times
    except Exception as e:
        print("USGS fetch failed, fallback:", e)
        return [0.2], [datetime.utcnow().isoformat()]

def build_dashboard():
    noaa_y, noaa_x = fetch_noaa()
    usgs_y, usgs_x = fetch_usgs()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=noaa_x, y=noaa_y, mode="lines+markers", name="NOAA ΔΦ Drift"))
    fig.add_trace(go.Scatter(x=usgs_x, y=usgs_y, mode="lines+markers", name="USGS Quakes"))

    fig.update_layout(
        title=f"SUPT Dashboard (NOAA + USGS) — Updated {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        xaxis_title="Time (UTC)",
        yaxis_title="Value",
        template="plotly_white"
    )

    os.makedirs("site", exist_ok=True)
    out = os.path.join("site", "index.html")
    pio.write_html(fig, file=out, auto_open=False)
    print(f"✅ Dashboard written to {out}")

if __name__ == "__main__":
    build_dashboard()
