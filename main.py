"""Entry point del scraper."""
import argparse
import json
from config.settings import HEADLESS
from scraper.auth import AuthManager
from scraper.apiradar import APIRadarScraper


def main():
    parser = argparse.ArgumentParser(description="APIRadar Leaks Scraper")
    parser.add_argument("--headless", action="store_true", default=HEADLESS,
                        help="Ejecutar sin interfaz gráfica")
    parser.add_argument("--limit", type=int, default=None,
                        help="Limitar número de leaks a extraer")
    parser.add_argument("--output", type=str, default=None,
                        help="Nombre del archivo de salida")
    parser.add_argument("--load-more", action="store_true",
                        help="Cargar más leaks automáticamente")
    
    args = parser.parse_args()
    
    print("🚀 Iniciando APIRadar Scraper")
    print(f"   Modo headless: {args.headless}\n")
    
    # Autenticación
    auth = AuthManager()
    
    # Si no hay sesión, forzar modo visible para login manual
    headless_mode = args.headless if auth.has_valid_session() else False
    
    page, browser, context = auth.login(headless=headless_mode)
    
    try:
        # Scraper
        scraper = APIRadarScraper(page)
        
        print("📄 Navegando a la sección de leaks...")
        scraper.navigate_to_leaks()
        
        print("🔍 Extrayendo datos...")
        leaks = scraper.extract_leaks(limit=args.limit)
        print(f"   Encontrados: {len(leaks)} leaks")
        
        # Cargar más si se solicita
        if args.load_more:
            print("⏳ Cargando más leaks...")
            while scraper.load_more():
                new_leaks = scraper.extract_leaks()
                print(f"   Total: {len(new_leaks)} leaks")
                if args.limit and len(new_leaks) >= args.limit:
                    break
        
        # Exportar
        if leaks:
            filepath = scraper.export_to_json(args.output)
            
            # Mostrar stats
            stats = scraper.get_stats()
            print("\n📊 Estadísticas:")
            print(f"   Total: {stats['total']}")
            if stats.get("by_provider"):
                print("   Por proveedor:")
                for provider, count in sorted(stats["by_provider"].items(), 
                                               key=lambda x: x[1], reverse=True)[:5]:
                    print(f"      - {provider}: {count}")
        else:
            print("⚠️ No se encontraron leaks. Verifica los selectores CSS.")
        
        print("\n✅ Listo!")
        
    finally:
        browser.close()


if __name__ == "__main__":
    main()
