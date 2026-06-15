import { memo, useCallback } from 'react';
import { usePipelineStore } from '../../store/usePipelineStore';
import type { SchemaClass, FourCs } from '../../store/usePipelineStore';
import { Plus, Trash2 } from 'lucide-react';

const FourCSection = memo(({ 
  title, 
  items, 
  onAdd, 
  onDelete 
}: { 
  title: string, 
  items: string[], 
  onAdd: () => void, 
  onDelete: (idx: number) => void 
}) => {
  return (
    <div className="mb-6 bg-surface p-4 rounded-xl shadow-sm border border-border transition-all hover:shadow-md">
      <div className="flex justify-between items-center mb-4 border-b border-border pb-2">
        <h3 className="font-semibold text-textPrimary capitalize">{title}</h3>
        <button 
          onClick={onAdd}
          className="flex items-center gap-1 text-xs text-primary bg-blue-50 hover:bg-blue-100 px-2 py-1 rounded-md transition-colors font-medium"
        >
          <Plus size={14} /> Add
        </button>
      </div>
      <div className="flex flex-col gap-2">
        {items.length === 0 && <p className="text-sm text-textSecondary italic py-2">No items added.</p>}
        {items.map((item, idx) => (
          <div key={idx} className="flex items-center gap-2 group">
            <input 
              type="text" 
              value={item} 
              readOnly
              className="flex-1 bg-background border border-border rounded-md px-3 py-2 text-sm text-textPrimary focus:outline-none"
            />
            <button 
              onClick={() => onDelete(idx)}
              className="p-1.5 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-md opacity-0 group-hover:opacity-100 transition-all"
              title="Remove Item"
            >
              <Trash2 size={16} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
});
FourCSection.displayName = 'FourCSection';

const ClassPromptTab = memo(({ activeNode }: { activeNode: SchemaClass }) => {
  const updateFourCs = usePipelineStore((state) => state.updateFourCs);
  const updateClassPrompt = usePipelineStore((state) => state.updateClassPrompt);

  const handleAdd = useCallback((category: keyof FourCs) => {
    const newVal = prompt(`Enter new ${category}:`);
    if (newVal) {
      updateFourCs(activeNode.schema_id, category, [...activeNode.four_cs[category], newVal]);
    }
  }, [activeNode, updateFourCs]);

  const handleDelete = useCallback((category: keyof FourCs, idx: number) => {
    const newArray = [...activeNode.four_cs[category]];
    newArray.splice(idx, 1);
    updateFourCs(activeNode.schema_id, category, newArray);
  }, [activeNode, updateFourCs]);

  return (
    <div className="p-6 h-full overflow-y-auto animate-in fade-in duration-300">
      <div className="mb-8">
        <h2 className="text-sm font-bold text-textSecondary uppercase tracking-wider mb-2">Class Prompt Instruction</h2>
        <textarea 
          className="w-full bg-surface border border-border rounded-xl p-4 text-sm text-textPrimary focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none transition-all shadow-sm resize-none"
          rows={3}
          value={activeNode.class_prompt}
          onChange={(e) => updateClassPrompt(activeNode.schema_id, e.target.value)}
        />
      </div>

      <h2 className="text-sm font-bold text-textSecondary uppercase tracking-wider mb-4">4C Configurations (Targeted Retrieval)</h2>
      <div className="grid grid-cols-2 gap-6">
        <FourCSection 
          title="Classes" 
          items={activeNode.four_cs.classes} 
          onAdd={() => handleAdd('classes')}
          onDelete={(idx) => handleDelete('classes', idx)}
        />
        <FourCSection 
          title="Components" 
          items={activeNode.four_cs.components} 
          onAdd={() => handleAdd('components')}
          onDelete={(idx) => handleDelete('components', idx)}
        />
        <FourCSection 
          title="Criteria" 
          items={activeNode.four_cs.criteria} 
          onAdd={() => handleAdd('criteria')}
          onDelete={(idx) => handleDelete('criteria', idx)}
        />
        <FourCSection 
          title="Conditions" 
          items={activeNode.four_cs.conditions} 
          onAdd={() => handleAdd('conditions')}
          onDelete={(idx) => handleDelete('conditions', idx)}
        />
      </div>
    </div>
  );
});

ClassPromptTab.displayName = 'ClassPromptTab';
export default ClassPromptTab;
