
import json
import requests
import re
import os

OUTPUT_FILE = "report_claves_mistral.md"
INPUT_FILE = "data/leaks_api_20260214_203200.json"

def get_raw_url(url):
    """Converts a GitHub blob URL to a raw URL."""
    if "github.com" in url and "/blob/" in url:
        return url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    return url

def search_keys(content):
    """Searches for Mistral keys in the content."""
    # Mistral keys don't have a specific prefix like 'sk-' consistently, but are 32 char hex or similar.
    # However, common leaks show simple 32-char alphanumeric strings.
    # We will search for high-entropy strings assigned to variables like MISTRAL_API_KEY.
    # A more specific pattern might be needed if Mistral standardizes prefixes.
    # For now, we rely on the provider filter and search for typical API key patterns near 'mistral'.
    
    # Actually, recent Mistral keys might be 32 chars. Let's look for 32-char alphanumeric strings.
    pattern = re.compile(r"\b[a-zA-Z0-9]{32}\b")
    matches = pattern.findall(content)
    return matches

def main():
    print(f"Reading {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, "r") as f:
            leaks = json.load(f)
    except FileNotFoundError:
        print(f"Error: File {INPUT_FILE} not found.")
        return

    # Filter for 'mistral' provider
    mistral_leaks = [leak for leak in leaks if leak.get("provider") == "mistral"]
    print(f"Found {len(mistral_leaks)} potential Mistral leaks.")

    report_content = "# Reporte de Claves Mistral Encontradas\n\n"

    for leak in mistral_leaks:
        file_url = leak.get("fileUrl")
        raw_url = get_raw_url(file_url)
        print(f"Checking {raw_url}...")

        try:
            response = requests.get(raw_url, timeout=10)
            if response.status_code == 200:
                content = response.text
                found_keys = search_keys(content)
                
                status = "NO ENCONTRADA"
                keys_str = ""
                # Simple heuristic: if we found 32-char strings in a file flagged as mistral leak
                if found_keys:
                    status = "ENCONTRADA"
                    found_keys = list(set(found_keys))
                    keys_str = "\n".join([f"- `{k}`" for k in found_keys])
                
                report_content += f"## Leak ID: {leak.get('id')}\n"
                report_content += f"- **Repositorio**: {leak.get('repoUrl')}\n"
                report_content += f"- **Archivo**: {leak.get('filePath')}\n"
                report_content += f"- **URL Raw**: {raw_url}\n"
                report_content += f"- **Estado**: {status}\n"
                if found_keys:
                    report_content += f"- **Claves Expuestas**:\n{keys_str}\n"
                report_content += "\n"

            else:
                report_content += f"## Leak ID: {leak.get('id')}\n"
                report_content += f"- **Repositorio**: {leak.get('repoUrl')}\n"
                report_content += f"- **Archivo**: {leak.get('filePath')}\n"
                report_content += f"- **URL Raw**: {raw_url}\n"
                report_content += f"- **Estado**: NO ACCESIBLE (HTTP {response.status_code})\n\n"

        except Exception as e:
            report_content += f"## Leak ID: {leak.get('id')}\n"
            report_content += f"- **Repositorio**: {leak.get('repoUrl')}\n"
            report_content += f"- **Archivo**: {leak.get('filePath')}\n"
            report_content += f"- **URL Raw**: {raw_url}\n"
            report_content += f"- **Estado**: ERROR ({str(e)})\n\n"

    with open(OUTPUT_FILE, "w") as f:
        f.write(report_content)
    
    print(f"Report generated: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
