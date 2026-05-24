# NASDAQ Deep Learning Stock Prediction Project

## 1. Descriere generală

Acest proiect este realizat pentru disciplina „Rețele neuronale și tehnici de Deep Learning”.

Scopul proiectului este de a utiliza date istorice de tranzacționare de pe piața NASDAQ pentru a construi modele de predicție bazate pe rețele neuronale.

În loc să prezicem valoarea exactă a prețului unei acțiuni, proiectul va aborda problema ca o problemă de clasificare binară: modelul va prezice dacă prețul de închidere al unei acțiuni va crește sau nu în următoarea zi de tranzacționare.

## 2. Dataset ales

Setul de date ales este NASDAQ.

Datele disponibile sunt organizate în fișiere CSV, câte un fișier pentru fiecare zi de tranzacționare.

Fiecare fișier conține următoarele coloane:

| Coloană | Descriere |
| --- | --- |
| `Symbol` | Simbolul companiei tranzacționate |
| `Date` | Data tranzacționării |
| `Open` | Prețul de deschidere |
| `High` | Prețul maxim intraday |
| `Low` | Prețul minim intraday |
| `Close` | Prețul de închidere |
| `Volume` | Numărul de acțiuni tranzacționate |

## 3. Simboluri selectate

Pentru a reduce dimensiunea proiectului și pentru a putea lucra eficient, vom folosi un subset de companii mari listate pe NASDAQ.

Simboluri propuse:

```text
AAPL, MSFT, NVDA, AMZN, GOOGL
```

Aceste simboluri au fost alese deoarece sunt companii mari, lichide, cunoscute și au suficiente date istorice pentru analiza seriilor de timp.

## 4. Obiectivul predicției

Obiectivul proiectului este predicția direcției prețului de închidere pentru următoarea zi de tranzacționare.

Mai exact, pentru fiecare simbol și fiecare zi, vom calcula o variabilă țintă binară:

```text
target = 1 dacă Close(t+1) > Close(t)
target = 0 dacă Close(t+1) <= Close(t)
```

Unde:

- `Close(t)` reprezintă prețul de închidere din ziua curentă.
- `Close(t+1)` reprezintă prețul de închidere din următoarea zi de tranzacționare.

Astfel, modelul va învăța să prezică dacă prețul va crește sau nu în ziua următoare.

## 5. Tipul problemei

Problema este de tip clasificare binară.

Clasele sunt:

| Clasă | Semnificație |
| --- | --- |
| `1` | Prețul de închidere crește în ziua următoare |
| `0` | Prețul de închidere scade sau rămâne constant în ziua următoare |

## 6. Preprocesarea datelor

Pașii principali de preprocesare vor fi:

1. Citirea fișierelor CSV NASDAQ.
2. Selectarea simbolurilor relevante: AAPL, MSFT, NVDA, AMZN, GOOGL.
3. Conversia coloanei `Date` în format datetime.
4. Sortarea datelor după `Symbol` și `Date`.
5. Eliminarea valorilor lipsă.
6. Eliminarea duplicatelor.
7. Calcularea indicatorilor tehnici.
8. Crearea variabilei țintă `target`.
9. Eliminarea rândurilor cu valori lipsă generate de calculele rolling.
10. Scalarea variabilelor numerice.
11. Împărțirea datelor în train, validation și test în ordine cronologică.

Foarte important: deoarece lucrăm cu serii de timp, împărțirea datelor nu va fi făcută random, ci cronologic.

Split propus:

| Set | Procent |
| --- | ---: |
| Train | 70% |
| Validation | 15% |
| Test | 15% |

## 7. Indicatori și variabile de intrare

Pe lângă variabilele originale din dataset, vom calcula indicatori suplimentari pentru a ajuta modelul să înțeleagă mai bine dinamica prețurilor.

Variabile originale:

```text
Open, High, Low, Close, Volume
```

Indicatori calculați:

| Indicator | Formulă / descriere |
| --- | --- |
| `daily_return` | `Close.pct_change()` |
| `log_return` | `log(Close / Close.shift(1))` |
| `intraday_range` | `(High - Low) / Open` |
| `close_open_change` | `(Close - Open) / Open` |
| `volume_change` | `Volume.pct_change()` |
| `sma_5` | Media mobilă a prețului `Close` pe 5 zile |
| `sma_10` | Media mobilă a prețului `Close` pe 10 zile |
| `sma_20` | Media mobilă a prețului `Close` pe 20 zile |
| `volatility_5` | Deviația standard rolling a randamentului pe 5 zile |
| `volatility_10` | Deviația standard rolling a randamentului pe 10 zile |
| `volatility_20` | Deviația standard rolling a randamentului pe 20 zile |
| `return_lag_1` | Randamentul din ziua anterioară |
| `return_lag_2` | Randamentul de acum 2 zile |
| `return_lag_3` | Randamentul de acum 3 zile |
| `return_lag_5` | Randamentul de acum 5 zile |

## 8. Modele propuse

Vom testa mai multe modele de rețele neuronale pentru a compara performanțele.

### Model 1: MLP baseline

Primul model va fi un Multi-Layer Perceptron simplu.

Acesta va folosi indicatorii calculați pentru fiecare zi și va prezice direcția prețului pentru ziua următoare.

Rolul acestui model este să avem un baseline simplu.

### Model 2: LSTM

Al doilea model va fi un LSTM.

LSTM este potrivit pentru serii de timp deoarece poate învăța dependențe temporale din secvențe de date.

Pentru acest model, vom folosi o fereastră temporală de 20 de zile.

Exemplu:

```text
Ultimele 20 de zile de date -> predicția pentru ziua următoare
```

Forma datelor pentru LSTM va fi:

```text
X = samples x 20 zile x număr_features
y = target
```

### Model 3: GRU

Al treilea model va fi GRU.

GRU este asemănător cu LSTM, dar are o arhitectură mai simplă și poate fi mai rapid de antrenat.

Scopul este să comparăm performanța GRU cu LSTM și MLP.

## 9. Funcția de pierdere și metrici

Pentru că problema este de clasificare binară, vom folosi următoarea funcție de pierdere:

```text
Binary Crossentropy
```

Metrici utilizate:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion Matrix

Accuracy arată proporția totală de predicții corecte.

Precision arată cât de corecte sunt predicțiile pozitive.

Recall arată câte dintre cazurile pozitive reale au fost detectate de model.

F1-score combină precision și recall într-o singură metrică.

Confusion Matrix arată câte exemple au fost clasificate corect sau greșit pentru fiecare clasă.

## 10. Experimente propuse

Pentru a demonstra o îmbunătățire iterativă a rezultatelor, vom realiza mai multe experimente.

| Experiment | Descriere |
| --- | --- |
| Experiment 1 | Model MLP folosind doar variabilele originale: `Open`, `High`, `Low`, `Close`, `Volume` |
| Experiment 2 | Model MLP folosind variabilele originale plus indicatori tehnici calculați |
| Experiment 3 | Model LSTM folosind secvențe de 20 de zile |
| Experiment 4 | Model GRU folosind secvențe de 20 de zile |

Rezultatele vor fi comparate pentru a vedea dacă indicatorii tehnici și modelele secvențiale îmbunătățesc performanța.

## 11. Grafice și rezultate

Vom genera următoarele grafice:

1. Evoluția prețului `Close` pentru fiecare simbol.
2. Evoluția randamentului zilnic.
3. Volatilitatea rolling.
4. Distribuția claselor `target`.
5. Training loss vs validation loss.
6. Training accuracy vs validation accuracy.
7. Confusion matrix pentru fiecare model.
8. Predicții vs valori reale.

Vom genera și un tabel comparativ cu modelele:

| Model | Accuracy | Precision | Recall | F1-score |
| --- | --- | --- | --- | --- |
| MLP basic | TBD | TBD | TBD | TBD |
| MLP + indicators | TBD | TBD | TBD | TBD |
| LSTM | TBD | TBD | TBD | TBD |
| GRU | TBD | TBD | TBD | TBD |
