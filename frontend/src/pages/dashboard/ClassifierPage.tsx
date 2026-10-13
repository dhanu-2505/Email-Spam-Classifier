import { Prediction } from '../../types';

const examples = [
  { label: 'Suspicious offer', message: 'Congratulations! You have won a free prize. Call now to claim your reward!' },
  { label: 'Everyday message', message: 'Hi, are we still meeting for lunch after class today?' },
];

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
    <section className="classifier-shell">
      <div className="classifier-header-block">
        <span className="home-eyebrow">MESSAGE ANALYSIS</span>
        <h1>Classifier</h1>
        <p>Paste a message below to see whether it resembles spam or a legitimate message.</p>
      </div>

      <div className="classifier-compose card">
        <div className="classifier-compose-heading">
          <div><strong>Your message</strong><span>Text stays in this app and is sent to the local classifier.</span></div>
          <span className="classifier-character-count">{message.length}/5000</span>
        </div>
        <textarea
          value={message}
          onChange={event => setMessage(event.target.value)}
          rows={7}
          maxLength={5000}
          className="classifier-input"
          aria-label="Message to classify"
          placeholder="Paste or type a message here..."
        />
        <div className="classifier-examples">
          <span>Try an example</span>
          {examples.map(example => (
            <button key={example.label} type="button" onClick={() => setMessage(example.message)}>{example.label}</button>
          ))}
          {message && <button type="button" className="classifier-clear" onClick={() => setMessage('')}>Clear</button>}
        </div>
      </div>

      <button onClick={predict} disabled={busy} className="classifier-button">
        {busy ? 'Checking message...' : 'Classify message'}
      </button>

      {result && (
        <div className={`classifier-result ${result.label === 'spam' ? 'is-spam' : 'is-ham'}`} aria-live="polite">
          <div className="classifier-result-heading">
            <span className="classifier-result-label">{result.label === 'spam' ? 'Spam-like patterns detected' : 'Looks like a legitimate message'}</span>
            {result.confidence !== null && result.confidence !== undefined && (
              <span className="classifier-confidence">{Math.round(result.confidence * 100)}% confidence</span>
            )}
          </div>
          <p>{result.explanation}</p>
          {result.top_features.length > 0 && (
            <div className="classifier-feature-list"><span>Influential terms</span>{result.top_features.map(feature => <span className="classifier-feature" key={feature}>{feature}</span>)}</div>
          )}
          <small>Model predictions are statistical estimates, not proof. Verify the sender and links yourself.</small>
        </div>
      )}
    </section>
  );
}
