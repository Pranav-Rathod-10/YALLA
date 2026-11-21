import createClient, { type Middleware } from 'openapi-fetch';

import type { components, paths } from './schema';

export type Schemas = components['schemas'];
export type Trip = Schemas['TripOut'];
export type TripDetail = Schemas['TripDetail'];
export type TripRequest = Schemas['TripRequestOut'];
export type Place = Schemas['PlaceOut'];
export type Event = Schemas['EventOut'];
export type Alert = Schemas['AlertOut'];
export type Me = Schemas['Me'];

/** RFC 7807 body returned by the API for every domain error. */
export type Problem = { title: string; status: number; code: string; detail: string };

export type YallaClientOptions = {
  baseUrl: string;
  /** Returns the current access token, or null when signed out. */
  getToken: () => string | null | Promise<string | null>;
};

export function createYallaClient({ baseUrl, getToken }: YallaClientOptions) {
  const client = createClient<paths>({ baseUrl });
  const auth: Middleware = {
    async onRequest({ request }) {
      const token = await getToken();
      if (token) request.headers.set('Authorization', `Bearer ${token}`);
      return request;
    },
  };
  client.use(auth);
  return client;
}

export type YallaClient = ReturnType<typeof createYallaClient>;
export type { components, paths };
