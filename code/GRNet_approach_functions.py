"""
Helper functions for GRNet goal recognition experiments.
Contains all the core functions extracted from GRNet_approach.ipynb
"""

import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Layer
from keras import initializers, regularizers, constraints
from keras.losses import BinaryCrossentropy
from os.path import join
import pickle
import os
import json
import tensorflow as tf
from typing import Union


# ============================================================================
# Custom Network Classes
# ============================================================================

class AttentionWeights(Layer):
    def __init__(self, step_dim,
                 W_regularizer=None, b_regularizer=None,
                 W_constraint=None, b_constraint=None,
                 bias=True, **kwargs):
        self.supports_masking = True
        self.init = initializers.get('glorot_uniform')

        self.W_regularizer = regularizers.get(W_regularizer)
        self.b_regularizer = regularizers.get(b_regularizer)

        self.W_constraint = constraints.get(W_constraint)
        self.b_constraint = constraints.get(b_constraint)

        self.bias = bias
        self.step_dim = step_dim
        self.features_dim = 0
        super(AttentionWeights, self).__init__(**kwargs)

    def build(self, input_shape):
        assert len(input_shape) == 3

        self.W = self.add_weight(shape=(input_shape[-1],),
                                 initializer=self.init,
                                 name='{}_W'.format(self.name),
                                 regularizer=self.W_regularizer,
                                 constraint=self.W_constraint)
        self.features_dim = input_shape[-1]

        if self.bias:
            self.b = self.add_weight(shape=(input_shape[1],),
                                     initializer='zero',
                                     name='{}_b'.format(self.name),
                                     regularizer=self.b_regularizer,
                                     constraint=self.b_constraint)
        else:
            self.b = None

        self.built = True

    def compute_mask(self, input, input_mask=None):
        return None

    def call(self, x, mask=None):
        import tensorflow.keras.backend as K
        features_dim = self.features_dim
        step_dim = self.step_dim

        eij = K.reshape(K.dot(K.reshape(x, (-1, features_dim)),
                        K.reshape(self.W, (features_dim, 1))), (-1, step_dim))

        if self.bias:
            eij += self.b

        eij = K.tanh(eij)

        a = K.exp(eij)

        if mask is not None:
            a *= K.cast(mask, K.floatx())

        a /= K.cast(K.sum(a, axis=1, keepdims=True) + K.epsilon(), K.floatx())

        return a

    def compute_output_shape(self, input_shape):
        return input_shape[0],  self.features_dim

    def get_config(self):
        config={'step_dim':self.step_dim}
        base_config = super(AttentionWeights, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))


class ContextVector(Layer):
    def __init__(self, **kwargs):
        super(ContextVector, self).__init__(**kwargs)
        self.features_dim = 0

    def build(self, input_shape):
        assert len(input_shape) == 2
        self.features_dim = input_shape[0][-1]
        self.built = True

    def call(self, x, **kwargs):
        import tensorflow.keras.backend as K
        assert len(x) == 2
        h = x[0]
        a = x[1]
        a = K.expand_dims(a)
        weighted_input = h * a
        return K.sum(weighted_input, axis=1)

    def compute_output_shape(self, input_shape):
        return input_shape[0][0], self.features_dim

    def get_config(self):
        base_config = super(ContextVector, self).get_config()
        return dict(list(base_config.items()))


# ============================================================================
# Constants Class
# ============================================================================

class C:
    """Constants class."""
    OBSERVATIONS = 0
    CORRECT_GOAL = 1
    POSSIBLE_GOALS = 2
    
    SATELLITE = 0
    LOGISTICS = 1
    ZENOTRAVEL = 2
    BLOCKSWORLD = 3
    DRIVERLOG = 4
    DEPOTS = 5
    
    MAX_PLAN_LENGTH = 0
    MODEL_FILE = 1
    DICTIONARIES_DICT = 2
    
    SMALL = 0
    COMPLETE = 1
    PERCENTAGE = 2
    
    MODELS_DIR = '../models/'
    DICTIONARIES_DIR = '../data/dictionaries/'
    
    MODEL_LOGISTICS = None
    MODEL_SATELLITE = None
    MODEL_ZENOTRAVEL = None
    MODEL_BLOCKSWORLS = None
    MODEL_DRIVERLOG = None
    MODEL_DEPOTS = None

    MAX_PLAN_PERCENTAGE = 0.7

    TABLE_HEADERS = ['', 'Pereira', 'Our', 'Support']
    
    CUSTOM_OBJECTS = {'AttentionWeights': AttentionWeights,
                   'ContextVector' : ContextVector,
                   'custom_multilabel_loss_v3' : BinaryCrossentropy}


# ============================================================================
# Exceptions
# ============================================================================

class PlanLengthError(Exception):
    pass

class FileFormatError(Exception):
    pass

class UnknownIndexError(Exception):
    pass


# ============================================================================
# Unpack Files Methods
# ============================================================================

def unzip_file(file_path: str, target_dir: str) -> None:
    """Unzip a file in an empty directory."""
    if os.path.exists(target_dir):
        for f in os.listdir(target_dir):
            os.remove(join(target_dir, f))
        os.rmdir(target_dir)
    os.mkdir(target_dir)
    os.system(f'unzip -qq {file_path} -d {target_dir}')
    

def unpack_bz2(file_path: str, target_dir: str) -> None:
    """Unpack a .bz2 file in an empty directory."""
    if os.path.exists(target_dir):
        for f in os.listdir(target_dir):
            os.remove(join(target_dir, f))
        os.rmdir(target_dir)
    os.mkdir(target_dir)
    os.system(f'tar -xf {file_path} -C {target_dir}')


# ============================================================================
# Input Parse Methods
# ============================================================================

def load_file(file: str, binary: bool = False, use_pickle: bool = False):
    """Get file content from path."""
    operation = 'r'
    if binary:
        operation += 'b'
    with open(file, operation) as rf:
        if use_pickle:
            output = pickle.load(rf)
        else:
            output = rf.readlines()
        rf.close()
    return output


def remove_parentheses(line: str) -> str:
    """Remove parentheses from a string."""
    msg = (f'Error while parsing a line. Expected "(custom '
    +f'text)" but found "{line}"')
    
    line = line.strip()
    if line.startswith('(') and line.endswith(')'):
        element = line[1:-1]
        element = element.strip()
        if len(element) == 0:
            return None
        else:
            return element
    elif len(line) == 0:
        return None
    else:
        raise FileFormatError(msg)


def retrieve_from_dict(key: str, dictionary: dict):
    """Return the dictionary value given the key."""
    msg_error = f'Key {key.upper()} is not in the dictionary'
    
    try:
        return dictionary[key.upper()]
    except KeyError:
        print(msg_error)
        np.random.seed(47)
        return np.random.randint(0,len(dictionary))


def parse_correct_goal(line: str, goals_dict: dict = None) -> list:
    """Parse the fluents that compose a goal."""
    msg_empty = 'Parsed goal is empty.'
    
    goal = list()
    line = line.strip()
    fluents = line.split(',')
    for f in fluents:
        fluent = remove_parentheses(f)
        if fluent is not None:
            if goals_dict is not None:
                fluent = retrieve_from_dict(fluent, goals_dict)
            goal.append(fluent)
    if len(goal) > 0:
        return goal
    else:
        raise FileFormatError(msg_empty)


def parse_observations(lines: list, obs_dict: dict = None) -> list:
    """Removes parentheses and empty strings from the observations list."""
    msg_empty='Observations list is empty.'
    
    observations = list()
    
    for line in lines:
        observation = remove_parentheses(line)
        if observation is not None:
            if obs_dict is not None:
                observation = retrieve_from_dict(observation, obs_dict)
            observations.append(observation)
    if len(observations)>0:
        return observations
    else:
        raise FileFormatError(msg_empty)


def parse_possible_goals(lines: list, goals_dict: dict = None) -> list:
    """Parse a list of goals."""
    msg_empty='Possible goals list is empty.'
    
    goals=list()
    for line in lines:
        line = line.strip()
        if len(line)>0:
            goals.append(parse_correct_goal(line, goals_dict))
    if len(goals) > 0:
        return goals
    else:
        raise FileFormatError(msg_empty)


def parse_file(read_file: str, content_type: int, dictionary: dict = None):
    """Parse different input files."""
    msg_empty = f'File {read_file} is empty.'
    msg_index = f'Content type {content_type} is unknown.' 
    
    elements = list()
    
    lines = load_file(read_file)
    if len(lines) == 0:
        raise FileFormatError(msg_empty)
    if content_type == C.OBSERVATIONS:
        elements = parse_observations(lines, dictionary)
    elif content_type == C.POSSIBLE_GOALS:
        elements = parse_possible_goals(lines, dictionary)
    elif content_type == C.CORRECT_GOAL:
        elements = parse_correct_goal(lines[0], dictionary)
    else:
        raise UnknownIndexError(msg_index)
    
    if len(elements) > 0:    
        return elements
    else:
        raise FileFormatError(msg_empty)


# ============================================================================
# Model Related Methods
# ============================================================================

def parse_domain(domain: Union[str, int]) -> int:
    """Converts domain name into integer."""
    msg = (f'Provided domain {domain} is not supported. '+
           f'Supported domains are: {C.SATELLITE} : satellite, ' +
           f'{C.LOGISTICS} : logistics, {C.BLOCKSWORLD} : blocksworld, ' +
           f'{C.ZENOTRAVEL} : zenotravel, {C.DRIVERLOG}: driverlog,' + 
           f'{C.DEPOTS}: depots.')
           
    if (str(domain).isdigit() and int(domain) == C.SATELLITE) or str(domain).lower().strip() == 'satellite':
        return C.SATELLITE
    elif (str(domain).isdigit() and int(domain) == C.LOGISTICS) or str(domain).lower().strip() == 'logistics':
        return C.LOGISTICS
    elif (str(domain).isdigit() and int(domain) == C.BLOCKSWORLD) or str(domain).lower().strip() == 'blocksworld':
        return C.BLOCKSWORLD
    elif (str(domain).isdigit() and int(domain) == C.ZENOTRAVEL) or str(domain).lower().strip() == 'zenotravel':
        return C.ZENOTRAVEL
    elif (str(domain).isdigit() and int(domain) == C.DRIVERLOG) or str(domain).lower().strip() == 'driverlog':
        return C.DRIVERLOG
    elif (str(domain).isdigit() and int(domain) == C.DEPOTS) or str(domain).lower().strip() == 'depots':
        return C.DEPOTS
    else:
        raise KeyError(msg)


def get_model(domain: int):
    """Loads the model for a specific domain."""
    msg = (f'Provided domain {domain} is not supported. '+
       f'Supported domains are: {C.SATELLITE} : satellite, ' +
       f'{C.LOGISTICS} : logistics, {C.BLOCKSWORLD} : blocksworld, ' +
       f'{C.ZENOTRAVEL} : zenotravel, {C.DRIVERLOG}: driverlog,' + 
       f'{C.DEPOTS}: depots.')
    
    if domain == C.LOGISTICS:
        return C.MODEL_LOGISTICS
    elif domain == C.SATELLITE:
        return C.MODEL_SATELLITE
    elif domain == C.DEPOTS:
        return C.MODEL_DEPOTS
    elif domain == C.BLOCKSWORLD:
        return C.MODEL_BLOCKSWORLS
    elif domain == C.DRIVERLOG:
        return C.MODEL_DRIVERLOG
    elif domain == C.ZENOTRAVEL:
        return C.MODEL_ZENOTRAVEL
    else:
        raise KeyError(msg)


def get_domain_related(domain: int, element: int, model_type: int = C.SMALL, 
                       percentage: float = 0) -> Union[int, str]:
    """Returns domain related information."""
    msg = (f'Provided domain {domain} is not supported. '+
           f'Supported domains are: {C.SATELLITE} : satellite, ' +
           f'{C.LOGISTICS} : logistics, {C.BLOCKSWORLD} : blocksworld, ' +
           f'{C.ZENOTRAVEL} : zenotravel.')
    if domain == C.LOGISTICS:
        v = {
            'max_plan_len' : 50,
            'name' : 'logistics',
        }
    elif domain == C.SATELLITE:
        v = {
            'max_plan_len' : 40,
            'name' : 'satellite',
        }
    elif domain == C.ZENOTRAVEL:
        v = {
            'max_plan_len' : 40,
            'name' : 'zenotravel',
        }
    elif domain == C.BLOCKSWORLD:
        v = {
            'max_plan_len' : 75,
            'name' : 'blocksworld',
        }
    elif domain == C.DRIVERLOG:
        v = {
            'max_plan_len' : 70,
            'name' : 'driverlog',
        }
    elif domain == C.DEPOTS:
        v = {
            'max_plan_len' : 64,
            'name' : 'depots'
        }
    else:
        raise KeyError(msg)
        
    if element == C.MAX_PLAN_LENGTH:
        return int(v['max_plan_len']*C.MAX_PLAN_PERCENTAGE)
    
    elif element == C.MODEL_FILE:
        if model_type == C.COMPLETE:
            return f'{v["name"]}.h5'
        elif model_type == C.SMALL:
            return f'{v["name"]}_small.h5'
        elif model_type == C.PERCENTAGE:
            return f'{v["name"]}_{int(percentage*100)}perc.h5'
        
    elif element == C.DICTIONARIES_DICT:
        return join(C.DICTIONARIES_DIR, f'{v["name"]}')


# ============================================================================
# Domain Component Methods
# ============================================================================

def get_observations_array(observations: list, max_plan_length: int) -> np.ndarray:
    """Create an array of observations index."""
    WARNING_MSG = (f'The action trace is too long. Only the first {max_plan_length}'+
                 f'actions will be considered.')
    
    observations_array = np.zeros((1, max_plan_length))
    if len(observations) > max_plan_length:
        print(WARNING_MSG)
    for index, observation in enumerate(observations):
        if index < max_plan_length:
            observations_array[0][index] = int(observation)
    return observations_array
        

def get_predictions(observations: list, 
                    max_plan_length: int, 
                    domain: int) -> np.ndarray:
    """Return the model predictions."""
    model = get_model(domain)
    
    model_input = tf.convert_to_tensor(get_observations_array(observations, max_plan_length))
    y_pred = model.predict(model_input)
    return y_pred


# ============================================================================
# GR Instance Component Methods
# ============================================================================

def get_score(prediction: np.ndarray, possible_goal: list) -> float:
    """Returns the score for a possible goal."""
    score=0
    
    for index in possible_goal:
        score += prediction[0][int(index)]
    return score


def get_scores(prediction: np.ndarray, possible_goals: list) -> np.ndarray:
    """Returns the scores for all possible goals."""
    scores = np.zeros((len(possible_goals, )), dtype=float)
    for index, possible_goal in enumerate(possible_goals):
        scores[index] = get_score(prediction, possible_goal)
    return scores
        

def get_max(scores: np.ndarray) -> list:
    """Returns a list with the index (or indexes) of the highest scores."""
    max_element = -1
    index_max = list()
    for i in range(len(scores)):
        if scores[i] > max_element:
            max_element = scores[i]
            index_max = [i]
        elif scores[i] == max_element:
            index_max.append(i)

    return index_max
    

def get_result(scores: np.ndarray, correct_goal: int) -> bool:
    """Computes if the goal recognition task is successful."""
    idx_max_list = get_max(scores)
    if len(idx_max_list) == 1:
        idx_max = idx_max_list[0]
    else:
        idx_max = idx_max_list[np.random.randint(0, len(idx_max_list))]
    if idx_max == correct_goal:
        return True
    else:
        return False
    

def get_correct_goal_idx(correct_goal: list, possible_goals: list) -> int:
    """Computes the correct goal index."""
    for index, possible_goal in enumerate(possible_goals):
        possible_goal = np.sort(possible_goal)
        correct_goal = np.sort(correct_goal)
        if np.all(possible_goal == correct_goal):
            return index
    return None


# ============================================================================
# Noisy Mask Methods
# ============================================================================

def load_mask_file(mask_file_path: str) -> dict:
    """Load a mask file containing noisy observations."""
    with open(mask_file_path, 'r') as f:
        return json.load(f)


def apply_mask(observations: list, problem_file: str, mask_data: dict) -> list:
    """
    Apply a noisy mask to observations if available.
    
    Raises:
        KeyError: If problem_file is not found in mask_data
    """
    if problem_file not in mask_data:
        raise KeyError(f"Problem {problem_file} not found in mask data")
    
    problem_mask = mask_data[problem_file]
    return problem_mask['obs']


def get_mask_path(domain: int, percentage_dir: str, noise_level: int) -> str:
    """Get the path to the mask file for a given domain, percentage, and noise level."""
    domain_name = get_domain_related(domain, C.MODEL_FILE).split('_')[0]
    mask_base_dir = '../data/validator_testset/noisy_masks'
    mask_file = f'{noise_level}_mask.json'
    return join(mask_base_dir, domain_name, percentage_dir, mask_file)
