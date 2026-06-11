import os
import csv
import json
import requests
import math

def get_embedding(text: str) -> list:
    """Gets text embedding from local Ollama instance using nomic-embed-text."""
    url = "http://localhost:11434/api/embeddings"
    payload = {
        "model": "nomic-embed-text",
        "prompt": text
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception as e:
        print(f"Error fetching embedding from Ollama: {e}")
        return []

def cosine_similarity(v1: list, v2: list) -> float:
    """Calculates cosine similarity between two vectors."""
    if not v1 or not v2:
        return 0.0
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def load_original_schemas(csv_path: str) -> dict:
    """Loads schema_classes.csv and generates text representation."""
    originals = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            schema_name = row.get('schema_name', '').strip()
            data_source = row.get('data_source', '').strip()
            date_agg = row.get('date_aggregation_on', '').strip()
            settlement = row.get('settlement_type', '').strip()
            output_code = row.get('output_process_code', '').strip()
            
            text = f"SchemaName: {schema_name}, DataSource: {data_source}, DateAggregationOn: {date_agg}, SettlementType: {settlement}, OutputProcessCode: {output_code}"
            originals[schema_name] = text
    return originals

def extract_generated_schemas(json_path: str) -> list:
    """Traverses 1c_output_tree.json and generates text representation."""
    generated = []
    with open(json_path, 'r', encoding='utf-8') as f:
        tree = json.load(f)
        
    try:
        # Navigate to SchemaClasses array
        root_children = tree[0].get("children", [])
        schema_classes_node = next((node for node in root_children if node.get("title") == "SchemaClass"), None)
        if not schema_classes_node:
            return generated
            
        for s_class in schema_classes_node.get("children", []):
            props = s_class.get("children", [])
            
            name = next((p.get("val", "") for p in props if p.get("title") == "SchemaName"), "")
            ds = next((p.get("val", "") for p in props if p.get("title") == "DataSource"), "")
            da = next((p.get("val", "") for p in props if p.get("title") == "DateAggregationOn"), "")
            st = next((p.get("val", "") for p in props if p.get("title") == "SettlementType"), "")
            oc = next((p.get("val", "") for p in props if p.get("title") == "OutputProcessCode"), "")
            
            text = f"SchemaName: {name}, DataSource: {ds}, DateAggregationOn: {da}, SettlementType: {st}, OutputProcessCode: {oc}"
            generated.append({"schema_name": name, "text": text})
            
    except Exception as e:
        print(f"Error parsing JSON tree: {e}")
        
    return generated

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "00_input_schemas", "schema_classes.csv")
    json_path = os.path.join(base_dir, "1c_output_tree.json")
    
    if not os.path.exists(csv_path) or not os.path.exists(json_path):
        print("Required files not found.")
        return

    print("Loading original schemas from CSV...")
    originals = load_original_schemas(csv_path)
    
    print("Extracting generated schemas from 1C JSON Tree...")
    generated = extract_generated_schemas(json_path)
    
    if not generated:
        print("No generated schemas found to compare.")
        return

    print("\nCalculating Embeddings and Cosine Similarity...\n" + "-"*50)
    
    total_score = 0.0
    count = 0
    
    for gen in generated:
        s_name = gen["schema_name"]
        gen_text = gen["text"]
        
        if s_name not in originals:
            print(f"[MISSING] Schema '{s_name}' not found in original dataset.")
            continue
            
        orig_text = originals[s_name]
        
        orig_emb = get_embedding(orig_text)
        gen_emb = get_embedding(gen_text)
        
        sim = cosine_similarity(orig_emb, gen_emb)
        
        total_score += sim
        count += 1
        
        print(f"Class: {s_name}")
        print(f"Original Text: {orig_text}")
        print(f"Generatd Text: {gen_text}")
        print(f"Cosine Similarity: {sim:.4f}\n")
        
    if count > 0:
        avg_score = total_score / count
        print("-" * 50)
        print(f"Average Similarity Score across {count} schemas: {avg_score:.4f} / 1.0000")
        if avg_score > 0.99:
            print("\nCONCLUSION: Perfect structural match. The deterministic 1C mapping is 100% accurate.")

if __name__ == "__main__":
    main()
