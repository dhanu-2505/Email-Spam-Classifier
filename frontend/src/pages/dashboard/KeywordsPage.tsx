import { KeywordInsights } from '../../types';

function TermList({ title, terms }: { title: string; terms: string[] }) {
  return (
    <div>
      <h2 className="font-semibold text-violet-200">{title}</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {terms.map(term => <span className="badge bg-slate-800 text-slate-200" key={term}>{term}</span>)}
      </div>
    </div>
  );
}

export default function KeywordsPage({ data }: { data: KeywordInsights | null }) {
  return (
    <section className="card p-6">
      <h1 className="text-2xl font-bold">Keyword insights</h1>
      <p className="mt-2 text-sm text-slate-400">Learned statistical features, not proof of malicious intent.</p>
      {data ? (
        <div className="mt-6 grid gap-6 md:grid-cols-2">
          <TermList title="Spam-associated" terms={data.spam_terms} />
          <TermList title="Ham-associated" terms={data.ham_terms} />
        </div>
      ) : <p className="mt-6 text-slate-400">Loading keyword insights...</p>}
    </section>
  );
}
