---
name: carousel-video
description: Converte um carrossel existente em video motion graphics para Instagram Reels usando Remotion. Use quando o usuario pedir para transformar carrossel em video, criar motion graphics, ou gerar reels.
arguments: [tema]
allowed-tools: Bash(npx*) Bash(npm*) Bash(python*) Bash(node*) Bash(mkdir*) Bash(cp*) Bash(ls*) Bash(sips*) Bash(curl*) Bash(wget*) Read Write Edit Glob Grep AskUserQuestion
---

# Gerador de Video Motion Graphics

Voce vai converter o carrossel sobre **$tema** em um video motion graphics para Instagram Reels usando Remotion.

## Passo 0 - Pre-requisitos

**Verificar:**
1. `assets/generated_carousels/[tema]_slide_*.png` existe (9 arquivos). Se NAO, parar e instruir o usuario a rodar `/carousel [tema]` antes.
2. `video_reels/src/brand.json` existe e tem mesmo conteudo de `assets/profile_config.json`. Se diferente, sincronizar (a skill `/carousel` ja faz isso, mas reconfirme).
3. `video_reels/node_modules/` existe. Se nao, rodar `cd video_reels && npm install`.
4. Existe foto de perfil em `video_reels/public/[serie]/profile.png`? Se nao, copiar de `assets/profile/profile_photo.{png,jpg}` na hora.

**Perguntar com `AskUserQuestion`** (se nao for obvio do contexto):
- `tom` — `dark` (sombrio, tipo Palantir), `tech` (moderno, tipo Xerox), `light` (clean), ou `custom` (perguntar paleta).
- `paleta_custom` — se escolher custom, pedir 3 hex codes (bg, accent, texto).

## Passo 1 - Preparar assets

```bash
mkdir -p video_reels/public/[serie_snake_case]/

# Copiar slides (9 imagens)
cp assets/generated_carousels/[tema]_slide_*.png video_reels/public/[serie]/
# OU melhor: copiar imagens originais (sem o overlay de texto) se existirem em assets/slide_images/
cp assets/slide_images/[tema]_slide_*.jpg video_reels/public/[serie]/

# Copiar profile
cp assets/profile/profile_photo.png video_reels/public/[serie]/profile.png

# Resize obrigatorio (>1200px causa falha no Remotion)
sips --resampleWidth 1200 video_reels/public/[serie]/slide_*.jpg
```

## Passo 2 - Criar componente React

Criar `video_reels/src/[ThemePascalCase].tsx` com:

```typescript
import React from "react";
import {
  AbsoluteFill, Img, staticFile, useCurrentFrame, useVideoConfig,
  interpolate, spring, Easing, random,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { BRAND } from "./brandConfig";  // OBRIGATORIO - evita hardcode de @handle
```

### Dados dos slides

```typescript
const SLIDES = [
  {
    tag: "TAG",
    headline: "Titulo\nmulti-linha",
    body: "Texto corrido do slide sem bullets.",
    source: BRAND.handle,  // sempre via BRAND, nunca hardcoded
  },
  // ... 9 slides
  // No slide 9 (CTA), adicionar { ..., cta: true }
];

const SLIDE_DURATION = 300;      // 10s a 30fps
const TRANSITION_DURATION = 18;  // 0.6s
```

### Toolkit de animacao (escolher conforme tom)

| Componente | Uso | Tom |
|------------|-----|-----|
| **FullscreenImage** | Imagem com Ken Burns + parallax 3D | Universal |
| **Headline** | Mask reveal + tilt 3D linha-a-linha | Universal |
| **BodyText** | Word-by-word blur resolve | Universal |
| **ChromaGlitch** | Aberracao cromatica + slice | Sombrio/Tech |
| **ScanLines** | Linhas CRT overlay | Sombrio/Retro |
| **FilmGrain** | SVG noise texture | Sombrio |
| **ProgressRing** | SVG ring animado | Tech/Moderno |
| **WordReveal** | Palavra-por-palavra com spring | Todos |

### Tecnicas-chave

```typescript
// Ken Burns
const scale = interpolate(frame, [0, durationInFrames], [1.08, 1.2], {
  extrapolateLeft: "clamp", extrapolateRight: "clamp",
});

// Spring (entradas organicas)
const entry = spring({ fps, frame: frame - delay, config: { damping: 40, mass: 0.5 } });

// Word-by-word
const wordDelay = startFrame + wordIndex * 1.5;

// Mask reveal (clip-path)
const clipReveal = interpolate(frame, [delay, delay + 14], [0, 100], { ... });
clipPath: `inset(0 ${100 - clipReveal}% 0 0)`

// Chromatic aberration: red offset + cyan inverse, mixBlendMode: "screen"

// 3D tilt
transform: `perspective(800px) rotateX(${rotX}deg) translateY(${y}px)`
```

### Footer (padrao two-column)

- **Esquerda**: profile photo (80px circular) + `{BRAND.handle}`
- **Direita**: `Fonte: {s.source}` em cima, contador `01 / 09` embaixo

### CTA do slide 9

```tsx
{s.cta && (
  <div style={{ ... }}>
    Siga {BRAND.handle}
    {BRAND.tagline && <div style={{ ... }}>{BRAND.tagline}</div>}
  </div>
)}
```

## Passo 3 - Safe zones do Reels (OBRIGATORIO)

Instagram cobre areas com UI:

| Zona | Area | Posicao do conteudo |
|------|------|---------------------|
| Topo | ~250px | Tag em `top: 280px`, Headline em `top: 340px` |
| Base | ~300px | Footer em `bottom: 300px`, CTA em `bottom: 430px`, Imagem ate `bottom: 300px` |

Adicionar fill preto nas zonas (topo 250px e base 300px).

## Passo 4 - Registrar no Root.tsx

```typescript
import { [ThemePascalCase] } from "./[ThemePascalCase]";

const THEME_SLIDES = 9;
const THEME_SLIDE_DURATION = 300;
const THEME_TRANSITION = 18;
const THEME_TOTAL_FRAMES =
  THEME_SLIDES * THEME_SLIDE_DURATION - (THEME_SLIDES - 1) * THEME_TRANSITION;

<Composition
  id="[ThemePascalCase]"
  component={[ThemePascalCase]}
  durationInFrames={THEME_TOTAL_FRAMES}
  fps={30}
  width={1080}
  height={1920}
  defaultProps={{}}
/>
```

## Passo 5 - Composicao final

```typescript
export const [ThemePascalCase]: React.FC = () => {
  return (
    <TransitionSeries>
      {SLIDES.map((_, i) => (
        <React.Fragment key={i}>
          <TransitionSeries.Sequence durationInFrames={SLIDE_DURATION}>
            <SlideComponent slideIndex={i} />
          </TransitionSeries.Sequence>
          {i < SLIDES.length - 1 && (
            <TransitionSeries.Transition
              timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
              presentation={fade()}
            />
          )}
        </React.Fragment>
      ))}
    </TransitionSeries>
  );
};
```

## Passo 6 - Preview e render

```bash
cd video_reels

# Preview
npx remotion studio src/index.ts

# Render MP4
npx remotion render src/index.ts [ThemePascalCase] out/[tema].mp4 --codec h264
```

Validar typecheck antes do render:

```bash
cd video_reels && npx tsc --noEmit
```

## Componentes de referencia

- `video_reels/src/PalantirManifesto.tsx` — sombrio, glitch, parallax 3D, dark theme
- `video_reels/src/XeroxStarStories.tsx` — tech, word-by-word, progress ring, light overlays

Ambos ja importam `BRAND` de `brandConfig.ts` — copie o padrao deles.

## Paletas pre-definidas

**Dark/Sombrio** (Palantir):
```
bg: #030303, accent: #E5173F, text: #F0F0F0
filter: saturate(0.3) brightness(0.5) contrast(1.2)
```

**Tech/Modern** (Xerox):
```
bg: #0A0A0A, accent: #1DA1F2, text: #FFFFFF
```

**Light/Clean**:
```
bg: #FFFFFF, accent: #1DA1F2, text: #14171A
```

## Regras Remotion

- Componentes **deterministicos** — sem `Math.random()`, usar `random('seed')` do Remotion.
- Sem `useState`, `useEffect`, `onClick` — tudo via `useCurrentFrame()`.
- Animacoes via `interpolate()` e `spring()` com `extrapolate: "clamp"`.
- Imagens com `<Img>` do Remotion + `staticFile()`.
- Consultar `video_reels/CLAUDE.md` para docs completos.

## Dimensoes

- **1080x1920px** (9:16) Reels/Stories
- **30fps** sempre
- **9 slides x 10s** = ~87s com transicoes

## Checklist final

- [ ] Carrossel verificado em `assets/generated_carousels/`
- [ ] `brand.json` sincronizado com `profile_config.json`
- [ ] Assets em `video_reels/public/[serie]/` (imagens <= 1200px)
- [ ] Componente importa `BRAND` de `brandConfig` — sem hardcode de @handle
- [ ] Registrado no `Root.tsx`
- [ ] Safe zones respeitadas (250px topo, 300px base)
- [ ] Footer com profile + source + contador
- [ ] Slide 9 com `Siga {BRAND.handle}` + `{BRAND.tagline}` (se existir)
- [ ] `npx tsc --noEmit` passa sem erros
- [ ] Video renderizado em `video_reels/out/[tema].mp4`
