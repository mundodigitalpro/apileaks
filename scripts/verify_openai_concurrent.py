
import requests
import re
import time
import concurrent.futures

REPORT_FILE = "report_claves_openai.md"
OUTPUT_FILE = "report_valid_openai.md"
MAX_WORKERS = 10

def extract_keys(filename):
    """Extracts OpenAI keys from the report file."""
    keys = set()
    try:
        with open(filename, "r") as f:
            content = f.read()
            # Match keys starting with sk- and capturing until whitespace or backtick
            matches = re.findall(r"sk-(?!ant-)[a-zA-Z0-9\-_]+", content)
            for key in matches:
                # Filter out obvious false positives
                if any(x in key.lower() for x in ["replace", "example", "your-key", "test-key", "docker-", "container-", "kubernetes-", "hf-", "my-key"]):
                    continue
                # OpenAI keys are usually at least 40 chars long (standard is 51, project keys are longer)
                if len(key) < 40:
                    continue
                keys.add(key)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    return list(keys)

def check_key(api_key):
    """Checks the validity of an OpenAI API key."""
    url = "https://api.openai.com/v1/models"
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
        elif response.status_code == 403: 
             return api_key, True, "VALID BUT RESTRICTED (403)"
        else:
            return api_key, False, f"UNKNOWN ({response.status_code})"
            
    except Exception as e:
        return api_key, False, f"ERROR: {str(e)}"

def main():
    print(f"Reading keys from {REPORT_FILE}...")
    keys = extract_keys(REPORT_FILE)
    print(f"Found {len(keys)} unique potential keys (after filtering short/junk keys).")

    verified_keys = []
    
    report_content = "# Reporte de Verificación de Claves OpenAI\n\n"
    report_content += "| Clave (Parcial) | Estado | Detalle |\n"
    report_content += "| --- | --- | --- |\n"

    print(f"Checking keys with {MAX_WORKERS} workers...")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_key = {executor.submit(check_key, key): key for key in keys}
        for future in concurrent.futures.as_completed(future_to_key):
            key, is_valid, status = future.result()
            
            masked_key = key[:10] + "..." + key[-4:] if len(key) > 14 else key
            row = f"| `{masked_key}` | {'VALIDA' if is_valid else 'INVALIDA'} | {status} |"
            
            # Only log valid keys to console to reduce noise
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
