#!/usr/bin/env python3
'''
NieMarkov: Niema's Python implementation of Markov chains
'''

# imports
from ast import literal_eval
from gzip import open as gopen
from pathlib import Path
from pickle import dump as pdump, load as pload
from random import randint

# useful constants
NIEMARKOV_VERSION = '1.0.2'
ALLOWED_STATE_TYPES = {int, str}
DEFAULT_BUFSIZE = 1048576 # 1 MB #8192 # 8 KB
MODEL_EXT = {'dict', 'pkl'}

def check_state_type(state_label):
    '''
    Helper function to check state type and throw an error if not allowed

    Args:
        state_label (str): The label of the state to check
    '''
    if type(state_label) not in ALLOWED_STATE_TYPES:
        raise TypeError("Invalid state type (%s). Must be one of: %s" % (type(state_label), ', '.join(str(t) for t in ALLOWED_STATE_TYPES)))

def open_file(p, mode='rt', buffering=DEFAULT_BUFSIZE):
    '''
    Open a file for reading/writing

    Args:
        p (Path): The path of the file to open, or `None` for `stdin`/`stdout`
        mode (str): The mode to open the file stream in
        buffering (int): The size of the file I/O buffer

    Returns:
        file: The opened file
    '''
    mode = mode.strip().lower()
    if isinstance(p, str):
        p = Path(p)
    if p is None:
        if 'r' in mode:
            from sys import stdin as f
        else:
            from sys import stdout as f
    elif p.suffix == '.gz':
        f = gopen(p, mode=mode)
    else:
        f = open(p, mode=mode)
    return f

def random_choice(options):
    '''
    Helper function to randomly pick from a collection of options

    Args:
        options (dict): The options to randomly pick from (keys = options, values = count weighting that option)

    Returns:
        object: A random element from `options`
    '''
    sum_options = sum(options.values())
    random_int = randint(1, sum_options)
    curr_total_count = 0
    for option, count in options.items():
        curr_total_count += count
        if random_int <= curr_total_count:
            return option

class MarkovChain:
    '''Class to represent Markov chains'''
    def __init__(self, order=1):
        '''
        Initialize a `MarkovChain` object

        Args:
            order (int): The order of this Markov chain
        '''
        if not isinstance(order, int) or order < 1:
            raise ValueError("`order` must be a positive integer")
        self.version = NIEMARKOV_VERSION  # NieMarkov version number
        self.order = order                # order of this Markov chain
        self.labels = list()              # labels of the states of this Markov chain
        self.label_to_state = dict()      # `label_to_state[label]` is the state (`int` from 0 to `num_states-1`) labeled by `label`
        self.transitions = dict()         # for an `order`-dimensional `tuple` of states `state_tuple`, `transitions[state_tuple]` is a `dict` where keys = outgoing state tuples, and values = transition counts
        self.initial_state_tuple = dict() # `initial_state_tuple[state_tuple]` is the number of times `state_tuple` is at the start of a path

    def __str__(self):
        '''
        Return a string summarizing this `MarkovChain`

        Returns:
            str: A string summarizing this `MarkovChain`
        '''
        return '<NieMarkov: order=%d; states=%d>' % (self.order, len(self.labels))

    def __iter__(self):
        '''
        Iterate over the state tuples of this `order`-order `MarkovChain`

        Yields:
            tuple: The next state tuple.
        '''
        state_tuples = set()
        for state_tuple_src, outgoing_dict in self.transitions.items():
            state_tuples.add(state_tuple_src)
            for state_tuple_dst in outgoing_dict:
                state_tuples.add(state_tuple_dst)
        for state_tuple in state_tuples:
            yield state_tuple

    def __getitem__(self, key):
        '''
        Return the outgoing transitions of a given state tuple

        Args:
            key (tuple): A state tuple

        Returns:
            dict: The outgoing transmissions of `key`
        '''
        try:
            return self.transitions[key]
        except KeyError:
            return dict()

    def dump(self, p, buffering=DEFAULT_BUFSIZE):
        '''
        Dump this `MarkovChain` to a file

        Args:
            p (Path): The path of the file where this `MarkovChain` should be dumped
            buffering (int): The size of the file I/O buffer
        '''
        if isinstance(p, str):
            p = Path(p)
        model = {'version':self.version, 'order':self.order, 'labels':self.labels, 'transitions':self.transitions, 'initial': self.initial_state_tuple}
        if p.suffix.lower() == '.pkl' or p.name.lower().endswith('.pkl.gz'):
            with open_file(p, mode='wb', buffering=buffering) as f:
                pdump(model, f)
        elif p.suffix.lower() == '.dict' or p.name.lower().endswith('.dict.gz'):
            with open_file(p, mode='wt', buffering=buffering) as f:
                f.write(str(model))
        else:
            raise ValueError("Invalid output NieMarkov model filename (%s). Valid extensions: %s" % (p, ', '.join(ext for ext in sorted(MODEL_EXT))))

    def load(p, buffering=DEFAULT_BUFSIZE):
        '''
        Load a `MarkovChain` from a file

        Args:
            p (Path): The path of the file from which to load a `MarkovChain`
            buffering (int): The size of the file I/O buffer

        Returns:
            MarkovChain: The loaded `MarkovChain`
        '''
        # load model from file
        if isinstance(p, str):
            p = Path(p)
        if p.suffix.lower() == '.pkl' or p.name.lower().endswith('.pkl.gz'):
            with open_file(p, mode='rb', buffering=buffering) as f:
                model = pload(f)
        elif p.suffix.lower() == '.dict' or p.name.lower().endswith('.dict.gz'):
            with open_file(p, mode='rt', buffering=buffering) as f:
                model = literal_eval(f.read())

        # check model for validity
        for k in ['order', 'labels', 'transitions', 'initial']:
            if k not in model:
                raise ValueError("Invalid model file (missing key '%s'): %s" % (k, p))

        # create and populate output `MarkovChain`
        mc = MarkovChain(order=model['order'])
        mc.version = model['version']
        mc.labels = model['labels']
        mc.label_to_state = {label:i for i, label in enumerate(mc.labels)}
        mc.transitions = model['transitions']
        mc.initial_state_tuple = model['initial']
        return mc

    def add_path(self, path):
        '''
        Add a path to this `MarkovChain`

        Args:
            path (list): A path of states
        '''
        # check `path` for validity
        if not isinstance(path, list):
            raise TypeError("`path` must be a list of state labels")
        if len(path) <= self.order:
            raise ValueError("Length of `path` (%d) must be > Markov chain order (%d)" % (len(path), self.order))


        # add new state labels
        for state_label in path:
            if state_label not in self.label_to_state:
                check_state_type(state_label)
                self.label_to_state[state_label] = len(self.labels)
                self.labels.append(state_label)

        # add path
        first_tup = tuple(self.label_to_state[path[j]] for j in range(self.order))
        if first_tup in self.initial_state_tuple:
            self.initial_state_tuple[first_tup] += 1
        else:
            self.initial_state_tuple[first_tup] = 1
        for i in range(len(path) - self.order):
            from_tup = tuple(self.label_to_state[path[j]] for j in range(i, i+self.order))
            to_tup = tuple(self.label_to_state[path[j]] for j in range(i+1, i+1+self.order))
            if from_tup in self.transitions:
                if to_tup in self.transitions[from_tup]:
                    self.transitions[from_tup][to_tup] += 1
                else:
                    self.transitions[from_tup][to_tup] = 1
            else:
                self.transitions[from_tup] = {to_tup: 1}

    def generate_path(self, max_len=float('inf'), start=None):
        '''
        Generate a random path in this `MarkovChain`

        Args:
            max_len (int): The maximum length of the random path to generate
            start (str): The starting state, or `None` to randomly pick a starting state

        Returns:
            list: The randomly-generated path
        '''
        if start is None:
            curr_state_tuple = random_choice(self.initial_state_tuple)
        elif len(start) == self.order:
            curr_state_tuple = tuple(self.label_to_state[label] for label in start)
            if curr_state_tuple not in self.transitions:
                raise ValueError("No outgoing edges from start: %s" % start)
        else: # in the future, can do something fancy to handle this scenario, e.g. randomly pick an initial state tuple ending with `start`
            raise ValueError("`start` length (%d) must be same as Markov model order (%d): %s" % (len(start), self.order, start))
        path = [self.labels[state] for state in curr_state_tuple]
        while len(path) < max_len:
            if curr_state_tuple not in self.transitions:
                break
            curr_state_tuple = random_choice(self.transitions[curr_state_tuple])
            path.append(self.labels[curr_state_tuple[-1]])
        return path

    def to_dot(self):
        '''
        Get a representation of this `MarkovChain` in the Graphviz DOT format

        Returns:
            str: The DOT representation of this `MarkovChain`
        '''
        state_tuples = list(self)
        state_tuple_to_ind = {state_tuple:i for i, state_tuple in enumerate(state_tuples)}
        state_tuple_labels = [' '.join(self.labels[state] for state in state_tuple) for state_tuple in state_tuples]
        nodes_str = '\n'.join('    %s [label="%s"];' % (state_tuple, state_tuple_label.strip().replace('"',"'")) for state_tuple, state_tuple_label in enumerate(state_tuple_labels))
        edges_str = '\n'.join('    %d -> %d [label="%s"];' % (state_tuple_to_ind[state_tuple_src], state_tuple_to_ind[state_tuple_dst], edge_count) for state_tuple_src in state_tuples for state_tuple_dst, edge_count in self[state_tuple_src].items())
        return 'digraph G {\n    // nodes\n%s\n\n    // edges\n%s\n}\n' % (nodes_str, edges_str)
