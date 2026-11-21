import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

import { tokenStore } from './api';

type Auth = { ready: boolean; token: string | null; setToken: (t: string | null) => Promise<void> };
const AuthContext = createContext<Auth | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);
  const [token, setTokenState] = useState<string | null>(null);

  useEffect(() => {
    void tokenStore.load().then((t) => {
      setTokenState(t);
      setReady(true);
    });
  }, []);

  const setToken = async (t: string | null) => {
    await tokenStore.set(t);
    setTokenState(t);
  };
  return <AuthContext.Provider value={{ ready, token, setToken }}>{children}</AuthContext.Provider>;
}

export function useAuth(): Auth {
  const auth = useContext(AuthContext);
  if (!auth) throw new Error('useAuth outside AuthProvider');
  return auth;
}
