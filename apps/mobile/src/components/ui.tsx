import type { ReactNode } from 'react';
import { Pressable, StyleSheet, Text, View, type ViewStyle } from 'react-native';

import { colors, radius, space } from '../theme';

export function Screen({ children }: { children: ReactNode }) {
  return <View style={styles.screen}>{children}</View>;
}

export function Card({ children, style }: { children: ReactNode; style?: ViewStyle }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Button({
  title,
  onPress,
  disabled,
  variant = 'primary',
}: {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary';
}) {
  const secondary = variant === 'secondary';
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled}
      style={[styles.button, secondary && styles.secondary, disabled && { opacity: 0.5 }]}
    >
      <Text style={[styles.buttonText, secondary && { color: colors.text }]}>{title}</Text>
    </Pressable>
  );
}

export function Chip({ label, tone }: { label: string; tone?: 'female' | 'warn' }) {
  const bg =
    tone === 'female' ? colors.femaleBg : tone === 'warn' ? colors.warnFill : colors.surfaceGray;
  const fg = tone === 'female' ? colors.femaleInk : tone === 'warn' ? colors.warnInk : colors.text;
  return (
    <View style={[styles.chip, { backgroundColor: bg }]}>
      <Text style={{ color: fg, fontSize: 12 }}>{label}</Text>
    </View>
  );
}

export const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.surfaceGray, padding: space.screen },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.card,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 8,
    shadowOffset: { width: 0, height: 2 },
    elevation: 1,
  },
  title: { fontSize: 17, fontWeight: '600', color: colors.text },
  h1: { fontSize: 26, fontWeight: '700', color: colors.text, marginBottom: 12 },
  muted: { color: colors.textMuted, fontSize: 13 },
  button: {
    backgroundColor: colors.brand,
    borderRadius: radius.button,
    minHeight: 44,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  secondary: { backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.line },
  buttonText: { color: colors.brandInk, fontWeight: '600', fontSize: 16 },
  chip: {
    borderRadius: radius.pill,
    paddingHorizontal: 10,
    paddingVertical: 3,
    marginRight: 6,
    marginTop: 6,
  },
  row: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center' },
  input: {
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 12,
    padding: 12,
    backgroundColor: colors.surface,
    marginBottom: 12,
  },
});
