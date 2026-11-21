import { useQuery } from '@tanstack/react-query';
import { router } from 'expo-router';
import { useState } from 'react';
import { FlatList, Text, TextInput } from 'react-native';

import { TripCard } from '../../components/TripCard';
import { Screen, styles } from '../../components/ui';
import { api, unwrap } from '../../lib/api';

export default function Trips() {
  const [to, setTo] = useState('');
  const query = { to: to || undefined };
  const { data = [], isLoading } = useQuery({
    queryKey: ['trips', query],
    queryFn: async () => unwrap(await api.GET('/v1/trips', { params: { query } })),
  });

  return (
    <Screen>
      <Text style={[styles.h1, { marginTop: 48 }]}>Explore all trips</Text>
      <TextInput style={styles.input} placeholder="Destination" value={to} onChangeText={setTo} />
      <FlatList
        data={data}
        keyExtractor={(t) => t.id}
        renderItem={({ item }) => (
          <TripCard trip={item} onPress={() => router.push(`/trip/${item.id}`)} />
        )}
        ListEmptyComponent={
          <Text style={styles.muted}>
            {isLoading ? 'Loading…' : 'No trips match these filters. Clear a filter to see more.'}
          </Text>
        }
      />
    </Screen>
  );
}
