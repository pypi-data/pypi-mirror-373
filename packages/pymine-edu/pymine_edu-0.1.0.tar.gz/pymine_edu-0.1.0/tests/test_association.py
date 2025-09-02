# tests/test_association.py

import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer
from pymine.association import Apriori

print("\n=== ASSOCIATION RULE MINING WITH IRIS DATASET ===")

# Load the Iris.csv file from the tests folder
df = pd.read_csv("tests/Iris.csv")

# Drop ID column if present
if 'Id' in df.columns:
    df.drop(columns=['Id'], inplace=True)

# Discretize continuous features into bins to make them categorical (necessary for Apriori)
features = df.drop(columns=['Species'])
kbins = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
binned_features = kbins.fit_transform(features)

# Map bins to string labels
binned_df = pd.DataFrame(binned_features, columns=features.columns)
binned_df = binned_df.astype(int).astype(str)

# Convert each row into a transaction (e.g., 'sepal_length=low')
transactions = []
for i, row in binned_df.iterrows():
    t = [f"{col}={val}" for col, val in row.items()]
    t.append(f"species={df['Species'].iloc[i]}")  # include class label as item
    transactions.append(t)

# Initialize and train the Apriori model
model = Apriori(mode='student', verbose=True)
model.fit(transactions, min_support=0.4)

# Generate association rules
rules = model.generate_rules(min_confidence=0.7)

# Test explanation of a frequent itemset
if model.frequent_itemsets:
    sample_itemset = model.frequent_itemsets[0]
    print("\nExplain Frequent Itemset:")
    print(model.explain(sample_itemset))
    print(model.explain(sample_itemset, mode='pseudocode'))

# Test explanation of a sample rule
if rules:
    print("\nExplain Prediction:")
    print(model.explain_prediction(rules[0]))

# Test what-if analysis
sample_transaction = transactions[0][:-1]  # remove label to simulate new customer
added_item = 'species=Iris-setosa'
print("\nWhat-If Analysis:")
what_if_result = model.what_if(sample_transaction, added_item)
print(what_if_result)

print("\n=== ASSOCIATION TEST COMPLETED ===")
