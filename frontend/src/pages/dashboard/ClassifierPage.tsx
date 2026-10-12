import { Prediction } from '../../types';

export default function ClassifierPage({
  message,
  setMessage,
  predict,
  busy,
  result,
}: {
  message: string;
  setMessage: (value: string) => void;
  predict: () => void;
  busy: boolean;
  result: Prediction | null;
}) {
  return (
    <section className="card p-6">
      <h1 className="text-2xl font-bold">Classifier</h1>
      <p className="mt-2 text-sm text-slate-400">Submit text to the trained UCI SMS model.</p>
      <textarea
        value={message}
        onChange={event => setMessage(event.target.value)}
        rows={9}
        maxLength={5000}
        className="mt-5 w-full rounded-xl border border-slate-700 bg-slate-950 p-4"
        placeholder="Enter a message..."
      />
      <button onClick={predict} disabled={busy} className="mt-3 rounded-xl bg-violet-600 px-5 py-3 font-semibold disabled:opacity-50">
        {busy ? 'Classifying...' : 'Classify message'}
      </button>
      {result && (
        <div className="mt-6 rounded-xl border border-slate-700 p-4" aria-live="polite">
          <strong className="text-2xl uppercase">{result.label}</strong>
          <p className="mt-2 text-slate-300">{result.explanation}</p>
          {result.top_features.length > 0 && <p className="mt-3 text-sm text-violet-200">Influential tokens: {result.top_features.join(', ')}</p>}
        </div>
      )}
    </section>
  );
}
