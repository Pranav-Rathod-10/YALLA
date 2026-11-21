/** Design tokens from docs/spec/frontend-spec.md section 4. Single source for colours and radii. */
export const colors = {
  brand: '#2F9E5E',
  brandInk: '#FFFFFF',
  brandTint: '#D7EFE0',
  brandDeep: '#1F6B3F',
  text: '#141816',
  textMuted: '#5B625E',
  textSubtle: '#7A817C',
  line: '#E3E7E3',
  surfaceGray: '#F1F2F1',
  surface: '#FFFFFF',
  timePill: '#2F6DF6',
  warnFill: '#F6A93B',
  warnInk: '#3B2500',
  femaleBg: '#FDE7F1',
  femaleInk: '#A3185F',
  danger: '#B3261E',
} as const;

export const radius = { card: 18, button: 14, sheet: 34, pill: 999 } as const;
export const space = { screen: 18 } as const;
