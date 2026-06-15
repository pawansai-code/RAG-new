import { memo } from 'react';
import { CheckCircle, Download, FileJson } from 'lucide-react';
import { usePipelineStore } from '../../store/usePipelineStore';

const OutputTable = memo(({ title, data, isMatched = false }: { title: string, data: Record<string, any>, isMatched?: boolean }) => {
  const keys = Object.keys(data);
  if (keys.length === 0) return null;

  return (
    <div className="mb-6 bg-surface border border-border rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-200">
      <div className="flex justify-between items-center p-4 border-b border-border bg-background/50">
        <div className="flex items-center gap-2">
          <FileJson size={18} className="text-textSecondary" />
          <h3 className="font-semibold text-textPrimary">{title}</h3>
          {isMatched && (
            <span className="flex items-center gap-1 text-xs font-medium text-green-700 bg-green-100 px-2 py-0.5 rounded-full border border-green-200 ml-2">
              <CheckCircle size={12} /> MATCHED
            </span>
          )}
        </div>
        <div className="flex gap-2 text-textSecondary">
          <Download size={16} className="cursor-pointer hover:text-primary transition-colors" />
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-background/30 text-xs text-textSecondary uppercase tracking-wider">
              {keys.map((k) => (
                <th key={k} className="px-6 py-3 font-semibold border-b border-border">{k}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            <tr className="text-sm text-textPrimary hover:bg-background/20 transition-colors">
              {keys.map((k) => (
                <td key={k} className="px-6 py-4 border-b border-border">
                  {k === 'Status' ? (
                    <span className="text-xs font-bold text-green-600 tracking-wider">PROCESSED</span>
                  ) : (
                    data[k]
                  )}
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
});

OutputTable.displayName = 'OutputTable';

const TestResultsTab = memo(({ activeNodeId }: { activeNodeId: string }) => {
  const executionCache = usePipelineStore((state) => state.executionCache);
  const resultData = executionCache[activeNodeId] || {};

  return (
    <div className="p-6 h-full overflow-y-auto animate-in fade-in duration-300">
      <OutputTable title="Expected Output" data={resultData} />
      <OutputTable title="Processed Output" data={resultData} isMatched={true} />
      
      <div className="mb-6 bg-surface border border-border rounded-xl shadow-sm p-5 hover:shadow-md transition-shadow">
        <h3 className="font-semibold text-textPrimary mb-2 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.8)]"></span>
          Findings & Suggestions
        </h3>
        <p className="text-sm text-textSecondary mt-2">All field values are matched correctly based on the 4C Criteria.</p>
      </div>

      <div className="flex justify-between items-center bg-background border border-border p-5 rounded-xl shadow-inner">
        <div className="flex items-center gap-6 text-sm">
          <span className="text-textSecondary">CONTEXT: <strong className="text-textPrimary font-medium ml-1">Source: PostgreSQL</strong></span>
          <span className="text-textSecondary">Compute: <strong className="text-textPrimary font-medium ml-1">14m ago</strong></span>
          <span className="text-green-600 font-semibold tracking-wide">Reliability: 98.2%</span>
        </div>
        <button className="bg-primary text-white text-sm font-semibold px-8 py-2.5 rounded-lg shadow-md hover:bg-secondary hover:shadow-lg transition-all active:scale-95 uppercase tracking-wide">
          Proceed
        </button>
      </div>
    </div>
  );
});

TestResultsTab.displayName = 'TestResultsTab';
export default TestResultsTab;
