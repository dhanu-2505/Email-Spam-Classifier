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
  const [modelLoading, setModelLoading] = useState(true);
  const [modelError, setModelError] = useState('');
  const [keywords, setKeywords] = useState<KeywordInsights | null>(null);
  const [keywordsLoading, setKeywordsLoading] = useState(true);
  const [keywordsError, setKeywordsError] = useState('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<Prediction | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let active = true;
    api<ModelInfo>('/api/model-info')
      .then(data => { if (active) setModel(data); })
      .catch(err => { if (active) setModelError(err instanceof Error ? err.message : 'Unable to load model information.'); })
      .finally(() => { if (active) setModelLoading(false); });
    api<{ keywords: KeywordInsights }>('/api/keywords')
      .then(data => { if (active) setKeywords(data.keywords); })
      .catch(err => { if (active) setKeywordsError(err instanceof Error ? err.message : 'Unable to load keyword insights.'); })
      .finally(() => { if (active) setKeywordsLoading(false); });
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
      content = <AnalyticsPage model={model} comparison={comparison} loading={modelLoading} error={modelError} />;
      break;
    case 'keywords':
      content = <KeywordsPage data={keywords} loading={keywordsLoading} error={keywordsError} />;
      break;
    case 'history':
      content = <HistoryPage data={history} clear={() => setHistory([])} />;
      break;
    case 'dashboard':
    default:
      content = <OverviewPage model={model} loading={modelLoading} error={modelError} onNavigate={onNavigate} />;
  }

  return (
    <div className="dashboard-shell">
      <aside className="dashboard-sidebar" aria-label="Dashboard navigation">
        <div className="sidebar-brand">
          <div className="brand-icon">
            <Shield size={18} />
          </div>
          <span>Classifier</span>
        </div>

        <nav className="sidebar-nav">
          <button className={section === 'dashboard' ? 'nav-item active' : 'nav-item neutral'} aria-current={section === 'dashboard' ? 'page' : undefined} onClick={() => onNavigate('/dashboard')}>
            Dashboard
          </button>
          <button className={section === 'classifier' ? 'nav-item active' : 'nav-item neutral'} aria-current={section === 'classifier' ? 'page' : undefined} onClick={() => onNavigate('/classifier')}>
            Classifier
          </button>
          <button className={section === 'analytics' ? 'nav-item active' : 'nav-item neutral'} aria-current={section === 'analytics' ? 'page' : undefined} onClick={() => onNavigate('/analytics')}>
            Analytics
          </button>
          <button className={section === 'keywords' ? 'nav-item active' : 'nav-item neutral'} aria-current={section === 'keywords' ? 'page' : undefined} onClick={() => onNavigate('/keywords')}>
            Keywords
          </button>
          <button className={section === 'history' ? 'nav-item active' : 'nav-item neutral'} aria-current={section === 'history' ? 'page' : undefined} onClick={() => onNavigate('/history')}>
            History
          </button>
        </nav>
      </aside>

      <main className="dashboard-main">
        <header className="dashboard-header">
          <div />
          <button
            onClick={() => onLogout().catch(err => setError(err instanceof Error ? err.message : 'Logout failed.'))}
            className="header-logout"
          >
            <LogOut size={15} />
            <span>Logout</span>
          </button>
        </header>

        {error && <div role="alert" className="main-alert">{error}</div>}
        <Suspense fallback={<div className="card p-6 text-slate-300">Loading section...</div>}>{content}</Suspense>
      </main>
    </div>
  );
}
