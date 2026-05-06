# Skills de Carrossel + Video para Instagram

Duas skills do Claude Code que automatizam o ciclo completo: pesquisa de tema → carrossel de 9 slides (PNG) → video motion graphics (MP4) para Reels.

## O que vem na caixa

- `/carousel <tema>` — gera 9 slides 1080x1440 a partir de um tema (Pillow + Helvetica).
- `/carousel-video <tema>` — converte o carrossel em um video Reels 1080x1920 com Remotion (Ken Burns, glitch cromatico, mask reveal, parallax 3D).

## Setup rapido

```bash
# 1. Clone
git clone <este-repo> meu-instagram
cd meu-instagram

# 2. Dependencias Python
pip install -r requirements.txt

# 3. Dependencias do Remotion
cd video_reels && npm install && cd ..

# 4. Sua identidade visual
cp assets/profile_config.example.json assets/profile_config.json
# edite handle, nome, iniciais, cores, tagline
# OBS: o lado Remotion le de video_reels/src/brand.json — copie o mesmo conteudo

# 5. Sua foto de perfil (circular no header)
cp /caminho/para/sua_foto.png assets/profile/profile_photo.png

# 6. (Opcional) Imagens customizadas por slide
# Coloque em assets/custom_images/1.png .. 9.png — tem prioridade sobre fallback do Pexels/Unsplash
```

Pronto. Agora abra o Claude Code no diretorio e rode `/carousel <seu tema>`.

## Estrutura do `profile_config.json`

```json
{
  "display_name": "Seu Nome",       // aparece no header dos slides e header do video
  "handle": "@seuhandle",           // aparece no @ do header e no CTA "Siga @seuhandle"
  "initials": "SN",                 // 2 letras de fallback se a foto nao carregar
  "verified": true,                 // mostra o badge azul de verificado
  "tagline": "",                    // texto opcional no rodape do slide 9 (ex: versiculo, citacao)
  "colors": {
    "background": "#FFFFFF",
    "primary": "#1DA1F2",           // cor principal (badge, accent)
    "text_primary": "#14171A",
    "text_secondary": "#657786",
    "accent": "#1DA1F2",
    "light_gray": "#F7F9FA"
  }
}
```

Quando voce edita esse arquivo, **tambem precisa atualizar `video_reels/src/brand.json`** com o mesmo conteudo. As skills cuidam disso automaticamente quando executadas.

## Como as skills funcionam

### `/carousel <tema>`
1. Pesquisa o tema na web e estrutura 9 slides (hook → numeros → tecnico → como funciona → casos → oficial → checklist → sinais → CTA).
2. Copia `MODELO_PADRAO_CARROSSEL/template_gerador_final.py` e personaliza com o conteudo.
3. Le `assets/profile_config.json` para o header (nome, @, foto, cores).
4. Gera `assets/generated_carousels/[tema]_slide_01..09.png`.
5. Gera copy do post em `assets/posts/[tema].md`.

### `/carousel-video <tema>`
1. Verifica que o carrossel ja foi gerado (senao, sugere rodar `/carousel` primeiro).
2. Copia imagens dos slides para `video_reels/public/[tema]/` (resize <= 1200px com `sips`).
3. Cria componente Remotion em `video_reels/src/[Tema].tsx` que importa `BRAND` de `brandConfig.ts`.
4. Registra a composicao em `video_reels/src/Root.tsx`.
5. Renderiza para `video_reels/out/[tema].mp4` (1080x1920, 30fps, ~87s).

## Regras de copy (importante)

- **Sem bullets nem numeracao** (`•`, `1.`, `2.`) — toda copy em prosa corrida.
- Margens simetricas obrigatorias.
- Tom envolvente, jornalistico, sem jargao.
- Slide 9 sempre com CTA "Siga {handle}" + tagline opcional do config.

## Personalizacao avancada

- **Paleta dark**: edite `colors` no `profile_config.json` para fundo escuro.
- **Estilo do video**: a skill `/carousel-video` tem 3 paletas pre-definidas (Dark/Sombrio, Tech, Light) — escolha pelo tom do tema, ou personalize no componente gerado.
- **Templates de referencia**: veja `video_reels/src/PalantirManifesto.tsx` (sombrio) e `XeroxStarStories.tsx` (tech).

## Requisitos

- Python 3.10+, Pillow, requests
- Node 18+ (para Remotion)
- macOS (`sips` para resize) ou ajuste o comando para Linux/Windows
- Helvetica Neue (macOS) ou ajustes de fonte em `professional_carousel.py`
