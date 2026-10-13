import { ArrowRight, BarChart3, CheckCircle2, Database, MailSearch, Tags } from 'lucide-react';
import { ModelInfo } from '../../types';

export default function OverviewPage({
  model,
  loading,
  error,
  onNavigate,
}: {
  model: ModelInfo | null;
  loading: boolean;
  error: string;
  onNavigate: (path: string) => void;
}) {
  const summary: Array<[string, string | number | undefined]> = [
    ['Rows', model?.dataset?.rows],
    ['Spam', model?.dataset?.spam_count],
    ['Ham', model?.dataset?.ham_count],
    ['Model', model?.selected_model],
  ];

  return (
    <section className="overview-page">
      <div className="overview-welcome">
        <div>
          <span className="home-eyebrow"><CheckCircle2 size={14} /> MODEL WORKSPACE</span>
          <h1>Your classifier at a glance</h1>
          <p>Test a message, explore model performance, or inspect the features learned during training.</p>
        </div>
        <button onClick={() => onNavigate('/classifier')} className="home-primary">Classify a message <ArrowRight size={16} /></button>
      </div>

      <div className="overview-stat-grid">
        {summary.map(([label, value]) => (
          <div className="overview-stat card" key={label}>
            <p className="text-sm text-slate-400">{label}</p>
            <strong className="mt-2 block text-2xl">{value ?? (loading ? 'Loading...' : 'Unavailable')}</strong>
          </div>
        ))}
      </div>
      {error && <p role="alert" className="text-sm text-rose-300">Unable to load model information: {error}</p>}

      <div className="overview-section-title">
        <div><h2>Explore your workspace</h2><p>Choose what you want to do next.</p></div>
      </div>
      <div className="overview-action-grid">
        <button className="overview-action card" onClick={() => onNavigate('/classifier')}>
          <span className="overview-action-icon violet"><MailSearch size={19} /></span>
          <strong>Message classifier</strong><span>Paste text and inspect its prediction.</span>
          <ArrowRight className="overview-arrow" size={17} />
        </button>
        <button className="overview-action card" onClick={() => onNavigate('/analytics')}>
          <span className="overview-action-icon blue"><BarChart3 size={19} /></span>
          <strong>Model analytics</strong><span>Compare evaluation metrics across models.</span>
          <ArrowRight className="overview-arrow" size={17} />
        </button>
        <button className="overview-action card" onClick={() => onNavigate('/keywords')}>
          <span className="overview-action-icon green"><Tags size={19} /></span>
          <strong>Learned keywords</strong><span>Review terms associated with spam and ham.</span>
          <ArrowRight className="overview-arrow" size={17} />
        </button>
      </div>

      <div className="overview-data-note card">
        <span className="overview-action-icon blue"><Database size={19} /></span>
        <div>
          <strong>Where is the data stored?</strong>
          <p>Account database: <code>backend\models\users.db</code>. Training messages: <code>data\raw\SMSSpamCollection.tsv</code>. These are separate from the trained model artifact.</p>
        </div>
      </div>
    </section>
  );
}
