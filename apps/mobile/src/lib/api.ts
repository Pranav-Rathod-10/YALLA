import { createYallaClient, type Problem } from '@yalla/api-client';
import * as SecureStore from 'expo-secure-store';

const TOKEN_KEY = 'yalla.token';
let cached: string | null = null;

export const tokenStore = {
  async load(): Promise<string | null> {
    cached = await SecureStore.getItemAsync(TOKEN_KEY);
    return cached;
  },
  async set(token: string | null): Promise<void> {
    cached = token;
    if (token) await SecureStore.setItemAsync(TOKEN_KEY, token);
    else await SecureStore.deleteItemAsync(TOKEN_KEY);
  },
  get: (): string | null => cached,
};

// Android emulator reaches the host machine on 10.0.2.2. Override with EXPO_PUBLIC_API_URL.
export const api = createYallaClient({
  baseUrl: process.env.EXPO_PUBLIC_API_URL ?? 'http://10.0.2.2:8000',
  getToken: tokenStore.get,
});

export function unwrap<T>(result: { data?: T; error?: unknown }): T {
  if (result.error !== undefined || result.data === undefined) {
    const problem = result.error as Partial<Problem> | undefined;
    throw new Error(problem?.detail ?? 'Something went wrong');
  }
  return result.data;
}

export function formatWindow(departsAt: string, endsAt: string): string {
  const start = new Date(departsAt);
  const end = new Date(endsAt);
  const day = start.toLocaleDateString(undefined, {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
  });
  const t = (d: Date) => d.toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' });
  return `${day} · ${t(start)} - ${t(end)}`;
}
