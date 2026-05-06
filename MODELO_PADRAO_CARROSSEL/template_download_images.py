#!/usr/bin/env python3
"""
TEMPLATE BAIXADOR DE IMAGENS TEMÁTICAS - MODELO PADRÃO

INSTRUÇÕES:
1. Copie este arquivo como: download_[SEU_TEMA]_images.py
2. Substitua [TEMA] e todas as URLs pelos valores do seu tema
3. Execute ANTES de gerar o carrossel para ter imagens temáticas

EXEMPLO: download_bitcoin_images.py
"""
import os
import requests
from PIL import Image
import urllib.parse

def download_thematic_images():
    """Baixa imagens específicas para [SEU TEMA]"""  # ← PERSONALIZAR

    # PERSONALIZAR AQUI: URLs de imagens REALMENTE temáticas para cada slide
    thematic_images = {
        1: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 1]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        2: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 2]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        3: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 3]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        4: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 4]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        5: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 5]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        6: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 6]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        7: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 7]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        8: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 8]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        },
        9: {
            'url': 'https://images.unsplash.com/photo-XXXXXX?w=800&h=600&fit=crop',  # ← SUBSTITUA
            'description': '[Descrição da imagem para slide 9]',  # ← PERSONALIZAR
            'keywords': '[palavra1, palavra2, palavra3]'  # ← PERSONALIZAR
        }
    }

    # PERSONALIZAR AQUI: URLs alternativas caso as principais falhem
    fallback_images = {
        1: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        2: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        3: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        4: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        5: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        6: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        7: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        8: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop',  # ← SUBSTITUA
        9: 'https://images.unsplash.com/photo-YYYYYY?w=800&h=600&fit=crop'   # ← SUBSTITUA
    }

    # Criar diretório para imagens temáticas
    image_dir = 'assets/slide_images'
    os.makedirs(image_dir, exist_ok=True)

    # PERSONALIZAR AQUI: Título do tema
    print("🎨 Baixando imagens TEMÁTICAS para [SEU TEMA]...")  # ← PERSONALIZAR
    print("="*60)

    downloaded_count = 0

    for slide_num, image_info in thematic_images.items():
        primary_url = image_info['url']
        fallback_url = fallback_images.get(slide_num)
        description = image_info['description']

        # PERSONALIZAR AQUI: Nome dos arquivos específicos
        filename = f'[tema]_slide_{slide_num}.jpg'  # ← SUBSTITUA [tema]
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

    # PERSONALIZAR AQUI: Padrão de nome dos arquivos
    files = [f for f in os.listdir(image_dir)
             if f.startswith('[tema]_slide_') and f.endswith('.jpg')]  # ← SUBSTITUA [tema]

    if files:
        # PERSONALIZAR AQUI: Nome do tema
        print(f"📁 Imagens [TEMA] disponíveis ({len(files)}):")  # ← PERSONALIZAR
        for filename in sorted(files):
            filepath = os.path.join(image_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                print(f"   ✅ {filename} ({size//1024} KB)")
    else:
        print("❌ Nenhuma imagem temática encontrada")

if __name__ == "__main__":
    # PERSONALIZAR AQUI: Títulos e descrições
    print("🎨 BAIXADOR DE IMAGENS TEMÁTICAS - [SEU TEMA]")  # ← PERSONALIZAR
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
        # PERSONALIZAR AQUI: Nome do arquivo gerador
        print("Execute: python3 generate_[tema]_modelo_principal.py")  # ← PERSONALIZAR
        print("As imagens temáticas serão usadas automaticamente!")
    else:
        print()
        print("⚠️ Se falhou, verifique sua conexão e tente novamente")