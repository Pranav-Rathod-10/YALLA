import type { Place } from '@yalla/api-client';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';

import { api, unwrap } from '../api';

/** Location sheet (spec 8.1), as an inline autocomplete. */
export function PlacePicker({
  label,
  value,
  onChange,
}: {
  label: string;
  value: Place | null;
  onChange: (place: Place | null) => void;
}) {
  const [q, setQ] = useState('');
  const { data = [] } = useQuery({
    queryKey: ['places', q],
    queryFn: async () => unwrap(await api.GET('/v1/places/search', { params: { query: { q } } })),
    enabled: q.trim().length > 0 && !value,
  });

  return (
    <label>
      {label}
      {value ? (
        <div className="row">
          <span>{value.name}</span>
          <button className="secondary" type="button" onClick={() => onChange(null)}>
            ×
          </button>
        </div>
      ) : (
        <>
          <input placeholder="Location" value={q} onChange={(e) => setQ(e.target.value)} />
          {q && (
            <ul className="suggestions">
              {data.length === 0 && <li className="muted">No matches. Try another place name.</li>}
              {data.map((p) => (
                <li key={p.id} onClick={() => onChange(p)}>
                  <strong>{p.name}</strong> <span className="muted">{p.address}</span>
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </label>
  );
}
