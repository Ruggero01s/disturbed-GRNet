# UP Utils - Unified Planning Utilities

## Descrizione

Modulo di utilità per la gestione di problemi PDDL e Unified Planning. Fornisce un'interfaccia semplificata per operazioni comuni come parsing, grounding, planning, validazione e simulazione.

## Categorie di Funzioni

### 🗜️ Gestione File Compressi

#### `open_compressed_file(file, output_dir)`
Estrae file compressi ZIP o TAR.BZ2.

```python
open_compressed_file('problem.zip', '/tmp/extracted')
```

---

### 📖 Lettura Dati da File

#### `get_observations(problem_dir, pereira=False)`
Legge le osservazioni dal file `obs.dat`.

```python
observations = get_observations('/path/to/problem')
# ['unstack b a', 'putdown b', 'pickup a']
```

#### `get_goals(problem_dir, pereira)`
Legge le ipotesi di goal dal file `hyps.dat`.

```python
goals = get_goals('/path/to/problem', pereira=False)
# [['on a b', 'on b c'], ['ontable a', 'ontable b']]
```

#### `get_real_goal(problem_dir, pereira)`
Legge il goal reale dal file `real_hyp.dat`.

#### `get_template(problem_dir)`
Legge il template PDDL completo.

#### `get_objects(problem_dir)`
Estrae la lista semplice degli oggetti.

#### `get_objects_with_types(problem_dir)`
Estrae oggetti con i loro tipi.

```python
objects = get_objects_with_types('/path/to/problem')
# [('a', 'block'), ('b', 'block'), ('truck1', 'truck')]
```

#### `get_init_state(problem_dir)`
Estrae lo stato iniziale dal template.

---

### 🔢 Encoding e Decoding

#### `encode_obs(observations, dizionario)`
Converte osservazioni testuali in IDs numerici.

```python
dizionario = {'PICKUP A': 0, 'PUTDOWN A': 1}
encoded = encode_obs(['pickup a', 'putdown a'], dizionario)
# [0, 1]
```

#### `decode_obs(encoded_obs, dizionario)`
Operazione inversa: da IDs a testo.

#### `encode_goal(goal, dizionario)`
Converte goal testuali in IDs numerici.

#### `decode_goal(encoded_goal, dizionario)`
Operazione inversa per goal.

#### `get_extended_goal(goal, dizionario)`
Crea rappresentazione one-hot encoding del goal.

```python
extended = get_extended_goal([0, 2], dizionario)
# [1, 0, 1]  # Predicati 0 e 2 presenti
```

---

### 📝 Creazione Problemi PDDL

#### `create_problem(problem_dir, pereira=False)`
Crea `problem.pddl` usando il goal reale.

#### `create_real_problem(problem_dir, problem_name, pereira=False)`
Crea un problema con nome personalizzato.

#### `create_problem_with_goal(problem_dir, goal, pereira=False)`
Crea problema con goal specificato.

#### `create_problem_with_goal_and_name(problem_dir, goal, problem_name, pereira=False)`
Massima flessibilità: goal e nome personalizzati.

#### `compose_new_problem(problem_dir, new_init, new_goal, pereira=False)`
Crea problema con init e goal completamente personalizzati.

```python
compose_new_problem(
    '/path/to/problem',
    '(ontable a)\n(ontable b)',
    '(on a b)'
)
```

#### `new_observation(problem_dir, filename, new_obs)`
Scrive nuove osservazioni in un file.

---

### ⚙️ Grounding e Azioni

#### `get_grounded_actions(problem_dir, grounder, pereira=False)`
Ottiene tutte le azioni groundate per un problema.

```python
grounder = Compiler(name="fast-downward-reachability-grounder")
actions = get_grounded_actions('/path/to/problem', grounder)
# ['pickup a', 'pickup b', 'putdown a', ...]
```

**Caratteristiche:**
- Filtra azioni con parametri duplicati
- Gestisce azioni composte (es. "take image" → "take_image")
- Normalizza nomi per consistency

---

### 🎯 Planning e Validazione

#### `compute_plan(problem_dir, problem_name)`
Computa un piano satisficing usando planner oneshot.

```python
plan = compute_plan('/path/to/problem', 'problem.pddl')
```

#### `compute_anytime_optimal_plan(problem_dir, problem_name)`
Cerca piano ottimale con planner anytime.

```python
optimal_plan = compute_anytime_optimal_plan('/path/to/problem', 'problem.pddl')
```

#### `compute_anytime_suboptimal_plan(problem_dir, problem_name)`
Computa piano con timeout di 30s, accetta subottimali.

#### `compute_optimum_or_anytime_plan(problem_dir, problem_name, primo_planner, planner)`
Tenta con anytime, fallback su planner di backup.

#### `plan_validation(problem_dir, plan_name, problem_name)`
Valida un piano usando il validatore "tamer".

```python
is_valid = plan_validation('/path/to/problem', 'plan.txt', 'problem.pddl')
# True o False
```

---

### 🔄 Simulazione Stati

#### `get_states(problem_dir, plan)`
Simula piano e ottiene tutti gli stati intermedi.

```python
states = get_states('/path/to/problem', plan)
# [stato_0, stato_1, ..., stato_finale]
```

#### `get_states_with_name(problem_dir, plan, problem_name)`
Come sopra ma con nome problema personalizzato.

#### `extractValues(state)`
Estrae ricorsivamente tutti i valori da uno stato.

#### `get_new_state(state)`
Converte stato in formato PDDL testuale.

```python
pddl_state = get_new_state(state)
# "(ONTABLE A)\n(ON B A)\n(CLEAR B)\n..."
```

---

### 🛠️ Utilità Varie

#### `kill_fast_downward_processes()`
Termina processi Fast Downward residui.

```python
kill_fast_downward_processes()
```

#### `pddl_style_strings_to_plan(action_strings, problem)`
Converte stringhe PDDL in piano sequenziale.

```python
actions = ["(pickup a)", "(stack a b)"]
plan = pddl_style_strings_to_plan(actions, problem)
```

---

## Configurazione

Il modulo configura automaticamente:
- **Random seed**: 42 (per riproducibilità)
- **Unified Planning credits**: Disabilitati

## Dipendenze

- `unified_planning`: Framework principale
- `psutil`: Gestione processi
- `numpy`: Operazioni numeriche
- `zipfile`, `tarfile`: Gestione archivi

## Note sul Formato Pereira

Molte funzioni accettano un flag `pereira` che indica se i dati sono in formato Pereira:
- Usa uppercase per le azioni
- Usa virgole come separatori
- Formattazione leggermente diversa

```python
# Formato standard
goals = get_goals('/path', pereira=False)

# Formato Pereira
goals = get_goals('/path', pereira=True)
```

## Best Practices

1. **Usa sempre path assoluti** per evitare problemi
2. **Chiama `create_problem()`** prima del grounding
3. **Gestisci i timeout** per planning su problemi difficili
4. **Valida sempre i piani** prima dell'uso in produzione
5. **Pulisci i processi** dopo l'uso con `kill_fast_downward_processes()`

## Esempi Completi

### Pipeline Completa

```python
from up_utils import *
from unified_planning.shortcuts import Compiler

# 1. Setup
problem_dir = '/path/to/problem'
grounder = Compiler(name="fast-downward-reachability-grounder")

# 2. Leggi dati
observations = get_observations(problem_dir)
real_goal = get_real_goal(problem_dir, pereira=False)
init_state = get_init_state(problem_dir)

# 3. Grounding
actions = get_grounded_actions(problem_dir, grounder)

# 4. Planning
plan = compute_plan(problem_dir, 'problem.pddl')

# 5. Validazione
is_valid = plan_validation(problem_dir, 'plan.txt', 'problem.pddl')

# 6. Simulazione
states = get_states(problem_dir, plan)

# 7. Cleanup
kill_fast_downward_processes()
```

### Encoding/Decoding

```python
# Carica dizionari
with open('dizionario.pkl', 'rb') as f:
    dizionario = pickle.load(f)

# Encode
encoded_obs = encode_obs(observations, dizionario)
encoded_goal = encode_goal(real_goal, dizionario)

# One-hot encoding
extended_goal = get_extended_goal(encoded_goal, dizionario)

# Decode
decoded_obs = decode_obs(encoded_obs, dizionario)
```

## Troubleshooting

### Problema: Processi Fast Downward rimasti appesi
**Soluzione**: Chiama `kill_fast_downward_processes()`

### Problema: Timeout durante planning
**Soluzione**: Usa `compute_anytime_suboptimal_plan()` o aumenta il timeout

### Problema: Azioni con parametri duplicati
**Soluzione**: `get_grounded_actions()` filtra automaticamente queste azioni

### Problema: Formato file non compatibile
**Soluzione**: Verifica il flag `pereira` e il formato dei file di input
