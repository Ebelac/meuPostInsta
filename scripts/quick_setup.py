#!/usr/bin/env python3
"""
Script de configuração rápida
"""
import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Instalar dependências"""
    print("📦 Instalando dependências...")

    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                      check=True)
        print("✅ Dependências instaladas")
    except subprocess.CalledProcessError:
        print("❌ Erro ao instalar dependências")
        return False

    return True

def setup_env_file():
    """Configurar arquivo .env"""
    if Path('.env').exists():
        print("✅ Arquivo .env já existe")
        return True

    print("📝 Criando arquivo .env...")

    # Copiar do exemplo
    try:
        with open('.env.example', 'r') as f:
            content = f.read()

        with open('.env', 'w') as f:
            f.write(content)

        print("✅ Arquivo .env criado")
        print("⚠️  Configure suas credenciais no arquivo .env")
        return True

    except Exception as e:
        print(f"❌ Erro ao criar .env: {e}")
        return False

def initialize_database():
    """Inicializar banco de dados"""
    print("🗄️  Inicializando banco de dados...")

    try:
        subprocess.run([sys.executable, 'main.py', '--init-db'], check=True)
        print("✅ Banco de dados inicializado")
        return True
    except subprocess.CalledProcessError:
        print("❌ Erro ao inicializar banco")
        return False

def check_config():
    """Verificar configuração"""
    print("🔍 Verificando configuração...")

    try:
        result = subprocess.run([sys.executable, 'main.py', '--check'],
                               capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Configuração válida")
            return True
        else:
            print("⚠️  Problemas de configuração encontrados:")
            print(result.stdout)
            return False

    except Exception as e:
        print(f"❌ Erro ao verificar configuração: {e}")
        return False

def main():
    print("""
🚀 InstaCalebeDigital - Setup Rápido
════════════════════════════════════

Este script irá configurar o projeto automaticamente.
    """)

    # Verificar se estamos no diretório correto
    if not Path('main.py').exists():
        print("❌ Execute este script do diretório raiz do projeto")
        sys.exit(1)

    steps = [
        ("Instalando dependências", install_dependencies),
        ("Configurando arquivo .env", setup_env_file),
        ("Inicializando banco de dados", initialize_database),
        ("Verificando configuração", check_config),
    ]

    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Falha em: {step_name}")
            print("\nPara configuração manual, consulte o README.md")
            sys.exit(1)

    print("""
✅ Setup completo!

📋 Próximos passos:

1. Configure suas credenciais no arquivo .env:
   - Instagram: username e password
   - APIs: OpenAI/Anthropic, News API, etc.

2. Execute o dashboard:
   python main.py --mode dashboard

3. Ou execute o pipeline completo:
   python main.py --mode full

4. Para automação contínua:
   python scripts/start_workers.py

📖 Consulte o README.md para mais informações.
    """)

if __name__ == "__main__":
    main()