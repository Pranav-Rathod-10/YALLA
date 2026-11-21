import { useQuery } from '@tanstack/react-query';

import { api, unwrap } from '../api';

export function Alerts() {
  const { data = [] } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => unwrap(await api.GET('/v1/me/alerts')),
  });
  return (
    <>
      <h1>Alerts</h1>
      {data.length === 0 && <p className="muted">No alerts yet.</p>}
      {data.map((a) => (
        <div className="card" key={a.id}>
          <p>
            <strong>{a.actor?.name || 'Someone'}</strong> {a.text}
          </p>
          <p className="muted">{new Date(a.created_at).toLocaleString()}</p>
        </div>
      ))}
    </>
  );
}
