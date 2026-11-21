import { useState } from 'react';

import { api, unwrap } from '../api';

export function Login({ onSignedIn }: { onSignedIn: (token: string) => void }) {
  const [phone, setPhone] = useState('+919800000001');
  const [code, setCode] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function requestCode() {
    setError(null);
    try {
      const res = unwrap(await api.POST('/v1/auth/otp/request', { body: { phone } }));
      setSent(true);
      if (res.dev_code) setCode(res.dev_code); // dev only: the API echoes the code
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function verify() {
    setError(null);
    try {
      const tokens = unwrap(await api.POST('/v1/auth/otp/verify', { body: { phone, code } }));
      onSignedIn(tokens.access_token);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <main>
      <div className="card">
        <h1>Yalla</h1>
        <p className="muted">Share a cab. Split the fare.</p>
        <label>
          Phone
          <input value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        {sent && (
          <label>
            Code
            <input value={code} onChange={(e) => setCode(e.target.value)} inputMode="numeric" />
          </label>
        )}
        {error && <p className="error">{error}</p>}
        <button onClick={sent ? verify : requestCode}>{sent ? 'Sign in' : 'Send code'}</button>
      </div>
    </main>
  );
}
