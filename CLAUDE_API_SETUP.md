# 🤖 CONFIGURAÇÃO DA API DO CLAUDE

## 🔑 **ONDE COLOCAR A API KEY**

### **PASSO 1: Obter API Key**

1. **Acesse**: https://console.anthropic.com/
2. **Criar conta** ou fazer login
3. **Ir em "API Keys"** no menu lateral
4. **Clicar em "Create Key"**
5. **Copiar a chave** (formato: `sk-ant-api03-...`)

### **PASSO 2: Configurar no Projeto**

#### **Opção 1: Arquivo .env.flask (Recomendado)**

1. **Abrir o arquivo**: `.env.flask`
2. **Substituir** `SEU_TOKEN_AQUI` pela sua API key:

```bash
# Antes
ANTHROPIC_API_KEY=sk-ant-api03-SEU_TOKEN_AQUI

# Depois (exemplo)
ANTHROPIC_API_KEY=sk-ant-api03-ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnop
```

#### **Opção 2: Variável de Ambiente do Sistema**

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-SUA_CHAVE_AQUI"
```

**Windows:**
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-SUA_CHAVE_AQUI
```

#### **Opção 3: Direto no Código (NÃO RECOMENDADO)**

```python
# Em claude_api_integration.py
claude_generator = ClaudeCarouselGenerator(api_key="sk-ant-api03-SUA_CHAVE")
```

---

## 📦 **INSTALAR DEPENDÊNCIAS**

```bash
cd instaCalebeDigital
pip install anthropic python-dotenv
```

---

## 🚀 **USAR A NOVA VERSÃO COM IA**

### **1. Usar App com Claude API**
```bash
python3 app_with_claude_api.py
```

### **2. Acessar Interface**
- **URL**: http://localhost:5002
- **Login**: calebe / calebe2024!

### **3. Gerar Carrossel**
1. Clique em **"Gerar Carrossel"**
2. Escolha método **"🤖 Claude AI"**
3. Digite o tópico desejado
4. Clique em **"Gerar Carrossel"**

---

## ⚙️ **CONFIGURAÇÕES AVANÇADAS**

### **Personalizar Prompts**

Edite o arquivo `claude_api_integration.py`:

```python
def generate_carousel_content(self, topic: str, slides_count: int = 9) -> Dict:
    prompt = f"""
    Crie um carrossel profissional para Instagram sobre: {topic}
    
    // SEU PROMPT PERSONALIZADO AQUI
    """
```

### **Alterar Modelo Claude**

```python
response = self.client.messages.create(
    model="claude-3-sonnet-20240229",  # ou "claude-3-opus-20240229"
    max_tokens=4000,
    messages=[...]
)
```

---

## 🔧 **TROUBLESHOOTING**

### **❌ Erro: "API key do Claude não encontrada"**

**Soluções:**
1. Verificar se a API key está no `.env.flask`
2. Verificar se o arquivo `.env.flask` está na raiz do projeto
3. Verificar se não há espaços extras na chave

```bash
# Testar API key
python3 -c "
from claude_api_integration import ClaudeCarouselGenerator
try:
    gen = ClaudeCarouselGenerator()
    print('✅ API key configurada corretamente!')
except Exception as e:
    print(f'❌ Erro: {e}')
"
```

### **❌ Erro: "Module anthropic not found"**

```bash
pip install anthropic
```

### **❌ Erro: "Rate limit exceeded"**

- Aguardar alguns minutos
- API do Claude tem limites de uso
- Considerar upgrade do plano

### **❌ Erro: "Invalid API key"**

1. Verificar se a chave foi copiada corretamente
2. Gerar nova chave no console
3. Verificar se a conta está ativa

---

## 💡 **EXEMPLO COMPLETO**

### **1. Arquivo .env.flask**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-ABC123DEF456GHI789JKL
FLASK_SECRET_KEY=minha-chave-secreta-super-forte
ADMIN_USER=calebe
ADMIN_PASS=calebe2024!
```

### **2. Testar API**
```bash
cd instaCalebeDigital
python3 claude_api_integration.py
```

### **3. Iniciar App**
```bash
python3 app_with_claude_api.py
```

---

## 📊 **MONITORAMENTO**

### **Health Check**
```bash
curl http://localhost:5002/health
```

### **Logs**
O app mostra status da API do Claude no terminal:
```
🤖 Claude API: ✅ Disponível
```

---

## 🎯 **PRÓXIMOS PASSOS**

1. ✅ **Configurar API key**
2. ✅ **Testar geração**
3. 🔄 **Personalizar prompts**
4. 🔄 **Integrar com gerador visual**
5. 🔄 **Deploy em produção**

---

## 🔒 **SEGURANÇA**

⚠️ **NUNCA** comitir arquivos com API keys!

Adicionar ao `.gitignore`:
```
.env.flask
.env.local
*.env
```

**Em produção**, usar variáveis de ambiente do servidor:
```bash
# Heroku
heroku config:set ANTHROPIC_API_KEY=sk-ant-...

# Railway
railway variables set ANTHROPIC_API_KEY=sk-ant-...

# Vercel
vercel env add ANTHROPIC_API_KEY
```

---

## 📞 **SUPORTE**

- **Documentação Claude**: https://docs.anthropic.com/
- **Console API**: https://console.anthropic.com/
- **Limites e Pricing**: https://www.anthropic.com/pricing

---

*Configuração criada para CalebeDigital - Abril 2026*