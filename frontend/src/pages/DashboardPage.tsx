import { lazy, Suspense, useEffect, useMemo, useState } from 'react';
import { CheckCircle2, LogOut, Shield } from 'lucide-react';
import { api } from '../lib/api';
import { HistoryItem, KeywordInsights, ModelInfo, Prediction } from '../types';

const AnalyticsPage = lazy(() => import('./dashboard/AnalyticsPage'));
const ClassifierPage = lazy(() => import('./dashboard/ClassifierPage'));
const HistoryPage = lazy(() => import('./dashboard/HistoryPage'));
const KeywordsPage = lazy(() => import('./dashboard/KeywordsPage'));
const OverviewPage = lazy(() => import('./dashboard/OverviewPage'));

const sections = ['dashboard', 'classifier', 'analytics', 'keywords', 'history'] as const;
type Section = typeof sections[number];

export default function DashboardPage({
  path,
  onNavigate,
  onLogout,
}: {
  path: string;
  onNavigate: (path: string) => void;
  onLogout: () => Promise<void>;
}) {
  const [model, setModel] = useState<ModelInfo | null>(null);
  const [keywords, setKeywords] = useState<KeywordInsights | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    api<ModelInfo>('/api/model-info')
      .then(data => { if (active) setModel(data); })
      .catch(err => { if (active) setError(err instanceof Error ? err.message : 'Unable to load model information.'); });
    api<{ keywords: KeywordInsights }>('/api/keywords')
      .then(data => { if (active) setKeywords(data.keywords); })
      .catch(err => { if (active) setError(err instanceof Error ? err.message : 'Unable to load keyword insights.'); });
    return () => { active = false; };
  }, []);

  const comparison = useMemo(() => model?.comparison || [], [model]);
  const section = path.split('/')[1] as Section;

  async function predict() {
    if (!message.trim()) {
      setError('Enter a message first.');
      return;
    }
    setBusy(true);
    setError('');
    try {
      const prediction = await api<Prediction>('/api/predict', {
        method: 'POST',
        body: JSON.stringify({ message }),
      });
      setResult(prediction);
      setHistory(current => [
        { timestamp: new Date().toISOString(), label: prediction.label, message_preview: message.slice(0, 80) },
        ...current,
      ].slice(0, 20));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Prediction failed.');
    } finally {
      setBusy(false);
    }
  }

  let content;
  switch (section) {
    case 'classifier':
      content = <ClassifierPage message={message} setMessage={setMessage} predict={predict} busy={busy} result={result} />;
      break;
    case 'analytics':
      content = <AnalyticsPage model={model} comparison={comparison} />;
      break;
    case 'keywords':
      content = <KeywordsPage data={keywords} />;
      break;
    case 'history':
      content = <HistoryPage data={history} clear={() => setHistory([])} />;
      break;
    case 'dashboard':
    default:
      content = <OverviewPage model={model} />;
  }

  return (
    <div className="min-h-screen px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 flex items-center justify-between">
          <button onClick={() => onNavigate('/dashboard')} className="flex items-center gap-3 text-xl font-bold">
            <Shield className="text-violet-300" /> Classifier
          </button>
          <button
            onClick={() => onLogout().catch(err => setError(err instanceof Error ? err.message : 'Logout failed.'))}
            className="rounded-xl border border-slate-700 px-3 py-2 text-sm"
          >
            <LogOut size={15} className="mr-1 inline" /> Logout
          </button>
        </header>
        <div className="grid gap-6 lg:grid-cols-[190px_1fr]">
          <aside className="card h-fit p-3" aria-label="Dashboard navigation">
            {sections.map(item => (
              <button
                key={item}
                onClick={() => onNavigate(`/${item}`)}
                aria-current={section === item ? 'page' : undefined}
                className={`block w-full rounded-lg px-3 py-2 text-left text-sm capitalize ${section === item ? 'bg-violet-600' : 'text-slate-300 hover:bg-slate-800'}`}
              >
                {item}
              </button>
            ))}
          </aside>
          <main className="space-y-6">
            {error && <div role="alert" className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-200">{error}</div>}
            <Suspense fallback={<div className="card p-6 text-slate-300">Loading section...</div>}>{content}</Suspense>
          </main>
        </div>
      </div>
    </div>
  );
}
