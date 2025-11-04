"""
Modulo di utilità per la gestione di problemi PDDL e Unified Planning.

Questo modulo fornisce funzioni per:
- Apertura e gestione di file compressi
- Lettura e parsing di osservazioni, goal e stati
- Encoding/decoding di osservazioni e goal
- Creazione e manipolazione di problemi PDDL
- Grounding di azioni
- Computazione e validazione di piani
- Simulazione di stati
"""

import random
import json
from unified_planning.shortcuts import *
from unified_planning.engines import PlanGenerationResultStatus, ValidationResultStatus, CompilationKind
from unified_planning.io import PDDLReader
import unified_planning as up
from unified_planning.plans import SequentialPlan, ActionInstance
import psutil
import os
import zipfile
import tarfile
import numpy as np

# Configurazione ambiente
random.seed(42)  # Imposta seed per riproducibilità
up.shortcuts.get_environment().credits_stream = None  # Disabilita output dei credits


# ============================================================================
# GESTIONE FILE COMPRESSI
# ============================================================================
# ============================================================================
# GESTIONE FILE COMPRESSI
# ============================================================================

def open_compressed_file(file, output_dir):
    """
    Estrae un file compresso (ZIP o TAR.BZ2) nella directory specificata.
    
    Args:
        file: Percorso del file compresso da estrarre
        output_dir: Directory di destinazione per l'estrazione
    
    Note:
        Supporta formati .zip e .tar.bz2
        Stampa un messaggio di errore per formati non supportati
    """
    if file.endswith('.zip'):
        # Estrae archivio ZIP
        with zipfile.ZipFile(file, 'r') as z:
            z.extractall(output_dir)
    elif file.endswith('.tar.bz2'):
        # Estrae archivio TAR.BZ2
        with tarfile.open(file, 'r:bz2') as t:
            t.extractall(output_dir)
    else:
        print('Unsupported file type')


# ============================================================================
# LETTURA DATI DA FILE
# ============================================================================
    
def get_observations(problem_dir, pereira=False):
    """
    Legge le osservazioni (azioni osservate) dal file obs.dat.
    
    Args:
        problem_dir: Directory contenente il file obs.dat
        pereira: Flag per dataset Pereira (attualmente non utilizzato)
    
    Returns:
        Lista di stringhe contenenti le osservazioni ripulite da parentesi
    
    Example:
        >>> get_observations('/path/to/problem')
        ['unstack b a', 'putdown b', 'pickup a']
    """
    observations = []
    with open(problem_dir + '/obs.dat', 'r') as f:
        for line in f:
            # Rimuove parentesi e whitespace da ogni osservazione
            observations.append(line.strip().replace('(', '').replace(')', ''))
    return observations

def get_goals(problem_dir: str, pereira: bool):
    """
    Legge le ipotesi di goal dal file hyps.dat.
    
    Args:
        problem_dir: Directory contenente il file hyps.dat
        pereira: Se True, usa formato Pereira (uppercase con virgole)
                 Se False, usa formato standard (con virgole e spazi)
    
    Returns:
        Lista di liste, dove ogni lista interna rappresenta un goal ipotizzato
    
    Example:
        >>> get_goals('/path/to/problem', pereira=False)
        [['on a b', 'on b c'], ['ontable a', 'ontable b']]
    """
    goals = []
    with open(problem_dir + '/hyps.dat', 'r') as f:
        for line in f:
            # Rimuove parentesi e whitespace
            cleaned_line = line.strip().replace('(', '').replace(')', '')
            
            if pereira:
                # Formato Pereira: converte in uppercase e split per virgola
                goals.append(cleaned_line.upper().split(','))
            else:
                # Formato standard: split per virgola e spazio
                goals.append(cleaned_line.split(', '))
    return goals


def get_real_goal(problem_dir: str, pereira: bool):
    """
    Legge il goal reale dal file real_hyp.dat.
    
    Args:
        problem_dir: Directory contenente il file real_hyp.dat
        pereira: Se True, usa formato Pereira (uppercase con virgole)
                 Se False, usa formato standard
    
    Returns:
        Lista di predicati che compongono il goal reale
    
    Example:
        >>> get_real_goal('/path/to/problem', pereira=False)
        ['on a b', 'on b c', 'ontable c']
    """
    with open(problem_dir + '/real_hyp.dat', 'r') as f:
        # Legge la prima linea (il file contiene solo il goal reale)
        line = f.readline().strip().replace('(', '').replace(')', '')
        
        if pereira:
            return line.upper().split(',')
        else:
            return line.split(', ')
        

def get_template(problem_dir: str):
    """
    Legge il file template PDDL che contiene la struttura del problema.
    
    Args:
        problem_dir: Directory contenente template.pddl
    
    Returns:
        Stringa contenente l'intero contenuto del template
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        return f.read()
    

def get_objects(problem_dir: str):
    """
    Estrae la lista degli oggetti dal template PDDL (formato semplice).
    
    Args:
        problem_dir: Directory contenente template.pddl
    
    Returns:
        Lista di nomi di oggetti (senza tipi)
    
    Note:
        Questa funzione assume una dichiarazione semplice degli oggetti.
        Per oggetti con tipi, usa get_objects_with_types()
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        # Estrae la sezione (:objects ...) e split per spazi
        content = f.read()
        objects_section = content.split('(:objects')[1].split(')')[0].strip()
        return objects_section.split(' ')


def get_objects_with_types(problem_dir: str):
    """
    Estrae oggetti e i loro tipi dal template PDDL.
    
    Args:
        problem_dir: Directory contenente template.pddl
    
    Returns:
        Lista di tuple (nome_oggetto, tipo_oggetto)
    
    Example:
        >>> get_objects_with_types('/path/to/problem')
        [('a', 'block'), ('b', 'block'), ('truck1', 'truck')]
    
    Note:
        Se un oggetto non ha tipo specificato, usa 'object' come default
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        # Estrae la sezione objects e separa per linee
        content = f.read()
        objects_section = content.split('(:objects')[1].split(')')[0].strip()
        objects_whole = objects_section.split('\n')
    
    objects = []
    for object_line in objects_whole:
        # Rimuove tab e split per ' - ' che separa nomi da tipi
        components = object_line.replace("\t", "").split(' - ')
        
        # Prima parte: nomi degli oggetti (possono essere multipli)
        objects_name = components[0].replace("\t", "").split(' ')
        
        # Seconda parte: tipo (se presente, altrimenti usa 'object')
        object_type = components[1].strip() if len(components) > 1 else "object"
        
        # Crea una tupla per ogni oggetto con il suo tipo
        for name in objects_name:
            objects.append((name, object_type))
    
    return objects


def get_init_state(problem_dir: str):
    """
    Estrae lo stato iniziale dal template PDDL.
    
    Args:
        problem_dir: Directory contenente template.pddl
    
    Returns:
        Lista di predicati che descrivono lo stato iniziale
    
    Example:
        >>> get_init_state('/path/to/problem')
        ['ONTABLE A', 'ONTABLE B', 'CLEAR A', 'CLEAR B', 'HANDEMPTY']
    
    Note:
        I predicati vengono convertiti in uppercase e puliti da parentesi
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        content = f.read()
        # Estrae la sezione tra (:init e (:goal
        init_section = content.split('(:init')[1].split('(:goal')[0]
        
        # Pulisce da tab, parentesi e converte in uppercase
        cleaned = init_section.replace("\t", "").replace("(", "").replace(")", "")
        init_state = cleaned.strip().upper().split('\n')
    
    return init_state


# ============================================================================
# ENCODING E DECODING
# ============================================================================
# ============================================================================
# ENCODING E DECODING
# ============================================================================

def encode_obs(observations: list, dizionario: dict):
    """
    Converte osservazioni testuali in rappresentazione numerica.
    
    Args:
        observations: Lista di osservazioni in formato stringa
        dizionario: Dizionario di mappatura {azione_stringa: id_numerico}
    
    Returns:
        Lista di ID numerici corrispondenti alle osservazioni
    
    Example:
        >>> dizionario = {'PICKUP A': 0, 'PUTDOWN A': 1}
        >>> encode_obs(['pickup a', 'putdown a'], dizionario)
        [0, 1]
    """
    encoded_obs = []
    for obs in observations:
        # Converte in uppercase e cerca nel dizionario
        encoded_obs.append(dizionario[obs.upper()])
    return encoded_obs


def decode_obs(encoded_obs: list, dizionario: dict):
    """
    Converte osservazioni numeriche in formato testuale.
    
    Args:
        encoded_obs: Lista di ID numerici
        dizionario: Dizionario di mappatura {azione_stringa: id_numerico}
    
    Returns:
        Lista di stringhe corrispondenti agli ID
    
    Note:
        Operazione inversa di encode_obs()
    """
    decoded_obs = []
    for obs in encoded_obs:
        # Cerca la chiave corrispondente al valore
        for key, value in dizionario.items():
            if value == obs:
                decoded_obs.append(key)
                break
    return decoded_obs


def encode_goal(goal: list, dizionario: dict):
    """
    Converte un goal testuale in rappresentazione numerica.
    
    Args:
        goal: Lista di predicati che compongono il goal
        dizionario: Dizionario di mappatura {predicato: id_numerico}
    
    Returns:
        Lista di ID numerici corrispondenti ai predicati del goal
    
    Note:
        I predicati non presenti nel dizionario vengono ignorati
    """
    encoded_goal = []
    for g in goal:
        # Salta predicati non presenti nel dizionario
        if g not in dizionario:
            continue
        # Converte in intero per garantire tipo corretto
        encoded_goal.append(int(dizionario[g.strip()]))
    return encoded_goal


def decode_goal(encoded_goal: list, dizionario: dict):
    """
    Converte un goal numerico in formato testuale.
    
    Args:
        encoded_goal: Lista di ID numerici
        dizionario: Dizionario di mappatura {predicato: id_numerico}
    
    Returns:
        Lista di stringhe corrispondenti ai predicati del goal
    
    Note:
        Operazione inversa di encode_goal()
    """
    decoded_goal = []
    for g in encoded_goal:
        # Cerca la chiave corrispondente al valore
        for key, value in dizionario.items():
            if value == g:
                decoded_goal.append(key)
                break
    return decoded_goal


def get_extended_goal(goal: list, dizionario: dict):
    """
    Crea una rappresentazione one-hot encoding del goal.
    
    Args:
        goal: Lista di ID numerici dei predicati del goal
        dizionario: Dizionario completo dei predicati
    
    Returns:
        Lista binaria dove 1 indica presenza del predicato nel goal
    
    Example:
        >>> dizionario = {'ON A B': 0, 'ON B C': 1, 'CLEAR A': 2}
        >>> get_extended_goal([0, 2], dizionario)
        [1, 0, 1]  # ON A B e CLEAR A sono presenti
    """
    # Crea vettore di zeri con lunghezza pari al dizionario
    extended_goal = np.zeros(len(dizionario))
    
    # Imposta a 1 le posizioni corrispondenti ai predicati del goal
    for g in goal:
        extended_goal[g] = 1
    
    return extended_goal.tolist()


# ============================================================================
# CREAZIONE PROBLEMI PDDL
# ============================================================================

def create_real_problem(problem_dir: str, problem_name: str, pereira=False):
    """
    Crea un file problema PDDL usando il goal reale dal file real_hyp.dat.
    
    Args:
        problem_dir: Directory contenente template.pddl e real_hyp.dat
        problem_name: Nome del file problema da creare
        pereira: Flag per dataset Pereira (attualmente non utilizzato)
    
    Note:
        Sostituisce il placeholder <HYPOTHESIS> nel template con il goal reale
    """
    # Legge il template
    with open(problem_dir + '/template.pddl', 'r') as f:
        template = f.read()
    
    # Legge il goal reale e converte virgole in newline per formato PDDL
    with open(problem_dir + '/real_hyp.dat', 'r') as f:
        goal = f.readline().strip().replace(',', '\n')
    
    # Sostituisce il placeholder e salva
    template = template.replace('<HYPOTHESIS>', f'{goal}')
    with open(problem_dir + f'/{problem_name}', 'w') as f:
        f.write(template)


def create_problem(problem_dir, pereira=False):
    """
    Crea un file problem.pddl usando il goal reale.
    
    Args:
        problem_dir: Directory contenente template.pddl e real_hyp.dat
        pereira: Flag per dataset Pereira (attualmente non utilizzato)
    
    Note:
        Versione semplificata di create_real_problem() con nome fisso 'problem.pddl'
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        template = f.read()
    with open(problem_dir + '/real_hyp.dat', 'r') as f:
        goal = f.readline().strip().replace(',', '\n')
    template = template.replace('<HYPOTHESIS>', f'{goal}')
    with open(problem_dir + '/problem.pddl', 'w') as f:
        f.write(template)


def create_problem_with_goal(problem_dir, goal, pereira=False):
    """
    Crea un file problem.pddl con un goal specificato.
    
    Args:
        problem_dir: Directory contenente template.pddl
        goal: Stringa contenente il goal in formato PDDL
        pereira: Flag per dataset Pereira (attualmente non utilizzato)
    
    Note:
        Utile per testare goal alternativi senza modificare real_hyp.dat
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        template = f.read()
    template = template.replace('<HYPOTHESIS>', f'{goal}')
    with open(problem_dir + '/problem.pddl', 'w') as f:
        f.write(template)


def create_problem_with_goal_and_name(problem_dir, goal, problem_name, pereira=False):
    """
    Crea un file problema PDDL con goal e nome specificati.
    
    Args:
        problem_dir: Directory contenente template.pddl
        goal: Stringa contenente il goal in formato PDDL
        problem_name: Nome del file da creare (senza estensione .pddl)
        pereira: Flag per dataset Pereira (attualmente non utilizzato)
    
    Note:
        Versione più flessibile che permette di specificare sia goal che nome
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        template = f.read()
    template = template.replace('<HYPOTHESIS>', f'{goal}')
    with open(problem_dir + f'/{problem_name}.pddl', 'w') as f:
        f.write(template)


def compose_new_problem(problem_dir, new_init, new_goal, pereira=False):
    """
    Compone un nuovo problema PDDL con stato iniziale e goal personalizzati.
    
    Args:
        problem_dir: Directory contenente template.pddl
        new_init: Stringa contenente i predicati dello stato iniziale
        new_goal: Stringa contenente i predicati del goal
        pereira: Se True, converte il template in lowercase
    
    Note:
        Sostituisce completamente la sezione (:init e (:goal del template
        Utile per creare sotto-problemi o problemi modificati
    """
    with open(problem_dir + '/template.pddl', 'r') as f:
        template = f.read()
    
    if pereira:
        template = template.lower().split('(:init')[0] + f'(:init\n{new_init})\n' + "(:goal\n(and\n" + f'{new_goal}\n)\n)\n)'
    else:
        template = template.split('(:init')[0] + f'(:init\n{new_init})\n' + "(:goal\n(and\n" + f'{new_goal}\n)\n)\n)'
    
    with open(problem_dir + '/new_problem.pddl', 'w') as f:
        f.write(template)


def new_observation(problem_dir: str, filename: str, new_obs: str):
    """
    Scrive nuove osservazioni in un file.
    
    Args:
        problem_dir: Directory dove creare il file
        filename: Nome del file da creare
        new_obs: Stringa contenente le osservazioni da scrivere
    
    Note:
        Utile per salvare osservazioni modificate o generate
    """
    with open(os.path.join(problem_dir, filename), 'w') as f:
        f.write(new_obs)


# ============================================================================
# GROUNDING E AZIONI
# ============================================================================
        
def get_grounded_actions(problem_dir, grounder, pereira=False):
    """
    Ottiene la lista di tutte le azioni groundate per un problema.
    
    Args:
        problem_dir: Directory contenente domain.pddl e template.pddl
        grounder: Istanza del compilatore per il grounding
        pereira: Flag per dataset Pereira
    
    Returns:
        Lista di stringhe con i nomi delle azioni groundate filtrate
    
    Note:
        - Crea automaticamente problem.pddl dal template
        - Filtra azioni con parametri duplicati
        - Gestisce azioni composte (es. "take image" -> "take_image")
    
    Example:
        >>> grounder = Compiler(name="fast-downward-reachability-grounder")
        >>> actions = get_grounded_actions('/path/to/problem', grounder)
        >>> print(actions)
        ['pickup a', 'pickup b', 'putdown a', ...]
    """
    # Crea il file problem.pddl dal template
    create_problem(problem_dir, pereira=pereira)
    
    # Legge e parsa il problema PDDL
    reader = PDDLReader()
    problem = reader.parse_problem(
        f'{problem_dir}/domain.pddl', 
        f'{problem_dir}/problem.pddl'
    )

    # Esegue il grounding del problema
    grounder_result = grounder.compile(problem, CompilationKind.GROUNDING)
    ground_problem = grounder_result.problem
    
    # Estrae le azioni groundate e normalizza i nomi
    ground_actions = list(ground_problem.instantaneous_actions)
    ground_actions_names = [a.name.replace("_", " ") for a in ground_actions]
    
    # Filtra le azioni con parti duplicate
    filtered_actions = []
    for action_name in ground_actions_names:
        # Normalizza whitespace
        action_name = action_name.strip()
        
        # Gestisce azioni composte specifiche (es. "take image" -> "take_image")
        # Necessario per alcuni domini come satellite
        if any(phrase in action_name for phrase in ["take image", "turn to", "switch on", "switch off"]):
            action_name = (action_name
                          .replace("take image", "take_image")
                          .replace("turn to", "turn_to")
                          .replace("switch on", "switch_on")
                          .replace("switch off", "switch_off"))
        
        # Divide l'azione in parti (nome + parametri)
        parts = action_name.split(" ")
        
        # Filtra azioni con parametri duplicati (es. "move a a" non è valido)
        if all(parts.count(p.strip()) <= 1 for p in parts):
            filtered_actions.append(action_name)
    
    return filtered_actions


# ============================================================================
# PLANNING E VALIDAZIONE
# ============================================================================

def compute_plan(problem_dir: str, problem_name: str):
    """
    Computa un piano per risolvere un problema PDDL.
    
    Args:
        problem_dir: Directory contenente domain.pddl e il file problema
        problem_name: Nome del file problema (es. 'problem.pddl')
    
    Returns:
        Piano sequenziale se trovato, None altrimenti
    
    Note:
        Usa un planner oneshot (risolve il problema una sola volta)
        Cerca una soluzione satisficing, non necessariamente ottimale
    """
    reader = PDDLReader()
    problem = reader.parse_problem(
        f"{problem_dir}/domain.pddl", 
        f"{problem_dir}/{problem_name}"
    )
    
    # Usa planner oneshot
    planner = OneshotPlanner()
    result = planner.solve(problem)
    
    if result.status == PlanGenerationResultStatus.SOLVED_SATISFICING:
        return result.plan
    else:
        print("No optimal plan found.")
        return None


def compute_anytime_optimal_plan(problem_dir: str, problem_name: str):
    """
    Computa un piano ottimale usando un planner anytime.
    
    Args:
        problem_dir: Directory contenente domain.pddl e il file problema
        problem_name: Nome del file problema
    
    Returns:
        Piano ottimale se trovato, altrimenti il piano più corto trovato
    
    Note:
        Cerca piani progressivamente migliori finché trova l'ottimo
        Se non trova l'ottimo, ritorna il piano più corto tra quelli trovati
    """
    reader = PDDLReader()
    problem = reader.parse_problem(
        f"{problem_dir}/domain.pddl", 
        f"{problem_dir}/{problem_name}"
    )
    
    # Aggiunge metrica di qualità: minimizza lunghezza piano
    problem.add_quality_metric(up.model.metrics.MinimizeSequentialPlanLength())
    
    # Usa planner anytime con garanzia di piani ottimali
    planner = AnytimePlanner(anytime_guarantee="OPTIMAL_PLANS")
    solutions = []
    
    for i, p in enumerate(planner.get_solutions(problem)):
        print(f'Solution {i+1} status: {p.status}')
        if p.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY:
            # Trovato piano ottimale, ritorna immediatamente
            return p.plan
        else:
            # Accumula soluzioni subottimali
            solutions.append(p.plan)
    
    # Se non trovato ottimo, ritorna il piano più corto
    return min(solutions, key=lambda x: len(x.actions)) if solutions else None


def compute_anytime_suboptimal_plan(problem_dir: str, problem_name: str):
    """
    Computa un piano (anche subottimale) con timeout.
    
    Args:
        problem_dir: Directory contenente domain.pddl e il file problema
        problem_name: Nome del file problema
    
    Returns:
        Piano trovato entro il timeout, può essere subottimale
    
    Note:
        Timeout di 30 secondi
        Ritorna il miglior piano trovato entro il tempo limite
    """
    reader = PDDLReader()
    problem = reader.parse_problem(
        f"{problem_dir}/domain.pddl", 
        f"{problem_dir}/{problem_name}"
    )
    
    # Aggiunge metrica di qualità
    problem.add_quality_metric(up.model.metrics.MinimizeSequentialPlanLength())
    
    # Usa planner anytime con garanzia di qualità crescente
    planner = AnytimePlanner(anytime_guarantee="INCREASING_QUALITY")
    solution = None
    
    for i, p in enumerate(planner.get_solutions(problem, timeout=30)):
        if p.status == PlanGenerationResultStatus.SOLVED_OPTIMALLY:
            return p.plan
        else:
            # Aggiorna con l'ultima soluzione trovata
            solution = p.plan
    
    return solution


def compute_optimum_or_anytime_plan(problem_dir: str, problem_name: str, primo_planner, planner):
    """
    Tenta di computare un piano usando un planner anytime, con fallback.
    
    Args:
        problem_dir: Directory contenente domain.pddl e il file problema
        problem_name: Nome del file problema
        primo_planner: Planner di backup da usare se il primario fallisce
        planner: Planner anytime principale
    
    Returns:
        Piano trovato dal planner anytime, o dal planner di backup
    
    Note:
        Timeout di 60 secondi per il planner anytime
        Se fallisce, usa il planner di backup (primo_planner)
    """
    reader = PDDLReader()
    problem = reader.parse_problem(
        f"{problem_dir}/domain.pddl", 
        f"{problem_dir}/{problem_name}"
    )
    
    # Aggiunge metrica di qualità
    problem.add_quality_metric(up.model.metrics.MinimizeSequentialPlanLength())
    
    solution = None
    # Tenta con planner anytime (timeout 60s)
    for i, p in enumerate(planner.get_solutions(problem, timeout=60)):
        solution = p.plan
    
    # Se non ha trovato soluzioni, usa planner di backup
    if solution is None:
        result = primo_planner.solve(problem)
        solution = result.plan
    return solution


def plan_validation(problem_dir: str, plan_name: str, problem_name: str):
    """
    Valida un piano rispetto a un problema PDDL.
    
    Args:
        problem_dir: Directory contenente domain.pddl e il problema
        plan_name: Nome del file contenente il piano
        problem_name: Nome del file problema
    
    Returns:
        True se il piano è valido, False altrimenti
    
    Note:
        Usa il validatore "tamer" per verificare la validità del piano
        Stampa lo status della validazione
    """
    reader = PDDLReader()
    problem = reader.parse_problem(
        f"{problem_dir}/domain.pddl", 
        f"{problem_dir}/{problem_name}"
    )
    plan = reader.parse_plan(problem, f"{problem_dir}/{plan_name}")
    
    # Valida il piano
    with PlanValidator(name="tamer") as validator:
        result = validator.validate(problem, plan)
    
    print(result.status)
    if result.status == ValidationResultStatus.VALID:
        print(f'Plan is valid.\n')
        return True
    else:
        print("Plan is not valid.")
        return False


# ============================================================================
# SIMULAZIONE STATI
# ============================================================================
    
def get_states(problem_dir: str, plan: SequentialPlan):
    """
    Simula l'esecuzione di un piano e ottiene tutti gli stati intermedi.
    
    Args:
        problem_dir: Directory contenente domain.pddl e problem.pddl
        plan: Piano sequenziale da simulare
    
    Returns:
        Lista di stati, dal s iniziale a quello finale
    
    Note:
        Ogni stato nella lista rappresenta la configurazione del mondo
        dopo l'applicazione dell'azione corrispondente
    """
    reader = PDDLReader()
    problem = reader.parse_problem(
        f"{problem_dir}/domain.pddl", 
        f"{problem_dir}/problem.pddl"
    )
    
    # Inizializza il simulatore e ottiene lo stato iniziale
    with SequentialSimulator(problem) as simulator:
        initial_state = simulator.get_initial_state()
    
    current_state = initial_state
    states = [current_state]
    
    # Simula l'applicazione di ogni azione
    for action_instance in plan.actions:
        current_state = simulator.apply(current_state, action_instance)
        if current_state is None:
            print(f'Error in applying: {action_instance}')
            break
        states.append(current_state)
    
    return states


def get_states_with_name(problem_dir: str, plan: SequentialPlan, problem_name: str):
    """
    Come get_states() ma permette di specificare il nome del problema.
    
    Args:
        problem_dir: Directory contenente domain.pddl e il problema
        plan: Piano sequenziale da simulare
        problem_name: Nome specifico del file problema
    
    Returns:
        Lista di stati risultanti dalla simulazione del piano
    """
    reader = PDDLReader()
    problem = reader.parse_problem(
        f"{problem_dir}/domain.pddl", 
        f"{problem_dir}/{problem_name}"
    )
    
    with SequentialSimulator(problem) as simulator:
        initial_state = simulator.get_initial_state()
    
    current_state = initial_state
    states = [current_state]
    
    for action_instance in plan.actions:
        current_state = simulator.apply(current_state, action_instance)
        if current_state is None:
            print(f'Error in applying: {action_instance}')
            break
        states.append(current_state)
    
    return states


def extractValues(state):
    """
    Estrae ricorsivamente tutti i valori da uno stato e i suoi antenati.
    
    Args:
        state: Stato da cui estrarre i valori
    
    Returns:
        Dizionario con tutti i valori dello stato e dei suoi predecessori
    
    Note:
        Funzione ricorsiva che risale la catena di stati padre
        I valori più recenti sovrascrivono quelli precedenti
    """
    values = {}
    
    # Risale ricorsivamente agli stati padre
    if state._father != None:
        values = extractValues(state._father)
    
    # Aggiorna/sovrascrive con i valori dello stato corrente
    for i in state._values:
        values[i] = state._values[i]
    
    return values


def get_new_state(state):
    """
    Converte uno stato in formato PDDL testuale con i fatti veri.
    
    Args:
        state: Stato da convertire
    
    Returns:
        Stringa contenente tutti i predicati veri in formato PDDL
    
    Note:
        Filtra solo i predicati veri (ignora quelli falsi)
        Converte i parametri in uppercase
    """
    true_facts = ""
    values = extractValues(state)
    
    for key, value in values.items():
        # Considera solo predicati veri
        if value.is_true():
            # Converte il predicato in formato leggibile
            parts = str(key).replace('(', ' ').replace(')', '').replace(',', '').split()
            
            # Converte parametri in uppercase (mantiene nome predicato lowercase)
            for p in range(len(parts[1:])):
                parts[p + 1] = parts[p + 1].upper()
            
            # Ricostruisce in formato PDDL
            formatted_key = "(" + " ".join(parts) + ")"
            true_facts += formatted_key + "\n"
    
    return true_facts


# ============================================================================
# UTILITÀ VARIE
# ============================================================================

def kill_fast_downward_processes():
    """
    Termina tutti i processi Fast Downward residui.
    
    Note:
        Utile per pulire processi rimasti appesi dopo timeout o errori
        Cerca processi con 'downward' nel nome del comando
    """
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'downward' in ' '.join(proc.info['cmdline']).lower():
                print(f"Killing leftover Fast Downward process (PID {proc.pid})")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


def pddl_style_strings_to_plan(action_strings, problem):
    """
    Converte stringhe di azioni in formato PDDL in un piano sequenziale.
    
    Args:
        action_strings: Lista di stringhe rappresentanti azioni (es. "(pickup a)")
        problem: Problema Unified Planning contenente le definizioni
    
    Returns:
        SequentialPlan contenente le azioni parsed
    
    Raises:
        ValueError: Se un'azione o un oggetto non esiste nel problema
    
    Example:
        >>> actions = ["(pickup a)", "(stack a b)"]
        >>> plan = pddl_style_strings_to_plan(actions, problem)
    """
    plan_actions = []
    
    for line in action_strings:
        # Rimuove parentesi esterne e whitespace
        line = line.strip().strip('()')
        if not line:
            continue

        # Separa nome azione da parametri
        parts = line.split()
        action_name = parts[0].lower()  # Nome azione in lowercase
        args = [p.strip() for p in parts[1:]]

        # Recupera l'azione dal dominio
        action = problem.action(action_name)
        if action is None:
            raise ValueError(f"Azione '{action_name}' non trovata nel dominio.")

        # Converte parametri in oggetti del problema
        obj_args = []
        for arg in args:
            obj = problem.object(arg)
            if obj is None:
                raise ValueError(f"Oggetto '{arg}' non trovato nel problema.")
            obj_args.append(obj)

        # Crea istanza dell'azione
        act_instance = ActionInstance(action, tuple(obj_args))
        plan_actions.append(act_instance)

    # Ritorna il piano sequenziale
    return SequentialPlan(plan_actions)