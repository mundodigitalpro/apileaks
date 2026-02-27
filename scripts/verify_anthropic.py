
import requests
import re
import time

REPORT_FILE = "report_claves_anthropic.md"
OUTPUT_FILE = "report_valid_anthropic.md"

def extract_keys(filename):
    """Extracts Anthropic keys from the report file."""
    keys = set()
    try:
        with open(filename, "r") as f:
            content = f.read()
            # Match keys starting with sk-ant- and capturing until whitespace or backtick
            # Since the report format is `- `key``, we can use a simpler regex or just search for sk-ant-...
            matches = re.findall(r"sk-ant-[a-zA-Z0-9\-_]+", content)
            for key in matches:
                # Filter out placeholder keys or obvious fakes if needed
                if "replace" in key.lower() or "example" in key.lower() or "your-key" in key.lower():
                    continue
                keys.add(key)
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")
    return list(keys)

def check_key(api_key):
    """Checks the validity of an Anthropic API key."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    data = {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1,
        "messages": [
            {"role": "user", "content": "Hi"}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            return True, "VALID (200 OK)"
        elif response.status_code == 400:
            # 400 usually means valid key but bad request parameters. 
            # However, with correct parameters, it should be 200.
            # If the model is invalid, it returns 400.
            # If the key is invalid, it returns 401.
            return True, f"LIKELY VALID ({response.status_code}): {response.text}"
        elif response.status_code == 401:
            return False, "INVALID (401 Unauthorized)"
        elif response.status_code == 402:
            return True, "VALID BUT NO CREDITS (402 Payment Required)"
        elif response.status_code == 429:
            return True, "VALID BUT RATE LIMITED (429 Too Many Requests)"
        else:
            return False, f"UNKNOWN ({response.status_code}): {response.text}"
            
    except Exception as e:
        return False, f"ERROR: {str(e)}"

def main():
    print(f"Reading keys from {REPORT_FILE}...")
    keys = extract_keys(REPORT_FILE)
    print(f"Found {len(keys)} unique potential keys.")

    verified_keys = []
    
    report_content = "# Reporte de Verificación de Claves Anthropic\n\n"
    report_content += "| Clave (Parcial) | Estado | Detalle |\n"
    report_content += "| --- | --- | --- |\n"

    for key in keys:
        print(f"Checking key: {key[:15]}...")
        is_valid, status = check_key(key)
        
        masked_key = key[:10] + "..." + key[-4:] if len(key) > 14 else key
        row = f"| `{masked_key}` | {'VALIDA' if is_valid else 'INVALIDA'} | {status} |"
        report_content += row + "\n"
        
        if is_valid:
            verified_keys.append((key, status))
        
        # Rate limit prevention
        time.sleep(1) 

    with open(OUTPUT_FILE, "w") as f:
        f.write(report_content)
    
    print(f"\nVerification complete. Found {len(verified_keys)} valid/active keys.")
    print(f"Report saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
