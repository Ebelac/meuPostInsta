#!/usr/bin/env python3
"""
InstaCalebeDigital - Sistema Automatizado de Conteúdo Tech para Instagram

Ponto de entrada principal da aplicação.
"""
import sys
import os
import argparse
import logging
from datetime import datetime
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from config.settings import settings
from src.database import init_database
from src.scrapers import NewsAggregator
from src.curator import ContentCurator
from src.writer import AIContentWriter
from src.designer import CarouselGenerator
from src.publisher import InstagramPublisher, PostScheduler
from src.scheduler import IntelligentScheduler, TaskManager


def setup_logging(log_level='INFO'):
    """Configurar sistema de logging"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.FileHandler('instagram_automation.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Reduzir verbosidade de bibliotecas externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)


def check_requirements():
    """Verificar se todas as dependências estão instaladas"""
    required_packages = [
        'requests', 'beautifulsoup4', 'feedparser', 'pandas',
        'openai', 'anthropic', 'Pillow', 'instagrapi',
        'sqlalchemy', 'pydantic', 'streamlit'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            # Mapear nomes de pacotes especiais
            import_name = package
            if package == 'beautifulsoup4':
                import_name = 'bs4'
            elif package == 'Pillow':
                import_name = 'PIL'
            elif '-' in package:
                import_name = package.replace('-', '_')

            __import__(import_name)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Pacotes faltando: {', '.join(missing_packages)}")
        print("Execute: pip install -r requirements.txt")
        return False

    return True


def check_configuration():
    """Verificar configurações essenciais"""
    config_issues = []

    # Verificar credenciais Instagram
    if not settings.instagram_username or not settings.instagram_password:
        config_issues.append("Credenciais do Instagram não configuradas")

    # Verificar pelo menos uma API de IA
    if not settings.openai_api_key and not settings.anthropic_api_key:
        config_issues.append("Nenhuma API de IA configurada (OpenAI ou Anthropic)")

    # Verificar arquivo .env
    if not Path('.env').exists():
        config_issues.append("Arquivo .env não encontrado - copie .env.example para .env")

    if config_issues:
        print("⚠️  Problemas de configuração encontrados:")
        for issue in config_issues:
            print(f"   - {issue}")
        print("\nVerifique o arquivo .env e configure as variáveis necessárias.")
        return False

    return True


def run_scraping(articles_count=20):
    """Executar scraping de notícias"""
    print(f"🔍 Iniciando scraping de notícias (máx. {articles_count} artigos)...")

    aggregator = NewsAggregator()
    stats = aggregator.run_scraping_cycle()

    print(f"✅ Scraping concluído!")
    print(f"   📰 Artigos coletados: {stats.get('total_scraped', 0)}")
    print(f"   🆕 Novos artigos: {stats.get('new_articles', 0)}")
    print(f"   ⏱️  Duração: {stats.get('duration_seconds', 0):.1f}s")

    return stats


def run_curation(target_posts=3):
    """Executar curadoria de conteúdo"""
    print(f"🎯 Iniciando curadoria de conteúdo (alvo: {target_posts} posts)...")

    curator = ContentCurator()
    curated_content = curator.curate_daily_content(target_posts=target_posts)

    print(f"✅ Curadoria concluída!")
    print(f"   📋 Artigos selecionados: {len(curated_content)}")

    if curated_content:
        print("   🏆 Top artigos:")
        for i, content in enumerate(curated_content[:3], 1):
            score = content.get('scores', {}).get('final_score', 0)
            title = content.get('title', 'Unknown')[:50]
            print(f"      {i}. {title}... (Score: {score:.1f})")

    return curated_content


def run_content_generation(curated_content):
    """Gerar conteúdo completo (texto + design)"""
    if not curated_content:
        print("❌ Nenhum conteúdo curado para gerar")
        return []

    print(f"✍️  Gerando conteúdo para {len(curated_content)} artigos...")

    writer = AIContentWriter()
    designer = CarouselGenerator()

    generated_posts = []

    for i, content_data in enumerate(curated_content, 1):
        try:
            print(f"   📝 Gerando post {i}/{len(curated_content)}: {content_data.get('title', 'Unknown')[:30]}...")

            # Gerar texto
            post_content = writer.generate_instagram_post(content_data)

            # Gerar imagens
            carousel_images = designer.generate_carousel(
                post_content['carousel_topics'],
                post_content['metadata']
            )

            # Combinar
            complete_post = {
                **post_content,
                'carousel_images': carousel_images,
                'source_article_id': content_data.get('article_id')
            }

            generated_posts.append(complete_post)

        except Exception as e:
            print(f"   ❌ Erro ao gerar post {i}: {e}")

    print(f"✅ Geração de conteúdo concluída! {len(generated_posts)} posts criados")
    return generated_posts


def run_scheduling(generated_posts):
    """Agendar posts inteligentemente"""
    if not generated_posts:
        print("❌ Nenhum post para agendar")
        return

    print(f"⏰ Agendando {len(generated_posts)} posts...")

    scheduler = IntelligentScheduler()

    # Preparar dados para agendamento
    content_for_scheduling = []
    for post in generated_posts:
        content_data = {
            'title': post.get('metadata', {}).get('title', 'Unknown'),
            'category': post.get('metadata', {}).get('category', 'Technology'),
            'article_id': post.get('source_article_id'),
            'scores': {'final_score': 8.0}  # Mock score
        }
        content_for_scheduling.append(content_data)

    # Usar o scheduling do sistema
    result = scheduler.schedule_content_intelligently(content_for_scheduling)

    if result.get('success'):
        scheduled_posts = result.get('scheduled_posts', [])
        print(f"✅ Agendamento concluído!")
        print(f"   📅 Posts agendados: {len(scheduled_posts)}")

        if scheduled_posts:
            next_post = min(scheduled_posts, key=lambda x: x['scheduled_time'])
            print(f"   ⏰ Próximo post: {next_post['scheduled_time']}")

    else:
        print(f"❌ Erro no agendamento: {result.get('error')}")


def run_full_pipeline(articles_count=20, target_posts=3):
    """Executar pipeline completo"""
    print("🚀 Iniciando pipeline completo InstaCalebeDigital\n")

    # 1. Scraping
    scraping_stats = run_scraping(articles_count)
    print()

    # 2. Curadoria
    curated_content = run_curation(target_posts)
    print()

    # 3. Geração de conteúdo
    generated_posts = run_content_generation(curated_content)
    print()

    # 4. Agendamento
    run_scheduling(generated_posts)
    print()

    print("🎉 Pipeline completo executado com sucesso!")

    # Resumo final
    print("\n📊 RESUMO FINAL:")
    print(f"   📰 Artigos coletados: {scraping_stats.get('total_scraped', 0)}")
    print(f"   🎯 Artigos curados: {len(curated_content)}")
    print(f"   📝 Posts gerados: {len(generated_posts)}")
    print(f"   ⏰ Posts agendados: {len(generated_posts)}")


def run_publish_scheduled():
    """Publicar posts agendados"""
    print("📤 Verificando posts agendados para publicação...")

    scheduler = PostScheduler()
    result = scheduler.publish_scheduled_posts()

    print(f"✅ Verificação concluída!")
    print(f"   📤 Posts publicados: {result['published']}")
    print(f"   ❌ Erros: {result['errors']}")


def run_update_metrics():
    """Atualizar métricas do Instagram"""
    print("📊 Atualizando métricas do Instagram...")

    publisher = InstagramPublisher()
    if not publisher.is_logged_in:
        print("❌ Não conectado ao Instagram")
        return

    result = publisher.bulk_update_metrics()

    print(f"✅ Métricas atualizadas!")
    print(f"   📊 Posts atualizados: {result['updated']}")
    print(f"   ❌ Erros: {result['errors']}")


def run_dashboard():
    """Executar dashboard web"""
    print("🌐 Iniciando dashboard web...")
    print("   Acesse: http://localhost:8501")

    import subprocess
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "dashboard/app.py",
        "--server.port=8501"
    ])


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="InstaCalebeDigital - Automação de Conteúdo Tech para Instagram"
    )

    parser.add_argument(
        '--mode',
        choices=['full', 'scraper', 'curator', 'generate', 'schedule', 'publish', 'metrics', 'dashboard'],
        default='full',
        help='Modo de execução'
    )

    parser.add_argument(
        '--articles',
        type=int,
        default=20,
        help='Número máximo de artigos para scraping'
    )

    parser.add_argument(
        '--posts',
        type=int,
        default=3,
        help='Número alvo de posts para curadoria'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Nível de logging'
    )

    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Inicializar banco de dados'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Verificar configurações e dependências'
    )

    args = parser.parse_args()

    # Configurar logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    print(f"""
🚀 InstaCalebeDigital
════════════════════════════════════════

Sistema Automatizado de Conteúdo Tech para Instagram
Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Modo: {args.mode}

════════════════════════════════════════
    """)

    # Verificações iniciais
    if args.check or args.mode != 'dashboard':
        print("🔍 Verificando dependências e configurações...")

        if not check_requirements():
            sys.exit(1)

        if not check_configuration():
            print("\n💡 Dica: Execute com --mode dashboard para configurar via interface web")
            sys.exit(1)

        print("✅ Verificações concluídas com sucesso!\n")

    # Inicializar banco de dados se solicitado
    if args.init_db:
        print("🗄️  Inicializando banco de dados...")
        init_database()
        print("✅ Banco de dados inicializado!\n")

    # Executar modo selecionado
    try:
        if args.mode == 'full':
            run_full_pipeline(args.articles, args.posts)

        elif args.mode == 'scraper':
            run_scraping(args.articles)

        elif args.mode == 'curator':
            run_curation(args.posts)

        elif args.mode == 'generate':
            # Precisaria de conteúdo curado existente
            print("🎯 Obtendo conteúdo curado...")
            curated_content = run_curation(args.posts)
            run_content_generation(curated_content)

        elif args.mode == 'schedule':
            # Executar agendamento em conteúdo existente
            print("⏰ Executando agendamento inteligente...")
            curator = ContentCurator()
            content = curator.curate_daily_content(args.posts)
            run_scheduling(run_content_generation(content))

        elif args.mode == 'publish':
            run_publish_scheduled()

        elif args.mode == 'metrics':
            run_update_metrics()

        elif args.mode == 'dashboard':
            run_dashboard()

    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

    print(f"\n✅ Execução concluída com sucesso! ({datetime.now().strftime('%H:%M:%S')})")


if __name__ == "__main__":
    main()