import { HistoryItem } from '../../types';

export default function HistoryPage({ data, clear }: { data: HistoryItem[]; clear: () => void }) {
  return (
    <section className="card p-6">
      <div className="flex justify-between">
        <h1 className="text-2xl font-bold">History</h1>
        <button onClick={clear} className="text-sm text-slate-400">Clear</button>
      </div>
      <p className="mt-2 text-xs text-slate-500">Predictions are kept in memory for this signed-in session only.</p>
      {data.length === 0 ? (
        <p className="mt-6 text-slate-400">No predictions in this session.</p>
      ) : (
        <div className="mt-6 space-y-3">
          {data.map(item => (
            <div className="rounded-xl border border-slate-700 p-3" key={item.timestamp}>
              <strong className="uppercase">{item.label}</strong>
              <p className="text-sm text-slate-400">{item.message_preview}</p>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
