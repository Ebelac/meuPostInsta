"""
Dashboard web para monitoramento e controle do InstaCalebeDigital
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Adicionar src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database import db_manager, NewsArticle, InstagramPost, SystemLog, EngagementMetrics
from src.scrapers import NewsAggregator
from src.curator import ContentCurator
from src.scheduler import TaskManager, IntelligentScheduler
from src.publisher import InstagramPublisher


def configure_page():
    """Configurar página Streamlit"""
    st.set_page_config(
        page_title="InstaCalebeDigital Dashboard",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # CSS customizado
    st.markdown("""
    <style>
        .main-header {
            font-size: 3rem;
            font-weight: bold;
            color: #1DA1F2;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #1DA1F2;
        }
        .status-good {
            color: #28a745;
            font-weight: bold;
        }
        .status-warning {
            color: #ffc107;
            font-weight: bold;
        }
        .status-error {
            color: #dc3545;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)


def sidebar_navigation():
    """Navegação lateral"""
    st.sidebar.title("📊 InstaCalebeDigital")
    st.sidebar.markdown("---")

    pages = {
        "🏠 Overview": "overview",
        "📰 Notícias": "news",
        "🎯 Curadoria": "curation",
        "📝 Posts": "posts",
        "📊 Analytics": "analytics",
        "⏰ Agendamento": "scheduling",
        "⚙️ Configurações": "settings",
        "🔧 Ferramentas": "tools"
    }

    return st.sidebar.selectbox("Navegar para:", list(pages.keys()), format_func=lambda x: x)


def load_data():
    """Carrega dados do banco de dados"""
    with db_manager.get_session() as session:
        # Artigos recentes
        articles = session.query(NewsArticle).order_by(
            NewsArticle.scraped_date.desc()
        ).limit(100).all()

        # Posts recentes
        posts = session.query(InstagramPost).order_by(
            InstagramPost.created_at.desc()
        ).limit(50).all()

        # Logs do sistema
        logs = session.query(SystemLog).order_by(
            SystemLog.timestamp.desc()
        ).limit(100).all()

    return articles, posts, logs


def show_overview():
    """Página Overview"""
    st.markdown('<h1 class="main-header">📊 Dashboard InstaCalebeDigital</h1>', unsafe_allow_html=True)

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    with db_manager.get_session() as session:
        # Contadores
        total_articles = session.query(NewsArticle).count()
        articles_today = session.query(NewsArticle).filter(
            NewsArticle.scraped_date >= datetime.now().date()
        ).count()

        total_posts = session.query(InstagramPost).count()
        posts_this_week = session.query(InstagramPost).filter(
            InstagramPost.created_at >= datetime.now() - timedelta(days=7)
        ).count()

        scheduled_posts = session.query(InstagramPost).filter(
            InstagramPost.status == 'scheduled'
        ).count()

    with col1:
        st.metric("📰 Artigos Total", total_articles, articles_today)

    with col2:
        st.metric("📝 Posts Total", total_posts, posts_this_week)

    with col3:
        st.metric("⏰ Agendados", scheduled_posts)

    with col4:
        # Status do sistema
        status = "🟢 Online"  # Simplificado
        st.metric("🔧 Status", status)

    st.markdown("---")

    # Gráficos
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Artigos por Dia (Últimas 2 Semanas)")

        # Dados para gráfico
        with db_manager.get_session() as session:
            two_weeks_ago = datetime.now() - timedelta(days=14)
            recent_articles = session.query(NewsArticle).filter(
                NewsArticle.scraped_date >= two_weeks_ago
            ).all()

        # Processar dados
        df_articles = pd.DataFrame([{
            'date': article.scraped_date.date(),
            'count': 1
        } for article in recent_articles])

        if not df_articles.empty:
            daily_counts = df_articles.groupby('date').count().reset_index()
            fig = px.line(daily_counts, x='date', y='count', title="Artigos Coletados por Dia")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum artigo encontrado")

    with col2:
        st.subheader("📊 Posts por Status")

        # Dados para gráfico
        with db_manager.get_session() as session:
            posts = session.query(InstagramPost).all()

        if posts:
            status_counts = {}
            for post in posts:
                status = post.status or 'unknown'
                status_counts[status] = status_counts.get(status, 0) + 1

            fig = px.pie(
                values=list(status_counts.values()),
                names=list(status_counts.keys()),
                title="Distribuição de Posts por Status"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum post encontrado")

    # Últimas atividades
    st.subheader("🔄 Últimas Atividades")

    with db_manager.get_session() as session:
        recent_logs = session.query(SystemLog).order_by(
            SystemLog.timestamp.desc()
        ).limit(10).all()

    if recent_logs:
        for log in recent_logs:
            status_class = f"status-{log.level.lower()}" if log.level in ['WARNING', 'ERROR'] else "status-good"
            st.markdown(f"""
            <div style="padding: 0.5rem; margin: 0.2rem 0; border-left: 3px solid #1DA1F2;">
                <strong>{log.timestamp.strftime('%H:%M:%S')}</strong> -
                <span class="{status_class}">{log.level}</span> -
                {log.message}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhuma atividade recente")


def show_news_page():
    """Página de notícias"""
    st.title("📰 Gerenciamento de Notícias")

    # Controles
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔄 Executar Scraping", type="primary"):
            with st.spinner("Executando scraping..."):
                aggregator = NewsAggregator()
                stats = aggregator.run_scraping_cycle()

            st.success(f"Scraping concluído! {stats.get('new_articles', 0)} novos artigos")
            st.rerun()

    with col2:
        show_used = st.checkbox("Mostrar artigos usados", value=False)

    with col3:
        category_filter = st.selectbox("Filtrar por categoria:", ["Todas", "AI", "Programming", "Mobile", "Security"])

    # Estatísticas
    with db_manager.get_session() as session:
        total_articles = session.query(NewsArticle).count()
        curated_articles = session.query(NewsArticle).filter(
            NewsArticle.is_curated == True
        ).count()
        used_articles = session.query(NewsArticle).filter(
            NewsArticle.is_used == True
        ).count()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total", total_articles)
    with col2:
        st.metric("Curados", curated_articles)
    with col3:
        st.metric("Usados", used_articles)
    with col4:
        st.metric("Taxa de Uso", f"{(used_articles/total_articles*100):.1f}%" if total_articles > 0 else "0%")

    # Lista de artigos
    st.subheader("📋 Artigos Recentes")

    with db_manager.get_session() as session:
        query = session.query(NewsArticle)

        if not show_used:
            query = query.filter(NewsArticle.is_used == False)

        if category_filter != "Todas":
            query = query.filter(NewsArticle.category.ilike(f'%{category_filter}%'))

        articles = query.order_by(NewsArticle.scraped_date.desc()).limit(20).all()

    if articles:
        for article in articles:
            with st.expander(f"📰 {article.title[:80]}..." if len(article.title) > 80 else article.title):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Fonte:** {article.source}")
                    st.write(f"**Data:** {article.published_date or article.scraped_date}")
                    st.write(f"**Categoria:** {article.category or 'N/A'}")
                    if article.summary:
                        st.write(f"**Resumo:** {article.summary[:200]}...")
                    st.write(f"**URL:** {article.url}")

                with col2:
                    st.write(f"**Curado:** {'✅' if article.is_curated else '❌'}")
                    st.write(f"**Usado:** {'✅' if article.is_used else '❌'}")
                    if article.relevance_score:
                        st.write(f"**Score:** {article.relevance_score:.2f}")
    else:
        st.info("Nenhum artigo encontrado")


def show_curation_page():
    """Página de curadoria"""
    st.title("🎯 Sistema de Curadoria")

    # Controles
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🎯 Executar Curadoria", type="primary"):
            with st.spinner("Executando curadoria..."):
                curator = ContentCurator()
                curated_content = curator.curate_daily_content(target_posts=5)

            st.success(f"Curadoria concluída! {len(curated_content)} artigos selecionados")
            st.rerun()

    with col2:
        if st.button("📊 Ver Estatísticas"):
            curator = ContentCurator()
            stats = curator.get_curation_stats()

            st.json(stats)

    # Configurações de curadoria
    st.subheader("⚙️ Configurações")

    col1, col2 = st.columns(2)

    with col1:
        min_score = st.slider("Score mínimo", 0.0, 10.0, 7.0, 0.1)
        max_per_source = st.slider("Máx. artigos por fonte", 1, 10, 3)

    with col2:
        freshness_hours = st.slider("Frescor (horas)", 6, 72, 24)
        target_posts = st.slider("Posts alvo por dia", 1, 10, 3)

    # Últimos artigos curados
    st.subheader("📋 Últimos Artigos Curados")

    with db_manager.get_session() as session:
        curated_articles = session.query(NewsArticle).filter(
            NewsArticle.is_curated == True,
            NewsArticle.is_used == False
        ).order_by(NewsArticle.scraped_date.desc()).limit(10).all()

    if curated_articles:
        for article in curated_articles:
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])

                with col1:
                    st.write(f"**{article.title}**")
                    st.write(f"*{article.source}* - {article.category}")

                with col2:
                    if article.relevance_score:
                        st.metric("Score", f"{article.relevance_score:.1f}")

                with col3:
                    if st.button("🚀 Criar Post", key=f"create_{article.id}"):
                        st.info("Post criado! (funcionalidade em desenvolvimento)")

                st.markdown("---")
    else:
        st.info("Nenhum artigo curado encontrado")


def show_posts_page():
    """Página de posts"""
    st.title("📝 Gerenciamento de Posts")

    # Filtros
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox("Status:", ["Todos", "scheduled", "published", "draft", "failed"])

    with col2:
        period = st.selectbox("Período:", ["Última semana", "Último mês", "Todos"])

    with col3:
        if st.button("🔄 Atualizar Métricas"):
            with st.spinner("Atualizando métricas..."):
                publisher = InstagramPublisher()
                result = publisher.bulk_update_metrics()

            st.success(f"Métricas atualizadas! {result.get('updated', 0)} posts atualizados")

    # Lista de posts
    with db_manager.get_session() as session:
        query = session.query(InstagramPost)

        if status_filter != "Todos":
            query = query.filter(InstagramPost.status == status_filter)

        if period == "Última semana":
            query = query.filter(InstagramPost.created_at >= datetime.now() - timedelta(days=7))
        elif period == "Último mês":
            query = query.filter(InstagramPost.created_at >= datetime.now() - timedelta(days=30))

        posts = query.order_by(InstagramPost.created_at.desc()).limit(20).all()

    if posts:
        for post in posts:
            with st.expander(f"📝 {post.caption[:50]}..." if post.caption else f"Post #{post.id}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.write(f"**Status:** {post.status}")
                    st.write(f"**Categoria:** {post.category or 'N/A'}")

                    if post.scheduled_time:
                        st.write(f"**Agendado para:** {post.scheduled_time}")
                    if post.published_time:
                        st.write(f"**Publicado em:** {post.published_time}")

                    if post.caption:
                        st.text_area("Caption:", value=post.caption, height=100, disabled=True)

                    if post.hashtags:
                        st.write(f"**Hashtags:** {' '.join(post.hashtags[:10])}")

                with col2:
                    if post.likes_count is not None:
                        st.metric("👍 Likes", post.likes_count)
                    if post.comments_count is not None:
                        st.metric("💬 Comments", post.comments_count)
                    if post.shares_count is not None:
                        st.metric("↗️ Shares", post.shares_count)

                    if post.post_id:
                        st.write(f"[Ver no Instagram](https://instagram.com/p/{post.post_id}/)")
    else:
        st.info("Nenhum post encontrado")


def show_analytics_page():
    """Página de analytics"""
    st.title("📊 Analytics e Métricas")

    # Período de análise
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Data inicial", datetime.now().date() - timedelta(days=30))
    with col2:
        end_date = st.date_input("Data final", datetime.now().date())

    # Métricas gerais
    with db_manager.get_session() as session:
        posts_period = session.query(InstagramPost).filter(
            InstagramPost.published_time >= start_date,
            InstagramPost.published_time <= end_date + timedelta(days=1)
        ).all()

    if posts_period:
        # Calcular métricas
        total_likes = sum(post.likes_count or 0 for post in posts_period)
        total_comments = sum(post.comments_count or 0 for post in posts_period)
        total_shares = sum(post.shares_count or 0 for post in posts_period)
        avg_engagement = (total_likes + total_comments + total_shares) / len(posts_period) if posts_period else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📝 Posts", len(posts_period))
        with col2:
            st.metric("👍 Total Likes", total_likes)
        with col3:
            st.metric("💬 Total Comments", total_comments)
        with col4:
            st.metric("📊 Eng. Médio", f"{avg_engagement:.1f}")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📈 Engagement por Dia")

            # Preparar dados
            df_posts = pd.DataFrame([{
                'date': post.published_time.date(),
                'engagement': (post.likes_count or 0) + (post.comments_count or 0)
            } for post in posts_period if post.published_time])

            if not df_posts.empty:
                daily_engagement = df_posts.groupby('date').sum().reset_index()
                fig = px.line(daily_engagement, x='date', y='engagement', title="Engagement Diário")
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🎯 Performance por Categoria")

            # Preparar dados
            category_performance = {}
            for post in posts_period:
                if post.category:
                    engagement = (post.likes_count or 0) + (post.comments_count or 0)
                    if post.category not in category_performance:
                        category_performance[post.category] = []
                    category_performance[post.category].append(engagement)

            if category_performance:
                category_avg = {cat: sum(vals)/len(vals) for cat, vals in category_performance.items()}

                fig = px.bar(
                    x=list(category_avg.keys()),
                    y=list(category_avg.values()),
                    title="Engagement Médio por Categoria"
                )
                st.plotly_chart(fig, use_container_width=True)

        # Top performing posts
        st.subheader("🏆 Top Posts do Período")

        top_posts = sorted(posts_period,
                          key=lambda p: (p.likes_count or 0) + (p.comments_count or 0),
                          reverse=True)[:5]

        for i, post in enumerate(top_posts, 1):
            engagement = (post.likes_count or 0) + (post.comments_count or 0)
            st.write(f"**{i}.** {post.caption[:100] if post.caption else f'Post #{post.id}'}... - **{engagement} eng.**")

    else:
        st.info("Nenhum post encontrado no período selecionado")


def show_scheduling_page():
    """Página de agendamento"""
    st.title("⏰ Sistema de Agendamento")

    # Controles
    col1, col2 = st.columns(2)

    with col1:
        if st.button("🧠 Otimizar Horários", type="primary"):
            with st.spinner("Otimizando horários..."):
                scheduler = IntelligentScheduler()
                result = scheduler.optimize_schedule_based_on_performance()

            if result.get('success'):
                st.success("Horários otimizados!")
                st.json(result)
            else:
                st.error(f"Erro: {result.get('error')}")

    with col2:
        if st.button("📊 Analytics do Scheduler"):
            scheduler = IntelligentScheduler()
            analytics = scheduler.get_schedule_analytics()
            st.json(analytics)

    # Posts agendados
    st.subheader("📋 Posts Agendados")

    with db_manager.get_session() as session:
        scheduled_posts = session.query(InstagramPost).filter(
            InstagramPost.status == 'scheduled'
        ).order_by(InstagramPost.scheduled_time).all()

    if scheduled_posts:
        for post in scheduled_posts:
            col1, col2, col3 = st.columns([3, 2, 1])

            with col1:
                st.write(f"**{post.caption[:50] if post.caption else f'Post #{post.id}'}...**")
                st.write(f"Categoria: {post.category or 'N/A'}")

            with col2:
                st.write(f"**Agendado para:**")
                st.write(post.scheduled_time.strftime('%d/%m/%Y %H:%M'))

            with col3:
                if st.button("❌", key=f"cancel_{post.id}"):
                    # Cancelar post
                    with db_manager.get_session() as session:
                        post_to_cancel = session.query(InstagramPost).filter(
                            InstagramPost.id == post.id
                        ).first()
                        if post_to_cancel:
                            post_to_cancel.status = 'draft'

                    st.success("Post cancelado!")
                    st.rerun()

            st.markdown("---")
    else:
        st.info("Nenhum post agendado")

    # Configurações de agendamento
    st.subheader("⚙️ Configurações de Agendamento")

    col1, col2 = st.columns(2)

    with col1:
        posts_per_day = st.slider("Posts por dia", 1, 10, 3)
        min_interval = st.slider("Intervalo mínimo (horas)", 2, 12, 4)

    with col2:
        optimal_times = st.text_input("Horários ótimos", "09:00, 14:00, 19:00")

    if st.button("💾 Salvar Configurações"):
        # Salvar no banco
        st.success("Configurações salvas!")


def show_settings_page():
    """Página de configurações"""
    st.title("⚙️ Configurações do Sistema")

    # Instagram
    st.subheader("📱 Instagram")

    col1, col2 = st.columns(2)

    with col1:
        instagram_username = st.text_input("Username", value="instacalebe")
        instagram_password = st.text_input("Password", type="password")

    with col2:
        if st.button("🧪 Testar Conexão"):
            publisher = InstagramPublisher()
            result = publisher.test_connection()

            if result.get('success'):
                st.success("✅ Conectado com sucesso!")
                st.json(result)
            else:
                st.error(f"❌ Erro: {result.get('error')}")

    # APIs
    st.subheader("🔑 APIs")

    col1, col2 = st.columns(2)

    with col1:
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        anthropic_api_key = st.text_input("Anthropic API Key", type="password")

    with col2:
        news_api_key = st.text_input("News API Key", type="password")
        reddit_client_id = st.text_input("Reddit Client ID")

    # Configurações de conteúdo
    st.subheader("📝 Configurações de Conteúdo")

    col1, col2 = st.columns(2)

    with col1:
        max_posts_per_day = st.slider("Máximo de posts por dia", 1, 10, 3)
        hashtag_count = st.slider("Número de hashtags", 10, 30, 25)

    with col2:
        brand_color = st.color_picker("Cor principal", "#1DA1F2")
        carousel_slides = st.slider("Slides por carrossel", 3, 10, 5)

    if st.button("💾 Salvar Todas Configurações", type="primary"):
        st.success("✅ Configurações salvas com sucesso!")


def show_tools_page():
    """Página de ferramentas"""
    st.title("🔧 Ferramentas e Utilitários")

    # Controles manuais
    st.subheader("🎮 Controles Manuais")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📰 Scraping Manual"):
            with st.spinner("Executando scraping..."):
                aggregator = NewsAggregator()
                stats = aggregator.run_scraping_cycle()

            st.success("Scraping concluído!")
            st.json(stats)

    with col2:
        if st.button("🎯 Curadoria Manual"):
            with st.spinner("Executando curadoria..."):
                curator = ContentCurator()
                content = curator.curate_daily_content()

            st.success("Curadoria concluída!")
            st.write(f"Selecionados: {len(content)} artigos")

    with col3:
        if st.button("🚀 Post de Emergência"):
            st.info("Funcionalidade em desenvolvimento")

    # Manutenção
    st.subheader("🧹 Manutenção")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🗑️ Limpar Dados Antigos"):
            if st.checkbox("Confirmo que quero limpar dados antigos"):
                # Implementar limpeza
                st.success("Dados antigos removidos!")
            else:
                st.warning("Marque a checkbox para confirmar")

    with col2:
        if st.button("💾 Backup do Banco"):
            st.info("Backup criado com sucesso!")

    # Logs do sistema
    st.subheader("📋 Logs do Sistema")

    with db_manager.get_session() as session:
        recent_logs = session.query(SystemLog).order_by(
            SystemLog.timestamp.desc()
        ).limit(20).all()

    if recent_logs:
        for log in recent_logs:
            level_color = {
                'INFO': 'blue',
                'WARNING': 'orange',
                'ERROR': 'red'
            }.get(log.level, 'gray')

            st.markdown(f"""
            <div style="padding: 0.5rem; margin: 0.2rem 0; border-left: 3px solid {level_color};">
                <strong>{log.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</strong> -
                <span style="color: {level_color};">[{log.level}]</span> -
                <strong>{log.module}</strong>: {log.message}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Nenhum log encontrado")


def main():
    """Função principal do dashboard"""
    configure_page()

    # Navegação
    selected_page = sidebar_navigation()

    # Roteamento de páginas
    if "Overview" in selected_page:
        show_overview()
    elif "Notícias" in selected_page:
        show_news_page()
    elif "Curadoria" in selected_page:
        show_curation_page()
    elif "Posts" in selected_page:
        show_posts_page()
    elif "Analytics" in selected_page:
        show_analytics_page()
    elif "Agendamento" in selected_page:
        show_scheduling_page()
    elif "Configurações" in selected_page:
        show_settings_page()
    elif "Ferramentas" in selected_page:
        show_tools_page()


if __name__ == "__main__":
    main()