# NASDAQ Deep Learning Project

Proiect Python pentru preprocesarea datelor istorice NASDAQ si pregatirea unui flux de lucru pentru modele de Deep Learning.

## Obiectiv

Predicția direcției prețului de închidere pentru următoarea zi de tranzacționare:

- `target = 1` dacă `Close(t+1) > Close(t)`
- `target = 0` dacă `Close(t+1) <= Close(t)`

Partea implementată acum acoperă responsabilitatea de Data Engineer: citirea datelor brute zilnice, filtrarea simbolurilor selectate, curățarea și salvarea datasetului procesat.

## Structură

```text
.
├── data/
│   ├── raw_sample/      # date brute NASDAQ, ignorate de git
│   └── processed/       # fisiere procesate mici
├── outputs/
│   ├── figures/
│   ├── predictions/
│   └── metrics/
├── src/
│   ├── config.py
│   ├── load_data.py
│   ├── preprocessing.py
│   ├── indicators.py
│   ├── train_models.py
│   ├── evaluate.py
│   └── plots.py
├── main.py
├── requirements.txt
└── raport_proiect.docx
```

## Instalare

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Rulare preprocesare

```powershell
python main.py
```

Rularea citește mii de fișiere CSV zilnice și poate dura aproximativ 1-2 minute. Scriptul afișează progres periodic în consolă.

Comanda implicită filtrează simbolurile:

```text
AAPL, MSFT, NVDA, AMZN, GOOGL
```

Poți schimba simbolurile astfel:

```powershell
python main.py --symbols AAPL MSFT NVDA AMZN GOOGL
```

## Validare separată

După rularea fluxului principal, poți verifica datasetul procesat cu:

```powershell
python validate_processed.py
```

## Output

Pipeline-ul generează:

- `data/processed/processed_nasdaq.csv`
- `outputs/metrics/preprocessing_summary.json`
- `outputs/figures/close_price_evolution.svg`
- `outputs/figures/average_volume_by_symbol.svg`
- `outputs/figures/observations_by_symbol.svg`

Datasetul procesat păstrează coloanele:

| Coloană | Descriere |
| --- | --- |
| `Symbol` | Simbolul companiei |
| `Date` | Data tranzacționării în format `YYYY-MM-DD` |
| `Open` | Prețul de deschidere |
| `High` | Prețul maxim intraday |
| `Low` | Prețul minim intraday |
| `Close` | Prețul de închidere |
| `Volume` | Numărul de acțiuni tranzacționate |

## Împărțire pe membri

- Membrul 1: preprocesare date brute NASDAQ.
- Membrul 2: feature engineering și indicatori tehnici.
- Membrul 3: modele MLP, LSTM și GRU.
- Membrul 4: evaluare, grafice și raport.

## Notă pentru arhivare

Datele brute din `data/raw_sample/` sunt mari și sunt excluse din git. Pentru încărcarea proiectului, include codul, documentația, dataseturile procesate mici și outputurile relevante.

Raportul Word este livrabil separat și se editează independent. `main.py` nu generează fișiere Word sau Markdown.
