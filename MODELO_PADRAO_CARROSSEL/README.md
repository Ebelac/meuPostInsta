# 🎨 MODELO PADRÃO CARROSSEL - CalebeDigital

Este é o **modelo definitivo** para gerar carrosséis Instagram seguindo nosso padrão profissional.

## 📐 ESPECIFICAÇÕES TÉCNICAS

### Layout Fixo (NUNCA MUDE):
- **Tamanho:** 1080x1440px (Instagram carousel)
- **Proporções:** 10% header + 55% conteúdo + 25% visual + 10% footer
- **Tipografia:** Helvetica Neue, 42px texto principal
- **Cores:** Fundo escuro (#171719), texto branco
- **Profile:** Foto circular com anti-aliasing 4x
- **Footer:** "[tagline] • @seuhandle"

### Estrutura de 9 Slides:
1. **Slide 1:** Capa impactante + ">>> Segue o fio..."
2. **Slides 2-8:** Desenvolvimento do tema
3. **Slide 9:** CTA para compartilhamento

## 📝 PROCESSO PARA NOVOS TEMAS

### OPÇÃO 1: IMAGENS CUSTOMIZADAS (RECOMENDADO)
```bash
# Colocar suas próprias imagens em:
assets/custom_images/1.jpg
assets/custom_images/2.jpg
...até 9.jpg
```
- **TOTAL CONTROLE** sobre as imagens
- Sistema usa primeiro suas imagens
- Formatos: .jpg, .jpeg, .png

### OPÇÃO 2: BAIXAR IMAGENS TEMÁTICAS  
```bash
python3 download_[TEMA]_images.py
```
- Cria 9 imagens específicas do tema
- Salva em `assets/slide_images/`
- Nomeia como `[tema]_slide_1.jpg` até `[tema]_slide_9.jpg`

### 2. ADAPTAR CONTEÚDO
- Manter **estrutura** do modelo principal
- Mudar apenas **texto/copy** para o tema específico
- Usar **tom alarmista** para gerar curiosidade
- Manter **palavras em CAPS** estratégicas

### 3. GERAR CARROSSEL
```bash
python3 generate_[TEMA]_modelo_principal.py
```

### 4. CRIAR POST COMPLETO
- Descrição otimizada
- Hashtags estratégicas  
- Timing ideal de postagem

## 🚫 O QUE NUNCA MUDAR

❌ **Layout/Design**
❌ **Proporções das áreas**
❌ **Tipografia base**
❌ **Sistema de cores**
❌ **Foto de perfil integrada**
❌ **Footer padrão**

## ✅ O QUE SEMPRE MUDAR

✅ **Conteúdo/copy do tema**
✅ **Imagens temáticas específicas**
✅ **Títulos dos slides**
✅ **Hashtags do tema**
✅ **Nome dos arquivos gerados**

## 📂 ESTRUTURA DE ARQUIVOS

```
MODELO_PADRAO_CARROSSEL/
├── README.md (este arquivo)
├── template_gerador.py (modelo base)
├── template_download_images.py (baixador base)
├── template_instagram_post.md (post base)
├── EXEMPLO_ANTHROPIC/
│   ├── generate_anthropic_modelo_principal.py
│   ├── download_anthropic_images.py  
│   ├── antropic_instagram_post.md
│   └── slides_gerados/
└── assets/
    ├── profile/profile_photo.png
    └── slide_images/
```

## 🎯 WORKFLOW PARA NOVOS TEMAS

1. **Copiar** template_gerador.py → generate_[TEMA]_modelo_principal.py
2. **Adaptar** conteúdo do tema no arquivo copiado
3. **Copiar** template_download_images.py → download_[TEMA]_images.py  
4. **Definir** URLs de imagens temáticas
5. **Executar** download de imagens
6. **Executar** gerador principal
7. **Criar** post Instagram com copy + hashtags

## 💡 DICAS IMPORTANTES

- **Tom:** Sempre alarmista para gerar curiosidade
- **Imagens:** Específicas para cada slide do tema
- **Design:** Manter padrão profissional sempre
- **Testes:** Usar esta pasta para testar novos temas
- **Limpeza:** Descartar arquivos desnecessários após validação

---

**🚀 ESTE É NOSSO PADRÃO DEFINITIVO!**
**Seguindo este modelo, todos os carrosséis terão qualidade e consistência profissional.**