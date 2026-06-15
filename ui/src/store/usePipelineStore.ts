import { create } from 'zustand';

export interface FourCs {
  classes: string[];
  components: string[];
  criteria: string[];
  conditions: string[];
}

export interface SchemaClass {
  schema_id: string;
  class_prompt: string;
  four_cs: FourCs;
}

export interface GlobalConfig {
  main_prompt: string;
}

export interface PipelineState {
  global_config: GlobalConfig;
  schema_classes: SchemaClass[];
  activeNodeId: string | null;
  activeTab: 'Main Prompt' | 'Class Prompt' | 'Test Results';
  executionCache: Record<string, any>;
  isLoading: boolean;
  
  // Actions
  setActiveNode: (id: string) => void;
  setActiveTab: (tab: 'Main Prompt' | 'Class Prompt' | 'Test Results') => void;
  updateFourCs: (schema_id: string, category: keyof FourCs, newValues: string[]) => void;
  updateClassPrompt: (schema_id: string, newPrompt: string) => void;
  
  // Async API Actions
  loadConfig: () => Promise<void>;
  saveDraft: () => Promise<void>;
  computeNode: (schema_id: string) => Promise<void>;
  uploadConfig: (file: File) => Promise<void>;
}

const API_BASE = 'http://127.0.0.1:8000/api';

export const usePipelineStore = create<PipelineState>((set, get) => ({
  global_config: { main_prompt: "" },
  schema_classes: [],
  activeNodeId: null,
  activeTab: 'Class Prompt',
  executionCache: {},
  isLoading: false,

  setActiveNode: (id) => set({ activeNodeId: id }),
  setActiveTab: (tab) => set({ activeTab: tab }),

  updateFourCs: (schema_id, category, newValues) => set((state) => ({
    schema_classes: state.schema_classes.map((cls) => 
      cls.schema_id === schema_id 
        ? { ...cls, four_cs: { ...cls.four_cs, [category]: newValues } }
        : cls
    )
  })),

  updateClassPrompt: (schema_id, newPrompt) => set((state) => ({
    schema_classes: state.schema_classes.map((cls) => 
      cls.schema_id === schema_id 
        ? { ...cls, class_prompt: newPrompt }
        : cls
    )
  })),

  loadConfig: async () => {
    set({ isLoading: true });
    try {
      const res = await fetch(`${API_BASE}/config`);
      const data = await res.json();
      set({
        global_config: data.config.global_config,
        schema_classes: data.config.schema_classes,
        executionCache: data.cache,
        activeNodeId: data.config.schema_classes.length > 0 ? data.config.schema_classes[0].schema_id : null,
      });
    } catch (e) {
      console.error("Failed to load config from backend", e);
    } finally {
      set({ isLoading: false });
    }
  },

  saveDraft: async () => {
    const state = get();
    try {
      const res = await fetch(`${API_BASE}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          global_config: state.global_config,
          schema_classes: state.schema_classes
        })
      });
      if (res.ok) alert("Draft successfully saved to sample_config.json on your hard drive!");
    } catch (e) {
      console.error("Failed to save draft", e);
      alert("Failed to connect to backend server.");
    }
  },

  computeNode: async (schema_id) => {
    const state = get();
    set({ isLoading: true });
    try {
      const res = await fetch(`${API_BASE}/compute/${schema_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          global_config: state.global_config,
          schema_classes: state.schema_classes
        })
      });
      const data = await res.json();
      
      if (data.status === "success") {
        set((state) => ({
          executionCache: {
            ...state.executionCache,
            [schema_id]: data.result
          }
        }));
      }
    } catch (e) {
      console.error("Failed to compute node", e);
      alert("Failed to execute Python script. Is the FastAPI server running on port 8000?");
    } finally {
      set({ isLoading: false });
    }
  },

  uploadConfig: async (file: File) => {
    set({ isLoading: true });
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await fetch(`${API_BASE}/upload`, {
        method: 'POST',
        body: formData
      });
      
      if (res.ok) {
        alert("Schema uploaded successfully!");
        get().loadConfig(); // Reload the UI with new data
      } else {
        alert("Failed to upload schema.");
      }
    } catch (e) {
      console.error("Failed to upload config", e);
      alert("Failed to connect to backend server.");
    } finally {
      set({ isLoading: false });
    }
  }
}));
