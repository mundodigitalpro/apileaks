"""Entry point del scraper."""
import argparse
import json
from config.settings import HEADLESS
from scraper.auth import AuthManager
from scraper.apiradar import APIRadarScraper


def run_api_mode(args):
    """Modo API directo: usa /api/leaks sin navegador."""
    from scraper.api_client import APIRadarClient

    print("🚀 Modo API directo\n")
    client = APIRadarClient()

    # Intentar autenticarse para desbloquear paginación completa
    client.setup_auth_from_session()

    # Mostrar stats globales
    try:
        lb = client.fetch_leaderboard()
        print(f"\n🌐 APIRadar global:")
        print(f"   Repos escaneados: {lb.get('totalReposScanned', '?')}")
        print(f"   Leaks totales:    {lb.get('totalLeaksFound', '?')}")
        print(f"   Leaks hoy:        {lb.get('leaksFoundToday', '?')}\n")
    except Exception:
        pass

    leaks = client.fetch_all_leaks(
        limit_per_page=50,
        max_leaks=args.limit,
        provider=args.provider,
        sort_by=args.sort_by,
        time_range=args.time_range,
    )

    if leaks:
        filepath = client.export_to_json(args.output)

        stats = client.get_stats()
        print(f"\n📊 Estadísticas:")
        print(f"   Total descargados: {stats['total']}")
        if stats.get("by_provider"):
            print("   Por proveedor:")
            for provider, count in sorted(stats["by_provider"].items(),
                                           key=lambda x: x[1], reverse=True)[:10]:
                print(f"      - {provider}: {count}")
    else:
        print("⚠️  No se obtuvieron leaks. Verifica tu sesión (ejecuta sin --api primero).")

    print("\n✅ Listo!")


def run_scraper_mode(args):
    """Modo scraper: usa Playwright para navegar y extraer datos."""
    print("🚀 Iniciando APIRadar Scraper (modo navegador)")
    print(f"   Modo headless: {args.headless}\n")

    auth = AuthManager()
    headless_mode = args.headless if auth.has_valid_session() else False
    page, browser, pw = auth.login(headless=headless_mode)

    try:
        scraper = APIRadarScraper(page)

        print("📄 Navegando a la sección de leaks...")
        scraper.navigate_to_leaks()

        print("🔍 Extrayendo datos...")
        leaks = scraper.extract_leaks(limit=args.limit)
        print(f"   Encontrados: {len(leaks)} leaks")

        if args.load_more:
            print("⏳ Cargando más leaks (scroll infinito)...")
            page_count = 0
            max_pages = args.max_pages or 0  # 0 = sin límite
            stale_count = 0

            while True:
                prev_count = len(scraper.data)
                if not scraper.load_more():
                    stale_count += 1
                    if stale_count >= 3:
                        print("   No se cargan más leaks. Fin del scroll.")
                        break
                    continue

                stale_count = 0
                page_count += 1
                leaks = scraper.extract_leaks()
                print(f"   Scroll {page_count}: {len(leaks)} leaks totales")

                if args.limit and len(leaks) >= args.limit:
                    break
                if max_pages and page_count >= max_pages:
                    print(f"   Alcanzado límite de {max_pages} scrolls.")
                    break

        if leaks:
            filepath = scraper.export_to_json(args.output)

            stats = scraper.get_stats()
            print(f"\n📊 Estadísticas:")
            print(f"   Total: {stats['total']}")
            if stats.get("by_provider"):
                print("   Por proveedor:")
                for provider, count in sorted(stats["by_provider"].items(),
                                               key=lambda x: x[1], reverse=True)[:5]:
                    print(f"      - {provider}: {count}")
        else:
            print("⚠️  No se encontraron leaks. Verifica los selectores CSS.")

        print("\n✅ Listo!")

    finally:
        browser.close()
        pw.stop()


def main():
    parser = argparse.ArgumentParser(description="APIRadar Leaks Scraper")

    # Modo de operación
    parser.add_argument("--api", action="store_true",
                        help="Usar API directa (más rápido, requiere sesión guardada)")

    # Opciones comunes
    parser.add_argument("--limit", type=int, default=None,
                        help="Limitar número de leaks a extraer")
    parser.add_argument("--output", type=str, default=None,
                        help="Nombre del archivo de salida")
    parser.add_argument("--provider", type=str, default=None,
                        help="Filtrar por proveedor (openai, anthropic, groq, google, etc.)")
    parser.add_argument("--sort-by", type=str, default="newest",
                        choices=["newest", "oldest"],
                        help="Orden de resultados (default: newest)")
    parser.add_argument("--time-range", type=str, default=None,
                        help="Rango de tiempo (7d, 30d, 90d)")

    # Opciones modo scraper
    parser.add_argument("--headless", action="store_true", default=HEADLESS,
                        help="Ejecutar sin interfaz gráfica")
    parser.add_argument("--load-more", action="store_true",
                        help="Cargar más leaks automáticamente (scroll infinito)")
    parser.add_argument("--max-pages", type=int, default=None,
                        help="Límite de scrolls en modo scraper (default: sin límite)")

    args = parser.parse_args()

    if args.api:
        run_api_mode(args)
    else:
        run_scraper_mode(args)


if __name__ == "__main__":
    main()
