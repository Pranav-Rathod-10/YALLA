import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { FlatList, Text, View } from 'react-native';

import { Button, Card, Chip, Screen, styles } from '../../components/ui';
import { api, unwrap } from '../../lib/api';

export default function Requests() {
  const qc = useQueryClient();
  const [direction, setDirection] = useState<'sent' | 'received'>('sent');
  const { data = [] } = useQuery({
    queryKey: ['requests', direction],
    queryFn: async () =>
      unwrap(await api.GET('/v1/me/requests', { params: { query: { direction } } })),
  });
  const decide = useMutation({
    mutationFn: async (v: { id: string; status: 'accepted' | 'declined' }) =>
      unwrap(
        await api.PATCH('/v1/requests/{request_id}', {
          params: { path: { request_id: v.id } },
          body: { status: v.status },
        }),
      ),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ['requests'] }),
  });

  return (
    <Screen>
      <View style={[styles.row, { gap: 8, marginTop: 48, marginBottom: 12 }]}>
        <Button
          title="Sent"
          variant={direction === 'sent' ? 'primary' : 'secondary'}
          onPress={() => setDirection('sent')}
        />
        <Button
          title="Received"
          variant={direction === 'received' ? 'primary' : 'secondary'}
          onPress={() => setDirection('received')}
        />
      </View>
      <FlatList
        data={data}
        keyExtractor={(r) => r.id}
        ListEmptyComponent={<Text style={styles.muted}>Nothing here yet.</Text>}
        renderItem={({ item: r }) => (
          <Card>
            <Text style={styles.title}>
              {direction === 'sent'
                ? r.trip_title
                : `${r.requester.name || 'Someone'} wants to join ${r.trip_title}`}
            </Text>
            <View style={[styles.row, { gap: 8 }]}>
              <Chip label={r.status} />
              {direction === 'received' && r.status === 'pending' && (
                <>
                  <Button
                    title="Decline"
                    variant="secondary"
                    onPress={() => decide.mutate({ id: r.id, status: 'declined' })}
                  />
                  <Button
                    title="Accept"
                    onPress={() => decide.mutate({ id: r.id, status: 'accepted' })}
                  />
                </>
              )}
            </View>
          </Card>
        )}
      />
    </Screen>
  );
}
