import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Redirect, Stack, useSegments } from 'expo-router';

import { AuthProvider, useAuth } from '../lib/auth';

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 15_000 } } });

function Gate() {
  const { ready, token } = useAuth();
  const segments = useSegments();
  if (!ready) return null;
  const onLogin = segments[0] === 'login';
  if (!token && !onLogin) return <Redirect href="/login" />;
  if (token && onLogin) return <Redirect href="/" />;
  return <Stack screenOptions={{ headerShown: false }} />;
}

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Gate />
      </AuthProvider>
    </QueryClientProvider>
  );
}
