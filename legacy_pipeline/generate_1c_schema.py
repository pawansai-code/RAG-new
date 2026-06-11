import json
import os
import argparse

def strip_components_and_criteria(node):
    """
    Recursively walks the JSON tree and strips out any nodes
    that represent Components, Criteria, or Calculations (2nd, 3rd, 4th C).
    """
    if isinstance(node, dict):
        # We want to keep the current node but filter its children
        cleaned_node = {}
        for key, value in node.items():
            if key == "children" and isinstance(value, list):
                # Filter out children that are strictly beyond the 1st C
                filtered_children = []
                for child in value:
                    title = child.get("title", "")
                    
                    # 1st C Rule Enforcement: Drop Components, Criteria, and their dynamic titles
                    if "Components" in title or "Criteria" in title:
                        continue
                        
                    # Recursively clean the allowed children
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

def main():
    parser = argparse.ArgumentParser(description="Strict 1st C Generator")
    parser.add_argument("-s", "--schema", default="SC00002 Bill Schema (2).json", help="Input schema path")
    parser.add_argument("-o", "--output", default="1c_strict_output.json", help="Output strictly 1C schema path")
    args = parser.parse_args()

    input_path = args.schema
    output_path = args.output

    if not os.path.exists(input_path):
        print(f"Error: Cannot find input schema at {input_path}")
        return

    print(f"Loading raw schema: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_schema = json.load(f)

    print("Enforcing 1st C Rule: Stripping Components, Conditions, and Calculations...")
    strict_1c_schema = strip_components_and_criteria(raw_schema)

    print(f"Saving strictly 1C schema to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(strict_1c_schema, f, indent=4)
        
    print("Success! The schema now contains ONLY the Classes.")

if __name__ == "__main__":
    main()
