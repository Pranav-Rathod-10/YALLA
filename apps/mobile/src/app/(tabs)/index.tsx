import { router } from 'expo-router';
import { Pressable, Text, View } from 'react-native';

import { Button, Card, Screen, styles } from '../../components/ui';
import { useAuth } from '../../lib/auth';

const CARDS = [
  ['TRIPS', 'Find trips. Join the ride', '/trips'],
  ['REQUESTS', 'Track your requests', '/requests'],
  ['SOCIAL', 'Rides to big events.', '/social'],
] as const;

export default function Home() {
  const { setToken } = useAuth();
  return (
    <Screen>
      <Text style={[styles.h1, { marginTop: 48 }]}>Hey!</Text>
      <View style={{ gap: 12 }}>
        {CARDS.map(([title, line, href]) => (
          <Pressable key={title} onPress={() => router.push(href)}>
            <Card>
              <Text style={styles.title}>{title}</Text>
              <Text style={styles.muted}>{line}</Text>
            </Card>
          </Pressable>
        ))}
      </View>
      <Button title="Log out" variant="secondary" onPress={() => void setToken(null)} />
    </Screen>
  );
}
