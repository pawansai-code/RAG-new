import os
import subprocess
import argparse
import sys

def run_step(command: str, cwd: str, step_name: str):
    print(f"\n{'='*50}")
    print(f"[*] RUNNING STAGE: {step_name}")
    print(f"[*] Command: {command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, cwd=cwd)
    if result.returncode != 0:
        print(f"\n[!] ERROR: {step_name} failed with exit code {result.returncode}")
        sys.exit(result.returncode)
        
    print(f"\n[SUCCESS] {step_name} completed.")

def main():
    parser = argparse.ArgumentParser(description="Master Orchestrator for the Legacy Pipeline")
    parser.add_argument("-p", "--problem-statement", required=True, help="Path to the markdown problem statement.")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    problem_path = os.path.abspath(args.problem_statement)
    
    if not os.path.exists(problem_path):
        print(f"Error: Could not find problem statement at {problem_path}")
        sys.exit(1)

    print(f"[*] Initializing Progressive 4C Legacy Pipeline for: {os.path.basename(problem_path)}")

    # 1. Sub-Problem Generation
    json_dir = os.path.join(base_dir, "01_sub_problem_generation", "output")
    cmd_1 = f'python 01_sub_problem_generation\\pipeline.py -i "{problem_path}" -o "{json_dir}"'
    run_step(cmd_1, base_dir, "STAGE 1: Sub-Problem Decomposition")
    
    # 2. Local Vectorization (Ingest schemas AND sub-problems into ChromaDB)
    json_dir = os.path.join(base_dir, "01_sub_problem_generation", "output")
    csv_file = os.path.join(base_dir, "00_input_schemas", "schema_classes.csv")
    cmd_2 = f'python 03_vectorization\\gemini_pipeline.py -i "{csv_file}" -j "{json_dir}"'
    run_step(cmd_2, base_dir, "STAGE 2: Local Vectorization into ChromaDB")

    # 3. Similarity Search (Retrieve top schema matches)
    db_dir = os.path.join(base_dir, "chroma_gemini_db")
    search_output = os.path.join(base_dir, "04_similarity_search", "output")
    cmd_3 = f'python 04_similarity_search\\semantic_search.py -d "{db_dir}" -o "{search_output}" -k 15 --threshold 0.60'
    run_step(cmd_3, base_dir, "STAGE 3: Cosine Similarity Search")

    # 4. Intelligent 1C Mapping (Semantic filtering, type inference, dynamic values)
    cmd_4 = f'python 05_intelligent_1c_mapping.py'
    run_step(cmd_4, base_dir, "STAGE 4: Intelligent 1C Schema Generation")

    # 5. Intelligent 2C Mapping (Component injection and pruning)
    cmd_5 = f'python 06_intelligent_2c_mapping.py'
    run_step(cmd_5, base_dir, "STAGE 5: Intelligent 2C Component Generation")

    # 6. Intelligent 3C Mapping (Criteria injection)
    cmd_6 = f'python 07_intelligent_3c_mapping.py'
    run_step(cmd_6, base_dir, "STAGE 6: Intelligent 3C Criteria Generation")

    # 7. Evaluate Cosine Similarity (Compare generated tree vs original schema)
    # cmd_7 = f'python 06_evaluate_1c_similarity.py'
    # run_step(cmd_7, base_dir, "STAGE 7: Evaluation & Similarity Scoring")

    print(f"\n{'='*50}")
    print("[*] PIPELINE COMPLETE!")
    print(f"[*] Target 1C UI Tree: {os.path.join(base_dir, '1c_output_tree.json')}")
    print(f"[*] Target 2C Logic Tree: {os.path.join(base_dir, '2c_output_tree.json')}")
    print(f"[*] Target 3C Rules Tree: {os.path.join(base_dir, '3c_output_tree.json')}")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    main()
