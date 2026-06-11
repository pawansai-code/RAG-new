import os
import json
import glob

def strip_components_and_criteria(node):
    """
    Recursively walks the JSON tree and strips out any nodes
    that represent Components, Criteria, or Calculations (2nd, 3rd, 4th C).
    """
    if isinstance(node, dict):
        cleaned_node = {}
        for key, value in node.items():
            if key == "children" and isinstance(value, list):
                filtered_children = []
                for child in value:
                    title = child.get("title", "")
                    # 1st C Rule Enforcement
                    if "Components" in title or "Criteria" in title:
                        continue
                    cleaned_child = strip_components_and_criteria(child)
                    if cleaned_child is not None:
                        filtered_children.append(cleaned_child)
                if filtered_children:
                    cleaned_node["children"] = filtered_children
            else:
                cleaned_node[key] = value
        return cleaned_node
    elif isinstance(node, list):
        return [strip_components_and_criteria(item) for item in node if item is not None]
    return node

def extract_top_matches(search_output_dir: str) -> list:
    """Reads the text output from similarity search and returns matched schema names."""
    if not os.path.exists(search_output_dir):
        return []
    
    # semantic_search.py sanitizes filename dots to underscores, yielding *_txt files
    txt_files = glob.glob(os.path.join(search_output_dir, "*_txt"))
    if not txt_files:
        return []
        
    top_matches = set()
    for file_path in txt_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("schema_name:"):
                    # line format: schema_name: ReverseCA\nsource_schema: SC00002...
                    parts = line.split("\\n")
                    if parts:
                        schema_name_part = parts[0]
                        schema_name = schema_name_part.replace("schema_name:", "").strip()
                        top_matches.add(schema_name)
            
    return list(filter(None, top_matches))

def get_class_name(class_node):
    """Finds the 'SchemaName' value inside a class node."""
    children = class_node.get("children", [])
    for child in children:
        if child.get("title") == "SchemaName":
            return child.get("val")
    return None

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    search_output_dir = os.path.join(base_dir, "04_similarity_search", "output")
    template_path = os.path.join(base_dir, "SC00002 Bill Schema (2).json")
    output_path = os.path.join(base_dir, "1c_output_tree.json")

    print("--- [OpenSpec] Executing End-to-End 1C Flow ---")
    print(f"Parsing matched classes from Similarity Search...")
    top_schema_names = extract_top_matches(search_output_dir)
    print(f"Matched classes: {top_schema_names}")

    if not os.path.exists(template_path):
        print(f"Error: Could not find template schema at {template_path}")
        return

    print(f"Loading Master Template: {os.path.basename(template_path)}")
    with open(template_path, 'r', encoding='utf-8') as f:
        raw_schema = json.load(f)

    # Find the SchemaClass array
    root_children = raw_schema[0].get("children", [])
    schema_group = next((c for c in root_children if c.get("title") == "SchemaClass"), None)
    
    if not schema_group:
        print("Error: Could not find 'SchemaClass' node in template.")
        return

    all_classes = schema_group.get("children", [])
    matched_class_nodes = []

    normalized_top_names = [str(n).strip().lower() for n in top_schema_names]

    for c_node in all_classes:
        raw_name = get_class_name(c_node)
        if raw_name:
            normalized_template_name = str(raw_name).strip().lower()
            
            is_match = any(
                normalized_template_name in top_name or top_name in normalized_template_name 
                for top_name in normalized_top_names
            )
            
            if is_match:
                matched_class_nodes.append(c_node)

    if not matched_class_nodes:
        print("Warning: No matched classes found in the master template. Outputting empty tree.")
        schema_group["children"] = []
    else:
        print(f"Extracted {len(matched_class_nodes)} strictly mapped classes from template.")
        schema_group["children"] = matched_class_nodes

    print("Enforcing strictly 1st C: Stripping Components and Conditions...")
    strict_1c_schema = strip_components_and_criteria(raw_schema)

    print(f"Saving strictly mapped 1C schema to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(strict_1c_schema, f, indent=4)
        
    print(f"\n[OpenSpec] Success! 1C Tree JSON strictly generated from template and saved.")

if __name__ == "__main__":
    main()
