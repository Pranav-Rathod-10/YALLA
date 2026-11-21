import { useState } from 'react';
import { Text, TextInput } from 'react-native';

import { Button, Card, Screen, styles } from '../components/ui';
import { api, unwrap } from '../lib/api';
import { useAuth } from '../lib/auth';
import { colors } from '../theme';

export default function Login() {
  const { setToken } = useAuth();
  const [phone, setPhone] = useState('+919800000001');
  const [code, setCode] = useState('');
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setError(null);
    try {
      if (!sent) {
        const res = unwrap(await api.POST('/v1/auth/otp/request', { body: { phone } }));
        setSent(true);
        if (res.dev_code) setCode(res.dev_code); // dev only
      } else {
        const tokens = unwrap(await api.POST('/v1/auth/otp/verify', { body: { phone, code } }));
        await setToken(tokens.access_token);
      }
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <Screen>
      <Card style={{ marginTop: 80 }}>
        <Text style={styles.h1}>Yalla</Text>
        <TextInput
          style={styles.input}
          value={phone}
          onChangeText={setPhone}
          keyboardType="phone-pad"
        />
        {sent && (
          <TextInput
            style={styles.input}
            value={code}
            onChangeText={setCode}
            keyboardType="number-pad"
            placeholder="Code"
          />
        )}
        {error && <Text style={{ color: colors.danger, marginBottom: 8 }}>{error}</Text>}
        <Button title={sent ? 'Sign in' : 'Send code'} onPress={() => void submit()} />
      </Card>
    </Screen>
  );
}
