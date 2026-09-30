# Data Engineering Learning Project

Repository didattico per consolidare Python moderno e fondamenti di Data
Engineering attraverso un unico progetto progressivo: **Retail Data Platform**.

Il progetto e iniziato durante la Week 1 ed e stato esteso durante la Week 2.
La directory storica resta `week1/retail-data-platform`, ma il suo contenuto
rappresenta il lavoro cumulativo di entrambe le settimane.

## Roadmap del percorso

| Week | Focus | Obiettivo pratico |
|---|---|---|
| 1 | Python fundamentals | venv, moduli, pathlib, CSV/JSON, datetime, exceptions, logging, type hints, DB connection, generatori, context manager, struttura progetto |
| 2 | Python production-oriented + testing | pytest, fixture, parametrizzazione, separation of concerns, config, validation, error strategy, idempotenza |
| 3 | PostgreSQL + Data Modeling | schema, fact/dimension, star schema, surrogate key, constraints, index, query plan |
| 4 | ETL/ELT + incremental loading | staging, upsert, merge, deduplica, incremental load, rerun sicuri |
| 5 | dbt | models, sources, refs, tests, lineage, incremental models |
| 6 | Docker | Dockerfile, image, container, volume, network, Compose |
| 7 | Airflow | DAG, task, retry, schedule, catchup, backfill, failure handling |
| 8 | Git + CI/CD | branching, PR, GitHub Actions, test automatici |
| 9 | Cloud fundamentals | object storage, managed DB, IAM, logging, secrets |
| 10 | Data Warehouse / Lake / Parquet | OLTP vs OLAP, warehouse, lake, lakehouse, partitioning, columnar storage |
| 11 | Spark + Kafka | distributed batch, lazy eval, partition, topic, consumer, offset |
| 12 | Portfolio + interview prep | README, architettura, trade-off, failure scenario, system design |

**Stato attuale:** Week 1 e Week 2 completate. Week 3 WIP

## Argomenti coperti

### Week 1

- ambiente virtuale e dipendenze;
- moduli, package e layout `src`;
- percorsi portabili con `pathlib`;
- lettura CSV e JSON;
- date e orari con `datetime`;
- eccezioni personalizzate e exception chaining;
- logging;
- type hint e `TypedDict`;
- connessioni SQLite;
- generatori;
- context manager;
- packaging con `pyproject.toml`.

### Week 2

- fondamenti di pytest;
- Arrange, Act, Assert;
- fixture integrate e personalizzate;
- test parametrizzati;
- separazione delle responsabilita nella pipeline;
- configurazione tramite variabili d'ambiente;
- validazione strutturale e di dominio;
- strategie di gestione degli errori batch;
- riepiloghi batch con `dataclass`;
- deduplicazione locale e introduzione all'idempotenza.

## Struttura

```text
DataEngineer/
|-- README.md
|-- docs/
|   `-- HANDBOOK.md
|-- week1/
|   `-- retail-data-platform/
|       |-- data/
|       |-- src/retail_ingestion/
|       |-- test/
|       `-- pyproject.toml
`-- .venv/
```

## Avvio rapido

Requisito: Python 3.12 o successivo.

```powershell
cd C:\Users\rubio\Desktop\DataEngineer
py -m venv .venv
.\.venv\Scripts\Activate.ps1
cd .\week1\retail-data-platform
python -m pip install -e ".[test]"
python -m pytest -v
```

## Flusso corrente

```text
CSV/JSON -> reader -> validator -> pipeline -> BatchSummary
```

La pipeline legge vendite, valida i campi, aggrega i motivi di scarto e rileva
duplicati nel singolo batch. Il caricamento persistente, la quarantena dei
record e l'idempotenza garantita dal database sono sviluppi successivi.

## Documentazione

Il riferimento tecnico completo, con concetti, decisioni progettuali e mappa
dei file, si trova in [`docs/HANDBOOK.md`](docs/HANDBOOK.md).

Questo README viene aggiornato al completamento di ogni settimana; il handbook
viene esteso quando vengono introdotti nuovi concetti o cambiano le decisioni
architetturali.
