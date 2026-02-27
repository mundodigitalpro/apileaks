
import requests
import re
import time
import concurrent.futures

REPORT_FILE = "report_claves_cerebras.md"
OUTPUT_FILE = "report_valid_cerebras.md"
MAX_WORKERS = 10

def extract_keys(filename):
    """Extracts Cerebras keys from the report file."""
    keys = set()
    try:
        with open(filename, "r") as f:
            content = f.read()
            # Match keys starting with csk-
            matches = re.findall(r"csk-[a-zA-Z0-9]{48}", content)
            for key in matches:
                keys.add(key)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    return list(keys)

def check_key(api_key):
    """Checks the validity of a Cerebras API key."""
    url = "https://api.cerebras.ai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return api_key, True, "VALID (200 OK)"
        elif response.status_code == 401:
            return api_key, False, "INVALID (401)"
        elif response.status_code == 429:
            return api_key, True, "VALID BUT RATE LIMITED (429)"
        else:
            return api_key, False, f"UNKNOWN ({response.status_code})"
            
    except Exception as e:
        return api_key, False, f"ERROR: {str(e)}"

def main():
    print(f"Reading keys from {REPORT_FILE}...")
    keys = extract_keys(REPORT_FILE)
    print(f"Found {len(keys)} unique potential keys.")

    verified_keys = []
    
    report_content = "# Reporte de Verificación de Claves Cerebras\n\n"
    report_content += "| Clave (Parcial) | Estado | Detalle |\n"
    report_content += "| --- | --- | --- |\n"

    print(f"Checking keys with {MAX_WORKERS} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_key = {executor.submit(check_key, key): key for key in keys}
        for future in concurrent.futures.as_completed(future_to_key):
            key, is_valid, status = future.result()
            
            masked_key = key[:10] + "..." + key[-4:] if len(key) > 14 else key
            row = f"| `{masked_key}` | {'VALIDA' if is_valid else 'INVALIDA'} | {status} |"
            
            if is_valid:
                print(f"[FOUND] {masked_key}: {status}")
                verified_keys.append((key, status))
            
            report_content += row + "\n"

    with open(OUTPUT_FILE, "w") as f:
        f.write(report_content)
    
    print(f"\nVerification complete. Found {len(verified_keys)} valid/active keys.")
    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
