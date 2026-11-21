import { createYallaClient, type Problem } from '@yalla/api-client';

const TOKEN_KEY = 'yalla.token';

export const tokenStore = {
  get: (): string | null => {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  },
  set: (token: string | null) => {
    try {
      if (token) localStorage.setItem(TOKEN_KEY, token);
      else localStorage.removeItem(TOKEN_KEY);
    } catch {
      /* storage unavailable: stay signed in for this tab only */
    }
  },
};

export const api = createYallaClient({
  baseUrl: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  getToken: tokenStore.get,
});

/** Unwraps an openapi-fetch result, throwing the API's problem detail as an Error. */
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
