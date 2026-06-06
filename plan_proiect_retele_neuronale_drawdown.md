# Plan proiect – Rețele neuronale și tehnici de Deep Learning

## Titlu propus

**Predicția scăderii maxime viitoare pe termen scurt pentru acțiunile NASDAQ utilizând rețele neuronale**

## Ideea proiectului

Proiectul urmărește estimarea riscului de scădere pe termen scurt pentru acțiunile listate pe NASDAQ. În loc să prezicem direct prețul sau direcția de creștere/scădere, modelul estimează **scăderea maximă viitoare pe următoarele 10 zile de tranzacționare**.

Pentru fiecare simbol bursier și fiecare zi de tranzacționare `t`, folosim informațiile istorice disponibile până în ziua `t` pentru a estima cea mai mare scădere procentuală posibilă în următoarele 10 zile.

## Obiectivul predicției

Pentru fiecare observație de tip `Symbol-Date`, modelul primește o secvență de date istorice și produce o estimare numerică a drawdown-ului maxim viitor.

Formula conceptuală a targetului este:

FutureMaxDrawdown_10d = - min( Close_t+k / Close_t - 1 ), pentru k = 1, ..., 10

Dacă toate randamentele viitoare sunt pozitive, targetul este 0.

Interpretare:

| Valoare target | Interpretare |
|---:|---|
| 0.00 | Nu apare o scădere în următoarele 10 zile |
| 0.03 | Scădere maximă estimată de 3% |
| 0.10 | Scădere maximă estimată de 10% |

## Tipul problemei

| Element | Alegere |
|---|---|
| Set de date | NASDAQ - primele 50 de simboluri dupa pondere din Nasdaq100 |
| Tip problemă | Regresie |
| Unitate de observație | Symbol-Date |
| Target | future_max_drawdown_10d |
| Orizont de predicție | 10 zile de tranzacționare |
| Modele | Baseline naiv, MLP, LSTM |
| Loss | Huber Loss sau MSE |
| Metrici | MAE, RMSE, R², corelație actual-predicted |
| Split | Temporal: train, validation, test |

## De ce este o temă bună

 Drawdown-ul maxim viitor este relevant pentru investitori, pentru managementul riscului și pentru evaluarea vulnerabilității pe termen scurt a unei acțiuni.

# Flow-ul general al proiectului

<pre class="mermaid">
flowchart TD
    A[Fișiere CSV zilnice NASDAQ] --> B[Încărcare și concatenare date]
    B --> C[Dataset panel brut: Symbol, Date, Open, High, Low, Close, Volume]
    C --> D[Curățare date]
    D --> E[Dataset panel curățat]
    E --> F[Feature engineering]
    F --> G[Calcul target: future_max_drawdown_10d]
    G --> H[Dataset final: features + target]
    H --> I[Split temporal: train, validation, test]
    I --> J[Scalare features folosind doar train]
    J --> L[MLP]
    J --> M[LSTM]
    L --> N[Metrici și predicții]
    M --> N
    N --> O[Grafice și tabele]
    O --> P[Document Word + arhivă proiect]
</pre>

## Output-ul fiecărei etape

| Etapă | Input | Output |
|---|---|---|
| Încărcare date | Fișiere CSV zilnice | Dataset brut concatenat |
| Curățare date | Dataset brut | processed_panel.csv |
| Feature engineering | processed_panel.csv | features_targets.csv |
| Calcul target | Prețuri Close pe simbol | future_max_drawdown_10d |
| Split temporal | features_targets.csv | train.csv, validation.csv, test.csv |
| Scalare | train, validation, test | variante scalate ale seturilor |
| Baseline | features + target | predicții baseline + metrici |
| MLP | features tabelare | predicții MLP + metrici |
| LSTM | secvențe temporale | predicții LSTM + metrici |
| Evaluare | predicții + valori reale | grafice, tabele, interpretări |

# Flow-ul modelului

<pre class="mermaid">
flowchart LR
    A[Date istorice pentru un simbol] --> B[Secvență de intrare]
    B --> C[Indicatori calculați pe ultimele N zile]
    C --> D[Model neuronal]
    D --> E[Predicție numerică]
    E --> F[future_max_drawdown_10d estimat]
    F --> G[Interpretare: risc de scădere pe următoarele 10 zile]
</pre>

## Cum arată input-ul modelului

Pentru modelul LSTM, input-ul este o secvență de zile istorice pentru același simbol.

Exemplu conceptual:

| Dimensiune | Semnificație |
|---|---|
| samples | numărul de observații/secvențe construite |
| timesteps | numărul de zile istorice folosite ca input, de exemplu 10, 30 sau 60 |
| features | numărul de indicatori calculați pentru fiecare zi |

Forma input-ului pentru LSTM:

(samples, timesteps, features)

Exemplu:

| Componentă | Exemplu |
|---|---|
| sample | AAPL la data 2022-05-10 |
| timesteps | ultimele 30 de zile de tranzacționare până la 2022-05-10 |
| features | randamente, volatilitate, drawdown istoric, volum, medii mobile |
| output | drawdown-ul maxim în următoarele 10 zile |

Pentru MLP, input-ul este mai simplu: o singură linie pentru fiecare observație Symbol-Date, cu indicatorii calculați până în ziua respectivă.

Forma input-ului pentru MLP:

(samples, features)

## Exemple de features

| Feature | Semnificație |
|---|---|
| log_return_1d | Randamentul logaritmic zilnic |
| return_5d | Randamentul pe ultimele 5 zile |
| return_10d | Randamentul pe ultimele 10 zile |
| return_20d | Randamentul pe ultimele 20 zile |
| volatility_5d | Volatilitatea randamentelor pe ultimele 5 zile |
| volatility_10d | Volatilitatea randamentelor pe ultimele 10 zile |
| volatility_20d | Volatilitatea randamentelor pe ultimele 20 zile |
| volatility_60d | Volatilitatea randamentelor pe ultimele 60 zile |
| past_max_drawdown_10d | Drawdown-ul maxim observat în ultimele 10 zile |
| past_max_drawdown_20d | Drawdown-ul maxim observat în ultimele 20 zile |
| past_max_drawdown_60d | Drawdown-ul maxim observat în ultimele 60 zile |
| intraday_range | Diferența High-Low raportată la Open |
| open_close_return | Diferența Close-Open raportată la Open |
| volume_change_1d | Variația volumului față de ziua precedentă |
| volume_ratio_20d | Volumul curent raportat la volumul mediu pe 20 zile |
| ma_5_ratio | Close raportat la media mobilă pe 5 zile |
| ma_20_ratio | Close raportat la media mobilă pe 20 zile |
| ma_60_ratio | Close raportat la media mobilă pe 60 zile |

## Cum arată output-ul modelului

Output-ul modelului este o valoare numerică pozitivă sau zero.

| Output model | Interpretare |
|---:|---|
| 0.000 | Modelul estimează risc foarte redus de scădere |
| 0.025 | Modelul estimează o scădere maximă de aproximativ 2.5% |
| 0.070 | Modelul estimează o scădere maximă de aproximativ 7% |
| 0.150 | Modelul estimează o scădere maximă de aproximativ 15% |

Exemplu de output final în fișierul de predicții:

| Symbol | Date | Actual future_max_drawdown_10d | Predicted future_max_drawdown_10d | Error |
|---|---|---:|---:|---:|
| AAPL | 2023-02-10 | 0.041 | 0.036 | 0.005 |
| MSFT | 2023-02-10 | 0.028 | 0.031 | -0.003 |
| NVDA | 2023-02-10 | 0.094 | 0.081 | 0.013 |

# Flow specific pentru MLP

<pre class="mermaid">
flowchart TD
    A[Un rând Symbol-Date] --> B[Features calculate până în ziua t]
    B --> C[Standardizare features]
    C --> D[Input MLP: samples x features]
    D --> E[Dense layers + ReLU + Dropout]
    E --> F[Output: predicted future_max_drawdown_10d]
</pre>

## Input și output MLP

| Element | Descriere |
|---|---|
| Input | Indicatorii calculați pentru ziua t |
| Formă input | samples x features |
| Exemplu input | AAPL, 2022-05-10, cu indicatorii calculați până în acea zi |
| Output | O singură valoare numerică |
| Exemplu output | 0.047, adică drawdown maxim estimat de 4.7% |

# Flow specific pentru LSTM

<pre class="mermaid">
flowchart TD
    A[Date ordonate pentru fiecare Symbol] --> B[Construire secvențe separate pe simbol]
    B --> C[Secvență de N zile până la ziua t]
    C --> D[Input LSTM: samples x timesteps x features]
    D --> E[LSTM layer]
    E --> F[Dense layer]
    F --> G[Output: predicted future_max_drawdown_10d]
</pre>

## Input și output LSTM

| Element | Descriere |
|---|---|
| Input | Secvență de N zile pentru același simbol |
| Formă input | samples x timesteps x features |
| Timesteps testate | 10, 30, 60 zile |
| Features | Indicatorii calculați pentru fiecare zi din secvență |
| Output | O singură valoare numerică pentru ziua t |
| Exemplu output | 0.083, adică drawdown maxim estimat de 8.3% în următoarele 10 zile |

Important: secvențele LSTM nu trebuie să amestece simboluri diferite. O secvență trebuie construită doar din observații consecutive ale aceluiași simbol.

# Modele și experimente


## Model 1 – MLP

MLP-ul este folosit ca baseline neuronal. Acesta primește indicatorii calculați pentru ziua t și produce direct o predicție numerică pentru drawdown-ul maxim viitor.

Rolul MLP-ului este să testeze dacă indicatorii agregați conțin informație utilă pentru predicția riscului.

## Model 2 – LSTM simplu

LSTM-ul este modelul secvențial principal. Acesta primește o secvență de N zile și încearcă să învețe dinamica temporală a riscului.

Rolul LSTM-ului este să testeze dacă ordinea temporală și evoluția recentă a indicatorilor ajută mai mult decât indicatorii agregați folosiți de MLP.

## Model 3 – LSTM optimizat

Se testează mai multe configurații ale LSTM-ului.

| Variantă | Sequence length | Units | Dropout | Loss |
|---|---:|---:|---:|---|
| LSTM 1 | 10 | 32 | 0.1 | MSE sau Huber |
| LSTM 2 | 30 | 64 | 0.2 | MSE sau Huber |
| LSTM 3 | 60 | 64 | 0.2 | MSE sau Huber |
| LSTM 4 | 30 | 128 | 0.3 | MSE sau Huber |

# Metrici de evaluare

| Metrică | Rol |
|---|---|
| MAE | Eroarea medie absolută, ușor de interpretat în puncte procentuale |
| RMSE | Penalizează mai mult erorile mari |
| R² | Măsoară proporția variației explicate de model |
| Corelație actual-predicted | Arată dacă modelul surprinde ordonarea riscului |
| Huber Loss | Loss robust la outlieri |
| MSE | Loss clasic pentru regresie |

Interpretare exemplu:

MAE = 0.012 înseamnă o eroare medie de aproximativ 1.2 puncte procentuale de drawdown.

# Grafice recomandate

| Grafic | Scop |
|---|---|
| Distribuția targetului | Arată cum este distribuit future_max_drawdown_10d |
| Training loss vs validation loss | Arată învățarea și eventualul overfitting |
| Actual vs predicted | Arată calitatea predicțiilor |
| Distribuția erorilor | Arată dacă modelul supraestimează sau subestimează riscul |
| Comparație modele | Compară baseline, MLP și LSTM |
| Evoluția riscului prezis pentru câteva simboluri | Ajută la interpretare intuitivă |

# Împărțirea pe persoane

## Persoana 1 – Data pipeline

Responsabilitate: transformă datele brute în dataset curățat.

Taskuri:

1. Citește toate fișierele CSV zilnice.
2. Unește fișierele într-un singur dataset.
3. Parsează coloana Date.
4. Convertește Open, High, Low, Close și Volume în tipuri numerice.
5. Elimină valori lipsă, prețuri invalide și volume invalide.
6. Sortează datele după Symbol și Date.
7. Păstrează simbolurile cu istoric suficient.
8. Salvează processed_panel.csv.
9. Generează data_quality_report.csv.


## Persoana 2 – Feature engineering și target

Responsabilitate: construiește datasetul de modelare.

Taskuri:

1. Calculează randamentele.
2. Calculează volatilitățile rolling.
3. Calculează drawdown-ul istoric.
4. Calculează indicatorii de volum.
5. Calculează indicatorii de medii mobile.
6. Calculează targetul future_max_drawdown_10d.
7. Elimină rândurile incomplete.
8. Face split temporal train, validation, test.
9. Aplică scalarea corectă folosind doar train.
10. Generează statistici descriptive și grafice pentru target.


## Persoana 3 – Modele și evaluare

Responsabilitate: antrenează modelele și produce rezultatele finale.

Taskuri:

1. Implementează MLP-ul.
2. Construiește secvențele pentru LSTM.
3. Implementează LSTM simplu.
4. Testează câteva configurații LSTM.
5. Aplică early stopping.
6. Calculează metricile finale.
7. Salvează predicțiile pe setul de test.
8. Generează graficele pentru raport.


## Persoana 4 – Document Word: metodologie

Responsabilitate: prima parte a documentului.

Secțiuni:

1. Introducere.
2. Obiectivul proiectului.
3. Descrierea setului de date.
4. Definirea drawdown-ului maxim viitor.
5. Preprocesarea datelor.
6. Indicatorii calculați.
7. Împărțirea train, validation, test.


## Persoana 5 – Document Word: modele, rezultate, concluzii

Responsabilitate: a doua parte a documentului.

Secțiuni:

1. Modelele utilizate.
2. Funcțiile de pierdere.
3. Metricile de evaluare.
4. Rezultatele obținute.
5. Interpretarea rezultatelor.
6. Limitări.
7. Concluzii.

