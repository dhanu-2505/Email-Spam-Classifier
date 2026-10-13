import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { EvaluationMetrics, ModelComparison, ModelInfo } from '../../types';

const metrics: Array<keyof EvaluationMetrics> = ['accuracy', 'precision', 'recall', 'f1'];

export default function AnalyticsPage({
  model,
  comparison,
  loading,
  error,
}: {
  model: ModelInfo | null;
  comparison: ModelComparison[];
  loading: boolean;
  error: string;
}) {
  return (
    <section className="card p-6">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <p className="mt-2 text-sm text-slate-400">Held-out test metrics from the current trained model comparison.</p>
      <div className="mt-6 grid gap-3 md:grid-cols-4">
        {metrics.map(metric => {
          const value = model?.evaluation?.[metric];
          return (
            <div className="rounded-xl bg-slate-950 p-4" key={metric}>
              <span className="text-sm text-slate-400">{metric}</span>
              <strong className="mt-2 block text-xl">{value === undefined ? (loading ? 'Loading...' : 'Unavailable') : `${(value * 100).toFixed(1)}%`}</strong>
            </div>
          );
        })}
      </div>
      <div className="mt-8 h-80">
        {comparison.length > 0 ? (
          <ResponsiveContainer>
            <BarChart data={comparison}>
              <CartesianGrid stroke="#334155" />
              <XAxis dataKey="model" stroke="#cbd5e1" />
              <YAxis domain={[0, 1]} stroke="#cbd5e1" />
              <Tooltip />
              <Legend />
              <Bar dataKey="accuracy" fill="#8b5cf6" />
              <Bar dataKey="f1" fill="#38bdf8" />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p role={error ? 'alert' : undefined} className={error ? 'text-rose-300' : 'text-slate-400'}>
            {loading ? 'Loading evaluation data...' : error ? `Evaluation data unavailable: ${error}` : 'No evaluation data is available.'}
          </p>
        )}
      </div>
    </section>
  );
}
