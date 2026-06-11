import os
import json
import re
import argparse
from typing import List, Dict, Any

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError:
    print("Please install the required packages: pip install google-generativeai python-dotenv")
    exit(1)

# Load environment variables from .env file
load_dotenv()

def parse_header(text: str) -> tuple[str, str, str]:
    """Extracts ID, Project Name, and returns the full text."""
    header_match = re.search(r'^(?:#\s*)?([A-Z0-9]+):\s*(.*?)$', text, re.MULTILINE)
    problem_id = header_match.group(1) if header_match else "UNKNOWN_ID"
    project_name = header_match.group(2) if header_match else "Unknown Project"
    return problem_id, project_name, text

def decompose_with_llm(problem_statement: str, target_count: int = 10) -> List[str]:
    """Uses Gemini API to decompose the problem statement into granular sub-problems."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is missing from environment.")
        exit(1)
        
    genai.configure(api_key=api_key)
    # Use gemini-2.5-flash for JSON generation
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = f"""
    I will provide you with a problem statement for a software system.
    Your task is to decompose this problem statement into AT LEAST {target_count} highly granular, distinct functional requirements or sub-problems.
    
    Problem Statement:
    {problem_statement}
    
    IMPORTANT: Return your response strictly as a JSON object containing a single key "sub_problems" which maps to an array of strings. Do not include markdown formatting.
    Example format:
    {{
      "sub_problems": [
        "Validate incoming vendor bills against purchase orders",
        "Extract line item details from the vendor bill",
        "Match bill quantities with received goods receipts",
        "Calculate GST on individual bill items"
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        data = json.loads(response_text)
        
        sub_problems = data.get("sub_problems", [])
        if not isinstance(sub_problems, list) or len(sub_problems) == 0:
            raise ValueError("LLM did not return a valid 'sub_problems' array.")
            
        return sub_problems
    except Exception as e:
        print(f"Failed to parse LLM response. Error: {e}")
        return []

def generate_embedding_jsons(problem_id: str, project_name: str, sub_problems: List[str]) -> List[Dict[str, Any]]:
    """Converts the parsed sub-problems into individual JSON objects for embeddings."""
    json_objects = []
    for i, sp in enumerate(sub_problems, 1):
        obj = {
            "id": f"{problem_id}_SUB_{i:03d}",
            "parent_id": problem_id,
            "project_name": project_name,
            "sub_problem_statement": sp,
            "context": f"Requirement extracted from {project_name} problem statement.",
            "metadata": {
                "source_type": "llm_problem_statement_decomposition",
                "embedding_text": f"{project_name}: {sp}"
            }
        }
        json_objects.append(obj)
        
    return json_objects

def process_file(input_filepath: str, output_dir: str):
    with open(input_filepath, 'r', encoding='utf-8') as f:
        text = f.read()
        
    problem_id, project_name, content = parse_header(text)
    
    print(f"Analyzing {input_filepath} with Groq API (Llama3-70b) to generate 10+ sub-problems...")
    sub_problems = decompose_with_llm(content, target_count=10)
    
    if not sub_problems:
        print(f"Warning: No sub-problems extracted from {input_filepath}")
        return
        
    json_objects = generate_embedding_jsons(problem_id, project_name, sub_problems)
    
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, f"{problem_id}_embeddings.json")
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(json_objects, f, indent=4)
        
    print(f"Processed {input_filepath} -> {len(json_objects)} sub-problems saved to {output_filename}")

def main():
    parser = argparse.ArgumentParser(description="Process problem statements into embedding JSONs using Groq LLM.")
    parser.add_argument("--input", "-i", type=str, help="Input markdown file containing the problem statement.")
    parser.add_argument("--input-dir", "-d", type=str, help="Input directory containing multiple markdown files.")
    parser.add_argument("--output", "-o", type=str, default="./output", help="Output directory for JSON files.")
    
    args = parser.parse_args()
    
    if args.input:
        process_file(args.input, args.output)
    elif args.input_dir:
        for filename in os.listdir(args.input_dir):
            if filename.endswith(".md") or filename.endswith(".txt"):
                filepath = os.path.join(args.input_dir, filename)
                process_file(filepath, args.output)
    else:
        print("Please provide either --input or --input-dir")

if __name__ == "__main__":
    main()
