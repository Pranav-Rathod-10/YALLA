import type { Trip } from '@yalla/api-client';
import { Pressable, Text, View } from 'react-native';

import { formatWindow } from '../lib/api';
import { colors } from '../theme';
import { Card, Chip, styles } from './ui';

export function TripCard({ trip, onPress }: { trip: Trip; onPress?: () => void }) {
  return (
    <Pressable onPress={onPress} disabled={!onPress}>
      <Card>
        <View
          style={{
            alignSelf: 'flex-start',
            backgroundColor: colors.timePill,
            borderRadius: 999,
            paddingHorizontal: 10,
            paddingVertical: 4,
            marginBottom: 8,
          }}
        >
          <Text style={{ color: '#fff', fontSize: 12, fontWeight: '600' }}>
            {formatWindow(trip.departs_at, trip.window_ends_at)}
          </Text>
        </View>
        <Text style={styles.title}>{trip.title}</Text>
        <Text style={styles.muted}>
          {trip.from_place.name} → {trip.to_place.name} · {trip.seats_taken}/{trip.passenger_seats}{' '}
          going
        </Text>
        <View style={styles.row}>
          <Chip label={trip.vehicle} />
          <Chip
            label={
              trip.cost_per_person != null ? `₹${trip.cost_per_person} / person` : 'Cost shared'
            }
          />
          {trip.seats_left === 1 && <Chip label="Only 1 seat" tone="warn" />}
          {trip.females_only && <Chip label="Females only" tone="female" />}
        </View>
      </Card>
    </Pressable>
  );
}
