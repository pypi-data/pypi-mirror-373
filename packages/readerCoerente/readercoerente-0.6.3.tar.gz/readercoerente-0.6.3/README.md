# Sensore Coerente Cohaerentia - lettore file TDMS

Pacchetto per lettura e visualizzazione delle misure salvate da software per sensore Coerente sviluppato da Cohaerentia.

## Installazione

Il pacchetto è disponibile su PyPi e può essere installato tramite pip:

```bash
pip install readerCoerente
```

In alternativa, scaricare il wheel dal repository e installare tramite pip:

```bash
pip install <path_to_wheel>
```

## Utilizzo

Importare pacchetto:

```python
from readerCoerente import File, multipleFiles, detrend,
```

### Caricamento dei dati

#### Singolo file

Si utilizza la classe `File`, specificando il percorso al file da caricare.

```python
prova = File('data/2023-07-19_15-15-20_prova0_Ph.tdms')
print(prova)
```

Dove si è usato `print` per ottenere alcune informazioni di base sul file caricato.

#### Multipli files concatenati

E' possibile concatenare i dati contenuti in multipli files, se contenuti nella stessa cartella `folder` e con le stesse proprietà (per esempio, stessa frequenza di campionamento). Il pacchetto *non* verifica la continuità temporale dei dati contenuti nei files. Indicare nel parametro `filename` il path "comune" nei files. Per esempio, se i files sono:

```plain
data/2023-07-19_15-23-53_prova3_Ph.tdms
data/2023-07-19_15-24-06_prova3_Ph.tdms
data/2023-07-19_15-24-12_prova3_Ph.tdms
data/2023-07-19_15-24-37_prova3_Ph.tdms
```

è sufficiente indicare `filename = 'prova3'`.

```python
provaMulti = multipleFiles(folder="data",filename="prova3")
print(provaMulti)
```

#### Lettura file .ini con parametri di normalizzazione

```python
from readerCoerente import read_config
para = read_config("Cohaerentia3PD_003.ini")
print(para)
```

### Metodi

## Utilizzo

Per accedere al numpy array della fase, per esempio per plottarlo:

```python
import plotly.graph_objects as go
go.Figure(layout=dict(title=prova.filename, xaxis_title='Time (s)', yaxis_title='Phase (rad)'),
          data=[go.Scatter(x=prova.time, y=prova.phase)]).show()
```

Per convertire i radianti ad allungamento relativo misurato si può utilizzare il metodo `convertToElongation` che converte i radianti in metri. Di default viene utilizzato il coefficiente teorico per fibra in silica: rad = 9.239e6 metri. E' possibile utilizzarne uno differente attraverso il parametro opzionale `coefficient`.

```python
allungamento = prova.convert_to_elongation()
```

O, analogamente, per convertire a variazione di temperatura, utilizzare il metodo `.convert_to_temperature()` che utilizza il coefficiente di temperatura per fibra pari a 42.56 rad/°C*m ed è quindi necessario indicare anche la lunghezza del ramo dell'interferometro. Anche in questo caso è possibile utilizzare un coefficiente differente specificandolo nel parametro `coefficient`.

Se presenti nel file TDMS, è possibile accedere a tutti i canali, per esempio per plottarne una parte:

```python
for ch in prova.channels_name:
    data = getattr(prova,ch)
```

### Analisi spettrali

Per calcolare la **power spectrum density**, per esempio della fase:

```python
from scipy import signal

freqs, psd = signal.welch(sig, fs=prova.freq_sampling,nperseg=1024)

go.Figure(layout=dict(title='PSD: power spectral density',
                      xaxis_title='Frequency [Hz]',
                      yaxis_title='Power', yaxis_type='log'),
          data=[go.Scatter(x=freqs, y=psd)]).show()
```

### Detrend

Per esempio, utilizzando la funzione `detrend` del pacchetto, che è un `filtfilt` passa alto.

```python
ph_detrend = detrend(prova.phase, prova.freq_sampling, highpass_cutoff_Hz=100)

go.Figure(layout=dict(title=f"{prova.filename} detrended", xaxis_title='Time (s)', yaxis_title='Phase (rad)'),
          data=[go.Scatter(x=prova.time, y=ph_detrend)]).show()
```

### Esportazione dei dati in file h5

Per visualizzare i file h5 si può utilizzare Visual Studio Code con l'estensione H5Web.

```python
prova.export_to_h5('data/prova.h5')
```

### Sottocampionamento

Il metodo della classe si chiama `.undersampling()` e accetta parametro opzionale chiamato `factor` il cui valore di default è pari a 100. Esiste poi parametro opzionale `what` che accetta valori `{'all', 'phase', 'channel'}` e serve per stabilire cosa viene sottocampionato.

Nel caso in cui si sia interessati a non perdere per sempre quei campioni sarebbe necessario o ricaricare il file, creando di fatto un nuovo oggetto da zero, oppure si deve copiare in un nuovo oggetto prima di effettuare il sottocampionamento. La copia di oggetti non può essere effettuata con un semplice:

```python
provaunder = prova
```

ma è necessario utilizzare il pacchetto `copy`:

```python
import copy
provaunder = copy.deepcopy(prova)
```

### Asse dei tempi assoluta

Attenzione che plotly diventa particolarmente lento in questo caso; si consiglia quindi di sottocampionare i dati prima di plottarli. Utilizzando la proprietà `.absolute_time`:

```python
import copy
under_data = copy.deepcopy(misure[0])
under_data.undersampling(factor=50)
go.Figure(data=go.Scatter(x=under_data.absolute_time, y=under_data.phase)).show()
```
