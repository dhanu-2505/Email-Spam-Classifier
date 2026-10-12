import { FormEvent, useState } from 'react';
import { api } from '../lib/api';

export default function AuthPage({ register, onLogin }: { register: boolean; onLogin: (destination: string | null) => void }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [show, setShow] = useState(false);
  const registered = !register && new URLSearchParams(window.location.search).get('registered') === '1';

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      if (register) {
        await api('/api/auth/register', { method: 'POST', body: JSON.stringify({ email, password }) });
        navigate('/login?registered=1');
        return;
      }
      await api('/api/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
      await api('/api/auth/me');
      onLogin(new URLSearchParams(window.location.search).get('next'));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed.');
    } finally {
      setBusy(false);
    }
  }

  function navigate(path: string) {
    window.history.pushState({}, '', path);
    window.dispatchEvent(new PopStateEvent('popstate'));
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <form onSubmit={submit} className="card w-full max-w-md p-8">
        <button type="button" onClick={() => navigate('/')} className="text-sm text-slate-400 hover:text-white">← Back home</button>
        <h1 className="mt-8 text-3xl font-bold">{register ? 'Create account' : 'Welcome back'}</h1>
        <p className="mt-2 text-slate-400">{register ? 'Create a local account to use the classifier.' : 'Sign in to access the protected dashboard.'}</p>
        {registered && <div role="status" className="mt-5 rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-3 text-sm text-emerald-200">Account created. Sign in with your new account.</div>}
        {error && <div role="alert" className="mt-5 rounded-xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-200">{error}</div>}
        <label className="mt-6 block text-sm text-slate-300">
          Email
          <input required type="email" value={email} onChange={event => setEmail(event.target.value)} className="mt-2 w-full rounded-xl border border-slate-700 bg-slate-950 p-3" />
        </label>
        <label className="mt-4 block text-sm text-slate-300">
          Password
          <div className="mt-2 flex">
            <input required minLength={register ? 8 : 1} type={show ? 'text' : 'password'} value={password} onChange={event => setPassword(event.target.value)} className="w-full rounded-l-xl border border-slate-700 bg-slate-950 p-3" />
            <button type="button" onClick={() => setShow(!show)} className="rounded-r-xl border border-l-0 border-slate-700 px-3 text-xs">Show</button>
          </div>
        </label>
        <button disabled={busy} className="mt-6 w-full rounded-xl bg-violet-600 p-3 font-semibold disabled:opacity-50">{busy ? 'Please wait...' : register ? 'Register' : 'Login'}</button>
        <button type="button" onClick={() => navigate(register ? '/login' : '/register')} className="mt-4 w-full text-sm text-violet-300">{register ? 'Already have an account? Login' : 'Need an account? Register'}</button>
      </form>
    </div>
  );
}
