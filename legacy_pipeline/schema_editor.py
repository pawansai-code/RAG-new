import json
import os
import shutil
import time
import re
from datetime import datetime
import google.generativeai as genai
# Initialize Gemini Client
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
# We use gemini-2.5-flash for incredibly fast and cheap structured JSON outputs
model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})

# ==========================================
# FILE UTILITIES
# ==========================================

def load_tree(filepath):
    """Loads the massive 1MB JSON tree safely."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tree(filepath, tree):
    """Saves the modified tree back to the disk and creates a backup."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy(filepath, backup_path)
    print(f"\n[*] Backup created at: {backup_path}")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(tree, f, indent=4)
    print(f"[*] Tree successfully saved to: {filepath}\n")

def find_schema_class_container(node):
    """Recursively searches for the array that contains the SchemaClasses."""
    if isinstance(node, dict):
        if "children" in node:
            for child in node["children"]:
                if isinstance(child, dict) and child.get("title", "").startswith("#SchemaClass#"):
                    return node["children"]
            return find_schema_class_container(node["children"])
    elif isinstance(node, list):
        for item in node:
            res = find_schema_class_container(item)
            if res is not None:
                return res
    return None

def call_gemini_with_retry(prompt, max_retries=3):
    """Wraps Gemini API calls with an automatic retry and sleep mechanism for 429 Quota Exceeded limits."""
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "Quota exceeded" in error_str:
                wait_time = 30.0 # Default 30s
                # Try to extract exact wait time if Google provides it in the error
                match = re.search(r"retry in (\d+\.?\d*)s", error_str)
                if match:
                    wait_time = float(match.group(1)) + 2.0
                
                print(f"[!] Rate Limit Hit (429). Sleeping for {wait_time:.1f} seconds (Attempt {attempt+1}/{max_retries})...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries exceeded for Gemini API.")

# ==========================================
# GEMINI LLM ENGINES
# ==========================================

def validate_schema_node(node, expected_title=None):
    """Validates that the LLM output is a structurally sound SchemaClass."""
    if not isinstance(node, dict):
        print("[X] Validation Error: Root is not a JSON object.")
        return False
    if "title" not in node or "children" not in node:
        print("[X] Validation Error: Missing core architectural keys ('title', 'children').")
        return False
    if expected_title and node.get("title") != expected_title:
        print(f"[X] Validation Error: Title was maliciously or accidentally changed to '{node.get('title')}'.")
        return False
    if not isinstance(node["children"], list):
        print("[X] Validation Error: 'children' key must be an array.")
        return False
    return True

def parse_llm_json(text):
    """Safely extracts JSON from markdown blocks and parses it."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())

def gemini_llm_base(prompt, target_id):
    """Uses Gemini to generate the initial empty SchemaClass base structure."""
    full_prompt = f"""You are a senior data architect generating rigid JSON structures.
You must output ONLY valid JSON representing a single SchemaClass object. Do not include markdown formatting like ```json.
The object must strictly follow this structure:
{{
  "title": "{target_id}",
  "technicalName": "{target_id}",
  "children": [
    {{ "title": "SchemaName", "technicalName": "SchemaName", "val": "<derive_from_prompt>" }},
    {{ "title": "DataSource", "technicalName": "DataSource", "val": "<derive_from_prompt>" }},
    {{
      "title": "Components", "technicalName": "Components",
      "children": []
    }},
    {{
      "title": "Criteria", "technicalName": "Criteria",
      "children": []
    }},
    {{
      "title": "Conditions", "technicalName": "Conditions",
      "children": []
    }}
  ]
}}
Ensure the JSON is strictly formatted and valid.

USER PROMPT: {prompt}
"""
    try:
        response = call_gemini_with_retry(full_prompt)
        result = parse_llm_json(response.text)
        if validate_schema_node(result, expected_title=target_id):
            print("[LLM] Successfully generated Base SchemaClass via Gemini.")
            return result
        else:
            print("[X] Base generation aborted due to schema validation failure.")
            return {"title": target_id, "technicalName": target_id, "children": []}
    except json.decoder.JSONDecodeError as e:
        print(f"[X] Gemini JSON Decode Error: {e}\n[X] The LLM generated malformed JSON.")
        return {"title": target_id, "technicalName": target_id, "children": []}
    except Exception as e:
        print(f"[X] Gemini API Error: {e}")
        return {"title": target_id, "technicalName": target_id, "children": []}

def gemini_llm_modify(target_node, prompt):
    """Uses Gemini to intelligently apply omni-prompt modifications across the whole SchemaClass."""
    system_prompt = """You are a JSON schema editor.
You are given a JSON object representing a single SchemaClass node.
The user will provide a natural language instruction to modify it.
Apply their modification and return ONLY the completely updated valid JSON object.
You have ABSOLUTE PERMISSION to add, modify, empty, or completely DELETE any elements, arrays, or keys inside this JSON if the user instructs you to.
Do not wrap it in markdown.
"""
    full_prompt = f"""{system_prompt}

Existing JSON:
{json.dumps(target_node, indent=2)}

Instruction:
{prompt}

Apply the instruction and return the full updated JSON.
"""
    try:
        response = call_gemini_with_retry(full_prompt)
        result = parse_llm_json(response.text)
        if validate_schema_node(result, expected_title=target_node.get("title")):
            print("[LLM] Successfully applied JSON modification via Gemini.")
            return result
        else:
            print("[X] Modification aborted due to schema validation failure.")
            return target_node
    except json.decoder.JSONDecodeError as e:
        print(f"[X] Gemini JSON Decode Error: {e}\n[X] The LLM generated malformed JSON. Changes aborted.")
        return target_node
    except Exception as e:
        print(f"[X] Gemini API Error: {e}")
        return target_node

def gemini_intent_router(prompt):
    """Parses a natural language prompt to determine if it's an ADD, MODIFY, DELETE, or EXIT intent."""
    system_prompt = """You are an Intent Router for a JSON schema editor.
Analyze the user's natural language command and classify their intent.
Available Intents:
- "ADD": They want to create a brand new SchemaClass. (Words like 'create', 'build', 'new')
- "MODIFY": They want to change, edit, update, or add components INSIDE an existing SchemaClass.
- "DELETE": They want to delete an entire existing SchemaClass.
- "EXIT": They want to close, quit, or exit the application.

If the intent is MODIFY or DELETE, you MUST extract the Target ID they are referring to (e.g., "#SchemaClass#5"). If they don't specify an exact ID but refer to a number, format it as #SchemaClass#N. If no ID is specified, return "UNKNOWN" for target_id.
If the intent is ADD, and they specify they want to insert it AFTER a specific SchemaClass (e.g., "Create a new schema after #SchemaClass#10"), set target_id to that ID. If they don't specify an insertion point, set target_id to "NEW".

You MUST output ONLY valid JSON exactly matching these keys:
{
    "intent": "ADD" | "MODIFY" | "DELETE" | "EXIT" | "UNKNOWN",
    "target_id": "<extracted_id_or_NEW>"
}
Do not include markdown formatting.
"""
    try:
        response = call_gemini_with_retry(f"{system_prompt}\n\nUSER COMMAND: {prompt}")
        result = json.loads(response.text.strip('```json').strip('```').strip())
        return result
    except Exception as e:
        print(f"[X] Gemini Router Error: {e}")
        return {"intent": "UNKNOWN", "target_id": "UNKNOWN"}

# ==========================================
# MAIN INTERACTIVE WIZARD
# ==========================================

def main():
    file_path = "3c_output_tree.json"
    if not os.path.exists(file_path):
        print(f"[X] Error: {file_path} not found in the current directory.")
        return
        
    print(f"[*] Loading massive JSON tree into memory...")
    tree = load_tree(file_path)
    schema_classes = find_schema_class_container(tree)
    
    if schema_classes is None:
        print("[X] Error: Could not locate the 'SchemaClass' node in the legacy tree.")
        return
        
    print(f"[*] Loaded successfully. Found {len(schema_classes)} existing SchemaClasses.")

    while True:
        print("\n========================================")
        print("  AGENTIC SCHEMA EDITOR (Zero-Menu)     ")
        print("========================================")
        print("Agent: How can I help you modify the Schema Tree today?")
        
        prompt = input("You: ").strip()
        if not prompt:
            continue
            
        print("[*] Routing Intent...")
        route = gemini_intent_router(prompt)
        intent = route.get("intent", "UNKNOWN")
        target_id = route.get("target_id", "UNKNOWN")
        
        if intent == "EXIT":
            print("Exiting...")
            break
            
        elif intent == "DELETE":
            if target_id == "UNKNOWN":
                print("[X] Could not determine which SchemaClass to delete. Please specify the ID (e.g., Delete #SchemaClass#2).")
                continue
            original_len = len(schema_classes)
            schema_classes[:] = [sc for sc in schema_classes if sc.get("title") != target_id]
            if len(schema_classes) < original_len:
                print(f"[+] Sliced out and deleted {target_id}.")
                save_tree(file_path, tree)
            else:
                print(f"[X] Target '{target_id}' not found in the tree.")
                
        elif intent in ["ADD", "CREATE"]:
            insert_index = len(schema_classes)
            if target_id != "NEW" and target_id != "UNKNOWN":
                for i, sc in enumerate(schema_classes):
                    if sc.get("title") == target_id:
                        insert_index = i + 1
                        break
                        
            new_target_id = f"#SchemaClass#{len(schema_classes) + 1}"
            print(f"\n--- [PROGRESSIVE 4C GENERATOR: {new_target_id}] ---")
            if insert_index < len(schema_classes):
                print(f"[*] Will insert {new_target_id} immediately AFTER {target_id}")
            
            # Step 1: Base
            prompt1 = input(f"\n[Step 1/4] Base Configuration\nDescribe the high-level purpose for {new_target_id}:\n> ").strip()
            print(f"[*] Generating Base Container...")
            new_schema = gemini_llm_base(prompt1, new_target_id)
            
            # Step 2: Components
            prompt2 = input(f"\n[Step 2/4] Components\nDescribe the Components (or leave blank to skip):\n> ").strip()
            if prompt2:
                print(f"[*] Generating Components...")
                new_schema = gemini_llm_modify(new_schema, f"Add these components: {prompt2}")
                
            # Step 3: Criteria
            prompt3 = input(f"\n[Step 3/4] Criteria\nDescribe the Criteria (or leave blank to skip):\n> ").strip()
            if prompt3:
                print(f"[*] Generating Criteria...")
                new_schema = gemini_llm_modify(new_schema, f"Add these criteria: {prompt3}")
                
            # Step 4: Conditions
            prompt4 = input(f"\n[Step 4/4] Conditions\nDescribe the Conditions (or leave blank to skip):\n> ").strip()
            if prompt4:
                print(f"[*] Generating Conditions...")
                new_schema = gemini_llm_modify(new_schema, f"Add these conditions: {prompt4}")
                
            schema_classes.insert(insert_index, new_schema)
            save_tree(file_path, tree)
            print(f"\n[+] Successfully completed Progressive Generation for {new_target_id}!")
            
        elif intent == "MODIFY":
            if target_id == "UNKNOWN":
                print("[X] Could not determine which SchemaClass to modify. Please specify the ID (e.g., Modify #SchemaClass#3 to add X).")
                continue
                
            target_index = next((i for i, sc in enumerate(schema_classes) if sc.get("title") == target_id), None)
            
            if target_index is None:
                print(f"[X] Target '{target_id}' not found.")
                continue
                
            isolated_node = schema_classes[target_index]
            
            print(f"\n--- [LLM ENGINE] (Live via Gemini) ---")
            print(f"Isolating Node: {target_id}")
            print(f"Extraction Size: {len(json.dumps(isolated_node))} bytes (out of 1MB total)")
            print(f"Executing Omni-Prompt: '{prompt}'")
            print(f"-----------------------------------\n")
            
            modified_node = gemini_llm_modify(isolated_node, prompt)
            schema_classes[target_index] = modified_node
            save_tree(file_path, tree)
            
        else:
            print("[X] I didn't quite understand that. Please try rephrasing your command (e.g., 'Modify #SchemaClass#1 to add X' or 'Delete #SchemaClass#2').")

if __name__ == "__main__":
    main()
