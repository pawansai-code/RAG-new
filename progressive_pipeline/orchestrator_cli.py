import argparse
import json
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from state_manager import StateManager
from node_executor import NodeExecutor

def load_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_all(config, executor):
    global_prompt = config["global_config"]["main_prompt"]
    for node in config["schema_classes"]:
        executor.compute_schema_class(node, global_prompt)

def compute_node(config, executor, target_schema_id):
    global_prompt = config["global_config"]["main_prompt"]
    target_node = None
    for node in config["schema_classes"]:
        if node["schema_id"] == target_schema_id:
            target_node = node
            break
            
    if not target_node:
        print(f"Error: Node {target_schema_id} not found in configuration.")
        return

    executor.compute_schema_class(target_node, global_prompt)

def save_final_output(state_manager):
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extraction_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    cache = state_manager.get_full_cache()
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)
        
    print(f"\n==============================================")
    print(f"[+] PIPELINE COMPLETE")
    print(f"[+] Final output successfully saved to:")
    print(f"    -> {filepath}")
    print(f"==============================================\n")

def main():
    parser = argparse.ArgumentParser(description="Progressive HITL RAG Orchestrator")
    parser.add_argument("--config", required=True, help="Path to the JSON configuration file")
    parser.add_argument("--run-all", action="store_true", help="Execute all steps progressively")
    parser.add_argument("--compute-node", type=str, help="Execute a specific SchemaClass by ID (Targeted Regeneration)")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the conversational cache before running")

    args = parser.parse_args()

    config = load_config(args.config)
    # Store cache in the progressive_pipeline directory
    cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "session_cache.json")
    state_manager = StateManager(cache_file=cache_path)
    
    if args.clear_cache:
        state_manager.clear_cache()
        
    executor = NodeExecutor(state_manager=state_manager, use_mock_llm=True)

    if args.run_all:
        print("Starting Progressive Execution...")
        run_all(config, executor)
        save_final_output(state_manager)
    elif args.compute_node:
        print(f"Starting Targeted Regeneration for {args.compute_node}...")
        compute_node(config, executor, args.compute_node)
        save_final_output(state_manager)
    else:
        print("Please specify --run-all or --compute-node <ID>.")

if __name__ == "__main__":
    main()
