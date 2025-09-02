"""
PyMine Association Rule Mining Module
Author: Fash
Description: Implements Apriori algorithm with explainability, reverse reasoning,
what-if analysis, and teaching mode.
"""

import math
from collections import defaultdict, Counter
from itertools import combinations, chain

class BaseAssociation:
    def fit(self, transactions, min_support): ...
    def generate_rules(self, min_confidence): ...
    def explain(self, itemset, mode='text'): ...
    def explain_prediction(self, rule): ...
    def what_if(self, transaction, added_item): ...

class Apriori(BaseAssociation):
    def __init__(self, mode='default', verbose=False):
        self.frequent_itemsets = []
        self.rules = []
        self.mode = mode
        self.verbose = verbose

    def _support(self, itemset, transactions):
        count = sum(1 for t in transactions if set(itemset).issubset(set(t)))
        return count / len(transactions)

    def _get_candidates(self, prev_freq_sets, k):
        items = set(chain(*prev_freq_sets))
        return [tuple(sorted(c)) for c in combinations(items, k)]

    def fit(self, transactions, min_support=0.5):
        self.transactions = transactions
        item_counts = Counter(item for t in transactions for item in t)
        n = len(transactions)

        # Step 1: Get frequent 1-itemsets
        L1 = [tuple([item]) for item in item_counts if item_counts[item] / n >= min_support]
        current_L = L1
        k = 2

        if self.verbose or self.mode == 'student':
            print(f"Frequent 1-itemsets: {L1}")

        while current_L:
            self.frequent_itemsets.extend(current_L)
            candidates = self._get_candidates(current_L, k)

            current_L = []
            for candidate in candidates:
                support = self._support(candidate, transactions)
                if support >= min_support:
                    current_L.append(candidate)
                    if self.verbose:
                        print(f"Candidate {candidate} has support {support:.2f}")

            k += 1

        if self.verbose or self.mode == 'student':
            print(f"Final frequent itemsets: {self.frequent_itemsets}")

    def generate_rules(self, min_confidence=0.7):
        self.rules = []
        for itemset in self.frequent_itemsets:
            if len(itemset) < 2:
                continue
            for i in range(1, len(itemset)):
                for antecedent in combinations(itemset, i):
                    consequent = tuple(sorted(set(itemset) - set(antecedent)))
                    if not consequent:
                        continue
                    conf = self._support(itemset, self.transactions) / self._support(antecedent, self.transactions)
                    if conf >= min_confidence:
                        rule = {
                            'antecedent': antecedent,
                            'consequent': consequent,
                            'confidence': conf
                        }
                        self.rules.append(rule)

                        if self.verbose:
                            print(f"Rule: {antecedent} => {consequent} [Confidence: {conf:.2f}]")
        return self.rules

    def explain(self, itemset, mode='text'):
        if itemset not in self.frequent_itemsets:
            return f"Itemset {itemset} is not frequent."
        support = self._support(itemset, self.transactions)

        if mode == 'pseudocode':
            return f"IF all items in {itemset} appear in enough transactions (support ≥ threshold) THEN keep itemset"
        return f"Itemset {itemset} appears in {support*100:.2f}% of transactions and is considered frequent."

    def explain_prediction(self, rule):
        explanation = f"RULE: {rule['antecedent']} ⇒ {rule['consequent']}\n"
        explanation += f"Means: If a transaction contains {rule['antecedent']}, it will likely also contain {rule['consequent']}\n"
        explanation += f"Confidence: {rule['confidence']*100:.2f}%"
        return explanation

    def what_if(self, transaction, added_item):
        modified = transaction + [added_item] if added_item not in transaction else transaction
        triggered_rules = []

        for rule in self.rules:
            if set(rule['antecedent']).issubset(set(modified)):
                triggered_rules.append(rule)

        return {
            'original_transaction': transaction,
            'modified_transaction': modified,
            'newly_triggered_rules': triggered_rules
        }
