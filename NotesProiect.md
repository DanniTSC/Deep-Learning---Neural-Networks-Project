# Ce am început să fac?

Predicția direcției randamentului pentru următoarea zi pentru câteva companii NASDAQ mari, folosind date istorice și indicatori tehnici calculați.

Exemplu:

Pentru simbolurile AAPL, MSFT, NVDA, AMZN și GOOGL, modelul prezice dacă randamentul de mâine va fi pozitiv sau negativ, folosind ultimele 20 de zile de tranzacționare.

Variabila țintă este binară:

```text
1 = Close(t+1) > Close(t)
0 = Close(t+1) <= Close(t)
```

Înseamnă că nu încercăm să prezicem prețul exact de mâine, ci încercăm să prezicem direcția: crește sau scade.

Avem prețul de închidere de azi:

```text
Close(t)
```

și prețul de închidere din ziua următoare:

```text
Close(t+1)
```

Dacă mâine prețul este mai mare decât azi:

```text
Close(t+1) > Close(t)
```

atunci punem:

```text
target = 1
```

adică prețul a crescut.

Dacă mâine prețul este mai mic sau egal cu cel de azi:

```text
Close(t+1) <= Close(t)
```

punem:

```text
target = 0
```

adică prețul nu a crescut.

| Date | Symbol | Close | Close mâine | Target |
| --- | --- | ---: | ---: | ---: |
| 01-Jan | AAPL | 100 | 103 | 1 |
| 02-Jan | AAPL | 103 | 101 | 0 |
| 03-Jan | AAPL | 101 | 101 | 0 |
| 04-Jan | AAPL | 101 | 105 | 1 |

## Am ales AAPL, MSFT, NVDA, AMZN, GOOGL, META, TSLA

## Împărțirea pe 4 membri

### Membrul 1: Data Engineer / Preprocesare date

Responsabil cu partea de date brute NASDAQ.

Ce face:

- citește fișierele CSV zilnice;
- filtrează doar simbolurile alese: AAPL, MSFT, NVDA, AMZN, GOOGL;
- unește fișierele într-un singur dataset;
- sortează datele după `Symbol` și `Date`;
- curăță lipsuri, duplicate, date greșite;
- salvează un dataset final mic, de tip `processed_nasdaq.csv`.

Coloane de bază:

```text
Symbol, Date, Open, High, Low, Close, Volume
```

### Membrul 2: Feature Engineering / Indicatori tehnici

Responsabil cu transformarea datelor în input bun pentru model.

Ce face:

- calculează indicatori:
  - daily return;
  - log return;
  - SMA 5, SMA 10, SMA 20;
  - volatilitate rolling 5/10/20 zile;
  - volume change;
  - intraday range;
  - lag returns;
  - RSI, dacă vreți ceva mai avansat.
- creează variabila țintă:

```text
target_next_day = 1 dacă Close de mâine > Close de azi, altfel 0
```

- elimină rândurile cu NaN generate de rolling windows;
- salvează datasetul final pentru model: `features_nasdaq.csv`.

### Membrul 3: Modelare Deep Learning

Responsabil cu modelele neuronale.

Ce face:

- împarte datele în train/validation/test cronologic, nu random;
- scalează variabilele numerice;
- creează secvențe de 20 de zile pentru LSTM/GRU;
- implementează modelele:
  - MLP baseline;
  - LSTM;
  - GRU, opțional.
- antrenează modelele;
- salvează:
  - loss curves;
  - accuracy curves;
  - predicții;
  - model summary.

Modele recomandate:

1. Model 1: MLP baseline
2. Model 2: LSTM
3. Model 3: GRU

### Membrul 4: Evaluare, grafice, raport

Responsabil cu partea de interpretare și prezentare.

Ce face:

- compară modelele;
- generează tabele cu rezultate;
- face grafice:
  - training loss vs validation loss;
  - training accuracy vs validation accuracy;
  - confusion matrix;
  - distribuția claselor;
  - prețul de închidere în timp;
  - returns/volatility.
- scrie raportul Word:
  - obiectiv;
  - date;
  - preprocesare;
  - indicatori;
  - modele;
  - rezultate;
  - interpretări;
  - concluzii.
