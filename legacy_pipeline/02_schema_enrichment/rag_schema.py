import pandas as pd
from groq import Groq
import json
import time
import argparse
import os
from dotenv import load_dotenv

# Load the environment variables from the .env file
load_dotenv()

# Initialize the Groq client
API_KEY = os.getenv("GROQ_API_KEY") 
if not API_KEY:
    # fallback
    API_KEY = os.getenv("GEMINI_API_KEY")
client = Groq(api_key=API_KEY)

def generate_nl_columns(row_data, column_names):
    """
    Sends the row data to the LLM and asks for two natural language descriptions.
    """
    prompt = f"""
    You are a data architect and business analyst. I am going to provide you with a row of data from a database schema.
    
    Columns: {', '.join(column_names)}
    Row Values: {row_data}
    
    Based on this data, please generate two natural language descriptions:
    1. "purpose": A short business explanation of what this row/component is meant to achieve.
    2. "technical_logic": A brief technical explanation of how it operates based on the given fields.
    
    Respond STRICTLY in valid JSON format only, with no other text, like this: {{"purpose": "...", "technical_logic": "..."}}
    """
    
    try:
        # Call the Groq LLM
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant", # fast Groq model
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        # Parse the structured JSON response
        response_text = response.choices[0].message.content.strip()
        result = json.loads(response_text)
        return result.get("purpose", ""), result.get("technical_logic", "")
        
    except Exception as e:
        print(f"Error generating content for row: {e}")
        return "Error generating text", "Error generating text"

def enrich_schema(input_path, output_dir):
    import glob
    if os.path.isdir(input_path):
        csv_files = glob.glob(os.path.join(input_path, "*.csv"))
    else:
        csv_files = [input_path]
        
    if not csv_files:
        print(f"No CSV files found in {input_path}")
        return
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_path in csv_files:
        print(f"\n{'='*40}")
        print(f"Reading file: {file_path}")
        df = pd.read_csv(file_path)
        
        purposes = []
        technical_logics = []
        
        column_names = df.columns.tolist()
        total_rows = len(df)
        
        print(f"Found {total_rows} rows. Starting enrichment process...")
        
        for index, row in df.iterrows():
            print(f"Processing row {index + 1}/{total_rows}...")
            
            row_dict = row.to_dict()
            purpose, tech_logic = generate_nl_columns(row_dict, column_names)
            
            purposes.append(purpose)
            technical_logics.append(tech_logic)
            
            # Short pause to stay under Groq rate limits
            time.sleep(1.0) 
            
        df['purpose'] = purposes
        df['technical_logic'] = technical_logics
        
        filename = os.path.basename(file_path)
        output_csv = os.path.join(output_dir, f"enriched_{filename}")
        df.to_csv(output_csv, index=False)
        print(f"Successfully saved enriched schema to: {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automate adding natural language columns to schema CSVs.")
    parser.add_argument("-i", "--input", required=True, help="Path to the input CSV file or directory")
    parser.add_argument("-o", "--output", required=True, help="Path to save the enriched CSV files (directory)")
    
    args = parser.parse_args()
    enrich_schema(args.input, args.output)
    