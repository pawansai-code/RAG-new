import os
import json

def extract_original_criteria(original_classes: list, target_schema_name: str, target_component_name: str):
    """Finds the class and component in the template and returns its raw Criteria node."""
    for cls in original_classes:
        name_node = next((c for c in cls.get("children", []) if c.get("title") == "SchemaName"), None)
        if name_node and name_node.get("val") == target_schema_name:
            # Find the Components node
            comp_node = next((c for c in cls.get("children", []) if "Components" in c.get("title", "")), None)
            if comp_node:
                for comp in comp_node.get("children", []):
                    comp_name_node = next((c for c in comp.get("children", []) if c.get("title") == "ComponentName"), None)
                    comp_name = comp_name_node.get("val", "") if comp_name_node else comp.get("title", "")
                    
                    if str(comp_name).lower() == str(target_component_name).lower():
                        # Found the matching component, now extract its Criteria node
                        criteria_node = next((c for c in comp.get("children", []) if c.get("title") == "Criteria"), None)
                        return criteria_node
    return None

def get_schema_name(class_node):
    for child in class_node.get("children", []):
        if child.get("title") == "SchemaName":
            return child.get("val")
    return None

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(base_dir, "2c_output_tree.json")
    template_path = os.path.join(base_dir, "SC00002 Bill Schema (2).json")
    output_path = os.path.join(base_dir, "3c_output_tree.json")

    print("--- [OpenSpec] Executing Intelligent 3C Mapping Flow ---")

    if not os.path.exists(input_path) or not os.path.exists(template_path):
        print("Error: Missing required 2C logic tree or Master Template files.")
        return
    
    print("Loading 2C Skeleton...")
    with open(input_path, 'r', encoding='utf-8') as f:
        tree_3c = json.load(f)
        
    print("Loading Master Template...")
    with open(template_path, 'r', encoding='utf-8') as f:
        master_tree = json.load(f)

    try:
        # 3C skeleton structure matching 1C/2C without metadata injection
        skeleton_schema_group = next(c for c in tree_3c[0].get("children", []) if c.get("title") == "SchemaClass")
        skeleton_classes = skeleton_schema_group.get("children", [])
        
        master_schema_group = next(c for c in master_tree[0].get("children", []) if c.get("title") == "SchemaClass")
        master_classes = master_schema_group.get("children", [])
    except StopIteration:
        print("Error: Could not parse SchemaClass grouping.")
        return

    print(f"Injecting 3rd C Criteria into Components for {len(skeleton_classes)} classes...")
    
    total_criteria_injected = 0
    for s_cls in skeleton_classes:
        schema_name = get_schema_name(s_cls)
        if not schema_name:
            continue
            
        # Find the Components node in the 2C tree
        comps_node = next((c for c in s_cls.get("children", []) if "Components" in c.get("title", "")), None)
        if not comps_node:
            continue
            
        for comp in comps_node.get("children", []):
            comp_name_node = next((c for c in comp.get("children", []) if c.get("title") == "ComponentName"), None)
            comp_name = comp_name_node.get("val", "") if comp_name_node else comp.get("title", "")
            
            # Fetch the original Criteria node
            raw_criteria_node = extract_original_criteria(master_classes, schema_name, comp_name)
            
            if raw_criteria_node:
                # Inject it directly (Option A: Pure Template Copy)
                comp["children"].append(raw_criteria_node)
                total_criteria_injected += 1

    print(f"Successfully adapted and injected {total_criteria_injected} Intelligent Criteria Rules.")
    print(f"Saving 3C schema to: {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(tree_3c, f, indent=4)
        
    print(f"\n[OpenSpec] Success! 3C Tree JSON generated and saved.")

if __name__ == "__main__":
    main()
