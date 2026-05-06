# InstaCalebeDigital - Automação de Conteúdo Tech

Sistema automatizado para varredura, curadoria, escrita e publicação de conteúdo tech no Instagram.

## 🚀 Funcionalidades

- **News Scraper**: Coleta automática de notícias de tecnologia
- **Content Curator**: Filtragem e seleção inteligente de conteúdo
- **AI Writer**: Geração de textos otimizados para Instagram
- **Design Generator**: Criação automática de carrosséis visuais
- **Instagram Publisher**: Publicação automatizada
- **Smart Scheduler**: Agendamento inteligente baseado em engagement

## 📁 Estrutura do Projeto

```
instaCalebeDigital/
├── src/
│   ├── scrapers/           # Módulos de varredura de notícias
│   ├── curator/            # Sistema de curadoria
│   ├── writer/             # Geração de conteúdo
│   ├── designer/           # Criação de designs
│   ├── publisher/          # Publicação no Instagram
│   ├── scheduler/          # Sistema de agendamento
│   └── database/           # Modelos e migrações
├── assets/                 # Recursos visuais
├── templates/              # Templates de design
├── config/                 # Configurações
├── tests/                  # Testes automatizados
└── dashboard/              # Interface web de controle
```

## ⚙️ Configuração

1. Clone o repositório
2. Copie `.env.example` para `.env` e configure as variáveis
3. Instale as dependências: `pip install -r requirements.txt`
4. Execute as migrações: `python -m alembic upgrade head`
5. Inicie o sistema: `python main.py`

## 🔧 Uso

### Via CLI
```bash
python main.py --mode scraper  # Executar apenas scraping
python main.py --mode curator  # Executar curadoria
python main.py --mode full     # Pipeline completo
```

### Via Dashboard
```bash
streamlit run dashboard/app.py
```

## 📊 Monitoramento

O sistema inclui dashboard web para:
- Monitorar posts publicados
- Configurar fontes de notícias
- Ajustar parâmetros de curadoria
- Visualizar métricas de engagement