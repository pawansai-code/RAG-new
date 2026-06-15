import os
import json

class StateManager:
    def __init__(self, cache_file="session_cache.json"):
        self.cache_file = cache_file
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        else:
            self.cache = {"completed_steps": {}, "global_context": {}}

    def _save_cache(self):
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(self.cache, f, indent=4)

    def save_step_output(self, schema_id, output):
        """Saves or overwrites the output for a specific SchemaClass step."""
        self.cache["completed_steps"][schema_id] = output
        self._save_cache()
        print(f"[State Manager] Saved state for {schema_id}")

    def get_context_history(self, up_to_schema_id=None):
        """
        Retrieves the conversational history.
        If up_to_schema_id is provided, returns all completed steps chronologically
        (In a real DAG, we'd order them or follow edges. For now, we return all completed).
        """
        if not self.cache["completed_steps"]:
            return "No previous context available."
            
        history = "--- Previous Extraction Context ---\n"
        for s_id, out in self.cache["completed_steps"].items():
            if s_id != up_to_schema_id: # Don't include the current step if it exists (targeted regeneration)
                history += f"\n[{s_id} Output]:\n{json.dumps(out, indent=2)}\n"
        return history
    
    def get_step_output(self, schema_id):
        return self.cache["completed_steps"].get(schema_id, None)

    def get_full_cache(self):
        """Returns the complete payload of all extracted data."""
        return self.cache.get("completed_steps", {})

    def clear_cache(self):
        self.cache = {"completed_steps": {}, "global_context": {}}
        self._save_cache()
        print("[State Manager] Cache cleared.")
