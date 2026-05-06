#!/usr/bin/env python3
"""
Script para configurar perfil - baixa uma foto de exemplo se não houver
"""
import os
import requests
from PIL import Image, ImageDraw, ImageFont

def setup_profile():
    """Configura perfil com foto de exemplo"""

    profile_dir = "assets/profile"
    os.makedirs(profile_dir, exist_ok=True)

    # Verificar se já existe foto
    photo_path = os.path.join(profile_dir, "profile_photo.jpg")

    if not os.path.exists(photo_path):
        print("📷 Criando foto de perfil de exemplo...")

        try:
            # Criar foto de perfil simples
            img = Image.new('RGB', (200, 200), color='#1DA1F2')
            draw = ImageDraw.Draw(img)

            # Tentar usar fonte do sistema
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
            except:
                font = ImageFont.load_default()

            # Desenhar iniciais
            draw.text((100, 100), "CD", font=font, fill='white', anchor='mm')

            # Salvar
            img.save(photo_path, "JPEG", quality=95)
            print(f"✅ Foto de perfil criada: {photo_path}")

        except Exception as e:
            print(f"❌ Erro ao criar foto: {e}")
    else:
        print(f"✅ Foto de perfil já existe: {photo_path}")

    print(f"""
📁 PASTA DO PERFIL: {os.path.abspath(profile_dir)}

🖼️ PARA USAR SUA FOTO REAL:
1. Substitua o arquivo: {photo_path}
2. Use uma imagem quadrada (200x200px ou maior)
3. Formatos aceitos: .jpg, .png, .jpeg

✅ SÍMBOLO VERIFICADO:
   • Já implementado automaticamente (azul padrão)
   • Para customizar: coloque 'verified_badge.png' na pasta profile/

🔄 DEPOIS DE TROCAR SUA FOTO, RODE:
   python3 generate_single_carousel.py
""")

if __name__ == "__main__":
    setup_profile()