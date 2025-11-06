"""
Modulo per la generazione di piani avversariali con attacchi di tipo  random.

Questo modulo genera dataset di validazione con osservazioni modificate tramite
sostituzione casuale di azioni nel piano originale. Gli attacchi vengono applicati
con diverse percentuali configurabili.
"""

import random
import os
import pickle
import json
from typing import List, Tuple, Dict, Any
from unified_planning.shortcuts import *
from tqdm import tqdm
from up_utils import *
import psutil

# Costanti Generali
RANDOM_SEED = 42
MASK_ORIGINAL = 0  # Identificatore per azione originale nella maschera
MASK_MODIFIED = 1  # Identificatore per azione modificata nella maschera

# Percorsi Base
BASE_PATH = './'
DATA_DIR = f'{BASE_PATH}/data'
CODE_DIR = f'{BASE_PATH}/code'
TMP_DIR = f"{BASE_PATH}/tmp"

# Percorsi Relativi Template
DICTIONARIES_DIR_TEMPLATE = f'{DATA_DIR}/dictionaries/{{domain}}'
DICTIONARY_FILE_TEMPLATE = f'{DICTIONARIES_DIR_TEMPLATE}/dizionario'
GOAL_DICTIONARY_FILE_TEMPLATE = f'{DICTIONARIES_DIR_TEMPLATE}/dizionario_goal'
PLANS_DIR_TEMPLATE = f'{DATA_DIR}/{{domain}}'  # Directory dei piani da processare
OUTPUT_DIR_TEMPLATE = f'{DATA_DIR}/validator_testset/noisy_masks/{{domain}}/{{hole_perc}}/'

# Configurazione Domini e Percentuali
# DOMAINS = ['blocksworld', 'logistics', 'driverlog', 'satellite', 'depots', 'zenotravel']
DOMAINS = ['zenotravel']
HOLE_PERCENTAGES = [10,30,50,70,100]  # Percentuali di "buchi" nei piani
ATTACK_PERCENTAGES = [10, 20, 30]  # Percentuali di azioni da attaccare

# Nome del Grounder
GROUNDER_NAME = "fast-downward-reachability-grounder"

# Imposta il seed per la riproducibilità degli esperimenti
random.seed(RANDOM_SEED)


def adversarial_plan(
    observations: List[str], 
    perc_actions: float, 
    valid_actions: List[str]
) -> Tuple[List[str], List[int], int]:
    """
    Applica un attacco avversariale a una sequenza di osservazioni sostituendo
    casualmente alcune azioni con azioni valide scelte random.
    
    Args:
        observations: Lista delle azioni osservate nel piano originale
        perc_actions: Percentuale di azioni da modificare (0-100)
        valid_actions: Lista delle azioni valide che possono essere utilizzate
                      per la sostituzione
    
    Returns:
        Tuple contenente:
        - new_obs: Lista delle osservazioni modificate
        - mask: Lista di flag (0=originale, 1=modificato) per ogni osservazione
        - num_atks: Numero totale di azioni modificate
    
    Example:
        >>> obs = ['action1', 'action2', 'action3']
        >>> valid = ['action1', 'action2', 'action3', 'action4']
        >>> new_obs, mask, count = adversarial_plan(obs, 50, valid)
        >>> # Circa il 50% delle azioni sarà sostituito
    """
    # Seleziona casualmente gli indici delle azioni da modificare
    indices_to_modify = []
    for idx in range(len(observations)):
        if random.random() < perc_actions / 100:
            indices_to_modify.append(idx)

    # Costruisce la nuova sequenza di osservazioni e la maschera
    new_obs = []
    mask = []
    num_atks = len(indices_to_modify)
    
    for i, obs in enumerate(observations):
        if i in indices_to_modify:
            # Sostituisce l'azione originale con una casuale
            action = random.choice(valid_actions)
            new_obs.append(action.upper())
            mask.append(MASK_MODIFIED)
        else:
            # Mantiene l'azione originale
            new_obs.append(obs)
            mask.append(MASK_ORIGINAL)
    
    return new_obs, mask, num_atks

'''
CODICE ORIGINALE CON ANCHE AGGIUNTE E RIMOZIONI DI AZIONI IN MODO RANDOM:
def adversarial_plan(observations, perc_actions, valid_actions):
    idx_aggiunta = []
    for idx in range(len(observations)):
        if random.random() < perc_actions / 100:
            idx_aggiunta.append(idx)

    new_obs = []
    mask = []  # Maschera per tracciare le osservazioni originali e modificate
    num_atks = len(idx_aggiunta)
    for i, obs in enumerate(observations):
        if i in idx_aggiunta:
            # operazione = random.randint(1, 3)
            # if operazione == 1:  # Cambio azione
            action = random.choice(valid_actions)
            new_obs.append(action.upper())
            mask.append(1)  # Aggiunto elemento modificato
            # elif operazione == 2:  # Aggiungo azione
            #     action = random.choice(valid_actions)
            #     new_obs.append(obs)
            #     mask.append(0)  # Elemento originale
            #     new_obs.append(action.upper())
            #     mask.append(1)  # Elemento aggiunto
            # elif operazione == 3:  # Rimuovo azione
            #     continue  # Non aggiungo nulla a new_obs o alla maschera
        else:
            new_obs.append(obs)
            mask.append(0)  # Elemento originale
    return new_obs, mask, num_atks
'''


def load_dictionary(dictionary_path: str) -> Dict[str, Any]:
    """
    Carica un dizionario serializzato da file pickle.
    
    Args:
        dictionary_path: Percorso del file pickle contenente il dizionario
    
    Returns:
        Il dizionario caricato dal file
    
    Raises:
        FileNotFoundError: Se il file non esiste
        pickle.UnpicklingError: Se il file non è un pickle valido
    """
    with open(dictionary_path, 'rb') as f:
        return pickle.load(f)


def get_init_state_safe(problem_dir: str) -> List[str]:
    """
    Estrae lo stato iniziale dal template PDDL in modo robusto.
    Gestisce sia il formato con predicati su più righe che su una singola riga.
    
    Args:
        problem_dir: Directory contenente template.pddl
    
    Returns:
        Lista di predicati che descrivono lo stato iniziale
    """
    try:
        with open(problem_dir + '/template.pddl', 'r') as f:
            content = f.read()
            
        # Estrae la sezione tra (:init o (:INIT e (:goal o (:goal (case insensitive)
        content_lower = content.lower()
        init_idx = content_lower.find('(:init')
        goal_idx = content_lower.find('(:goal')
        
        if init_idx == -1 or goal_idx == -1:
            print(f"Warning: Could not find init or goal section in template.pddl")
            return []
        
        init_section = content[init_idx:goal_idx]
        
        # Rimuove la parte "(:init" o "(:INIT" dall'inizio
        init_section = init_section[6:].strip()
        
        # Estrae tutti i predicati tra parentesi usando regex
        import re
        # Trova tutte le stringhe tra parentesi
        predicates_raw = re.findall(r'\(([^)]+)\)', init_section)
        
        # Pulisce e converte in uppercase
        result = []
        for pred in predicates_raw:
            pred_clean = pred.strip().upper()
            if pred_clean:  # Ignora predicati vuoti
                result.append(pred_clean)
        
        return result
        
    except Exception as e:
        # Se qualcosa va storto, ritorna lista vuota
        print(f"Warning: Could not parse init state from {problem_dir}: {e}")
        import traceback
        traceback.print_exc()
        return []


def process_single_plan(
    plan_name: str,
    plans_path: str,
    tmp_path: str,
    attack_percentage: float,
    grounder: Any,
    dizionario: Dict[str, Any],
    dizionario_goal: Dict[str, Any]
) -> Tuple[Dict[str, Any], int, int]:
    """
    Processa un singolo piano applicando l'attacco avversariale.
    
    Args:
        plan_name: Nome del file del piano da processare
        plans_path: Percorso della directory contenente i piani
        tmp_path: Percorso della directory temporanea per l'estrazione
        attack_percentage: Percentuale di azioni da modificare
        grounder: Compilatore per il grounding delle azioni
        dizionario: Dizionario per l'encoding delle osservazioni
        dizionario_goal: Dizionario per l'encoding dei goal
    
    Returns:
        Tuple contenente:
        - Dizionario con i dati del piano processato
        - Numero di attacchi effettuati
        - Numero totale di osservazioni
    """
    # Determina se è un dataset Pereira
    is_pereira = plan_name.endswith('.tar.bz2')
    
    try:
        # Estrae il problema dalla directory compressa
        problem_dir = os.path.join(plans_path, plan_name)
        open_compressed_file(problem_dir, tmp_path)
    except Exception as e:
        raise Exception(f"Error opening compressed file: {e}")
    
    try:
        # Legge i dati del problema
        observations = get_observations(tmp_path)
    except Exception as e:
        raise Exception(f"Error getting observations: {e}")
    
    try:
        goals = get_goals(tmp_path, is_pereira)
    except Exception as e:
        raise Exception(f"Error getting goals: {e}")
    
    try:
        real_goal = get_real_goal(tmp_path, is_pereira)
    except Exception as e:
        raise Exception(f"Error getting real goal: {e}")
    
    try:
        init_state = get_init_state_safe(tmp_path)
    except Exception as e:
        raise Exception(f"Error getting init state: {e}")
    
    try:
        # Ottiene le azioni valide per l'attacco
        valid_actions = get_grounded_actions(tmp_path, grounder, is_pereira)
    except Exception as e:
        print(plan_name)
        raise Exception(f"Error getting grounded actions: {e}")
        
    
    try:
        # Applica l'attacco avversariale
        modified_obs, mask, num_attacks = adversarial_plan(
            observations, 
            attack_percentage, 
            valid_actions
        )
    except Exception as e:
        raise Exception(f"Error applying adversarial plan: {e}")
    
    try:
        # Costruisce il risultato con i dati encoded
        result = {
            'init_state': encode_goal(init_state, dizionario_goal),
            'obs': encode_obs(modified_obs, dizionario),
            'real_goal': encode_goal(real_goal, dizionario_goal),
            'mask': mask,
            'goals': [encode_goal(goal, dizionario_goal) for goal in goals]
        }
    except Exception as e:
        raise Exception(f"Error encoding results: {e}")
    
    return result, num_attacks, len(observations)


def process_domain(
    domain: str,
    hole_percentages: List[int],
    attack_percentages: List[int]
) -> None:
    """
    Processa un intero dominio applicando attacchi con diverse percentuali.
    
    Args:
        domain: Nome del dominio (es. 'blocksworld', 'logistics')
        hole_percentages: Lista delle percentuali di "buchi" da processare
        attack_percentages: Lista delle percentuali di attacco da applicare
    """
    print(f'\n{"="*60}')
    print(f'Processing domain: {domain.upper()}')
    print(f'{"="*60}')
    
    # Carica i dizionari del dominio usando i template
    dictionary_file = DICTIONARY_FILE_TEMPLATE.format(domain=domain)
    dizionario = load_dictionary(dictionary_file)
    print(f'Loaded action dictionary with {len(dizionario)} entries')
    
    goal_dictionary_path = GOAL_DICTIONARY_FILE_TEMPLATE.format(domain=domain)
    dizionario_goal = load_dictionary(goal_dictionary_path)
    print(f'Loaded goal dictionary with {len(dizionario_goal)} entries')
    
    # Inizializza il grounder
    grounder = Compiler(name=GROUNDER_NAME)
    
    # Dizionario per raccogliere le statistiche sugli attacchi
    attack_histogram = {}
    
    # Itera su ogni percentuale di "buchi"
    for hole_perc in hole_percentages:
        print(f'\n--- Processing plans with {hole_perc}% observability ---')
        attack_histogram[hole_perc] = {}
        
        # Percorso dei piani da processare per questa percentuale di "buchi"
        plans_path = f'{PLANS_DIR_TEMPLATE.format(domain=domain)}/{hole_perc}'
        
        # Verifica che la directory esista
        if not os.path.exists(plans_path):
            print(f'WARNING: Directory {plans_path} does not exist. Skipping...')
            continue
        
        # Itera su ogni percentuale di attacco
        for attack_perc in attack_percentages:
            print(f'\nApplying {attack_perc}% attack rate...')
            
            # Inizializza le strutture dati per questa configurazione
            solutions_dict = {}
            attack_histogram[hole_perc][attack_perc] = {}
            
            total_attacks = 0
            total_observations = 0
            
            # Processa ogni piano nella directory
            plan_files = [f for f in os.listdir(plans_path) 
                         if f.endswith('.zip') or f.endswith('.tar.bz2')]
            
            print(f'Found {len(plan_files)} plans to process.')
            
            for plan_name in tqdm(plan_files, desc=f'{attack_perc}% attack'):
                try:
                    result, num_attacks, num_obs = process_single_plan(
                        plan_name,
                        plans_path,
                        TMP_DIR,
                        attack_perc,
                        grounder,
                        dizionario,
                        dizionario_goal
                    )
                    
                    solutions_dict[plan_name] = result
                    total_attacks += num_attacks
                    total_observations += num_obs
                    
                    # Aggiorna l'istogramma degli attacchi
                    if num_attacks not in attack_histogram[hole_perc][attack_perc]:
                        attack_histogram[hole_perc][attack_perc][num_attacks] = 0
                    attack_histogram[hole_perc][attack_perc][num_attacks] += 1
                    
                except Exception as e:
                    print(f'\nError processing {plan_name}: {str(e)}')
                    import traceback
                    traceback.print_exc()
                    continue
            
            # Calcola la percentuale effettiva di attacchi
            if total_observations > 0:
                actual_attack_perc = (total_attacks / total_observations) * 100
                attack_histogram[hole_perc][attack_perc]["actual_atk_perc"] = actual_attack_perc
                print(f'Actual attack percentage: {actual_attack_perc:.2f}%')
            
            # Salva i risultati per questa configurazione usando il template
            output_dir = OUTPUT_DIR_TEMPLATE.format(domain=domain, hole_perc=hole_perc)
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = f'{output_dir}/{attack_perc}_mask.json'
            with open(output_file, 'w') as f:
                json.dump(solutions_dict, f, indent=4)
            print(f'Saved results to {output_file}')
        
        # Salva l'analisi degli attacchi per questa percentuale di hole
        analysis_file = f'{output_dir}/atk_analysis.json'
        with open(analysis_file, 'w') as f:
            json.dump(attack_histogram[hole_perc], f, indent=4)
        print(f'\nSaved attack analysis to {analysis_file}')


def main():
    """
    Funzione principale che orchestra il processo di generazione dei dataset
    avversariali per tutti i domini specificati.
    """
    print('='*60)
    print('ADVERSARIAL PLAN GENERATOR')
    print('='*60)
    print(f'Base path: {BASE_PATH}')
    print(f'Domains to process: {", ".join(DOMAINS)}')
    print(f'Hole percentages: {HOLE_PERCENTAGES}')
    print(f'Attack percentages: {ATTACK_PERCENTAGES}')
    
    # Processa ogni dominio
    for domain in DOMAINS:
        try:
            process_domain(
                domain,
                HOLE_PERCENTAGES,
                ATTACK_PERCENTAGES
            )
        except Exception as e:
            print(f'\nFATAL ERROR processing domain {domain}: {repr(e)}')
            continue
    
    print('\n' + '='*60)
    print('Processing completed successfully!')
    print('='*60)


if __name__ == '__main__':
    main()
