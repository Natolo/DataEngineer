# Retail Data Platform Handbook

Questo documento raccoglie i concetti studiati e le decisioni prese nel progetto
progressivo Retail Data Platform. Va aggiornato insieme al README al termine di
ogni settimana.

## Indice

1. [Architettura corrente](#architettura-corrente)
2. [Week 1: fondamenti Python](#week-1-fondamenti-python)
3. [Week 2: produzione e test](#week-2-produzione-e-test)
4. [Riferimento dei moduli](#riferimento-dei-moduli)
5. [Strategia di test](#strategia-di-test)
6. [Esecuzione del progetto](#esecuzione-del-progetto)
7. [Limiti attuali e prossimi passi](#limiti-attuali-e-prossimi-passi)
8. [Riferimenti ufficiali](#riferimenti-ufficiali)

## Architettura corrente

Il progetto usa un layout `src` e un package Python installabile in modalita
editable.

```text
week1/retail-data-platform/
|-- data/
|   |-- orders.json
|   `-- sales.csv
|-- src/retail_ingestion/
|   |-- __init__.py
|   |-- config.py
|   |-- csv_reader.py
|   |-- database.py
|   |-- json_reader.py
|   |-- models.py
|   |-- paths.py
|   |-- pipeline.py
|   |-- run.py
|   `-- validation.py
|-- test/
`-- pyproject.toml
```

Flusso logico corrente:

```text
file CSV/JSON
    -> reader
    -> validazione del record
    -> coordinamento della pipeline
    -> conteggi in BatchSummary
```

Responsabilita principali:

- i reader estraggono dati senza applicare regole di business;
- il validator decide se un record rispetta le regole e restituisce i motivi;
- la pipeline decide se accettare o scartare il record;
- `BatchSummary` conserva le metriche aggregate;
- il livello database gestisce connessioni e ciclo di vita delle risorse.

## Week 1: fondamenti Python

### 1. Ambiente virtuale

`.venv` isola interprete e pacchetti del repository. Non viene versionato perche
contiene file specifici della macchina e puo essere ricreato.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
```

Usare `python -m pip` collega esplicitamente `pip` all'interprete attivo.

File correlati:

- [`.gitignore`](../.gitignore)
- [`pyproject.toml`](../week1/retail-data-platform/pyproject.toml)

### 2. Moduli, package e layout `src`

Un modulo e un file Python. Un package e una directory importabile, qui
`retail_ingestion`, marcata da `__init__.py`.

Il layout `src` riduce gli import accidentali dalla directory di lavoro. Il
progetto e installato in modalita editable, quindi le modifiche sotto `src`
sono disponibili senza reinstallazione.

File correlati:

- [`src/retail_ingestion/__init__.py`](../week1/retail-data-platform/src/retail_ingestion/__init__.py)
- [`pyproject.toml`](../week1/retail-data-platform/pyproject.toml)

### 3. Percorsi con `pathlib`

`Path` costruisce percorsi portabili senza concatenare separatori Windows o
Linux. `get_data_file()` risale dalla posizione del modulo alla root del
progetto e aggiunge `data/<filename>`.

```python
project_root = Path(__file__).parent.parent.parent
file_path = project_root / "data" / filename
```

Un percorso relativo alla directory corrente dipende da dove viene avviato il
processo; un percorso basato su `__file__` dipende invece dalla posizione del
modulo.

File correlati:

- [`paths.py`](../week1/retail-data-platform/src/retail_ingestion/paths.py)
- [`test_paths.py`](../week1/retail-data-platform/test/test_paths.py)

### 4. CSV e JSON

`csv.DictReader` restituisce una riga alla volta come dizionario. I valori CSV
restano stringhe e devono essere convertiti esplicitamente.

`json.load()` deserializza un file JSON conservando i tipi rappresentati dal
formato: numeri, stringhe, booleani, liste, oggetti e `null` come `None`.

Sono disponibili due strategie CSV:

- `read_sales()` materializza tutte le righe in una lista;
- `iter_sales()` usa `yield` e produce una riga alla volta.

File correlati:

- [`csv_reader.py`](../week1/retail-data-platform/src/retail_ingestion/csv_reader.py)
- [`json_reader.py`](../week1/retail-data-platform/src/retail_ingestion/json_reader.py)
- [`sales.csv`](../week1/retail-data-platform/data/sales.csv)
- [`orders.json`](../week1/retail-data-platform/data/orders.json)

### 5. Date e orari

`datetime.fromisoformat()` converte una stringa ISO in `datetime`. La
conversione separa il dato testuale grezzo dal valore temporale sul quale si
possono fare confronti e calcoli.

`parse_datetime()` traduce il `ValueError` tecnico in
`InvalidDatetimeError`, errore specifico del dominio applicativo.

File correlati:

- [`validation.py`](../week1/retail-data-platform/src/retail_ingestion/validation.py)
- [`test_validation.py`](../week1/retail-data-platform/test/test_validation.py)

### 6. Eccezioni

Si intercettano solo eccezioni previste. `raise ... from error` conserva la
causa originale:

```python
try:
    return datetime.fromisoformat(value)
except ValueError as error:
    raise InvalidDatetimeError(...) from error
```

Distinzione adottata:

- errore di formato previsto: diventa un motivo di scarto;
- configurazione invalida: interrompe l'avvio;
- errore tecnico transitorio: puo richiedere retry limitati;
- errore inatteso di programmazione: deve propagarsi e fallire il batch.

### 7. Logging

Il logging registra livello, contesto e messaggio. Livelli usati o discussi:

- `INFO`: avanzamento normale;
- `WARNING`: record scartato con batch ancora in esecuzione;
- `ERROR`: operazione fallita;
- `EXCEPTION`: errore con traceback dentro un blocco `except`.

Il validator non registra errori: il log appartiene al punto in cui la pipeline
decide la politica da applicare, evitando messaggi duplicati.

File correlato:

- [`run.py`](../week1/retail-data-platform/src/retail_ingestion/run.py)

### 8. Type hint e `TypedDict`

I type hint descrivono il contratto ma non validano automaticamente a runtime.
Esempi:

```python
def is_present(value: str | None) -> bool:
    ...

def read_sales(path: Path) -> list[dict[str, str]]:
    ...
```

`Order` e un `TypedDict`: descrive le chiavi e i valori attesi di un normale
dizionario JSON senza creare una nuova classe runtime.

File correlato:

- [`json_reader.py`](../week1/retail-data-platform/src/retail_ingestion/json_reader.py)

### 9. Connessioni database

Il progetto usa SQLite dalla standard library. `connect_database()` restituisce
una connessione; chi la riceve deve chiuderla.

`Path(":memory:")` crea un database temporaneo in memoria utile nei test.

File correlati:

- [`database.py`](../week1/retail-data-platform/src/retail_ingestion/database.py)
- [`test_database.py`](../week1/retail-data-platform/test/test_database.py)

### 10. Generatori

Una funzione che contiene `yield` restituisce un generatore. `yield` consegna un
valore, sospende la funzione e conserva lo stato fino alla richiesta successiva.

`iter_sales()` mantiene aperto il file mentre il generatore viene consumato e lo
chiude quando il ciclo termina o il generatore viene chiuso.

Un generatore evita di materializzare tutto il CSV, ma altre strutture, come un
set di tutti gli ID, possono comunque crescere linearmente con il dataset.

File correlato:

- [`csv_reader.py`](../week1/retail-data-platform/src/retail_ingestion/csv_reader.py)

### 11. Context manager

Un context manager gestisce acquisizione e rilascio di una risorsa:

```text
chiamante -> open_database()
chiamato  -> apre la connessione
chiamato  -> yield connection e si sospende
chiamante -> usa la connessione nel blocco with
chiamato  -> riprende ed esegue finally/close
```

`@contextmanager` trasforma il generatore in un oggetto usabile con `with`.
`finally` garantisce la chiusura anche se il chiamante solleva un errore.

File correlato:

- [`database.py`](../week1/retail-data-platform/src/retail_ingestion/database.py)

### 12. Struttura del progetto

`pyproject.toml` definisce build system, metadati, versione minima di Python e
dipendenze opzionali per i test. L'installazione editable collega il package
nella virtual environment al codice sotto `src`.

File correlato:

- [`pyproject.toml`](../week1/retail-data-platform/pyproject.toml)

## Week 2: produzione e test

### 1. Fondamenti pytest

Pytest scopre file e funzioni con prefisso `test_`. I test sono normali funzioni
che usano `assert`. `python -m pytest` esegue pytest con l'interprete Python
attivo, riducendo il rischio di usare un eseguibile installato altrove.

File correlato:

- [`test_validation_pytest.py`](../week1/retail-data-platform/test/test_validation_pytest.py)

### 2. Arrange, Act, Assert

Ogni test viene pensato in tre fasi:

1. Arrange: prepara input e dipendenze;
2. Act: esegue il comportamento;
3. Assert: verifica un risultato osservabile.

Separare scenari indipendenti rende immediata l'identificazione del fallimento.

### 3. Fixture

Le fixture preparano dati o risorse riutilizzabili. Pytest associa il nome del
parametro del test alla fixture omonima.

`tmp_path` crea una directory temporanea distinta per ogni test. Una fixture
personalizzata prepara `sales.csv` senza dipendere dai dati reali del progetto.

`conftest.py` viene scoperto automaticamente da pytest e serve a condividere
fixture tra piu file di test. Non va importato manualmente.

File correlato:

- [`test_csv_reader_pytest.py`](../week1/retail-data-platform/test/test_csv_reader_pytest.py)

### 4. Test parametrizzati

`@pytest.mark.parametrize` esegue lo stesso comportamento con piu combinazioni
di input e risultato atteso. Ogni combinazione e un caso indipendente.

Regola pratica:

- stesso flusso, dati diversi: parametrizzazione;
- setup condiviso: fixture;
- flussi o responsabilita diverse: test separati.

File correlati:

- [`test_validation_pytest.py`](../week1/retail-data-platform/test/test_validation_pytest.py)
- [`test_config_pytest.py`](../week1/retail-data-platform/test/test_config_pytest.py)

### 5. Separazione delle responsabilita

La pipeline segue una separazione simile a Extract, Validate, Load:

- reader: legge i record;
- validator: restituisce validita e motivazioni;
- coordinator: applica la politica;
- loader: persiste i record accettati;
- reject writer: conserva gli scarti.

Nel progetto loader e reject writer non sono ancora implementati.

La funzione `validate_sale()` non apre file, non scrive log e non decide se
interrompere il batch. Raccoglie tutti gli errori del record.

### 6. Configurazione e variabili d'ambiente

Le variabili d'ambiente sono stringhe e devono essere convertite e validate.
`RETAIL_REJECT_LIMIT` usa `10` solo quando la variabile e assente. Un valore
presente ma invalido causa `InvalidConfigurationError`.

`monkeypatch` modifica temporaneamente l'ambiente nel test e ripristina lo stato
originale al termine.

File correlati:

- [`config.py`](../week1/retail-data-platform/src/retail_ingestion/config.py)
- [`test_config_pytest.py`](../week1/retail-data-platform/test/test_config_pytest.py)

### 7. Strategie di validazione

Livelli discussi:

- struttura: colonne obbligatorie del file;
- campo: presenza, formato, range e nullabilita;
- record: coerenza tra campi;
- dataset: duplicati, conteggi e percentuale di scarti;
- referenziale: corrispondenza con entita esistenti.

`validate_sale()` controlla:

- `sale_id` presente;
- `sale_date` presente e ISO-convertibile;
- `amount` presente e convertibile con `Decimal`;
- `amount` finito e maggiore di zero.

`Decimal("NaN")` e `Decimal("Infinity")` sono rappresentabili, ma vengono
rifiutati dalle regole di dominio.

File correlati:

- [`validation.py`](../week1/retail-data-platform/src/retail_ingestion/validation.py)
- [`test_validation_pytest.py`](../week1/retail-data-platform/test/test_validation_pytest.py)

### 8. Strategie di errore nei batch

Politica discussa:

| Evento | Azione |
|---|---|
| Record malformato | Scarta, traccia e continua |
| Colonna obbligatoria assente | Interrompi il batch |
| Database temporaneamente bloccato | Retry limitato, poi interrompi |
| Configurazione invalida | Interrompi prima del processing |
| Duplicato | Applica politica esplicita e traccia |
| Impossibile scrivere gli scarti | Interrompi per evitare perdita silenziosa |
| Bug inatteso | Fallisci e conserva il traceback |

`BatchSummary` e una dataclass che conserva stato, conteggi, motivazioni aggregate
e timestamp del batch. `field(default_factory=dict)` crea un dizionario distinto
per ogni istanza.

File correlati:

- [`models.py`](../week1/retail-data-platform/src/retail_ingestion/models.py)
- [`pipeline.py`](../week1/retail-data-platform/src/retail_ingestion/pipeline.py)
- [`test_models.py`](../week1/retail-data-platform/test/test_models.py)
- [`test_pipeline_pytest.py`](../week1/retail-data-platform/test/test_pipeline_pytest.py)

### 9. Introduzione all'idempotenza

Un'operazione idempotente produce lo stesso stato finale se viene ripetuta.
`process_sales()` usa `seen_sale_ids: set[str]` per rifiutare ID gia accettati
nella stessa esecuzione.

Politica adottata:

- un record invalido non registra il suo ID nel set;
- una successiva versione valida dello stesso ID puo essere accettata;
- dopo l'accettazione, ulteriori occorrenze vengono scartate come duplicate.

Il set offre ricerca media `O(1)` ma usa memoria `O(n)` rispetto agli ID distinti.
Non protegge tra riavvii del processo. La garanzia persistente deve essere nel
database, per esempio con `PRIMARY KEY (sale_id)` oppure
`UNIQUE (source_system, sale_id)` se l'ID non e globale.

File correlati:

- [`pipeline.py`](../week1/retail-data-platform/src/retail_ingestion/pipeline.py)
- [`test_pipeline_pytest.py`](../week1/retail-data-platform/test/test_pipeline_pytest.py)

## Riferimento dei moduli

### `config.py`

- `InvalidConfigurationError`: errore di configurazione applicativo;
- `check_reject_limit()`: rifiuta limiti negativi;
- `get_reject_limit()`: legge, converte e valida `RETAIL_REJECT_LIMIT`.

### `csv_reader.py`

- `read_sales()`: lettura eager in una lista;
- `iter_sales()`: lettura lazy tramite generatore.

### `database.py`

- `connect_database()`: apre una connessione SQLite;
- `open_database()`: context manager che chiude sempre la connessione.

### `json_reader.py`

- `Order`: schema statico con `TypedDict`;
- `read_orders()`: deserializza una lista di ordini JSON.

### `models.py`

- `BatchSummary`: stato e metriche aggregate del batch.

Campi principali:

- `batch_id` e `started_at` obbligatori;
- `status` inizialmente `running`;
- `records_read`, `records_loaded`, `records_rejected` inizialmente zero;
- `rejection_reasons`: motivo -> numero di occorrenze;
- `finished_at`: `None` finche il batch non termina.

### `paths.py`

- `get_data_file()`: costruisce il percorso di un file sotto `data`.

### `pipeline.py`

- `record_rejection()`: incrementa record scartati e motivazioni aggregate;
- `process_sales()`: valida, conta e deduplica vendite.

### `validation.py`

- `InvalidDatetimeError` e `InvalidAmountError`: errori di dominio;
- `is_present()`: rifiuta `None`, stringa vuota e soli spazi;
- `parse_datetime()`: converte ISO string in `datetime`;
- `parse_amount()`: converte stringa in `Decimal`;
- `validate_sale()`: applica le regole al singolo record.

### `run.py`

Esempio minimale di logging ed exception handling. Non e ancora l'entry point della
pipeline completa.

## Strategia di test

La suite contiene test `unittest` originari della Week 1 e test pytest introdotti
nella Week 2. Pytest raccoglie entrambi.

Tecniche presenti:

- test unitari di funzioni pure;
- Arrange, Act, Assert;
- fixture integrate `tmp_path` e `monkeypatch`;
- fixture personalizzate;
- parametrizzazione;
- database SQLite in memoria;
- verifica del rilascio delle risorse;
- TDD Red, Green, Refactor;
- verifica dell'identita con `result is summary`;
- test su record validi, malformati e duplicati.

File di test:

- [`test_config_pytest.py`](../week1/retail-data-platform/test/test_config_pytest.py)
- [`test_csv_reader_pytest.py`](../week1/retail-data-platform/test/test_csv_reader_pytest.py)
- [`test_database.py`](../week1/retail-data-platform/test/test_database.py)
- [`test_models.py`](../week1/retail-data-platform/test/test_models.py)
- [`test_paths.py`](../week1/retail-data-platform/test/test_paths.py)
- [`test_pipeline_pytest.py`](../week1/retail-data-platform/test/test_pipeline_pytest.py)
- [`test_readers.py`](../week1/retail-data-platform/test/test_readers.py)
- [`test_validation.py`](../week1/retail-data-platform/test/test_validation.py)
- [`test_validation_pytest.py`](../week1/retail-data-platform/test/test_validation_pytest.py)

Il suffisso `_pytest` documenta la migrazione didattica da `unittest`; in futuro i
test duplicati potranno essere consolidati in una sola convenzione pytest.

## Esecuzione del progetto

Dalla root del repository:

```powershell
.\.venv\Scripts\Activate.ps1
cd .\week1\retail-data-platform
python -m pip install -e ".[test]"
python -m pytest -v
```

Test mirati:

```powershell
python -m pytest test/test_validation_pytest.py -v
python -m pytest test/test_pipeline_pytest.py -v
```

Verifica import:

```powershell
python -c "import retail_ingestion; print(retail_ingestion.__file__)"
```

Esempio logging:

```powershell
python -m retail_ingestion.run
```

## Limiti attuali e prossimi passi

- `process_sales()` aggiorna `records_loaded`, ma non persiste ancora le vendite;
- gli scarti sono aggregati nel riepilogo, ma i record completi non sono ancora
  scritti in quarantena;
- `status` e `finished_at` non vengono ancora aggiornati dal coordinatore;
- `RETAIL_REJECT_LIMIT` e validato ma non ancora applicato alla pipeline;
- la deduplicazione con set vale solo nella singola esecuzione;
- non esiste ancora una transazione di caricamento completa;
- `run.py` non orchestra ancora reader, pipeline, loader e logging;
- la suite contiene ancora test duplicati tra `unittest` e pytest;
- non e configurata una misura di coverage.

Questi limiti sono intenzionali: delimitano gli esercizi futuri senza nascondere
il comportamento reale del progetto.

## Riferimenti ufficiali

- Python `venv`: https://docs.python.org/3/library/venv.html
- Python `pathlib`: https://docs.python.org/3/library/pathlib.html
- Python `csv`: https://docs.python.org/3/library/csv.html
- Python `json`: https://docs.python.org/3/library/json.html
- Python `datetime`: https://docs.python.org/3/library/datetime.html
- Python `logging`: https://docs.python.org/3/library/logging.html
- Python type hints: https://docs.python.org/3/library/typing.html
- Python `sqlite3`: https://docs.python.org/3/library/sqlite3.html
- Python `contextlib`: https://docs.python.org/3/library/contextlib.html
- Python `dataclasses`: https://docs.python.org/3/library/dataclasses.html
- Python `decimal`: https://docs.python.org/3/library/decimal.html
- Python packaging: https://packaging.python.org/
- pytest documentation: https://docs.pytest.org/
