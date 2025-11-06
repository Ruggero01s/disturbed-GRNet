# Adversarial Plan Generator

## Descrizione

Questo modulo genera test dataset per noisy goal recognition, applicando attacchi di vario tipo ai piani originali.

## Funzionalità Principali

### 1. Attacco Avversariale
La funzione `adversarial_plan()` modifica casualmente le azioni osservate in un piano sostituendole con azioni valide scelte random. Questo simula un avversario che cerca di ingannare un sistema di goal recognition.

### 2. Processamento Multi-Dominio
Il sistema processa automaticamente diversi domini PDDL:
- Blocksworld
- Logistics
- Driverlog
- Satellite
- Depots
- Zenotravel

### 3. Configurazioni Multiple
Per ogni dominio, vengono generate diverse configurazioni con:
- Percentuali variabili di "buchi" nei piani (default: 100%)
- Percentuali variabili di attacco (default: 10%, 20%, 30%)

## Struttura del Codice

```
main.py
├── adversarial_plan()          # Applica l'attacco a una sequenza di azioni
├── load_dictionary()           # Carica dizionari serializzati
├── process_single_plan()       # Processa un singolo piano
├── process_domain()            # Processa un intero dominio
└── main()                      # Funzione principale
```

## Output

Il sistema genera:

1. **File di soluzioni**: `{attack_perc}_mask.json`
   - Contiene i piani modificati con le rispettive maschere
   - Una maschera per ogni azione (0=originale, 1=modificata)

2. **File di analisi**: `atk_analysis.json`
   - Statistiche sugli attacchi effettuati
   - Istogrammi della distribuzione degli attacchi
   - Percentuali effettive di attacco

### Struttura Dati Output

```json
{
  "problem_name.zip": {
    "init_state": [encoded_initial_state],
    "obs": [encoded_observations],
    "real_goal": [encoded_real_goal],
    "mask": [0, 1, 0, 0, 1, ...],
    "goals": [[encoded_goal_1], [encoded_goal_2], ...]
  }
}
```

## Configurazione

Le costanti principali possono essere modificate nella funzione `main()`:

## Uso

```bash
python main.py
```

## Note Tecniche

- **Seed Random**: Impostato a 42 per garantire riproducibilità
- **Maschera**: 0 = azione originale, 1 = azione modificata
- **Formato**: Supporta sia file .zip che .tar.bz2
- **Pulizia**: La directory temporanea viene pulita dopo ogni piano

## Gestione Errori

Il sistema include gestione degli errori per:
- File corrotti o non validi
- Problemi di I/O
- Errori durante il grounding delle azioni

Gli errori vengono loggati ma non interrompono l'elaborazione degli altri piani.
