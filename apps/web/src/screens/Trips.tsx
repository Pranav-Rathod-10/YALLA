import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { api, unwrap } from '../api';
import { TripCard } from './TripCard';

export function Trips({ onOpen }: { onOpen: (id: string) => void }) {
  const [to, setTo] = useState('');
  const [from, setFrom] = useState('');
  const [date, setDate] = useState('');
  const query = { to: to || undefined, from: from || undefined, date: date || undefined };

  const { data, isLoading, error } = useQuery({
    queryKey: ['trips', query],
    queryFn: async () => unwrap(await api.GET('/v1/trips', { params: { query } })),
  });

  return (
    <>
      <div className="card">
        <h2>Filter by</h2>
        <div className="row">
          <input placeholder="Destination" value={to} onChange={(e) => setTo(e.target.value)} />
          <input placeholder="Start point" value={from} onChange={(e) => setFrom(e.target.value)} />
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
      </div>
      <h2>Explore all trips</h2>
      {isLoading && <p className="muted">Loading…</p>}
      {error && <p className="error">{(error as Error).message}</p>}
      {data?.length === 0 && (
        <p className="muted">No trips match these filters. Clear a filter to see more.</p>
      )}
      {data?.map((t) => <TripCard key={t.id} trip={t} onOpen={() => onOpen(t.id)} />)}
    </>
  );
}
