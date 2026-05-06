#!/usr/bin/env python3
"""
Script para iniciar workers Celery
"""
import subprocess
import sys
import os

def start_redis():
    """Iniciar Redis se não estiver rodando"""
    try:
        result = subprocess.run(['redis-cli', 'ping'], capture_output=True, text=True)
        if result.returncode != 0:
            print("🔧 Iniciando Redis...")
            subprocess.Popen(['redis-server'])
        else:
            print("✅ Redis já está rodando")
    except FileNotFoundError:
        print("❌ Redis não encontrado. Instale o Redis primeiro:")
        print("   macOS: brew install redis")
        print("   Ubuntu: sudo apt-get install redis-server")
        sys.exit(1)

def start_celery_worker():
    """Iniciar worker Celery"""
    print("🚀 Iniciando Celery Worker...")
    subprocess.Popen([
        sys.executable, '-m', 'celery', 'worker',
        '-A', 'src.scheduler.task_manager',
        '--loglevel=info'
    ])

def start_celery_beat():
    """Iniciar Celery Beat (scheduler)"""
    print("⏰ Iniciando Celery Beat...")
    subprocess.Popen([
        sys.executable, '-m', 'celery', 'beat',
        '-A', 'src.scheduler.task_manager',
        '--loglevel=info'
    ])

def main():
    print("🔧 Configurando ambiente de execução...")

    # Mudar para diretório do projeto
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)

    # Iniciar serviços
    start_redis()
    start_celery_worker()
    start_celery_beat()

    print("✅ Todos os serviços iniciados!")
    print("📊 Para monitorar, acesse: http://localhost:5555 (se Flower estiver instalado)")
    print("⚠️  Mantenha este terminal aberto")

    try:
        input("Pressione Enter para parar todos os serviços...")
    except KeyboardInterrupt:
        pass

    print("🛑 Parando serviços...")

if __name__ == "__main__":
    main()