import { lazy, Suspense, useEffect, useState } from 'react';
import { api } from './lib/api';

const HomePage = lazy(() => import('./pages/HomePage'));
const AuthPage = lazy(() => import('./pages/AuthPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));

type SessionState = 'unknown' | 'authenticated' | 'anonymous';

function navigate(path: string) {
  window.history.pushState({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
}

function safeDestination(value: string | null) {
  return value && value.startsWith('/') && !value.startsWith('//') ? value : '/dashboard';
}

export default function App() {
  const [path, setPath] = useState(window.location.pathname);
  const [session, setSession] = useState<SessionState>('unknown');

  useEffect(() => {
    const handlePopState = () => setPath(window.location.pathname);
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const isPublicRoute = path === '/' || path === '/login' || path === '/register';
  useEffect(() => {
    if (isPublicRoute || session === 'authenticated') return;
    if (session === 'anonymous') {
      navigate(`/login?next=${encodeURIComponent(path)}`);
      return;
    }

    let active = true;
    api('/api/auth/me')
      .then(() => {
        if (active) setSession('authenticated');
      })
      .catch(() => {
        if (!active) return;
        setSession('anonymous');
        navigate(`/login?next=${encodeURIComponent(path)}`);
      });

    return () => {
      active = false;
    };
  }, [isPublicRoute, path, session]);

  const fallback = <div className="p-10 text-slate-300">Loading...</div>;
  if (path === '/' || path === '') {
    return <Suspense fallback={fallback}><HomePage onLogin={() => navigate('/login')} /></Suspense>;
  }
  if (path === '/login' || path === '/register') {
    return (
      <Suspense fallback={fallback}>
        <AuthPage
          register={path === '/register'}
          onLogin={destination => {
            setSession('authenticated');
            window.history.pushState({}, '', safeDestination(destination));
            setPath(window.location.pathname);
          }}
        />
      </Suspense>
    );
  }
  if (session !== 'authenticated') return fallback;

  return (
    <Suspense fallback={fallback}>
      <DashboardPage
        path={path}
        onNavigate={navigate}
        onLogout={async () => {
          await api('/api/auth/logout', { method: 'POST' });
          setSession('anonymous');
          navigate('/');
        }}
      />
    </Suspense>
  );
}
