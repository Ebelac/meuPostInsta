#!/usr/bin/env python3
"""
Baixa imagens temáticas específicas para TikTok + Banco Central + Empréstimos
"""
import os
import requests
from PIL import Image
import urllib.parse

def download_thematic_images():
    """Baixa imagens específicas para TikTok empréstimos bancários"""

    # URLs de imagens temáticas para cada slide sobre TikTok + Banco Central
    thematic_images = {
        1: {
            'url': 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=800&h=600&fit=crop',
            'description': 'TikTok logo and mobile phone with app',
            'keywords': 'tiktok, logo, mobile, app'
        },
        2: {
            'url': 'https://images.unsplash.com/photo-1541354329998-f4d9a9f9297f?w=800&h=600&fit=crop',
            'description': 'Banco Central do Brasil building in Brasilia',
            'keywords': 'banco central, brasilia, government, building'
        },
        3: {
            'url': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&h=600&fit=crop',
            'description': 'Banking licenses and financial documents',
            'keywords': 'banking, license, documents, financial'
        },
        4: {
            'url': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=800&h=600&fit=crop',
            'description': 'Social media meets fintech disruption',
            'keywords': 'fintech, disruption, social media'
        },
        5: {
            'url': 'https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=600&fit=crop',
            'description': 'Brazilian market, financial crisis concerns',
            'keywords': 'brazil, market, crisis, concern'
        },
        6: {
            'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop',
            'description': 'Legal documents, regulatory approval process',
            'keywords': 'legal, documents, approval, law'
        },
        7: {
            'url': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop',
            'description': 'Warning signs, financial risks alerts',
            'keywords': 'warning, risk, alert, danger'
        },
        8: {
            'url': 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=600&fit=crop',
            'description': 'Banking security, protection measures',
            'keywords': 'banking, security, protection, safe'
        },
        9: {
            'url': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&h=600&fit=crop',
            'description': 'Community sharing, financial education',
            'keywords': 'community, sharing, education, finance'
        }
    }

    # URLs alternativas caso as principais falhem
    fallback_images = {
        1: 'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=800&h=600&fit=crop',  # Tech mobile
        2: 'https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&h=600&fit=crop',  # Government/law
        3: 'https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800&h=600&fit=crop',  # Money/banking
        4: 'https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&h=600&fit=crop',  # Tech disruption
        5: 'https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800&h=600&fit=crop',  # Market analysis
        6: 'https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=800&h=600&fit=crop',  # Business documents
        7: 'https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800&h=600&fit=crop',  # Warning/alert
        8: 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&h=600&fit=crop',  # Security
        9: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800&h=600&fit=crop'   # Community
    }

    # Criar diretório para imagens temáticas
    image_dir = 'assets/slide_images'
    os.makedirs(image_dir, exist_ok=True)

    print("🎨 Baixando imagens TEMÁTICAS para TikTok Empréstimos...")
    print("="*60)

    downloaded_count = 0

    for slide_num, image_info in thematic_images.items():
        primary_url = image_info['url']
        fallback_url = fallback_images.get(slide_num)
        description = image_info['description']

        # Nome dos arquivos específicos para TikTok empréstimos
        filename = f'tiktok_emprestimo_slide_{slide_num}.jpg'
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

    files = [f for f in os.listdir(image_dir)
             if f.startswith('tiktok_emprestimo_slide_') and f.endswith('.jpg')]

    if files:
        print(f"📁 Imagens TikTok Empréstimo disponíveis ({len(files)}):")
        for filename in sorted(files):
            filepath = os.path.join(image_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   ✅ {filename} ({size//1024} KB)")
    else:
        print("❌ Nenhuma imagem temática encontrada")

if __name__ == "__main__":
    print("🎨 BAIXADOR DE IMAGENS TEMÁTICAS - TIKTOK EMPRÉSTIMOS")
    print("Substitui imagens genéricas por temáticas específicas")
    print()

    # Baixar imagens
    success = download_thematic_images()

    print()

    # Listar resultado
    list_downloaded_images()

    if success:
        print()
        print("🚀 PRÓXIMO PASSO:")
        print("Execute: python3 generate_tiktok_emprestimo_modelo_principal.py")
        print("As imagens temáticas serão usadas automaticamente!")
    else:
        print()
        print("⚠️ Se falhou, verifique sua conexão e tente novamente")