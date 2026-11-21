import type { Trip } from '@yalla/api-client';

import { formatWindow } from '../api';

export function TripCard({ trip, onOpen }: { trip: Trip; onOpen?: () => void }) {
  return (
    <div className="card" onClick={onOpen} style={{ cursor: onOpen ? 'pointer' : undefined }}>
      <div className="row" style={{ marginBottom: 8 }}>
        <span className="pill">{formatWindow(trip.departs_at, trip.window_ends_at)}</span>
        {trip.seats_left <= 1 && (
          <span className="chip warn">{trip.seats_left === 0 ? 'Full' : 'Only 1 seat'}</span>
        )}
      </div>
      <h3>{trip.title}</h3>
      <p className="muted">
        {trip.from_place.name} → {trip.to_place.name} · {trip.seats_taken}/{trip.passenger_seats}{' '}
        going
      </p>
      <div className="row">
        <span className="chip">{trip.vehicle}</span>
        <span className="chip">
          {trip.cost_per_person != null ? `₹${trip.cost_per_person} / person` : 'Cost shared'}
        </span>
        {trip.joining === 'instant' && <span className="chip">Instant join</span>}
        {trip.females_only && <span className="chip female">Females only</span>}
      </div>
    </div>
  );
}
