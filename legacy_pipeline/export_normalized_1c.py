import json
import os

def normalize_tree(input_path: str, output_path: str):
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        tree = json.load(f)

    normalized_schemas = []
    
    try:
        # Navigate to SchemaClasses array
        root_children = tree[0].get("children", [])
        schema_classes_node = next((node for node in root_children if node.get("title") == "SchemaClasses"), None)
        
        if schema_classes_node:
            for s_class in schema_classes_node.get("children", []):
                props = s_class.get("children", [])
                
                # Extract clean key-value pairs
                schema_obj = {}
                for p in props:
                    key = p.get("title")
                    val = p.get("val")
                    if key and val is not None:
                        schema_obj[key] = val
                        
                normalized_schemas.append(schema_obj)
                
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(normalized_schemas, f, indent=4)
            
        print(f"Success! Normalized {len(normalized_schemas)} schemas to {output_path}")
        
    except Exception as e:
        print(f"Error parsing tree: {e}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    in_file = os.path.join(base_dir, "1c_output_tree.json")
    out_file = os.path.join(base_dir, "1c_normalized.json")
    normalize_tree(in_file, out_file)
