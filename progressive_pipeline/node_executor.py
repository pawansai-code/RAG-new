import json
from retriever import TargetedRetriever

class NodeExecutor:
    def __init__(self, state_manager, use_mock_llm=True):
        self.state_manager = state_manager
        self.retriever = TargetedRetriever(use_mock=True)
        self.use_mock_llm = use_mock_llm

    def compute_schema_class(self, schema_node, global_prompt):
        schema_id = schema_node["schema_id"]
        class_prompt = schema_node["class_prompt"]
        four_cs = schema_node["four_cs"]

        print(f"\n==============================================")
        print(f"[*] EXECUTING NODE: {schema_id}")
        print(f"==============================================")

        # 1. Fetch Conversational History (Targeted generation magic)
        history = self.state_manager.get_context_history(up_to_schema_id=schema_id)
        
        # 2. Targeted Retrieval based on 4Cs
        print(f"[Retriever] Searching vector DB with {len(four_cs.get('conditions', []))} conditions...")
        retrieved_chunks = self.retriever.retrieve(four_cs)

        # 3. Assemble Prompt
        strict_rules = "\n- ".join(four_cs.get("criteria", []) + four_cs.get("conditions", []))
        if not strict_rules.strip():
            strict_rules = "None"

        final_prompt = f"""
{global_prompt}

{history}

TARGETED CONTEXT:
{retrieved_chunks}

TASK INSTRUCTION:
{class_prompt}

STRICT RULES (Criteria & Conditions):
- {strict_rules}

Please extract the data as a JSON dictionary containing the components: {four_cs.get('components', [])}.
"""
        print(f"[Node Executor] Assembling Prompt Window...")
        print(f"[LLM] Generating JSON payload...\n")
        
        # 4. LLM Generation
        if self.use_mock_llm:
            output_json = self._mock_llm_call(schema_id)
        else:
            print("[Node Executor] Calling real LLM...")
            # response = llm.predict(final_prompt)
            output_json = {} # Parse response

        # 5. Save to Cache
        self.state_manager.save_step_output(schema_id, output_json)
        
        print(f"[Payload Generated]:")
        print(json.dumps(output_json, indent=2))
        print(f"----------------------------------------------\n")
        return output_json

    def _mock_llm_call(self, schema_id):
        if "BILLHEADER" in schema_id:
            return {"Bill ID": "BILL-2026-991", "Date": "01-04-2026"}
        elif "VENDORMASTER" in schema_id:
            return {"Vendor Name": "Global Supply Co.", "Vendor Address": "123 Industrial Way, CA"}
        return {"extracted": "dummy_data"}
