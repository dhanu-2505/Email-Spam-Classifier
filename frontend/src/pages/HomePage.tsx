import { ArrowRight, BarChart3, CheckCircle2, Database, MailSearch, Shield, Sparkles, Tags, type LucideIcon } from 'lucide-react';

function InfoCard({ icon: Icon, title, text }: { icon: LucideIcon; title: string; text: string }) {
  return (
    <article className="card home-feature-card">
      <span className="home-feature-icon"><Icon size={19} /></span>
      <h3>{title}</h3>
      <p>{text}</p>
    </article>
  );
}

export default function HomePage({ onLogin, onRegister }: { onLogin: () => void; onRegister: () => void }) {
  return (
    <div className="home-page">
      <nav className="home-nav">
        <a href="/" className="home-brand">
          <span className="home-brand-icon"><Shield size={19} /></span>
          <span>Email Spam Classifier</span>
        </a>
        <div className="home-nav-links">
          <a href="#features">Features</a>
          <a href="#model">About the model</a>
          <button className="home-login" onClick={onLogin}>Login</button>
          <button className="home-register" onClick={onRegister}>Create account <ArrowRight size={15} /></button>
        </div>
      </nav>

      <main>
        <section className="home-hero">
          <div className="home-hero-copy">
            <span className="home-eyebrow"><Sparkles size={14} /> A transparent machine-learning demo</span>
            <h1>Know what your message might be hiding.</h1>
            <p>Check suspicious message text, review the model’s evaluation, and explore the words it learned to associate with spam.</p>
            <div className="home-hero-actions">
              <button onClick={onLogin} className="home-primary">Open classifier <ArrowRight size={17} /></button>
              <button onClick={onRegister} className="home-secondary">Create a free account</button>
            </div>
            <div className="home-trust-note"><CheckCircle2 size={16} /> No email inbox connection. Test message text only.</div>
          </div>

          <div className="home-preview card">
            <div className="home-preview-top">
              <div><span className="home-preview-label">MESSAGE CHECK</span><h2>Pattern detected</h2></div>
              <span className="home-preview-icon"><MailSearch size={20} /></span>
            </div>
            <div className="home-message">
              <span>MESSAGE</span>
              <p>“You have won a prize! Call now to claim your reward.”</p>
            </div>
            <div className="home-result">
              <span className="home-result-dot" />
              <div><strong>Spam-like signals</strong><small>Example preview · Try your own after login</small></div>
              <span className="home-result-score">REVIEW</span>
            </div>
            <div className="home-preview-foot">Predictions are indicators, not proof. Always check the sender and links.</div>
          </div>
        </section>

        <section className="home-stat-strip" aria-label="Model overview">
          <div><strong>5,169</strong><span>messages in evaluated dataset</span></div>
          <div><strong>98.4%</strong><span>held-out accuracy</span></div>
          <div><strong>Linear SVM</strong><span>selected text classifier</span></div>
          <div><strong>SMS</strong><span>training data type</span></div>
        </section>

        <section id="features" className="home-features">
          <div className="home-section-heading">
            <span className="home-eyebrow">YOUR WORKSPACE</span>
            <h2>Everything useful, one place.</h2>
            <p>Sign in to explore the model and its results—not just a single prediction box.</p>
          </div>
          <div className="home-feature-grid">
            <InfoCard icon={MailSearch} title="Classify a message" text="Paste a message and get a spam/ham prediction with influential words." />
            <InfoCard icon={BarChart3} title="Explore analytics" text="Compare models using accuracy, precision, recall, and F1 on held-out data." />
            <InfoCard icon={Tags} title="Inspect learned terms" text="See which text features the trained classifier associates with each class." />
            <InfoCard icon={Database} title="Understand the data" text="Review dataset counts and see where the local training data and account database live." />
          </div>
        </section>

        <section id="model" className="home-model-note">
          <div className="home-model-mark"><Shield size={22} /></div>
          <div>
            <h2>About this model</h2>
            <p>It was trained on the UCI SMS Spam Collection, not real email. Results on email messages may differ. The model is a learning aid, not a security guarantee.</p>
          </div>
          <button onClick={onLogin} className="home-text-link">Explore the results <ArrowRight size={16} /></button>
        </section>
      </main>

      <footer className="home-footer">
        <span>Email Spam Classifier</span>
        <span>Local demo · UCI SMS Spam Collection · Verify suspicious messages independently</span>
      </footer>
    </div>
  );
}
