# meuPostInsta — Carrossel + Reels para Instagram

Pipeline completo via **skills do Claude Code** para gerar carrosséis de 9 slides (PNG 1080x1440) e converter em vídeos Reels (MP4 1080x1920) a partir de um tema.

- `/carousel <tema>` → 9 slides Pillow + Helvetica em `assets/generated_carousels/`
- `/carousel-video <tema>` → Reels via Remotion em `video_reels/out/`

## Pré-requisitos

- **[Claude Code](https://claude.com/claude-code)** instalado e funcionando no terminal (as skills só rodam dentro dele).
- **Python 3.10+** (Pillow e requests).
- **Node 18+** (apenas se for usar `/carousel-video`).
- **macOS** ou ajustes para Linux/Windows (o `/carousel-video` usa `sips` para resize).
- **Helvetica Neue** (default macOS) ou ajuste de fonte em `src/designer/professional_carousel.py`.

## Setup rápido

```bash
# 1. Clone
git clone https://github.com/Ebelac/meuPostInsta.git
cd meuPostInsta

# 2. Dependências mínimas (só o necessário pras skills)
pip install -r requirements-minimal.txt

# 3. (Opcional) Dependências do Remotion (Reels)
cd video_reels && npm install && cd ..

# 4. Sua identidade visual
cp assets/profile_config.example.json assets/profile_config.json
# Edite handle, display_name, iniciais, cores, tagline

# 5. (Opcional) Sua foto de perfil
# Coloque em assets/profile/profile_photo.png (recomendado 400x400).
# Se não tiver, o gerador usa as iniciais como fallback.

# 6. Abra o Claude Code dentro do diretório
claude
```

## Uso

Dentro do Claude Code, basta:

```
/carousel Tesla virou empresa de IA disfarçada de montadora?
```

A skill faz o ciclo completo:

1. Pergunta tom + nível de escrita + fonte de imagens (salva preferências em `assets/content_preferences.json`)
2. Pesquisa o tema na web (`WebSearch`) e verifica números/datas/casos
3. Estrutura 9 slides aplicando o **PADRÃO** (hook magnético → foreshadowing → mas/então → linguagem 5ª série → satisfação+surpresa)
4. Copia `MODELO_PADRAO_CARROSSEL/template_gerador_final.py` para `generators/generate_<tema>_modelo_principal.py`, personaliza copy
5. Lê `assets/profile_config.json` para o header (nome, @, foto, cores)
6. Gera `assets/generated_carousels/<tema>_slide_01..09.png`
7. Salva copy do post em `assets/posts/<tema>.md` com fontes verificadas

Para virar Reels:

```
/carousel-video <tema>
```

## Estrutura

```
meuPostInsta/
├── .claude/skills/
│   ├── carousel/SKILL.md          # Skill /carousel
│   └── carousel-video/SKILL.md    # Skill /carousel-video
├── MODELO_PADRAO_CARROSSEL/
│   └── template_gerador_final.py  # Template base (clonado pela skill)
├── src/designer/
│   └── professional_carousel.py   # Classe base (header, footer, profile loading)
├── video_reels/
│   ├── src/                       # Componentes Remotion (TSX)
│   └── public/                    # Imagens dos slides para o vídeo
├── assets/
│   ├── profile/                   # Sua foto de perfil
│   ├── custom_images/             # Imagens customizadas por slide (1.png..9.png)
│   ├── generated_carousels/       # Output dos PNGs (gitignored)
│   └── posts/                     # Output das copies markdown (gitignored)
├── requirements-minimal.txt       # Dependências só das skills
└── requirements.txt               # Pipeline completo (scraper, scheduler, db, etc)
```

## Estrutura do `profile_config.json`

```json
{
  "display_name": "Seu Nome",
  "handle": "@seuhandle",
  "initials": "SN",
  "verified": true,
  "tagline": "",
  "colors": {
    "background": "#FFFFFF",
    "primary": "#1DA1F2",
    "secondary": "#14171A",
    "text_primary": "#14171A",
    "text_secondary": "#657786",
    "accent": "#1DA1F2",
    "light_gray": "#F7F9FA"
  }
}
```

A `tagline` (opcional) aparece no rodapé do slide 9 — pode ser uma citação, versículo, slogan ou ficar vazia.

Quando você edita esse arquivo, o `/carousel-video` espelha automaticamente em `video_reels/src/brand.json` na primeira execução.

## Regras de copy aplicadas pela skill

- **Sem bullets nem numeração** (`•`, `1.`, `2.`) — toda copy em prosa corrida.
- **Margens simétricas obrigatórias.**
- **Tom envolvente, jornalístico, sem jargão** (configurável via `content_preferences.json`).
- **Slide 9 sempre com CTA** "Siga {handle}" + tagline opcional.
- **Dados verificados** — a skill roda `WebSearch` antes de redigir números/datas/casos. Sem chute em tom alarmista.

## Personalização

- **Paleta dark**: edite `colors` no `profile_config.json` para fundo escuro.
- **Imagens customizadas**: coloque PNGs em `assets/custom_images/` com nome `1.png` … `9.png` e responda `pasta` quando a skill perguntar a fonte de imagens.
- **URLs específicas**: responda `links` e cole as URLs no chat.
- **Auto (Unsplash)**: deixe a skill buscar — funciona bem em temas concretos, falha em ângulos abstratos (capex, governança, etc).

## Pipeline de automação completo (legado)

O diretório também contém um pipeline antigo de scraping + curadoria + agendamento (em `src/scrapers/`, `src/curator/`, `src/scheduler/`, `src/publisher/`, `dashboard/`, `app.py`). Esse fluxo requer o `requirements.txt` cheio + `.env` com OPENAI/ANTHROPIC/INSTAGRAM credentials. **Não é necessário para usar as skills** — só se você quiser o scraper/scheduler de notícias.

## Licença

MIT.
