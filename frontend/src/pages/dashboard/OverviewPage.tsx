import { CheckCircle2 } from 'lucide-react';
import { ModelInfo } from '../../types';

export default function OverviewPage({ model }: { model: ModelInfo | null }) {
  const summary: Array<[string, string | number | undefined]> = [
    ['Rows', model?.dataset?.rows],
    ['Spam', model?.dataset?.spam_count],
    ['Ham', model?.dataset?.ham_count],
    ['Model', model?.selected_model],
  ];

  return (
    <section className="space-y-6">
      <div className="card p-8">
        <CheckCircle2 className="text-emerald-400" />
        <h1 className="mt-4 text-3xl font-bold">Protected dashboard</h1>
        <p className="mt-2 text-slate-300">Backend-connected ML workspace. Choose a section to inspect the trained model.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-4">
        {summary.map(([label, value]) => (
          <div className="card p-5" key={label}>
            <p className="text-sm text-slate-400">{label}</p>
            <strong className="mt-2 block text-2xl">{value ?? 'Loading...'}</strong>
          </div>
        ))}
      </div>
    </section>
  );
}
