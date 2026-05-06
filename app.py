#!/usr/bin/env python3
"""
Flask App - Gerador de Carrosséis CalebeDigital
Aplicação web com autenticação para gerar carrosséis remotamente
"""
import os
import sys
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import secrets

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Importar nosso gerador
from generate_single_carousel import SingleCarouselGenerator

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Configurações de autenticação
USERS = {
    'calebe': generate_password_hash('calebe2024!'),  # Usuário: calebe, Senha: calebe2024!
    'admin': generate_password_hash('admin123!')     # Usuário backup
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
                         existing_carousels=existing_carousels)

@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_carousel():
    """Geração de carrossel"""
    if request.method == 'POST':
        try:
            # Dados do carrossel
            carousel_data = {
                'id': 'quantum_crypto_webapp',
                'title': '🚨 Criptografia em Risco: Era Quântica',
                'approach': 'Carrossel gerado via WebApp'
            }

            # Gerar carrossel
            generator = SingleCarouselGenerator()
            slides = generator.generate_complete_9_slide_carousel(carousel_data)

            flash(f'Carrossel gerado com sucesso! {len(slides)} slides criados.', 'success')
            return redirect(url_for('download_carousel', carousel_id='quantum_crypto'))

        except Exception as e:
            flash(f'Erro ao gerar carrossel: {str(e)}', 'danger')

    return render_template('generate.html')

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
            for file in os.listdir(carousel_dir):
                if file.endswith('.png') and 'quantum_crypto' in file:
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
        carousel_data = {
            'id': 'quantum_crypto_api',
            'title': '🚨 Criptografia em Risco: Era Quântica',
            'approach': 'Carrossel gerado via API'
        }

        generator = SingleCarouselGenerator()
        slides = generator.generate_complete_9_slide_carousel(carousel_data)

        return jsonify({
            'success': True,
            'message': f'Carrossel gerado com sucesso!',
            'slides_count': len(slides),
            'download_url': url_for('download_carousel', carousel_id='quantum_crypto')
        })

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

@app.route('/content-generator', methods=['GET', 'POST'])
@login_required
def content_generator():
    """Gerador completo de conteúdo"""
    if request.method == 'POST':
        try:
            from intelligent_content_generator import generate_intelligent_content_from_theme

            theme = request.form.get('theme', '').strip()
            content_type = request.form.get('content_type', 'educativo')
            tone = request.form.get('tone', 'profissional')

            if not theme:
                flash('Por favor, digite um tema para o conteúdo.', 'danger')
                return render_template('content_generator.html')

            if len(theme) < 5:
                flash('O tema deve ter pelo menos 5 caracteres.', 'danger')
                return render_template('content_generator.html')

            # Gerar conteúdo inteligente com pesquisa
            print(f"🧠 Gerando conteúdo INTELIGENTE para: {theme}")
            content_data = generate_intelligent_content_from_theme(theme)

            flash(f'🧠 Conteúdo inteligente gerado com sucesso! Baseado em pesquisa de mercado.', 'success')
            return render_template('content_result_intelligent.html', content=content_data)

        except Exception as e:
            flash(f'❌ Erro ao gerar conteúdo: {str(e)}', 'danger')
            print(f"Erro detalhado: {e}")

    return render_template('content_generator.html')

@app.route('/download-content/<filename>')
@login_required
def download_generated_content(filename):
    """Download do pacote de conteúdo gerado"""
    try:
        # Procurar arquivo de conteúdo na pasta temp
        temp_dir = 'temp'
        content_files = [f for f in os.listdir(temp_dir) if f.startswith('content_package_') and f.endswith('.json')]

        if not content_files:
            flash('Nenhum conteúdo encontrado para download.', 'danger')
            return redirect(url_for('content_generator'))

        # Usar o arquivo mais recente
        latest_file = max(content_files, key=lambda f: os.path.getctime(os.path.join(temp_dir, f)))

        # Criar ZIP com conteúdo + slides (se existirem)
        zip_filename = f'conteudo_completo_{filename}.zip'
        zip_path = os.path.join('temp', zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Adicionar arquivo JSON com todo o conteúdo
            zip_file.write(os.path.join(temp_dir, latest_file), f'conteudo_detalhado.json')

            # Adicionar slides se existirem
            carousel_dir = 'assets/generated_carousels'
            if os.path.exists(carousel_dir):
                slides = [f for f in os.listdir(carousel_dir) if f.endswith('.png')]
                for slide in slides[-9:]:  # Últimos 9 slides
                    slide_path = os.path.join(carousel_dir, slide)
                    zip_file.write(slide_path, f'slides/{slide}')

        return send_file(zip_path, as_attachment=True, download_name=zip_filename)

    except Exception as e:
        flash(f'Erro ao baixar conteúdo: {str(e)}', 'danger')
        return redirect(url_for('content_generator'))

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('assets/generated_carousels', exist_ok=True)
    os.makedirs('assets/profile', exist_ok=True)
    os.makedirs('temp', exist_ok=True)
    os.makedirs('templates', exist_ok=True)

    print("🚀 Iniciando Flask App - Gerador de Carrosséis")
    print("📱 Acesse via: http://localhost:5002")
    print("👤 Usuário: calebe | Senha: calebe2024!")
    print("="*50)

    # Executar em modo debug para desenvolvimento
    app.run(host='0.0.0.0', port=5002, debug=True)