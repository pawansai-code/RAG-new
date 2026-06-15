import { memo, useCallback } from 'react';
import { usePipelineStore } from '../store/usePipelineStore';
import ClassPromptTab from './Tabs/ClassPromptTab';
import TestResultsTab from './Tabs/TestResultsTab';
import classNames from 'classnames';
import { Play } from 'lucide-react';

const MainPanel = memo(() => {
  const schemaClasses = usePipelineStore((state) => state.schema_classes);
  const activeNodeId = usePipelineStore((state) => state.activeNodeId);
  const activeTab = usePipelineStore((state) => state.activeTab);
  const setActiveTab = usePipelineStore((state) => state.setActiveTab);
  const computeNode = usePipelineStore((state) => state.computeNode);
  const saveDraft = usePipelineStore((state) => state.saveDraft);
  const isLoading = usePipelineStore((state) => state.isLoading);

  const activeNode = schemaClasses.find(c => c.schema_id === activeNodeId);

  const handleCompute = useCallback(() => {
    if (activeNodeId) {
      computeNode(activeNodeId);
      setActiveTab('Test Results');
    }
  }, [activeNodeId, computeNode, setActiveTab]);

  if (!activeNode) return <div className="flex-1 flex items-center justify-center text-textSecondary bg-background">Select a node from the sidebar</div>;

  return (
    <div className="flex-1 flex flex-col bg-background h-screen overflow-hidden">
      {/* Header */}
      <div className="flex justify-between items-center p-5 border-b border-border bg-surface shadow-sm z-10">
        <div className="flex items-center gap-4">
          <div className="bg-blue-50 text-primary border border-blue-200 px-3 py-1 rounded-md text-xs font-bold uppercase tracking-wider shadow-sm">
            Active Node
          </div>
          <h2 className="text-xl font-bold text-textPrimary tracking-tight">
            {activeNode.schema_id.replace('SC_', '#SCLASS#')}
          </h2>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => saveDraft()}
            className="bg-surface border border-border text-textPrimary text-sm font-semibold px-5 py-2 rounded-lg shadow-sm hover:bg-background hover:border-gray-300 transition-all active:scale-95"
          >
            Save Draft
          </button>
          <button 
            onClick={handleCompute}
            disabled={isLoading}
            className="flex items-center gap-2 bg-primary text-white text-sm font-semibold px-6 py-2 rounded-lg shadow-[0_4px_14px_0_rgba(29,78,216,0.39)] hover:bg-secondary hover:shadow-[0_6px_20px_rgba(59,130,246,0.23)] disabled:opacity-75 disabled:cursor-not-allowed transition-all active:scale-95"
          >
            <Play size={16} fill="currentColor" />
            {isLoading ? 'Computing...' : 'Compute'}
          </button>
        </div>
      </div>

      {/* Data Sources */}
      <div className="px-6 py-4 border-b border-border bg-surface/80 backdrop-blur-md flex items-center gap-3">
        <span className="text-xs font-bold text-textSecondary uppercase tracking-widest mr-2">Data Sources:</span>
        {['AccountDetermination', 'Active_MD', 'Active_IM'].map(tag => (
          <span key={tag} className="border border-border bg-surface text-textSecondary text-xs font-medium px-4 py-1.5 rounded-full shadow-sm hover:border-primary/50 transition-colors cursor-pointer">
            {tag}
          </span>
        ))}
        <button className="border border-dashed border-primary text-primary font-medium bg-blue-50/50 text-xs px-4 py-1.5 rounded-full hover:bg-blue-50 transition-colors flex items-center gap-1">
          + Add
        </button>
      </div>

      {/* Tabs */}
      <div className="flex px-6 border-b border-border bg-surface">
        {['Main Prompt', 'Class Prompt', 'Test Results'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as any)}
            className={classNames(
              "px-5 py-3.5 text-sm font-semibold border-b-2 transition-all relative",
              activeTab === tab 
                ? "border-primary text-primary" 
                : "border-transparent text-textSecondary hover:text-textPrimary"
            )}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden relative bg-background/50">
        {activeTab === 'Class Prompt' && <ClassPromptTab activeNode={activeNode} />}
        {activeTab === 'Test Results' && <TestResultsTab activeNodeId={activeNodeId!} />}
        {activeTab === 'Main Prompt' && (
          <div className="p-8 text-textSecondary italic animate-in fade-in text-sm">Global schema main prompt editor placeholder...</div>
        )}
      </div>
    </div>
  );
});

MainPanel.displayName = 'MainPanel';
export default MainPanel;
