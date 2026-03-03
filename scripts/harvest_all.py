"""
Maximiza los leaks descargados combinando todas las queries posibles
(proveedor × rango de tiempo × orden) y deduplicando por id.
"""
import json
import time
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scraper.api_client import APIRadarClient
from config.settings import DATA_DIR

PROVIDERS = [None, "openai", "anthropic", "google", "groq", "mistral", "cerebras", "xai"]
TIME_RANGES = [None, "7d", "30d", "90d"]
SORT_ORDERS = ["newest", "oldest"]


def harvest():
    client = APIRadarClient()
    client.setup_auth_from_session()

    seen_ids = set()
    all_leaks = []

    combos = [
        (provider, time_range, sort_by)
        for provider in PROVIDERS
        for time_range in TIME_RANGES
        for sort_by in SORT_ORDERS
    ]

    total_combos = len(combos)
    print(f"\n🔄 Ejecutando {total_combos} combinaciones de queries...\n")

    for i, (provider, time_range, sort_by) in enumerate(combos, 1):
        label = f"provider={provider or 'all':12s}  range={time_range or 'all':5s}  sort={sort_by}"
        try:
            data = client.fetch_leaks(
                page=1,
                limit=50,
                provider=provider,
                sort_by=sort_by,
                time_range=time_range,
            )
            leaks = data.get("leaks", [])
            new = [l for l in leaks if l["id"] not in seen_ids]
            for l in new:
                seen_ids.add(l["id"])
            all_leaks.extend(new)
            print(f"  [{i:3d}/{total_combos}] {label}  →  {len(leaks):2d} leaks, {len(new):2d} nuevos  (total: {len(all_leaks)})")
        except Exception as e:
            print(f"  [{i:3d}/{total_combos}] {label}  →  ERROR: {e}")

        time.sleep(0.4)  # evitar rate-limit

    print(f"\n✅ Total leaks únicos recolectados: {len(all_leaks)}")

    # Guardar
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output = DATA_DIR / f"harvest_{ts}.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(all_leaks, f, indent=2, ensure_ascii=False)
    print(f"💾 Guardado en: {output}")

    # Stats por proveedor
    by_provider = {}
    for l in all_leaks:
        p = l.get("provider", "unknown")
        by_provider[p] = by_provider.get(p, 0) + 1
    print("\n📊 Por proveedor:")
    for p, count in sorted(by_provider.items(), key=lambda x: x[1], reverse=True):
        print(f"   {p:15s}: {count}")

    return all_leaks


if __name__ == "__main__":
    harvest()
