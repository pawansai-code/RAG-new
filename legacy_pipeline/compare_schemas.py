import json
import os

def count_nodes(node, counters=None, depth=0, max_depth=0):
    if counters is None:
        counters = {'total': 0, 'titles': {}, 'max_depth': 0}
    counters['total'] += 1
    counters['max_depth'] = max(counters['max_depth'], depth)
    
    if isinstance(node, dict):
        title = node.get('title', 'Unknown')
        counters['titles'][title] = counters['titles'].get(title, 0) + 1
        if 'children' in node and isinstance(node['children'], list):
            for child in node['children']:
                count_nodes(child, counters, depth + 1, counters['max_depth'])
    elif isinstance(node, list):
        for item in node:
            count_nodes(item, counters, depth + 1, counters['max_depth'])
    return counters

with open('SC00002 Bill Schema (2).json', 'r', encoding='utf-8') as f:
    orig = json.load(f)
with open('1c_output_tree.json', 'r', encoding='utf-8') as f:
    new = json.load(f)

orig_stats = count_nodes(orig)
new_stats = count_nodes(new)

print(f"Original file size: {os.path.getsize('SC00002 Bill Schema (2).json') / 1024:.2f} KB")
print(f"Generated file size: {os.path.getsize('1c_output_tree.json') / 1024:.2f} KB")
print(f"Original total nodes: {orig_stats['total']}")
print(f"Generated total nodes: {new_stats['total']}")
print(f"Original max depth: {orig_stats['max_depth']}")
print(f"Generated max depth: {new_stats['max_depth']}")

orig_components = {k: v for k, v in orig_stats['titles'].items() if 'Component' in k or 'Criteria' in k}
new_components = {k: v for k, v in new_stats['titles'].items() if 'Component' in k or 'Criteria' in k}

print(f"Original components/criteria nodes: {sum(orig_components.values())}")
print(f"Generated components/criteria nodes: {sum(new_components.values())}")
