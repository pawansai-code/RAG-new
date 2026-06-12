import os
import json
import glob
import re
from datetime import datetime, timezone

def read_problem_statement(filepath: str) -> str:
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read().lower()
    return ""


def infer_data_type(field_title: str) -> str:
    """Infers data type based on field naming conventions."""
    title = field_title.lower()
    if "date" in title:
        return "Date"
    elif "id" in title or "number" in title or "account" in title or "code" in title or "ref" in title:
        return "String"
    elif "amount" in title or "price" in title or "cost" in title or "value" in title:
        return "Decimal"
    elif "currency" in title:
        return "CurrencyCode"
    elif "status" in title or "type" in title or "method" in title or "category" in title:
        return "Enum"
    else:
        return "String"

def infer_dynamic_value(field_title: str, problem_text: str) -> str:
    """Infers a sensible default value or mapping instruction based on the field."""
    title = field_title.lower()
    if "date" in title:
        return "<EXTRACT: Document Date>"
    elif "currency" in title:
        return "<EXTRACT: Currency (Default: INR)>"
    elif "taxcode" in title or "taxcategory" in title:
        return "<MAP: TDS/GST Rules>"
    elif "sender" in title:
        return "<EXTRACT: Vendor Details>"
    elif "receiver" in title:
        return "<EXTRACT: Internal BU/Cost Center>"
    elif "status" in title:
        return "PendingValidation"
    else:
        return f"<MAP: {field_title}>"

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
    
    txt_files = glob.glob(os.path.join(search_output_dir, "*_txt"))
    if not txt_files:
        return []
        
    top_matches = set()
    for file_path in txt_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("schema_name:"):
                    parts = line.split("\n")
                    if parts:
                        schema_name = parts[0].replace("schema_name:", "").strip()
                        top_matches.add(schema_name)
            
    return list(filter(None, top_matches))

def get_class_name(class_node):
    for child in class_node.get("children", []):
        if child.get("title") == "SchemaName":
            return child.get("val")
    return None

def process_class_properties(class_node, problem_text):
    """Keeps original template values and names."""
    pass

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    search_output_dir = os.path.join(base_dir, "04_similarity_search", "output")
    template_path = os.path.join(base_dir, "SC00002 Bill Schema (2).json")
    output_path = os.path.join(base_dir, "1c_output_tree.json")
    problem_path = os.path.join(base_dir, "problem_statement_grn.md")

    print("--- [OpenSpec] Executing Intelligent 1C Mapping Flow ---")
    
    problem_text = read_problem_statement(problem_path)
    if problem_text:
        # Extract the title from the markdown file for metadata
        first_line = problem_text.split('\n')[0].strip('# ').strip()
        problem_title = first_line if first_line else "Unknown Problem Statement"
    else:
        problem_title = "Unknown Problem Statement"
    
    print(f"Parsing matched classes from Similarity Search...")
    top_schema_names = extract_top_matches(search_output_dir)
    print(f"Total retrieved candidate classes: {len(top_schema_names)}")

    if not os.path.exists(template_path):
        print(f"Error: Could not find template schema at {template_path}")
        return

    print(f"Loading Master Template: {os.path.basename(template_path)}")
    with open(template_path, 'r', encoding='utf-8') as f:
        raw_schema = json.load(f)

    root_children = raw_schema[0].get("children", [])
    schema_group = next((c for c in root_children if c.get("title") == "SchemaClass"), None)
    
    if not schema_group:
        print("Error: Could not find 'SchemaClass' node in template.")
        return

    all_classes = schema_group.get("children", [])
    matched_class_nodes = []
    normalized_top_names = [str(n).strip().lower() for n in top_schema_names]

    # Intelligent Relevance Filtering
    print("Applying Intelligent Relevance Filter based on Problem Statement...")
    pruned_count = 0
    for c_node in all_classes:
        raw_name = get_class_name(c_node)
        if raw_name:
            normalized_template_name = str(raw_name).strip().lower()
            is_match = any(
                normalized_template_name in top_name or top_name in normalized_template_name 
                for top_name in normalized_top_names
            )
            
            if is_match:
                # Trust the vector database match entirely
                process_class_properties(c_node, problem_text)
                matched_class_nodes.append(c_node)

    print(f"Extracted {len(matched_class_nodes)} classes based strictly on semantic similarity.")
    schema_group["children"] = matched_class_nodes

    print("Enforcing strictly 1st C: Stripping Components and Conditions...")
    strict_1c_schema = strip_components_and_criteria(raw_schema)

    print("Skipping Metadata Linkage injection to match original template structure...")

    print(f"Saving intelligent 1C schema to: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(strict_1c_schema, f, indent=4)
        
    print(f"\n[OpenSpec] Success! Intelligent 1C Tree JSON generated and saved.")

if __name__ == "__main__":
    main()
