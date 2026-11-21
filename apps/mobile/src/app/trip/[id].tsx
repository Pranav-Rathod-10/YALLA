import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { ScrollView, Text, TextInput } from 'react-native';

import { TripCard } from '../../components/TripCard';
import { Button, Card, Screen, styles } from '../../components/ui';
import { api, unwrap } from '../../lib/api';

export default function TripDetails() {
  const { id } = useLocalSearchParams<{ id: string }>();
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
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['requests'] }),
  });

  if (!trip) return <Screen>{null}</Screen>;
  return (
    <Screen>
      <ScrollView style={{ marginTop: 48 }}>
        <Button title="← Back" variant="secondary" onPress={() => router.back()} />
        <TripCard trip={trip} />
        <Card>
          <Text style={styles.title}>Travellers ({trip.travellers.length})</Text>
          {trip.travellers.map((t, i) => (
            <Text key={t.id}>
              {t.name || 'Traveller'} {i === 0 ? '· Host' : ''}
            </Text>
          ))}
        </Card>
        <Card>
          <TextInput
            style={[styles.input, { minHeight: 80 }]}
            multiline
            maxLength={1024}
            placeholder="Send the host a message with any requests you may have (optional)."
            value={message}
            onChangeText={setMessage}
          />
          <Text style={styles.muted}>{message.length}/1024 characters</Text>
          {request.error && <Text>{request.error.message}</Text>}
          <Button
            title={request.isSuccess ? 'Request sent' : 'Request to Join'}
            disabled={!trip.can_request || request.isPending || request.isSuccess}
            onPress={() => request.mutate()}
          />
        </Card>
      </ScrollView>
    </Screen>
  );
}
