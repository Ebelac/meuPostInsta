# 🎨 TEMPLATE DEFINITIVO - MODELO PADRÃO CalebeDigital

## 📁 ARQUIVO PRINCIPAL: `template_gerador_final.py`

**ESTE É O MODELO QUE FUNCIONA PERFEITAMENTE!**  
Baseado nos padrões testados e aprovados do TikTok empréstimo + Malware Android.

---

## 🚀 COMO USAR PARA NOVOS TEMAS

### 1️⃣ COPIAR O TEMPLATE
```bash
cp template_gerador_final.py ../generate_[SEU_TEMA]_modelo_principal.py
```

### 2️⃣ SUBSTITUIR TODAS AS MARCAÇÕES [TEMA]

**Busque e substitua em TODO o arquivo:**
- `[TEMA]` → seu tema (ex: `bitcoin`, `nft`, `ia`)
- `[SEU TEMA]` → descrição do tema (ex: `Bitcoin Mining`, `NFT Crash`)

### 3️⃣ PERSONALIZAR APENAS ESTES PONTOS:

#### ✏️ Função `_get_slide_content()` - LINHA ~733
```python
content_map = {
    1: {
        'copy': '[SEU CONTEÚDO SLIDE 1]\n\n[Texto impactante]\n\n>>> Segue o fio...'
    },
    2: {
        'copy': '[SEU CONTEÚDO SLIDE 2]...'
    },
    # ... continue para os 9 slides
}
```

#### ✏️ Fontes dos slides - LINHA ~850
```python
slide_sources = {
    1: "[Sua Fonte 1], [Sua Fonte 2]",
    2: "[Fonte do Slide 2], [Fonte Adicional]",
    # ... continue para os 8 slides (slide 9 sempre "[tagline opcional]")
}
```

#### ✏️ Informações principais - LINHA ~880
```python
print("🚨 Gerando CARROSSEL [SEU TEMA] com 9 Slides")
carousel_data = {
    'id': '[tema_id]',
    'title': '[TÍTULO DO SEU CARROSSEL]',
}
print(f"   1️⃣ Slide 1: [Título do slide 1]")
# ... continue para os 9 slides
```

---

## ❌ O QUE NUNCA ALTERAR

- ✅ Layout e proporções (10% header, 55% content, 25% visual, 10% footer)
- ✅ Sistema de cores e tipografia 
- ✅ Estrutura de classes e métodos
- ✅ Sistema de imagens customizadas
- ✅ Foto de perfil circular
- ✅ Footer "[tagline] • @seuhandle"
- ✅ Lógica de geração de slides
- ✅ Quebra de texto e espaçamentos

---

## 📊 ESTRUTURA DOS 9 SLIDES

### 🎯 PADRÃO COMPROVADO:
1. **Slide 1:** Gancho alarmista + ">>> Segue o fio..."
2. **Slide 2:** Números/dados impressionantes
3. **Slide 3:** Aspecto técnico ou detalhamento
4. **Slide 4:** Como funciona ou metodologia
5. **Slide 5:** Exemplos geográficos ou casos
6. **Slide 6:** Resposta oficial ou institucional
7. **Slide 7:** Checklist ou dicas práticas
8. **Slide 8:** Sinais ou próximos passos
9. **Slide 9:** CTA compartilhamento + follow

---

## 🎨 SISTEMA DE IMAGENS

### 📁 Prioridade automática:
1. **`assets/custom_images/1.png`** até **`9.png`** → SUAS IMAGENS
2. **`assets/slide_images/[tema]_slide_1.jpg`** → fallback automático

### 💡 Dica:
Coloque suas 9 imagens numeradas em `assets/custom_images/` e o sistema usará automaticamente!

---

## ✅ CHECKLIST FINAL

- [ ] Arquivo copiado e renomeado corretamente
- [ ] Todas as marcações `[TEMA]` substituídas  
- [ ] Conteúdo dos 9 slides personalizado
- [ ] Fontes dos slides atualizadas
- [ ] Títulos e descrições principais alterados
- [ ] Imagens colocadas em `assets/custom_images/`
- [ ] Teste executado: `python3 generate_[tema]_modelo_principal.py`

---

## 🎯 RESULTADO GARANTIDO

✅ **9 slides profissionais** (1080x1440px)  
✅ **Layout CalebeDigital** padronizado  
✅ **Suas imagens** integradas automaticamente  
✅ **Copy humanizada** com tom conversacional  
✅ **Fontes verificáveis** por slide  
✅ **CTA otimizado** para compartilhamento  

---

**🚀 ESTE TEMPLATE ESTÁ 100% TESTADO E APROVADO!**

Qualquer novo tema seguindo estas instruções gerará carrosséis com a mesma qualidade profissional dos modelos TikTok empréstimo e Malware Android.