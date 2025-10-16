#!/usr/bin/env python3
"""
check_suid_gtfobins.py (fix)
Legge dall'input incollato l'output di `find`; per ogni basename prova:
  1) https://gtfobins.github.io/gtfobins/<name>/
  2) fallback: https://gtfobins.github.io/<name>/
Restituisce se la pagina esiste e gli headings (senza mostrare exploit).
"""

import sys
import os
import argparse
import requests
import time
from urllib.parse import quote
from bs4 import BeautifulSoup

# base corretta per GTFOBins e fallback
GTFOBASES = [
    "https://gtfobins.github.io/gtfobins",  # principale
    "https://gtfobins.github.io"           # fallback (mirror / legacy)
]

HEADERS = {
    "User-Agent": "suid-gtfobins-checker/1.2 (+https://gtfobins.github.io/)"
}

def parse_find_output(lines):
    basenames = set()
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        path = ln.split()[-1] if " " in ln else ln
        if not path.startswith("/"):
            continue
        base = os.path.basename(path)
        if base:
            basenames.add(base)
    return sorted(basenames)

def check_single_url(url, session, timeout=10):
    try:
        r = session.get(url, headers=HEADERS, timeout=timeout)
    except requests.RequestException as e:
        return None, str(e)
    return r, None

def parse_headings_from_response(r):
    soup = BeautifulSoup(r.text, "html.parser")
    headings = []
    for h in soup.find_all(["h2", "h3"]):
        text = h.get_text(strip=True)
        if text:
            headings.append(text)
    badges = []
    for span in soup.find_all("span", {"class": lambda x: x and "badge" in x}):
        t = span.get_text(strip=True)
        if t:
            badges.append(t)
    seen = set()
    headings_unique = [x for x in (badges + headings) if not (x in seen or seen.add(x))]
    return headings_unique

def check_gtfobin(name, session):
    # normalizza il nome: lowercase (gtfobins usa nomi minuscoli per la maggior parte)
    name_norm = name.lower()
    for base in GTFOBASES:
        url = f"{base}/{quote(name_norm)}/"
        r, err = check_single_url(url, session)
        if err:
            # rete/error tecnico: fallisce la richiesta, segnala e continua a next base
            return {"name": name, "url": url, "exists": False, "error": err}
        if r.status_code == 200:
            headings = parse_headings_from_response(r)
            return {"name": name, "url": url, "exists": True, "headings": headings}
        # se 404 proviamo il prossimo base (fallback)
    # nessuna base ha trovato la pagina
    return {"name": name, "url": f"{GTFOBASES[0]}/{quote(name_norm)}/", "exists": False, "status_code": 404}

def main():
    ap = argparse.ArgumentParser(description="Verifica SUID binaries vs gtfobins; incolla output di find e invia EOF")
    ap.add_argument("-i", dest="input", help="file con output di find; se omesso legge da stdin")
    ap.add_argument("-r", dest="rate", type=float, default=0.5, help="delay tra richieste in secondi; default 0.5")
    ap.add_argument("-o", dest="csv", help="salva output CSV in percorso dato")
    args = ap.parse_args()

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"Errore apertura file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        sys.stdout.write("Incolla l'output di `find` qui; poi premi Ctrl+D (Linux/macOS) o Ctrl+Z + Invio (Windows) per inviare EOF:\n")
        sys.stdout.flush()
        try:
            data = sys.stdin.read()
        except KeyboardInterrupt:
            print("\nInput interrotto; esco.")
            sys.exit(1)
        lines = data.splitlines()

    basenames = parse_find_output(lines)
    if not basenames:
        print("Nessun percorso valido trovato; esco.")
        sys.exit(0)

    session = requests.Session()
    results = []
    print(f"Trovati {len(basenames)} binari unici; controllo su gtfobins...")

    for i, name in enumerate(basenames, 1):
        res = check_gtfobin(name, session)
        results.append(res)
        if res.get("exists"):
            print(f"[{i}/{len(basenames)}] {name} -> PAGE FOUND: {res['url']}")
            if res.get("headings"):
                print("    Sections:", "; ".join(res["headings"]))
        else:
            sc = res.get("status_code")
            if sc:
                print(f"[{i}/{len(basenames)}] {name} -> not found (HTTP {sc})")
            else:
                print(f"[{i}/{len(basenames)}] {name} -> error; {res.get('error','')}")
        time.sleep(args.rate)

    if args.csv:
        import csv
        try:
            with open(args.csv, "w", newline="", encoding="utf-8") as csvf:
                writer = csv.writer(csvf)
                writer.writerow(["name", "url", "exists", "status_code", "sections_or_error"])
                for r in results:
                    if r.get("exists"):
                        writer.writerow([r["name"], r["url"], "yes", "", "; ".join(r.get("headings", []))])
                    else:
                        writer.writerow([r["name"], r["url"], "no", r.get("status_code",""), r.get("error","")])
            print(f"CSV scritto in: {args.csv}")
        except Exception as e:
            print(f"Errore scrittura CSV: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
