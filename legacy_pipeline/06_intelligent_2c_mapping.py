import os
import json
import re
from datetime import datetime, timezone

def read_problem_statement(filepath: str) -> str:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().lower()
    return ""

def adapt_expression(expr: str, comp_name: str) -> str:
    """Dynamically adapts component expressions to make them intelligent."""
    expr_lower = str(expr).lower()
    comp_lower = str(comp_name).lower()
    
    if "tax" in comp_lower or "gst" in comp_lower or "tds" in comp_lower:
        return "<CALC: BaseAmount * DynamicTaxRate>"
    elif "cost" in comp_lower or "allocation" in comp_lower:
        return "<CALC: AllocatedPercentage * TotalCost>"
    elif "currency" in expr_lower:
        return "<CALC: Amount * ExchangeRate>"
    elif "quantity" in expr_lower:
        return "<CALC: ReceivedQty - RejectedQty>"
    
    return expr

def filter_and_clean_components(components_list: list, problem_text: str) -> list:
    """Filters irrelevant components and strips out 3rd C (Criteria)."""
    cleaned_components = []
    
    for comp in components_list:
        # Check component title/name for relevance
        comp_name_node = next((c for c in comp.get("children", []) if c.get("title") == "ComponentName"), None)
        comp_name = comp_name_node.get("val", "") if comp_name_node else comp.get("title", "")
        
        name_lower = str(comp_name).lower()
        
        # Pruning heuristics: if it's explicitly irrelevant to billing/provisioning
        if "irrelevant" in name_lower or "deprecated" in name_lower:
            continue
            
        # Strip Criteria (3rd C) and adapt expressions
        new_children = []
        for child in comp.get("children", []):
            child_title = child.get("title", "")
            
            # Delete 3rd C entirely
            if "Criteria" in child_title:
                continue
                
            # Adapt expressions dynamically
            if child_title == "ComponentExpr":
                child["val"] = adapt_expression(child.get("val", ""), comp_name)
                
            new_children.append(child)
            
        comp["children"] = new_children
        cleaned_components.append(comp)
        
    return cleaned_components

def extract_original_components(original_classes: list, target_schema_name: str):
    """Finds the class in the template and returns its raw Components node."""
    for cls in original_classes:
        name_node = next((c for c in cls.get("children", []) if c.get("title") == "SchemaName"), None)
        if name_node and name_node.get("val") == target_schema_name:
            # Find the Components node
            comp_node = next((c for c in cls.get("children", []) if "Components" in c.get("title", "")), None)
            return comp_node
    return None

def get_schema_name(class_node):
    for child in class_node.get("children", []):
        if child.get("title") == "SchemaName":
            return child.get("val")
    return None

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    skeleton_path = os.path.join(base_dir, "1c_output_tree.json")
    template_path = os.path.join(base_dir, "SC00002 Bill Schema (2).json")
    output_path = os.path.join(base_dir, "2c_output_tree.json")
    problem_path = os.path.join(base_dir, "problem_statement_grn.md")

    print("--- [OpenSpec] Executing Intelligent 2C Mapping Flow ---")

    if not os.path.exists(skeleton_path) or not os.path.exists(template_path):
        print("Error: Missing required 1C skeleton or Master Template files.")
        return

    problem_text = read_problem_statement(problem_path)
    
    print("Loading 1st C Skeleton...")
    with open(skeleton_path, 'r', encoding='utf-8') as f:
        skeleton_tree = json.load(f)
        
    print("Loading Master Template...")
    with open(template_path, 'r', encoding='utf-8') as f:
        master_tree = json.load(f)

    # Extract class lists
    try:
        # skeleton structure: [Metadata, SchemaClass] or just [SchemaClass] if no metadata.
        # find SchemaClass
        skeleton_schema_group = next(c for c in skeleton_tree[0].get("children", []) if c.get("title") == "SchemaClass")
        skeleton_classes = skeleton_schema_group.get("children", [])
        
        master_schema_group = next(c for c in master_tree[0].get("children", []) if c.get("title") == "SchemaClass")
        master_classes = master_schema_group.get("children", [])
    except StopIteration:
        print("Error: Could not parse SchemaClass grouping.")
        return

    print(f"Injecting 2nd C Components into {len(skeleton_classes)} classes...")
    
    total_components_injected = 0
    for s_cls in skeleton_classes:
        schema_name = get_schema_name(s_cls)
        if not schema_name:
            continue
            
        raw_comp_node = extract_original_components(master_classes, schema_name)
        
        if raw_comp_node:
            raw_comps = raw_comp_node.get("children", [])
            
            # Prune and clean
            cleaned_comps = filter_and_clean_components(raw_comps, problem_text)
            
            # Reconstruct the Components node
            new_comp_node = {
                "title": "Components",
                "technicalName": "Components",
                "children": cleaned_comps
            }
            
            # Inject into skeleton class
            s_cls["children"].append(new_comp_node)
            total_components_injected += len(cleaned_comps)

    # Update Metadata
    metadata_node = next((c for c in skeleton_tree[0].get("children", []) if c.get("title") == "Metadata"), None)
    if metadata_node:
        metadata_node["children"].append({
            "title": "PipelineStage", "val": "2C Generation", "dataType": "String"
        })

    print(f"Successfully adapted and injected {total_components_injected} Intelligent Components.")
    print(f"Saving 2C schema to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(skeleton_tree, f, indent=4)
        
    print(f"\n[OpenSpec] Success! 2C Tree JSON generated and saved.")

if __name__ == "__main__":
    main()
