import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { api, unwrap } from '../api';

export function Requests() {
  const qc = useQueryClient();
  const [direction, setDirection] = useState<'sent' | 'received'>('sent');
  const { data = [] } = useQuery({
    queryKey: ['requests', direction],
    queryFn: async () =>
      unwrap(await api.GET('/v1/me/requests', { params: { query: { direction } } })),
  });
  const decide = useMutation({
    mutationFn: async ({ id, status }: { id: string; status: 'accepted' | 'declined' }) =>
      unwrap(
        await api.PATCH('/v1/requests/{request_id}', {
          params: { path: { request_id: id } },
          body: { status },
        }),
      ),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['requests'] }),
  });
  const cancel = useMutation({
    mutationFn: async (id: string) =>
      unwrap(
        await api.DELETE('/v1/requests/{request_id}', { params: { path: { request_id: id } } }),
      ),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['requests'] }),
  });

  return (
    <>
      <div className="row" style={{ marginBottom: 12 }}>
        {(['sent', 'received'] as const).map((d) => (
          <button
            key={d}
            className={direction === d ? '' : 'secondary'}
            onClick={() => setDirection(d)}
          >
            {d === 'sent' ? 'Sent' : 'Received'}
          </button>
        ))}
      </div>
      {data.length === 0 && <p className="muted">Nothing here yet.</p>}
      {data.map((r) => (
        <div className="card" key={r.id}>
          <p>
            {direction === 'sent' ? (
              <strong>{r.trip_title}</strong>
            ) : (
              <>
                <strong>{r.requester.name || 'Someone'}</strong> wants to join{' '}
                <strong>{r.trip_title}</strong>
              </>
            )}
          </p>
          <div className="row">
            <span className="chip">{r.status}</span>
            {direction === 'received' && r.status === 'pending' && (
              <>
                <button
                  className="secondary"
                  onClick={() => decide.mutate({ id: r.id, status: 'declined' })}
                >
                  Decline
                </button>
                <button onClick={() => decide.mutate({ id: r.id, status: 'accepted' })}>
                  Accept
                </button>
              </>
            )}
            {direction === 'sent' && (r.status === 'pending' || r.status === 'accepted') && (
              <button
                className="secondary"
                onClick={() => {
                  // YAL-B06: confirm before cancelling instead of a single accidental tap.
                  if (window.confirm('Cancel this request?')) cancel.mutate(r.id);
                }}
              >
                Cancel request
              </button>
            )}
          </div>
        </div>
      ))}
    </>
  );
}
