# gtfobinsSOS

🧰 **gtfobinsSOS** è uno script Python pensato per agevolare il *privilege escalation triage* su sistemi Unix-like.
Prende in input l'output del comando:

```
find / -perm -u=s -type f 2>/dev/null
```

e controlla automaticamente, tramite **https://gtfobins.github.io**, se i binari trovati hanno una scheda documentata su GTFOBins.


---

## Installazione

1. Clona il repository:
```bash
git clone https://github.com/ph3mt/gtfobinsSOS.git
cd gtfobinsSOS
```

2. (Opzionale) crea un ambiente virtuale e installa le dipendenze:
```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

---

## Uso

### Metodo interattivo
1. Esegui:
```bash
python3 gtfobinsSOS.py
```
2. Incolla l'output del comando:
```bash
sudo find / -perm -u=s -type f 2>/dev/null
```
3. Premi **Ctrl+D** (Linux/macOS) o **Ctrl+Z + Invio** (Windows) per inviare EOF; il tool eseguirà i controlli e stamperà i risultati.

### Metodo con file
```bash
python3 gtfobinsSOS.py -i examples/sample_input.txt -o results.csv
```

---

## Esempio di output
```
Trovati 22 binari unici; controllo su gtfobins...
[1/22] php -> PAGE FOUND: https://gtfobins.github.io/gtfobins/php/
    Sections: SUID; Shell; File Write
[2/22] passwd -> not found (HTTP 404)
...
CSV scritto in: results.csv
```

---

## Struttura consigliata
```
gtfobinsSOS/
├── gtfobinsSOS.py
├── requirements.txt
├── README.md
├── examples/
│   └── sample_input.txt
└── .gitignore
```

---

## Licenza
Distribuito sotto licenza **MIT** — aggiungi un file `LICENSE` se desideri pubblicarlo.

---

## Avvertenze
- La presenza di una pagina su GTFOBins **non implica automaticamente vulnerabilità**.  
- Verifica versione, percorso, permessi, SELinux/AppArmor e capability.  
- Non usare su sistemi per cui non hai autorizzazione.

---

## Autore
**ph3mt**
https://github.com/ph3mt/gtfobinsSOS
