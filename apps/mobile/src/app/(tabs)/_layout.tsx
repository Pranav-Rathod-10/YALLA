import { Tabs } from 'expo-router';

import { colors } from '../../theme';

/** Four tabs from spec section 5. The floating pill styling is left for the real UI pass. */
export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: colors.brandDeep,
        tabBarActiveBackgroundColor: colors.brandTint,
      }}
    >
      <Tabs.Screen name="index" options={{ title: 'Home' }} />
      <Tabs.Screen name="trips" options={{ title: 'Trips' }} />
      <Tabs.Screen name="requests" options={{ title: 'Requests' }} />
      <Tabs.Screen name="social" options={{ title: 'Social' }} />
    </Tabs>
  );
}
