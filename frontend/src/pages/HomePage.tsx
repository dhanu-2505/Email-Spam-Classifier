import { Shield, ShieldAlert, Sparkles } from 'lucide-react';

function InfoCard({ title, text }: { title: string; text: string }) {
  return (
    <div className="card p-6">
      <Sparkles className="text-violet-300" />
      <h3 className="mt-4 font-bold">{title}</h3>
      <p className="mt-2 text-sm leading-6 text-slate-400">{text}</p>
    </div>
  );
}

export default function HomePage({ onLogin }: { onLogin: () => void }) {
  return (
    <div className="min-h-screen text-slate-100">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
        <div className="flex items-center gap-3 text-lg font-bold"><Shield className="text-violet-300" /> Email Spam Classifier</div>
        <button onClick={onLogin} className="rounded-xl bg-violet-600 px-5 py-2 font-semibold hover:bg-violet-500">Login</button>
      </nav>
      <main className="mx-auto max-w-7xl space-y-20 px-6 py-16">
        <section className="grid items-center gap-12 lg:grid-cols-2">
          <div>
            <span className="badge bg-violet-500/10 text-violet-200">NLP-powered threat awareness</span>
            <h1 className="mt-5 text-5xl font-black tracking-tight sm:text-6xl">Spot suspicious messages before they reach your inbox.</h1>
            <p className="mt-6 max-w-xl text-lg leading-8 text-slate-300">A transparent machine-learning demonstrator that classifies spam and ham text using the approved UCI SMS Spam Collection dataset.</p>
            <div className="mt-8 flex gap-3">
              <button onClick={onLogin} className="rounded-xl bg-violet-600 px-5 py-3 font-semibold hover:bg-violet-500">Login to classify</button>
              <a href="#how" className="rounded-xl border border-slate-700 px-5 py-3 font-semibold hover:border-violet-400">Learn more</a>
            </div>
          </div>
          <div className="card p-8">
            <ShieldAlert className="h-16 w-16 text-sky-300" />
            <h2 className="mt-6 text-2xl font-bold">Signal, not certainty</h2>
            <p className="mt-3 text-slate-300">Predictions are statistical indicators. Always verify links, senders, and requests independently.</p>
          </div>
        </section>
        <section id="how" className="grid gap-5 md:grid-cols-3">
          <InfoCard title="Clean text" text="Normalize message text while preserving useful spam signals such as links and urgency." />
          <InfoCard title="Learn patterns" text="Compare Naive Bayes, Logistic Regression, and Linear SVM with TF-IDF features." />
          <InfoCard title="Inspect results" text="Review real evaluation metrics, feature signals, and session prediction history." />
        </section>
        <section className="card p-8">
          <h2 className="text-2xl font-bold">Built for transparent experimentation</h2>
          <p className="mt-3 max-w-3xl text-slate-300">The current model is trained on SMS messages, not real email. The project supports the SMS collection and SpamAssassin as separate dataset choices.</p>
        </section>
      </main>
      <footer className="border-t border-slate-800 px-6 py-8 text-center text-sm text-slate-400">Dataset: UCI SMS Spam Collection. No public deployment is claimed.</footer>
    </div>
  );
}
