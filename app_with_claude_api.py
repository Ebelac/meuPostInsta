#!/usr/bin/env python3
"""
Flask App - Gerador de Carrosséis CalebeDigital com API do Claude
Aplicação web independente que usa a API do Claude para gerar conteúdo
"""
import os
import sys
import zipfile
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from dotenv import load_dotenv
import secrets

# Carregar variáveis de ambiente
load_dotenv('.env.flask')

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar nosso gerador original (fallback)
try:
    from generate_single_carousel import SingleCarouselGenerator
except ImportError:
    print("⚠️  Gerador original não encontrado - usando apenas API do Claude")

# Importar integração com Claude
try:
    from claude_api_integration import ClaudeCarouselGenerator
    CLAUDE_AVAILABLE = True
except ImportError:
    print("⚠️  SDK do Claude não instalado. Execute: pip install anthropic")
    CLAUDE_AVAILABLE = False

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(16))

# Configurações de autenticação
USERS = {
    os.getenv('ADMIN_USER', 'calebe'): generate_password_hash(os.getenv('ADMIN_PASS', 'calebe2024!')),
    os.getenv('BACKUP_USER', 'admin'): generate_password_hash(os.getenv('BACKUP_PASS', 'admin123!'))
}

def login_required(f):
    """Decorator para páginas que requerem autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Página inicial - redireciona conforme autenticação"""
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and check_password_hash(USERS[username], password):
            session['username'] = username
            session['login_time'] = datetime.now().isoformat()
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout do usuário"""
    session.pop('username', None)
    session.pop('login_time', None)
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal"""
    username = session.get('username')
    login_time = session.get('login_time')

    # Verificar carrosséis existentes
    carousel_dir = 'assets/generated_carousels'
    existing_carousels = []

    if os.path.exists(carousel_dir):
        files = [f for f in os.listdir(carousel_dir) if f.endswith('.png')]
        # Agrupar por carrossel
        carousels = {}
        for file in files:
            prefix = file.rsplit('_slide_', 1)[0]
            if prefix not in carousels:
                carousels[prefix] = []
            carousels[prefix].append(file)

        for carousel_name, slides in carousels.items():
            existing_carousels.append({
                'name': carousel_name,
                'slides': len(slides),
                'files': sorted(slides)
            })

    return render_template('dashboard.html',
                         username=username,
                         login_time=login_time,
                         existing_carousels=existing_carousels,
                         claude_available=CLAUDE_AVAILABLE)

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_carousel():
    """Geração de carrossel"""
    if request.method == 'POST':
        try:
            generation_method = request.form.get('method', 'original')
            topic = request.form.get('topic', 'Criptografia Quântica e Impactos na Segurança Digital')

            if generation_method == 'claude' and CLAUDE_AVAILABLE:
                # Usar API do Claude
                claude_generator = ClaudeCarouselGenerator()

                # Gerar conteúdo via Claude
                carousel_data = claude_generator.generate_carousel_content(topic, slides_count=9)

                # Salvar dados gerados
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                content_file = f'generated_content_{timestamp}.json'
                content_path = os.path.join('temp', content_file)

                os.makedirs('temp', exist_ok=True)
                with open(content_path, 'w', encoding='utf-8') as f:
                    json.dump(carousel_data, f, ensure_ascii=False, indent=2)

                flash(f'✨ Conteúdo gerado via Claude! {len(carousel_data.get("slides", []))} slides criados.', 'success')
                flash(f'📄 Conteúdo salvo em: {content_file}', 'info')

                # TODO: Integrar com gerador visual
                return redirect(url_for('view_generated_content', filename=content_file))

            else:
                # Método original (fallback)
                carousel_data = {
                    'id': 'quantum_crypto_webapp',
                    'title': topic,
                    'approach': 'Carrossel gerado via WebApp (método original)'
                }

                generator = SingleCarouselGenerator()
                slides = generator.generate_complete_9_slide_carousel(carousel_data)

                flash(f'✅ Carrossel gerado com sucesso! {len(slides)} slides criados.', 'success')
                return redirect(url_for('download_carousel', carousel_id='quantum_crypto'))

        except Exception as e:
            flash(f'❌ Erro ao gerar carrossel: {str(e)}', 'danger')
            print(f"Erro detalhado: {e}")

    return render_template('generate_advanced.html', claude_available=CLAUDE_AVAILABLE)

@app.route('/view-content/<filename>')
@login_required
def view_generated_content(filename):
    """Visualizar conteúdo gerado via Claude"""
    try:
        content_path = os.path.join('temp', filename)

        if not os.path.exists(content_path):
            flash('Arquivo de conteúdo não encontrado!', 'danger')
            return redirect(url_for('dashboard'))

        with open(content_path, 'r', encoding='utf-8') as f:
            content_data = json.load(f)

        return render_template('view_content.html',
                             content=content_data,
                             filename=filename)

    except Exception as e:
        flash(f'Erro ao visualizar conteúdo: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/download/<carousel_id>')
@login_required
def download_carousel(carousel_id):
    """Download do carrossel em ZIP"""
    try:
        carousel_dir = 'assets/generated_carousels'
        zip_filename = f'{carousel_id}_carousel_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip'
        zip_path = os.path.join('temp', zip_filename)

        # Criar diretório temp se não existir
        os.makedirs('temp', exist_ok=True)

        # Criar ZIP com os slides
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            if os.path.exists(carousel_dir):
                for file in os.listdir(carousel_dir):
                    if file.endswith('.png') and carousel_id in file:
                        file_path = os.path.join(carousel_dir, file)
                        zip_file.write(file_path, file)

        return send_file(zip_path, as_attachment=True, download_name=zip_filename)

    except Exception as e:
        flash(f'Erro ao baixar carrossel: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/api/generate', methods=['POST'])
@login_required
def api_generate():
    """API endpoint para geração via AJAX"""
    try:
        data = request.json
        topic = data.get('topic', 'Tecnologia e Inovação')
        method = data.get('method', 'claude')

        if method == 'claude' and CLAUDE_AVAILABLE:
            claude_generator = ClaudeCarouselGenerator()
            carousel_data = claude_generator.generate_carousel_content(topic, slides_count=9)

            return jsonify({
                'success': True,
                'message': f'Conteúdo gerado via Claude!',
                'slides_count': len(carousel_data.get('slides', [])),
                'data': carousel_data
            })

        else:
            # Fallback para método original
            return jsonify({
                'success': False,
                'error': 'Método não disponível ou API do Claude não configurada'
            }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/preview/<slide_name>')
@login_required
def preview_slide(slide_name):
    """Visualizar slide específico"""
    try:
        slide_path = os.path.join('assets/generated_carousels', slide_name)
        if os.path.exists(slide_path):
            return send_file(slide_path)
        else:
            flash('Slide não encontrado!', 'danger')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Erro ao visualizar slide: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/health')
def health_check():
    """Health check para monitoramento"""
    return jsonify({
        'status': 'healthy',
        'claude_api': CLAUDE_AVAILABLE,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('assets/generated_carousels', exist_ok=True)
    os.makedirs('assets/profile', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    print("🚀 Iniciando Flask App - Gerador de Carrosséis (com Claude API)")
    print("📱 Acesse via: http://localhost:5004")
    print(f"👤 Usuário: {os.getenv('ADMIN_USER', 'calebe')} | Senha: {os.getenv('ADMIN_PASS', 'calebe2024!')}")
    print(f"🤖 Claude API: {'✅ Disponível' if CLAUDE_AVAILABLE else '❌ Não configurado'}")
    print("="*60)

    # Executar em modo debug para desenvolvimento
    app.run(host='0.0.0.0', port=5004, debug=os.getenv('FLASK_DEBUG', 'True').lower() == 'true')