import { memo, useRef } from 'react';
import { usePipelineStore } from '../store/usePipelineStore';
import { ChevronDown, FileText, Search, Upload } from 'lucide-react';
import classNames from 'classnames';

const Sidebar = memo(() => {
  const schemaClasses = usePipelineStore((state) => state.schema_classes);
  const activeNodeId = usePipelineStore((state) => state.activeNodeId);
  const setActiveNode = usePipelineStore((state) => state.setActiveNode);
  const uploadConfig = usePipelineStore((state) => state.uploadConfig);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      uploadConfig(file);
    }
  };

  return (
    <div className="w-72 bg-surface border-r border-border h-screen flex flex-col shadow-sm z-10">
      <div className="p-4 border-b border-border">
        <h1 className="text-primary font-bold text-lg tracking-wide uppercase">SchemaArchitect</h1>
      </div>
      
      <div className="p-4 border-b border-border bg-background/50">
        <label className="text-xs font-semibold text-textSecondary uppercase tracking-wider mb-2 block">
          Select a Schema
        </label>
        <div className="flex flex-col gap-2">
          <select 
            className="w-full bg-surface border border-border rounded px-2 py-1.5 text-sm outline-none focus:border-secondary focus:ring-2 focus:ring-primary/20 transition-all"
            value={activeNodeId || ""}
            onChange={(e) => setActiveNode(e.target.value)}
          >
            {schemaClasses.length === 0 && <option value="">No Schemas</option>}
            {schemaClasses.map((cls) => (
              <option key={cls.schema_id} value={cls.schema_id}>
                {cls.schema_id}
              </option>
            ))}
          </select>
          
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            accept=".json" 
            className="hidden" 
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            className="flex items-center justify-center gap-1 w-full bg-primary text-white text-xs px-3 py-2 rounded font-medium hover:bg-secondary transition-colors shadow-sm"
          >
            <Upload size={14} /> Upload Custom JSON
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="relative mb-4">
          <Search size={14} className="absolute left-2.5 top-2.5 text-textSecondary" />
          <input 
            type="text" 
            placeholder="Search Schema..." 
            className="w-full bg-surface border border-border rounded-md pl-8 pr-3 py-2 text-sm text-textPrimary placeholder:text-textSecondary focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all shadow-sm"
          />
        </div>

        <div className="flex items-center gap-2 text-textPrimary font-medium mb-3">
          <ChevronDown size={16} className="text-textSecondary" />
          <span>Schemas</span>
        </div>
        
        <div className="pl-6 flex flex-col gap-1">
          {schemaClasses.map((cls) => (
            <div 
              key={cls.schema_id}
              onClick={() => setActiveNode(cls.schema_id)}
              className={classNames(
                "flex items-center gap-2 px-2 py-2 rounded cursor-pointer text-sm transition-all duration-200",
                activeNodeId === cls.schema_id 
                  ? "bg-blue-50 text-primary font-semibold border-l-2 border-primary shadow-sm" 
                  : "text-textSecondary hover:bg-background hover:text-textPrimary border-l-2 border-transparent"
              )}
            >
              <FileText size={14} className={activeNodeId === cls.schema_id ? "text-primary" : "text-textSecondary flex-shrink-0"} />
              <span className="truncate">{cls.schema_id}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
});

Sidebar.displayName = 'Sidebar';
export default Sidebar;
