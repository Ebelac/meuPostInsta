# 🎨 GUIA TEMPLATE - CARROSSÉIS PADRÃO CALEBEDIGITAL

## 📋 RESUMO DO PADRÃO CONSOLIDADO

Baseado no carrossel de **Criptografia Quântica** que desenvolvemos, este é o template definitivo para criar carrosséis profissionais no estilo Tiago Guitián.

## 🎯 ESPECIFICAÇÕES TÉCNICAS

### 📱 Formato & Dimensões
- **Dimensões**: 1080x1440px (proporção vertical Instagram 2024)
- **Layout**: 10% header + 55% content + 25% visual + 10% footer
- **Margens de segurança**: 60px esquerda, 40px direita
- **Fonte principal**: Helvetica Neue / fonte de sistema

### 🎨 Estrutura Visual
```
┌─────────────────────────────────────┐
│ HEADER (144px)                      │ 10%
│ [Foto 100px] @seuhandle ✓       │
├─────────────────────────────────────┤
│ CONTEÚDO (792px)                    │ 55%
│ Copy fluido com parágrafos          │
│ estratégicos e storytelling         │
├─────────────────────────────────────┤
│ ÁREA VISUAL (360px)                 │ 25%
│ Imagem temática full-width          │
├─────────────────────────────────────┤
│ FOOTER (144px)                      │ 10%
│ Fonte: [Autoridade] | Slide X/9    │
└─────────────────────────────────────┘
```

## 📝 TEMPLATE DE CONTEÚDO (9 SLIDES)

### Slide 1: HOOK/CAPA
- **Função**: Capturar atenção e introduzir o tema
- **Tom**: Intrigante mas não alarmista
- **Estrutura**: Situação atual → Revolução happening → História que vamos contar

### Slides 2-3: EXPLICAÇÃO/EDUCAÇÃO  
- **Função**: Educar sobre a tecnologia/conceito
- **Tom**: Educativo e fascinante
- **Estrutura**: Como funciona → Dados impressionantes → Contexto técnico

### Slides 4-5: IMPACTO/RELEVÂNCIA
- **Função**: Tornar pessoal e relevante
- **Tom**: Informativo com soluções em vista
- **Estrutura**: Implicações práticas → Escala do impacto → Perspectiva balanceada

### Slide 6: TIMELINE/URGÊNCIA
- **Função**: Criar senso de timing sem pânico
- **Tom**: Factual com preparação
- **Estrutura**: Quando acontece → Consenso especialistas → Tempo para preparar

### Slide 7: SOLUÇÕES/ESPERANÇA
- **Função**: Mostrar que há respostas
- **Tom**: Otimista e construtivo  
- **Estrutura**: Soluções em desenvolvimento → Quem está trabalhando → Progresso atual

### Slide 8: PREPARAÇÃO/AÇÃO
- **Função**: Orientar próximos passos
- **Tom**: Prático e empoderador
- **Estrutura**: Como se preparar → Ações específicas → Mentalidade correta

### Slide 9: CTA COMPARTILHAMENTO
- **Função**: Viralização educativa
- **Tom**: Comunidade e conhecimento
- **Estrutura**: Compartilhe conhecimento → Valor para outros → Construção coletiva
- **Footer especial**: [tagline] (ou sua referência pessoal)

## 🎨 ESPECIFICAÇÕES DE DESIGN

### 📸 Header
- **Foto perfil**: 100px círculo, anti-aliasing 4x, centralizada
- **Username**: @seuhandle (68px, Helvetica Neue)
- **Badge verificado**: 32px, azul Twitter (#1DA1F2)
- **Posicionamento**: Username 10px acima do centro da foto

### 📝 Tipografia
```yaml
Fontes:
  profile_name: 44px    # Nome (se usado)
  title: 68px          # Username principal  
  body_medium: 42px    # Texto corpo padrão
  caption: 28px        # Footer/legendas

Espaçamento:
  Entre linhas: 52px
  Entre parágrafos: 36px
  Header-conteúdo: 50px (uniforme)
  
Margens:
  Esquerda: 60px + 30px texto = 90px total
  Direita: 40px
  Texto máximo: 920px largura
```

### 🖼️ Imagens Temáticas
- **Resolução**: 500x300px mínimo
- **Integração**: Full-width, crop inteligente
- **Backup**: 3 níveis (principal + alternativa + ultra-específica)
- **Temas**: Ultra-específicos para cada slide

## 📁 ESTRUTURA DE ARQUIVOS PARA NOVOS CARROSSÉIS

```
generate_[TEMA]_carousel.py
├── Herda de: ProfessionalCarouselGenerator
├── Método principal: generate_complete_9_slide_carousel()
├── Conteúdo: _get_slide_content() - 9 slides
├── Imagens: _get_slide_image() - URLs temáticas
└── Footer: _draw_footer_section() - fontes específicas
```

## 🚀 COMO CRIAR UM NOVO CARROSSEL

### 1. Copiar Template Base
```bash
cp generate_single_carousel.py generate_[NOVO_TEMA]_carousel.py
```

### 2. Personalizar Conteúdo
Editar o método `_get_slide_content()`:

```python
content_map = {
    1: {'copy': 'Hook/Capa sobre [TEMA]...'},
    2: {'copy': 'Explicação técnica de [CONCEITO]...'},
    3: {'copy': 'Dados impressionantes sobre [IMPACTO]...'},
    4: {'copy': 'Relevância pessoal para [PÚBLICO]...'},
    5: {'copy': 'Escala do impacto em [NÚMEROS]...'},
    6: {'copy': 'Timeline para [EVENTO/MUDANÇA]...'},
    7: {'copy': 'Soluções sendo desenvolvidas...'},
    8: {'copy': 'Como se preparar para [TEMA]...'},
    9: {'copy': 'CTA compartilhamento educativo...'}
}
```

### 3. Configurar Imagens Temáticas
Atualizar URLs nos métodos:
- `image_urls` (principal)
- `fallback_urls` (alternativa) 
- `ultra_specific_urls` (backup)

### 4. Definir Fontes de Autoridade
```python
slide_sources = {
    1: "MIT Technology Review, [FONTE_RELEVANTE]",
    2: "Nature, [JOURNAL_CIENTÍFICO]", 
    # ... para cada slide
    9: "[tagline opcional]"  # Manter referência pessoal
}
```

### 5. Ajustar Títulos e Descrições
```python
print("🚀 Gerando CARROSSEL ÚNICO - [TEMA]")
print("📰 Tema: [DESCRIÇÃO_COMPLETA]")
```

## ✅ CHECKLIST DE QUALIDADE

### Conteúdo
- [ ] Tom educativo (não alarmista)
- [ ] Storytelling fluido entre slides
- [ ] Fontes de autoridade relevantes
- [ ] CTA de compartilhamento no slide 9
- [ ] Quebras de parágrafo estratégicas (\n\n)

### Técnico  
- [ ] 9 slides total
- [ ] Dimensões 1080x1440px
- [ ] Margens respeitadas (60px/40px)
- [ ] Foto perfil integrada (profile_photo.png)
- [ ] Imagens temáticas específicas
- [ ] [tagline] no footer do slide 9

### Visual
- [ ] Tipografia uniforme (42px corpo)
- [ ] Espaçamento consistente (50px header)
- [ ] Badge verificado proporcional (32px)  
- [ ] Imagens full-width sem distorção
- [ ] Qualidade anti-aliasing na foto perfil

## 🎯 EXEMPLOS DE TEMAS FUTUROS

### Tecnologia
- IA e Automação de Empregos
- Web3 e Metaverso Explicado
- 5G e Internet das Coisas

### Finanças
- DeFi vs Bancos Tradicionais
- Inflação e Proteção Patrimonial  
- PIX Internacional e CBDCs

### Negócios
- Remote Work Revolution
- Startup vs Corporação
- Personal Branding Digital

## 💡 DICAS DE EXECUÇÃO

### Pesquisa de Conteúdo
1. **Fontes primárias**: MIT, Nature, McKinsey, BCG, Deloitte
2. **Dados atuais**: Últimos 6 meses
3. **Múltiplas perspectivas**: Não só alarmista ou otimista

### Storytelling
1. **Arco narrativo**: Situação → Mudança → Impacto → Solução → Ação
2. **Linguagem**: Acessível mas respeitosa com a audiência
3. **Ritmo**: Builds tension until slide 6, then resolution

### Otimização para Viral
1. **Slide 1**: Hook irresistível
2. **Slides 2-8**: Valor educativo real
3. **Slide 9**: CTA que apela ao valor social do compartilhamento

---

## 🚀 COMANDO DE GERAÇÃO

Para criar um novo carrossel baseado neste template:

```bash
cd instaCalebeDigital
python3 generate_[TEMA]_carousel.py
```

**Resultado**: 9 arquivos PNG prontos para upload no Instagram com qualidade profissional e padrão Tiago Guitián.

---

*Template consolidado baseado no carrossel de Criptografia Quântica - Abril 2026*