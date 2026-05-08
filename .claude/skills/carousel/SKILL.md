---
name: carousel
description: Gera um carrossel de 9 slides para Instagram a partir de um tema. Use quando o usuario pedir para criar um carrossel, posts, ou slides.
arguments: [tema]
allowed-tools: Bash(python*) Bash(mkdir*) Bash(cp*) Bash(ls*) Bash(curl*) Read Write Edit Glob Grep AskUserQuestion WebSearch WebFetch
---

# Gerador de Carrossel Instagram

Voce vai gerar um carrossel completo de 9 slides para Instagram sobre o tema: **$tema**

---

## Passo 0 — Setup de identidade (1x por repo)

Garanta que `assets/profile_config.json` existe.

Se NAO existir, perguntar via `AskUserQuestion`:
- `handle` — Instagram com @ (ex: `@seuhandle`)
- `display_name` — nome exibido no header (ex: `Seu Nome`)
- `initials` — 2 letras de fallback (ex: `SN`)
- `verified` — exibir badge azul? (sim/nao)
- `tagline` — texto opcional no rodape do slide 9 (versiculo, citacao, vazio)
- `paleta` — `light` / `dark` / `tech` / `custom` (5 hex codes)

Criar `assets/profile_config.json` (estrutura: ver `assets/profile_config.example.json`) e **espelhar** em `video_reels/src/brand.json`.

Se foto nao existir em `assets/profile/profile_photo.{png,jpg}`, **perguntar via `AskUserQuestion`** se o usuario quer:
- **Mandar agora**: usuario cola caminho local (ex: `/Users/voce/Downloads/foto.jpg`) ou URL. Drag-drop do Finder no chat tambem funciona — o caminho aparece como texto.
  Rode `python3 scripts/setup_profile_photo.py "<caminho-ou-url>"` — ele faz crop quadrado 400x400 e salva no lugar certo.
- **Pular**: uso as iniciais (do `profile_config.json`) como fallback.

Nao pedir pra usuario "abrir o Finder e copiar manualmente" — esse atrito ja foi resolvido pelo helper.

---

## Passo 1 — Preferencias de conteudo (perguntar/confirmar a cada execucao)

Ler `assets/content_preferences.json`. Se nao existir, criar com defaults a partir de `assets/content_preferences.example.json`.

**Mostrar ao usuario o estado atual** e perguntar se quer manter ou alterar:

> Configuracao atual:
> - Tom: **{tom}**
> - Nivel de escrita: **{nivel_escrita}**
> - Fonte de imagens: **{fonte_imagens}**
>
> Manter para este carrossel? (Voce pode alterar a qualquer momento editando `assets/content_preferences.json` ou rodando `/carousel` novamente.)

Se o usuario quiser alterar, usar `AskUserQuestion`:

### Pergunta A — Tom da copy
- `alarmista` — urgência, frases curtas, "ATENÇÃO", choque, perigo iminente
- `jornalistico` — objetivo, factual, "Segundo dados...", neutralidade, fontes
- `didatico` — explicativo, paciente, "Vamos entender...", passo-a-passo
- `descontraido` — coloquial, gírias jovens, leve, casual
- `inspiracional` — motivacional, "Você pode...", encorajador
- `tecnico` — jargão preservado, dados específicos, terminologia formal
- `ironico` — sarcástico, provocativo, crítica social, humor seco

### Pergunta B — Nivel de escrita
- `simples` — adolescentes / leitura básica: frases curtas, vocabulário cotidiano, zero jargão, analogias diárias
- `medio` — público geral: vocabulário corrente, termos técnicos explicados quando aparecem
- `culto` — leitor experiente: vocabulário rico, conceitos avançados não traduzidos, referências eruditas, frases mais longas

### Pergunta C — Fonte das imagens
- `auto` — skill busca sozinha em Pexels/Unsplash
- `pasta` — usuário ja colocou em `assets/custom_images/` com nome `1.png` … `9.png` (número do arquivo = número do slide)
- `links` — usuário vai colar URLs no chat agora, indicando o slide (ex: `slide 3: https://imgur.com/xyz.jpg`)

**Persistir** as escolhas em `assets/content_preferences.json` (sobrescrever) — isso atualiza o default.

Ao final desse passo, **dizer ao usuario**:

> Preferências salvas. Você pode alterá-las a qualquer momento editando `assets/content_preferences.json` ou rodando `/carousel` de novo. Vou usar essa configuração agora.

---

## Passo 2 — Pesquisar e estruturar conteudo

### REGRA DURA: pesquisar ANTES de escrever (OBRIGATORIO)

Antes de redigir qualquer slide, voce DEVE rodar `WebSearch` para verificar afirmacoes factuais. Numeros inventados em tom alarmista nao sao copy — sao desinformacao, e o usuario vai postar isso publicamente em nome dele.

**Sempre buscar fontes para:**
- Qualquer numero absoluto ("X bilhoes", "Y milhoes de vitimas", "Z por cento")
- Qualquer data, periodo ou tendencia ("cresceu N%", "dobrou em 2025", "no ultimo ano")
- Qualquer caso citado nominalmente (cidade, profissao, valor especifico)
- Qualquer citacao de instituicao (Febraban, BC, STJ, Anatel, Procon, ministerios)
- Qualquer afirmacao tecnica especifica ("burla biometria", "X em cada Y", "preco do dado vazado")

**Como pesquisar:**
1. Rodar 3-4 `WebSearch` em paralelo cobrindo angulos diferentes (estatistica geral, caso institucional, mecanica do problema, dado-surpresa do slide 9).
2. Anotar cada numero/fato com a fonte (Febraban, STJ, MJSP, etc).
3. Se um numero veio de uma fonte unica nao primaria (blog, agregador), buscar a fonte primaria antes de usar.
4. Se nenhuma fonte confiavel confirma o numero que voce queria escrever, **trocar a frase** por algo verificavel ou abandonar a afirmacao.

**Output da pesquisa:** apos pesquisar, listar mentalmente para o usuario os 5-8 fatos verificados que vai usar nos slides. Se ele aprovar/ajustar, ai sim escreve a copy.

### Casos onde pesquisa NAO e obrigatoria
- Conselhos genericos sem numero ("nenhum banco pede senha por telefone")
- Estrutura narrativa sem dado especifico ("voce recebe uma ligacao, a pessoa diz X…")
- Reflexoes interpretativas claramente subjetivas ("e isso muda como pensamos sobre Y")

### Anti-padroes proibidos
- Inventar estatistica "porque soa plausivel"
- Citar "estudo recente" / "pesquisa indica" sem ter o estudo
- Atribuir frase a uma instituicao sem ter a citacao
- Mencionar caso especifico (cidade + valor + tempo) sem reportagem real

### No final dos slides

No `assets/posts/[tema].md` SEMPRE incluir uma secao `## Fontes verificadas (consultadas em [mes/ano])` listando cada fonte com URL clicavel — isso protege voce e o usuario.

---

Pesquisar o tema na web. Estruturar 9 slides aplicando o **PADRAO** abaixo.

### PADRAO DE COPY (5 principios — sempre aplicar dentro dos 9 slides)

1. **Hook magnetico em 3 segundos** — usar power words: "segredo", "proibido", "gratis", "ninguem sabe", "ninguem te conta", "voce nao imagina", "ninguem te avisou".
2. **Foreshadowing** — prometer no inicio o que vem nos proximos slides ("vou te mostrar como…", "no proximo slide voce vai entender…").
3. **"Mas / Entao"** — cada slide deve criar tensao pro proximo: terminar com gancho, virada ou pergunta que so se resolve adiante.
4. **Linguagem de 5a serie** — frases simples, curtas, diretas. Vocabulario do dia-a-dia. Mesmo no nivel `medio`/`culto`, a estrutura da frase permanece direta — o vocabulario sobe, a complexidade sintatica nao.
5. **Satisfacao + surpresa no final** — slide 9 entrega a recompensa prometida no slide 1 com uma virada inesperada (dado curioso, conclusao oposta ao senso comum, revelacao).

### Mapeamento dentro dos 9 slides

| Slide | Funcao | Onde aplicar os principios |
|-------|--------|---------------------------|
| 1 | Hook + Foreshadowing | (1) Power word nas 3 primeiras palavras + (2) prometer o que vem ("segue o fio…") |
| 2 | Numeros / dados | (3) Mas/Entao: terminar com "mas tem mais…" / "e o pior nao e isso…" |
| 3 | Aspecto tecnico ou revelador | (3) Virada — contrariar expectativa do slide 2 |
| 4 | Como funciona / metodologia | (3) Mas/Entao: deixar uma duvida pendente pro slide 5 |
| 5 | Exemplos / casos reais | (3) Aterrissar o abstrato em algo concreto e proximo |
| 6 | Resposta oficial / institucional | (3) Mas/Entao: insinuar que a resposta oficial nao basta |
| 7 | Checklist ou dicas praticas | Em **prosa corrida** (sem bullets!) — dicas viram frases tipo "primeiro voce…, depois…, e por fim…" |
| 8 | Sinais / proximos passos | (3) Empurrar pra acao no slide 9 |
| 9 | CTA + Satisfacao + Surpresa | (5) Fechar o loop do slide 1 com uma virada (dado curioso, conclusao contra-intuitiva) + "Siga {handle}" + tagline |

**TODOS os 9 slides obedecem o principio (4) — linguagem de 5a serie na estrutura da frase.**

### Mapa tom × hook do slide 1

- `alarmista` → "ATENÇÃO: …", "URGENTE: …", "Você não imagina o que…"
- `jornalistico` → "Reportagem revela…", "Dados mostram que…"
- `didatico` → "Você sabia que…?", "Vamos entender…"
- `descontraido` → "Cara, você precisa ver isso…", "Não acredito que…"
- `inspiracional` → "E se eu te dissesse que…", "A história de…"
- `tecnico` → "Análise: …", "Estudo aponta…"
- `ironico` → "Mais uma vez…", "Surpreendentemente (não)…"

### Mapa nivel × construcao da frase

- `simples` → frases ate 12 palavras. Vocabulario do dia-a-dia. Sem jargão. Analogia concreta a cada slide ("é como…", "imagine que…").
- `medio` → frases ate 20 palavras. Termos técnicos explicados na primeira aparição.
- `culto` → frases ate 35 palavras. Vocabulário rico, conceitos avançados, referências cruzadas.

---

## Passo 3 — Regras de copy (OBRIGATORIO, independente do tom)

- **NUNCA usar bullet points (•) nem listas numeradas (1. 2. 3.)** — toda copy em prosa corrida.
- Paragrafos naturais. Itens viram frases.
- Margens simetricas.
- Cada slide: titulo curto (max 2 linhas) + corpo (3-5 linhas).
- **Numeros SEMPRE em algarismos, nao por extenso.** Use `R$ 10,1 bilhoes` (nao "dez virgula um bilhoes"), `220%` (nao "duzentos e vinte por cento"), `12 meses` (nao "doze meses"), `60 anos` (nao "sessenta anos"), `US$ 500` (nao "quinhentos dolares"). Algarismos sao mais visuais e impactantes em copy de carrossel.
- **Acentuacao em portugues SEMPRE correta na copy dos slides** — "milhões", "número", "ligação", "você", "já", "é", "às", "ninguém", "também", "São Paulo", "última", "três", "ânsia", "inflação", "dimensão", "ç" em todas as palavras com cedilha. O renderizador (Pillow + Helvetica Neue) suporta UTF-8 perfeitamente — nao tem motivo tecnico pra escrever sem acento. Acentuacao ausente em copy publicada parece amador. Vale tambem pro footer (`slide_sources` no template) e copy do post markdown.
- **Os 5 principios do PADRAO (passo 2) precisam aparecer no resultado** — antes de salvar a copy, releia mentalmente cada slide e marque: tem hook? tem foreshadowing no slide 1? cada um dos slides 2-8 termina com gancho? slide 9 fecha com surpresa? frase de 5a serie?

---

## Passo 4 — Gerar script Python

```bash
mkdir -p generators
cp MODELO_PADRAO_CARROSSEL/template_gerador_final.py generators/generate_[TEMA_SNAKE_CASE]_modelo_principal.py
```

No novo arquivo:
1. Substituir `[TEMA]` pelo tema.
2. Atualizar `_get_slide_content()` com a copy gerada conforme **tom** + **nivel_escrita**.
3. **NAO mexer** no header/footer — leem `profile_config.json` automaticamente.
4. No slide 9, montar CTA com `self.profile['handle']` + `self.profile.get('tagline', '')` (substituir hardcodes de `@seuhandle` e "[tagline]" do template).
5. Margem direita simetrica: `text_width = self.carousel_size[0] - (2 * text_x)`.

---

## Passo 5 — Imagens dos slides (conforme `fonte_imagens`)

### REGRA: cada imagem reflete o ANGULO do conteudo, nao o tema generico

Imagem do slide tem que reforcar o **angulo** especifico daquele slide, nao apenas o tema do carrossel. Exemplos do que NAO fazer:

- Slide sobre "R$ 10,1 bi tirados em golpes" recebendo foto de **planta brotando em moedas** — foto evoca prosperidade / investimento, oposto da mensagem (PREJUIZO).
- Slide sobre "vitimas idosas" recebendo foto de **handshake sorridente** — handshake evoca acordo positivo, nao golpe.
- Slide sobre "como o golpe funciona" recebendo foto de **kanban com post-its DONE/DOING** — sugere produtividade, sem relacao com ligacao fraudulenta.
- Slide sobre "regra que protege" recebendo foto de **casal relaxando em casa** — sem ligacao com seguranca/protecao.

A imagem precisa carregar a mesma **emocao/intencao** que a copy. Se a copy fala de PERDA, a imagem nao pode ser de prosperidade. Se fala de ALERTA, a imagem nao pode ser de celebracao.

### Por que `auto` falha frequentemente

Buscar imagens Unsplash as cegas por keyword tematica produz fotos do tema generico mas raramente do **angulo certo**. Em teste real, 5 de 9 imagens vieram desalinhadas, e 3 rodadas de troca subsequentes deram 0 acertos completos.

**Recomendacao forte para o usuario antes de rodar a skill:** se o conteudo tem angulo especifico (alerta, prejuizo, vitima, ataque, surpresa), preferir `fonte_imagens=pasta` ou `links` em vez de `auto`. A skill deve sugerir isso explicitamente ao perguntar a fonte na execucao quando o tom for `alarmista` ou `ironico`.



### Se `fonte_imagens == "pasta"`
- Verificar `assets/custom_images/1.png`…`9.png`. Se faltar algum, **avisar** quais slides estão sem imagem e perguntar se quer:
  - cair pra `auto` nesses slides;
  - parar e o usuario cola os arquivos faltantes agora;
  - cair pra `links` nesses slides.

### Se `fonte_imagens == "links"`
Pedir ao usuario:
> Cole os links agora, um por linha, no formato `slide N: URL` (não precisa cobrir os 9; os faltantes uso fallback automático).

Baixar cada URL pra `assets/slide_images/[tema]_slide_[1-9].jpg` (resize <= 1200px).

### Se `fonte_imagens == "auto"`
Buscar em Pexels/Unsplash/Wikimedia conforme o conteudo de cada slide. Resize <= 1200px. Salvar em `assets/slide_images/[tema]_slide_[1-9].jpg`.

### Se `fonte_imagens == "pergunta"` (o default mais conservador)
Perguntar agora qual das tres opcoes acima usar **so para esta execucao** (sem alterar o default no JSON).

---

## Passo 6 — Executar

```bash
python3 generators/generate_[TEMA_SNAKE_CASE]_modelo_principal.py
```

Output: `assets/generated_carousels/[tema]_slide_[01-09].png` (1080x1440px).

---

## Passo 7 — Copy do post

```bash
mkdir -p assets/posts
```

Salvar em `assets/posts/[tema].md` respeitando o **tom** e o **nivel_escrita**:
- 5 linhas envolventes
- 5 hashtags relevantes
- Tom conversacional ajustado (alarmista usa "🚨"-style verbal, descontraido usa gírias, etc.)

---

## Passo 8 — Apresentacao final (preview no chat + contact sheet)

Ao final, **sempre** apresentar o resultado pro usuario aqui no chat. Ele provavelmente nao vai abrir os arquivos no Finder/explorer — entrega tudo pronto pra ele baixar/copiar.

**1. Gerar contact sheet 3x3 dos 9 slides:**

```bash
python3 scripts/build_contact_sheet.py [tema]
```

Output: `assets/generated_carousels/[tema]_contact_sheet.png` — uma unica imagem 3x3 com os 9 slides em miniatura. Util pra revisar o carrossel inteiro de uma vez (e mandar pro celular pelo WhatsApp pra revisar antes de postar).

**2. Mostrar os 9 slides inline no chat:**

Use a tool `Read` em cada um dos 9 PNGs gerados em `assets/generated_carousels/[tema]_slide_01..09.png`. Eles renderizam visualmente no chat — usuario ve cada slide e pode salvar com clique direito ou drag & drop.

**3. Mostrar o contact sheet inline tambem:**

`Read` em `assets/generated_carousels/[tema]_contact_sheet.png` — preview compacto pra revisao geral.

**4. Imprimir a descricao do post em texto LIMPO (sem blockquote):**

NAO usar `>` de markdown. Texto puro, paragrafos com linha em branco entre, hashtags na ultima linha. Usuario copia direto pra caption do Instagram.

**5. Mostrar caminhos absolutos:**

```
Slides:        <abs>/assets/generated_carousels/[tema]_slide_01..09.png
Contact sheet: <abs>/assets/generated_carousels/[tema]_contact_sheet.png
Post:          <abs>/assets/posts/[tema].md
```

**6. Abrir a pasta automaticamente (cross-platform):**

Roda `python3 scripts/open_folder.py assets/generated_carousels` — abre direto no Finder (macOS), Explorer (Windows) ou xdg-open (Linux). Sem o usuario precisar copiar comando.

**Por que essa apresentacao final importa:** o usuario provavelmente esta no Claude Code/Desktop e quer baixar os PNGs pro celular OU pegar a descricao pra colar no Instagram. Sem essa etapa final, ele teria que ir manualmente no Finder achar a pasta — friccao desnecessaria.

---

## Checklist final

- [ ] `profile_config.json` + `video_reels/src/brand.json` sincronizados
- [ ] `content_preferences.json` reflete escolhas (ou foi confirmado o default)
- [ ] **WebSearch rodado ANTES de escrever copy** com numeros/datas/instituicoes (passo 2)
- [ ] **Cada numero, data, caso, citacao tem fonte verificada** — sem chute
- [ ] 9 slides em `assets/generated_carousels/`
- [ ] Copy sem bullets/numeros
- [ ] Tom e nivel coerentes com o config (re-ler antes de gerar)
- [ ] Margens simetricas
- [ ] Slide 9 com CTA dinamico (`{handle}`) e tagline (se houver)
- [ ] Copy do post em `assets/posts/[tema].md` com **secao `## Fontes verificadas` listando URLs**
- [ ] **5 principios do PADRAO presentes**: hook magnetico (slide 1), foreshadowing (slide 1), Mas/Entao em cada slide 2-8, linguagem de 5a serie em todos, satisfacao+surpresa no slide 9
- [ ] **Passo 8 (apresentacao) executado**: contact sheet gerado + 9 slides + contact sheet exibidos inline via `Read` + descricao em texto limpo + caminhos absolutos impressos

---

## Como o usuario muda preferencias depois

Avisar uma vez (no fim da execucao OU quando ele perguntar):
> Pra mudar tom, nível de escrita ou fonte de imagens permanentemente: edite `assets/content_preferences.json`. Pra mudar só nesta execução: rode `/carousel` de novo e responda diferente quando eu perguntar "Manter para este carrossel?".
