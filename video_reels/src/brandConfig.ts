// Fonte de branding para os reels (lado Remotion).
// Espelha assets/profile_config.json usado pelo gerador Python.
// As skills mantem os dois arquivos sincronizados.

import profileConfig from "./brand.json";

export type BrandColors = {
  background: string;
  primary: string;
  secondary: string;
  text_primary: string;
  text_secondary: string;
  accent: string;
  light_gray: string;
};

export type BrandConfig = {
  display_name: string;
  handle: string;
  initials: string;
  verified: boolean;
  tagline: string;
  colors: BrandColors;
};

export const BRAND: BrandConfig = profileConfig as BrandConfig;
