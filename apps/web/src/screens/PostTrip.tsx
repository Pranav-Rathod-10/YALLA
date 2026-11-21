import type { Place } from '@yalla/api-client';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';

import { api, unwrap } from '../api';
import { PlacePicker } from './PlacePicker';

export function PostTrip({ onPosted }: { onPosted: () => void }) {
  const qc = useQueryClient();
  const [from, setFrom] = useState<Place | null>(null);
  const [to, setTo] = useState<Place | null>(null);
  const [date, setDate] = useState('');
  const [time, setTime] = useState('18:00');
  const [windowMinutes, setWindow] = useState<15 | 30>(30);
  const [seats, setSeats] = useState(2);
  const [joining, setJoining] = useState<'approval' | 'instant'>('approval');
  const [femalesOnly, setFemalesOnly] = useState(false);
  const [cost, setCost] = useState('');
  const [shareCost, setShareCost] = useState(true);

  const post = useMutation({
    mutationFn: async () => {
      if (!from || !to || !date || !time) {
        throw new Error('Add destination, starting point, date and departure time to post.');
      }
      return unwrap(
        await api.POST('/v1/trips', {
          body: {
            from_place_id: from.id,
            to_place_id: to.id,
            depart_date: date,
            window_start: time,
            window_minutes: windowMinutes,
            passenger_seats: seats,
            joining,
            females_only: femalesOnly,
            cost_per_person: cost ? Number(cost) : null,
            cost_shared: shareCost,
            vehicle: 'Cab',
          },
        }),
      );
    },
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['trips'] });
      onPosted();
    },
  });

  return (
    <div className="card">
      <h1>Post a Trip</h1>
      <PlacePicker label="Destination" value={to} onChange={setTo} />
      <PlacePicker label="Starting from" value={from} onChange={setFrom} />
      <div className="row">
        <label>
          Date
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </label>
        <label>
          Departure time
          <input type="time" value={time} onChange={(e) => setTime(e.target.value)} />
        </label>
        <label>
          Window
          <select
            value={windowMinutes}
            onChange={(e) => setWindow(Number(e.target.value) as 15 | 30)}
          >
            <option value={15}>15 min</option>
            <option value={30}>30 min</option>
          </select>
        </label>
      </div>
      <label>
        Seats available (max 3)
        <input
          type="number"
          min={1}
          max={3}
          value={seats}
          onChange={(e) => setSeats(Number(e.target.value))}
        />
        <span className="muted">You + {seats} will be sitting in the cab</span>
      </label>
      <label>
        Joining
        <select
          value={joining}
          onChange={(e) => setJoining(e.target.value as 'approval' | 'instant')}
        >
          <option value="approval">Host approval</option>
          <option value="instant">Instant join</option>
        </select>
      </label>
      <label className="row">
        <input
          type="checkbox"
          style={{ width: 'auto' }}
          checked={femalesOnly}
          onChange={(e) => setFemalesOnly(e.target.checked)}
        />
        Females only
      </label>
      <label className="row">
        <input
          type="checkbox"
          style={{ width: 'auto' }}
          checked={shareCost}
          onChange={(e) => setShareCost(e.target.checked)}
        />
        Share cost
      </label>
      <label>
        Cost per person (₹, optional)
        <input inputMode="numeric" value={cost} onChange={(e) => setCost(e.target.value)} />
      </label>
      {post.error && <p className="error">{post.error.message}</p>}
      <button disabled={post.isPending} onClick={() => post.mutate()}>
        Post Trip
      </button>
    </div>
  );
}
