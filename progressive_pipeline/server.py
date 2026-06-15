from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from state_manager import StateManager
from node_executor import NodeExecutor

app = FastAPI(title="SchemaArchitect API")

# Enable CORS for the React frontend (Vite defaults to 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "sample_config.json")
CACHE_PATH = os.path.join(os.path.dirname(__file__), "session_cache.json")

# Initialize execution engine
state_manager = StateManager(cache_file=CACHE_PATH)
executor = NodeExecutor(state_manager=state_manager, use_mock_llm=True)

class ConfigUpdatePayload(BaseModel):
    global_config: dict
    schema_classes: list

@app.get("/api/config")
def get_config():
    """Loads the config and the execution cache for the UI on startup."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # Load the cache so the UI Test Results tab is populated
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                cache = json.load(f)
        else:
            cache = {}
            
        return {"config": config, "cache": cache}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save")
def save_config(payload: ConfigUpdatePayload):
    """Saves the modified config back to sample_config.json"""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(payload.dict(), f, indent=2)
        return {"status": "success", "message": "Draft saved successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_config(file: UploadFile = File(...)):
    """Accepts a JSON file upload and overwrites the active config."""
    try:
        contents = await file.read()
        config_data = json.loads(contents)
        
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
            
        return {"status": "success", "message": "Config uploaded and overwritten successfully!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compute/{schema_id}")
def compute_node(schema_id: str, payload: ConfigUpdatePayload):
    """Executes a specific node and returns the generated result."""
    try:
        # First save the latest 4C changes so the executor uses them
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(payload.dict(), f, indent=2)
            
        global_prompt = payload.global_config.get("main_prompt", "")
        target_node = next((node for node in payload.schema_classes if node["schema_id"] == schema_id), None)
        
        if not target_node:
            raise HTTPException(status_code=404, detail="Node not found in config")
            
        result = executor.compute_schema_class(target_node, global_prompt)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
