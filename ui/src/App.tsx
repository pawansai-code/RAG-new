import { memo, useEffect } from 'react';
import { usePipelineStore } from './store/usePipelineStore';
import Sidebar from './components/Sidebar';
import MainPanel from './components/MainPanel';

const App = memo(() => {
  const loadConfig = usePipelineStore((state) => state.loadConfig);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background font-sans text-textPrimary antialiased selection:bg-primary/20">
      <Sidebar />
      <MainPanel />
    </div>
  );
});

App.displayName = 'App';
export default App;
