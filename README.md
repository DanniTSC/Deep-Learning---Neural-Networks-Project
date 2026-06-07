# NASDAQ Deep Learning Project

Proiect Python pentru preprocesarea datelor istorice NASDAQ si construirea unui dataset de feature engineering pentru modele de Deep Learning.

## Obiectiv

Obiectivul curent al proiectului este estimarea riscului de scadere pe termen scurt pentru actiuni NASDAQ. Targetul modelului este o valoare numerica:

```text
future_max_drawdown_10d
```

Pentru fiecare observatie `Symbol-Date`, targetul reprezinta scaderea maxima viitoare pe urmatoarele 10 zile de tranzactionare, calculata din preturile `Close`. Daca in urmatoarele 10 zile nu apare o scadere fata de ziua curenta, targetul este `0`.

Problema este tratata ca regresie, nu clasificare. Planul detaliat al temei este documentat aici: [plan_proiect_retele_neuronale_drawdown.md](plan_proiect_retele_neuronale_drawdown.md).

## Ce este implementat acum

- citirea fisierelor CSV zilnice NASDAQ din `data/raw_sample/`;
- filtrarea simbolurilor selectate in `src/config.py`;
- curatarea si validarea datasetului OHLCV procesat;
- calculul indicatorilor tehnici si al targetului `future_max_drawdown_10d`;
- generarea sumarului JSON pentru preprocesare si feature engineering;
- generarea graficelor SVG pentru calitatea datelor si distributia targetului.

## Structura

```text
.
├── data/
│   ├── raw_sample/      # date brute NASDAQ, ignorate de git
│   └── processed/       # dataseturi procesate
├── outputs/
│   ├── figures/         # grafice SVG generate
│   ├── metrics/         # sumar JSON pentru pipeline
│   └── predictions/     # rezervat pentru predictii/modelare
├── src/
│   ├── config.py
│   ├── load_data.py
│   ├── preprocessing.py
│   ├── indicators.py
│   ├── validation.py
│   ├── pipeline.py
│   ├── train_models.py
│   ├── evaluate.py
│   └── plots.py
├── main.py
├── validate_processed.py
├── requirements.txt
├── plan_proiect_retele_neuronale_drawdown.md
└── raport_proiect_final.docx
```

## Instalare

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Pe macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Rulare script principal

Scriptul principal este `main.py`.

Rularea implicita refoloseste datasetul procesat existent si regenereaza datasetul de features + target:

```powershell
python main.py
```

Echivalent explicit:

```powershell
python main.py --step all --processed-mode reuse --features-mode regenerate
```

Pentru a regenera totul din fisierele brute NASDAQ:

```powershell
python main.py --step all --processed-mode regenerate --features-mode regenerate
```

Pentru a rula doar preprocesarea OHLCV:

```powershell
python main.py --step preprocess --processed-mode regenerate
```

Pentru a rula doar feature engineering-ul, folosind `data/processed/processed_nasdaq.csv` existent:

```powershell
python main.py --step features --features-mode regenerate
```

Pentru o rulare cu un subset de simboluri:

```powershell
python main.py --symbols AAPL MSFT NVDA AMZN GOOGL
```

Pentru a schimba orizontul targetului:

```powershell
python main.py --target-horizon-days 20
```

Optiuni utile:

| Optiune | Descriere |
| --- | --- |
| `--step all` | Ruleaza preprocesare + feature engineering. Este valoarea implicita. |
| `--step preprocess` | Ruleaza doar generarea/validarea datasetului OHLCV procesat. |
| `--step features` | Ruleaza doar generarea/validarea datasetului cu features si target. |
| `--processed-mode reuse` | Refoloseste `data/processed/processed_nasdaq.csv`. Este valoarea implicita. |
| `--processed-mode regenerate` | Regenereaza datasetul procesat din `data/raw_sample/`. |
| `--features-mode regenerate` | Regenereaza datasetul cu features si target. Este valoarea implicita. |
| `--features-mode reuse` | Refoloseste datasetul cu features si target existent. |
| `--raw-dir` | Schimba folderul cu fisiere CSV brute. |
| `--processed-output` | Schimba calea pentru datasetul OHLCV procesat. |
| `--features-output` | Schimba calea pentru datasetul cu features si target. |
| `--figures-dir` | Schimba folderul pentru graficele SVG generate. |
| `--quiet` | Ruleaza fara mesaje de progres. |

## Simboluri implicite

Comanda implicita filtreaza cele 50 de simboluri NASDAQ configurate in `src/config.py`:

```text
NVDA, AAPL, MSFT, AMZN, GOOGL, GOOG, AVGO, META, TSLA, MU,
WMT, AMD, ASML, INTC, CSCO, COST, LRCX, ARM, AMAT, NFLX,
PLTR, TXN, KLAC, LIN, SNDK, MRVL, QCOM, PANW, ADI, PEP,
TMUS, STX, AMGN, APP, WDC, CRWD, GILD, ISRG, SHOP, HON,
BKNG, PDD, VRTX, SBUX, FTNT, CDNS, MAR, ADBE, ADP, CEG
```

## Output

Pipeline-ul genereaza sau valideaza urmatoarele fisiere:

- `data/processed/processed_nasdaq.csv`
- `data/processed/features_targets_nasdaq.csv`
- `outputs/metrics/preprocessing_summary.json`
- `outputs/metrics/features_targets_summary.json`
- `outputs/figures/data_quality_observations_by_symbol.svg`
- `outputs/figures/target_future_drawdown_distribution.svg`
- `outputs/figures/target_average_drawdown_by_symbol.svg`
- `outputs/figures/target_drawdown_over_time.svg`

Nota: `data/processed/features_targets_nasdaq.csv` este generat local si este ignorat de git, deoarece poate deveni mare. Se regenereaza cu `python main.py --step features --features-mode regenerate`.

Datasetul procesat `processed_nasdaq.csv` pastreaza coloanele:

| Coloana | Descriere |
| --- | --- |
| `Symbol` | Simbolul companiei |
| `Date` | Data tranzactionarii in format `YYYY-MM-DD` |
| `Open` | Pretul de deschidere |
| `High` | Pretul maxim intraday |
| `Low` | Pretul minim intraday |
| `Close` | Pretul de inchidere |
| `Volume` | Numarul de actiuni tranzactionate |

Datasetul `features_targets_nasdaq.csv` contine coloanele OHLCV de mai sus, indicatori tehnici si targetul `future_max_drawdown_10d`. Exemple de features:

- randamente: `daily_return`, `log_return_1d`, `return_5d`, `return_10d`, `return_20d`;
- volum: `volume_change_1d`, `volume_ratio_20d`;
- medii mobile si rapoarte: `sma_5`, `sma_10`, `sma_20`, `sma_60`, `ma_5_ratio`, `ma_20_ratio`, `ma_60_ratio`;
- volatilitate: `volatility_5d`, `volatility_10d`, `volatility_20d`, `volatility_60d`;
- drawdown istoric: `past_max_drawdown_10d`, `past_max_drawdown_20d`, `past_max_drawdown_60d`;
- lag-uri: `return_lag_1`, `return_lag_2`, `return_lag_3`, `return_lag_5`.

## Validare separata

Validarea datasetului OHLCV procesat:

```powershell
python validate_processed.py
```

Validarea datasetului cu features si target:

```powershell
python validate_processed.py --features
```

Afisarea sablonului de metrici pentru regresie:

```powershell
python validate_processed.py --show-regression-metrics-template
```

## Impartire pe membri

- Membrul 1: preprocesare date brute NASDAQ.
- Membrul 2: feature engineering si indicatori tehnici.
- Membrul 3: modele MLP, LSTM si GRU.
- Membrul 4: evaluare, grafice si raport.

## Nota pentru arhivare

Datele brute din `data/raw_sample/` sunt mari si sunt excluse din git. Pentru incarcarea proiectului, include codul, documentatia, dataseturile procesate mici si outputurile relevante.

Raportul Word este livrabil separat si se editeaza independent. `main.py` nu genereaza fisiere Word sau Markdown.
