import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { api, unwrap } from '../api';
import { TripCard } from './TripCard';

export function TripDetail({ id, onBack }: { id: string; onBack: () => void }) {
  const qc = useQueryClient();
  const [message, setMessage] = useState('');
  const { data: trip } = useQuery({
    queryKey: ['trip', id],
    queryFn: async () =>
      unwrap(await api.GET('/v1/trips/{trip_id}', { params: { path: { trip_id: id } } })),
  });
  const request = useMutation({
    mutationFn: async () =>
      unwrap(
        await api.POST('/v1/trips/{trip_id}/requests', {
          params: { path: { trip_id: id } },
          body: { message: message || null },
        }),
      ),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['trip', id] });
      void qc.invalidateQueries({ queryKey: ['requests'] });
    },
  });

  if (!trip) return <p className="muted">Loading…</p>;
  return (
    <>
      <button className="secondary" onClick={onBack}>
        ← Back
      </button>
      <TripCard trip={trip} />
      <div className="card">
        <h3>Travellers ({trip.travellers.length})</h3>
        {trip.travellers.map((t, i) => (
          <p key={t.id}>
            {t.name || 'Traveller'} <span className="muted">{i === 0 ? '· Trip host' : ''}</span>
          </p>
        ))}
      </div>
      <div className="card">
        <h3>Request to Join</h3>
        <textarea
          maxLength={1024}
          rows={3}
          placeholder="Send the host a message with any requests you may have (optional)."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <p className="muted">{message.length}/1024 characters</p>
        {request.error && <p className="error">{request.error.message}</p>}
        {request.isSuccess ? (
          <p>Request sent ({request.data.status}).</p>
        ) : (
          <button
            disabled={!trip.can_request || request.isPending}
            onClick={() => request.mutate()}
          >
            {trip.can_request ? 'Send Request' : 'You cannot request this trip'}
          </button>
        )}
      </div>
    </>
  );
}
