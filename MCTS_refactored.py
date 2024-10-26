#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 22:06:01 2023

@author: shaivan
"""

# Original code obtained from https://gist.github.com/qpwo/c538c6f73727e254fdc7fab81024f6e1
# code modified here to include refactoring
# everwhere where code has been changed, is mentioned through comments.
# the changed code is explained in the report 

from abc import ABC, abstractmethod
from collections import defaultdict
import math

class MCTS:
    "Monte Carlo tree searcher. First rollout the tree then choose a move."

    def __init__(self, exploration_weight=1):
        self.Q = defaultdict(int)  # total reward of each node
        self.N = defaultdict(int)  # total visit count for each node
        self.children = defaultdict(set)  #CODE CHANGED HERE
        self.exploration_weight = exploration_weight

    def choose(self, node):
        "Choose the best successor of node. (Choose a move in the game)"
        if node.is_terminal():
            raise RuntimeError(f"choose called on terminal node {node}")

        if node not in self.children:
            return node.find_random_child()

        return max(self.children[node], key=self._score)

    def do_rollout(self, node):
        "Make the tree one layer better. (Train for one iteration.)"
        path = self._select(node)
        leaf = path[-1]
        self._expand(leaf)
        reward = self._simulate(leaf)
        self._backpropagate(path, reward)

# CODE CHANGED HERE
    def _select(self, node):
        "Find an unexplored descendant of `node`"
        path = []
        while True:
            path.append(node)
            if node not in self.children or not self.children[node]:
                return path
            unexplored = self.children[node] - set(self.children.keys())
            if unexplored:
                path.append(unexplored.pop())
                return path
            node = self._uct_select(node)

    def _expand(self, node):
        "Update the `children` dict with the children of `node`"
        if node not in self.children:
            self.children[node] = node.find_children()

# CODE CHANGED HERE 
    def _simulate(self, node):
        "Returns the reward for a random simulation (to completion) of `node`"
        invert_reward = True
        while not node.is_terminal():
            reward = node.reward()
            node = node.find_random_child()
            invert_reward = not invert_reward
        return 1 - reward if invert_reward else reward

    def _backpropagate(self, path, reward):
        "Send the reward back up to the ancestors of the leaf"
        for node in reversed(path):
            self.N[node] += 1
            self.Q[node] += reward
            reward = 1 - reward  # 1 for me is 0 for my enemy, and vice versa

# CODE CHANGED HERE
    def _score(self, n):
        "Calculate score for a node"
        if self.N[n] == 0:
            return float("-inf")
        return self.Q[n] / self.N[n]

# CODE CHANGED HERE
    def _uct_select(self, node):
        "Select a child of node, balancing exploration & exploitation"
        log_N_vertex = math.log(self.N[node])

        def uct(n):
            "Upper confidence bound for trees"
            return self._score(n) + self.exploration_weight * math.sqrt(log_N_vertex / self.N[n])

        return max(self.children[node], key=uct)


class Node(ABC):
    """
    A representation of a single board state.
    MCTS works by constructing a tree of these Nodes.
    Could be e.g. a chess or checkers board state.
    """

    @abstractmethod
    def find_children(self):
        "All possible successors of this board state"
        return set()

    @abstractmethod
    def find_random_child(self):
        "Random successor of this board state (for more efficient simulation)"
        return None

    @abstractmethod
    def is_terminal(self):
        "Returns True if the node has no children"
        return True

    @abstractmethod
    def reward(self):
        "Assumes `self` is terminal node. 1=win, 0=loss, .5=tie, etc"
        return 0

# CODE CHANGED HERE
    @abstractmethod
    def __eq__(self, other):
        "Nodes must be comparable"
        return True
