# 🚀 COMO USAR O MODELO PADRÃO CARROSSEL

## 📋 CHECKLIST PARA NOVOS TEMAS

### ✅ PASSO 1: PREPARAÇÃO
- [ ] Definir o tema específico (ex: "bitcoin", "openai", "tesla")
- [ ] Pesquisar 9 URLs de imagens temáticas no Unsplash
- [ ] Criar copy alarmista com 9 aspectos do tema
- [ ] Definir hashtags estratégicas do nicho

### ✅ PASSO 2: BAIXADOR DE IMAGENS
```bash
# 1. Copiar template
cp template_download_images.py download_[TEMA]_images.py

# 2. Personalizar arquivo (buscar por "PERSONALIZAR AQUI")
# 3. Executar
python3 download_[TEMA]_images.py
```

**O que personalizar:**
- [ ] Nome do tema em todas as ocorrências `[tema]` 
- [ ] 9 URLs de imagens específicas do Unsplash
- [ ] 9 URLs de backup (fallback)
- [ ] Descrições das imagens para cada slide
- [ ] Keywords de cada imagem

### ✅ PASSO 3: GERADOR PRINCIPAL  
```bash
# 1. Copiar template
cp template_gerador.py generate_[TEMA]_modelo_principal.py

# 2. Personalizar arquivo (buscar por "PERSONALIZAR AQUI")
# 3. Executar
python3 generate_[TEMA]_modelo_principal.py
```

**O que personalizar:**
- [ ] Nome do tema em `[TEMA]`
- [ ] Título principal do carrossel
- [ ] 9 conteúdos/copy dos slides
- [ ] Títulos dos slides na estrutura
- [ ] Nome dos arquivos gerados

### ✅ PASSO 4: POST INSTAGRAM
```bash
# 1. Copiar template
cp template_instagram_post.md [tema]_instagram_post.md

# 2. Personalizar conteúdo
```

**O que personalizar:**
- [ ] Descrição completa do post
- [ ] Hashtags específicas do tema
- [ ] Copy otimizada para o nicho
- [ ] Métricas esperadas
- [ ] Timing ideal de postagem

### ✅ PASSO 5: TESTE E VALIDAÇÃO
- [ ] Verificar que 9 imagens foram baixadas
- [ ] Conferir que 9 slides foram gerados
- [ ] Validar qualidade visual dos slides
- [ ] Revisar copy do Instagram
- [ ] Testar hashtags no Instagram

---

## 🎯 EXEMPLOS PRÁTICOS

### Bitcoin Crash
```bash
# Tema: bitcoin
cp template_download_images.py download_bitcoin_images.py
cp template_gerador.py generate_bitcoin_modelo_principal.py
cp template_instagram_post.md bitcoin_instagram_post.md

# Personalizar:
# - URLs: imagens de Bitcoin, gráficos, mercado
# - Copy: "Bitcoin DESABA 80%! Mercado em PÂNICO!"
# - Hashtags: #bitcoin #crypto #crash #mercado
```

### OpenAI Drama
```bash
# Tema: openai  
cp template_download_images.py download_openai_images.py
cp template_gerador.py generate_openai_modelo_principal.py
cp template_instagram_post.md openai_instagram_post.md

# Personalizar:
# - URLs: imagens de IA, OpenAI, drama corporativo
# - Copy: "GUERRA interna na OpenAI! CEO demitido!"
# - Hashtags: #openai #ia #chatgpt #startup
```

---

## ⚠️ ERROS COMUNS A EVITAR

### ❌ Layout/Design
- **NUNCA** altere proporções (10%, 55%, 25%, 10%)
- **NUNCA** mude tipografia base (Helvetica Neue, 42px)
- **NUNCA** altere sistema de cores
- **NUNCA** modifique estrutura do header/footer

### ❌ Imagens
- **NÃO** use imagens genéricas (sempre temáticas)
- **NÃO** esqueça de testar URLs antes de usar
- **NÃO** use imagens muito pequenas (min 800x600)
- **NÃO** use imagens com marca d'água

### ❌ Conteúdo
- **NÃO** use copy educativo demais (sempre alarmista)
- **NÃO** esqueça palavras em CAPS estratégicas
- **NÃO** faça textos muito longos por slide
- **NÃO** esqueça o CTA no slide 9

### ❌ Arquivos
- **NÃO** esqueça de alterar nomes de arquivos
- **NÃO** deixe placeholders `[TEMA]` sem substituir
- **NÃO** use caracteres especiais nos nomes
- **NÃO** esqueça de testar antes de postar

---

## 🔧 TROUBLESHOOTING

### Imagens não baixam
```bash
# Verificar conectividade
ping unsplash.com

# Testar URL individual
curl -I "https://images.unsplash.com/photo-xxxxx"

# Verificar diretório
ls -la assets/slide_images/
```

### Slides ficam sem imagem
```bash
# Verificar se imagens existem
ls assets/slide_images/[tema]_slide_*.jpg

# Verificar nomes no código
grep "[tema]_slide_" generate_[tema]_modelo_principal.py
```

### Fonte não carrega
- Sistema irá usar fonte padrão automaticamente
- Verificar se `/System/Library/Fonts/Helvetica.ttc` existe no Mac

### Slides ficam pequenos
- Verificar se `carousel_size = (1080, 1440)` está correto
- Não alterar dimensões base

---

## 📊 MÉTRICAS DE QUALIDADE

### ✅ Slides Perfeitos
- [ ] **Resolução:** 1080x1440px exatos
- [ ] **Tamanho:** 300-800 KB por slide
- [ ] **Imagem:** Temática e nítida na área visual
- [ ] **Texto:** Legível e bem posicionado
- [ ] **Header:** Foto de perfil circular integrada
- [ ] **Footer:** "[tagline] • @seuhandle"

### ✅ Copy Ideal
- [ ] **Tom:** Humano e conversacional (não robótico)
- [ ] **Linguagem:** Direta, sem muitas perguntas retóricas
- [ ] **Estrutura:** Problema → Análise → Solução → CTA  
- [ ] **Dados:** Números específicos e fatos reais
- [ ] **CAPS:** Palavras estratégicas em maiúscula
- [ ] **Expressões:** "A coisa é gigante", "vai rolar", "fique de olho"
- [ ] **Slide 1:** SEMPRE terminar com "👉 Segue o fio..."
- [ ] **CTA:** Natural, como conversa entre amigos

### ✅ Post Instagram
- [ ] **Hashtags:** 15-25 hashtags estratégicas
- [ ] **Timing:** Horário otimizado para audiência
- [ ] **Hook:** Primeira linha impactante
- [ ] **Estrutura:** Fácil de ler no mobile
- [ ] **CTA:** Incentiva swipe e engagement

---

## 🎨 ASSETS FINAIS

Após completar todos os passos, você terá:

```
📁 [TEMA]/
├── download_[tema]_images.py ✅
├── generate_[tema]_modelo_principal.py ✅  
├── [tema]_instagram_post.md ✅
└── slides_gerados/
    ├── [tema]_slide_01.png ✅
    ├── [tema]_slide_02.png ✅
    ├── ... ✅
    └── [tema]_slide_09.png ✅
```

🚀 **PRONTO PARA POSTAR E VIRALIZAR!**