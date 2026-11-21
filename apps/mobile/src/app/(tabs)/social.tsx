import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { FlatList, Pressable, Text, View } from 'react-native';

import { TripCard } from '../../components/TripCard';
import { Button, Card, Screen, styles } from '../../components/ui';
import { api, unwrap } from '../../lib/api';

export default function Social() {
  const [picked, setPicked] = useState<{ id: string; direction: 'to_event' | 'from_event' } | null>(
    null,
  );
  const { data: events = [] } = useQuery({
    queryKey: ['events'],
    queryFn: async () => unwrap(await api.GET('/v1/events')),
  });
  const { data: rides = [], error } = useQuery({
    queryKey: ['event-rides', picked],
    enabled: picked !== null,
    queryFn: async () =>
      unwrap(
        await api.GET('/v1/events/{event_id}/rides', {
          params: { path: { event_id: picked!.id }, query: { direction: picked!.direction } },
        }),
      ),
  });

  return (
    <Screen>
      <Text style={[styles.h1, { marginTop: 48 }]}>Big events</Text>
      <FlatList
        data={events}
        keyExtractor={(e) => e.id}
        renderItem={({ item: e }) => (
          <Pressable onPress={() => setPicked({ id: e.id, direction: 'to_event' })}>
            <Card>
              <Text style={styles.title}>{e.name}</Text>
              <Text style={styles.muted}>
                {new Date(e.starts_at).toLocaleString()} · {e.venue.name}
              </Text>
              {picked?.id === e.id && (
                <View style={{ marginTop: 8, gap: 8 }}>
                  <View style={[styles.row, { gap: 8 }]}>
                    <Button
                      title="Home → Event"
                      onPress={() => setPicked({ id: e.id, direction: 'to_event' })}
                    />
                    <Button
                      title="Event → Home"
                      variant="secondary"
                      onPress={() => setPicked({ id: e.id, direction: 'from_event' })}
                    />
                  </View>
                  {error && <Text style={styles.muted}>{(error as Error).message}</Text>}
                  {rides.length === 0 && !error && <Text style={styles.muted}>No rides yet.</Text>}
                  {rides.map((t) => (
                    <TripCard key={t.id} trip={t} />
                  ))}
                </View>
              )}
            </Card>
          </Pressable>
        )}
      />
    </Screen>
  );
}
