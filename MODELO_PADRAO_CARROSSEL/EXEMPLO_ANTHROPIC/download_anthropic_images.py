#!/usr/bin/env python3
"""
Baixa imagens TEMÁTICAS específicas para o vazamento da Anthropic
"""
import os
import requests
from PIL import Image
import urllib.parse

def download_anthropic_thematic_images():
    """Baixa imagens específicas para tema Anthropic/GitHub/Vazamento"""

    # URLs de imagens REALMENTE temáticas para cada slide
    thematic_images = {
        1: {
            'url': 'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=800&h=600&fit=crop',
            'description': 'GitHub interface with code repositories',
            'keywords': 'github, repositories, code'
        },
        2: {
            'url': 'https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=800&h=600&fit=crop',
            'description': 'Code on computer screens',
            'keywords': 'code, programming, screen'
        },
        3: {
            'url': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&h=600&fit=crop',
            'description': 'Technology crisis, AI systems',
            'keywords': 'ai, crisis, technology'
        },
        4: {
            'url': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&h=600&fit=crop',
            'description': 'Cybersecurity breach, hacking',
            'keywords': 'security, breach, hack'
        },
        5: {
            'url': 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&h=600&fit=crop',
            'description': 'Legal documents, lawyers',
            'keywords': 'legal, documents, law'
        },
        6: {
            'url': 'https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=600&fit=crop',
            'description': 'Market crash, financial panic',
            'keywords': 'market, crash, panic'
        },
        7: {
            'url': 'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&h=600&fit=crop',
            'description': 'Warning signs, alerts',
            'keywords': 'warning, alert, danger'
        },
        8: {
            'url': 'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&h=600&fit=crop',
            'description': 'Cybersecurity protection',
            'keywords': 'security, protection, shield'
        },
        9: {
            'url': 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&h=600&fit=crop',
            'description': 'Community sharing, network',
            'keywords': 'community, sharing, network'
        }
    }

    # URLs alternativas caso as principais falhem
    fallback_images = {
        1: 'https://images.unsplash.com/photo-1618401479427-c8ef9465fbe1?w=800&h=600&fit=crop',  # GitHub alternative
        2: 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=600&fit=crop',  # Code alternative
        3: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&h=600&fit=crop',  # Tech crisis alt
        4: 'https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=800&h=600&fit=crop',  # Security alt
        5: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop',  # Legal alt
        6: 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=600&fit=crop',  # Market alt
        7: 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop',  # Warning alt
        8: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',  # Security alt
        9: 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop'   # Community alt
    }

    # Criar diretório para imagens temáticas
    image_dir = 'assets/slide_images'
    os.makedirs(image_dir, exist_ok=True)

    print("🎨 Baixando imagens TEMÁTICAS para vazamento Anthropic...")
    print("="*60)

    downloaded_count = 0

    for slide_num, image_info in thematic_images.items():
        primary_url = image_info['url']
        fallback_url = fallback_images.get(slide_num)
        description = image_info['description']

        # Nome do arquivo específico para Anthropic
        filename = f'anthropic_slide_{slide_num}.jpg'
        filepath = os.path.join(image_dir, filename)

        print(f"📥 Slide {slide_num}: {description}")

        # Tentar baixar imagem principal
        success = False
        for attempt, url in enumerate([primary_url, fallback_url], 1):
            if not url:
                continue

            try:
                print(f"   Tentativa {attempt}: {url[:50]}...")

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }

                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    # Salvar imagem
                    with open(filepath, 'wb') as f:
                        f.write(response.content)

                    # Verificar se é imagem válida
                    try:
                        img = Image.open(filepath)
                        img.verify()  # Verificar integridade

                        print(f"   ✅ Sucesso: {filename} ({len(response.content)//1024} KB)")
                        downloaded_count += 1
                        success = True
                        break

                    except Exception as e:
                        print(f"   ❌ Imagem corrompida: {e}")
                        if os.path.exists(filepath):
                            os.remove(filepath)
                else:
                    print(f"   ❌ HTTP {response.status_code}")

            except Exception as e:
                print(f"   ❌ Erro: {e}")

        if not success:
            print(f"   ⚠️ Falhou - usando placeholder para slide {slide_num}")

    print("="*60)
    print(f"✅ Download concluído: {downloaded_count}/9 imagens")

    if downloaded_count > 0:
        print("🎯 Imagens temáticas prontas para usar!")
        print("📁 Local: assets/slide_images/")
        return True
    else:
        print("❌ Nenhuma imagem baixada - verifique conexão")
        return False

def list_downloaded_images():
    """Lista imagens baixadas"""
    image_dir = 'assets/slide_images'

    if not os.path.exists(image_dir):
        print("❌ Diretório de imagens não existe")
        return

    files = [f for f in os.listdir(image_dir) if f.startswith('anthropic_slide_') and f.endswith('.jpg')]

    if files:
        print(f"📁 Imagens Anthropic disponíveis ({len(files)}):")
        for filename in sorted(files):
            filepath = os.path.join(image_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   ✅ {filename} ({size//1024} KB)")
    else:
        print("❌ Nenhuma imagem temática encontrada")

if __name__ == "__main__":
    print("🎨 BAIXADOR DE IMAGENS TEMÁTICAS - ANTHROPIC")
    print("Substitui imagens genéricas por temáticas específicas")
    print()

    # Baixar imagens
    success = download_anthropic_thematic_images()

    print()

    # Listar resultado
    list_downloaded_images()

    if success:
        print()
        print("🚀 PRÓXIMO PASSO:")
        print("Execute: python3 generate_anthropic_modelo_principal.py")
        print("As imagens temáticas serão usadas automaticamente!")
    else:
        print()
        print("⚠️ Se falhou, verifique sua conexão e tente novamente")