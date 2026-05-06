#!/usr/bin/env python3
"""
Gera 9 vídeos individuais para carrossel de vídeos no Instagram.
Cada vídeo = slide estático (header + texto + footer) + foto animada na área visual + narração.
"""
import os
import json
import numpy as np
from PIL import Image
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, VideoClip
)

BASE_DIR = os.path.dirname(__file__)
PROJECT_DIR = os.path.dirname(BASE_DIR)
SLIDES_DIR = os.path.join(PROJECT_DIR, "assets", "generated_carousels")
PHOTOS_DIR = os.path.join(PROJECT_DIR, "assets", "slide_images")
AUDIO_DIR = os.path.join(BASE_DIR, "public", "audio")
OUTPUT_DIR = os.path.join(BASE_DIR, "out")

# Dimensões do carrossel
WIDTH = 1080
HEIGHT = 1440
VISUAL_START_Y = 936  # Onde começa a área da foto
VISUAL_HEIGHT = 360   # Altura padrão da área da foto
FPS = 30

# Slide 5 tem área visual maior (crop_top)
SPECIAL_SLIDES = {
    5: {"visual_height": int(360 * 1.45), "visual_start_y": 1440 - int(360 * 1.45) - (1440 - 144 - 792 - 360)}
}


def create_animated_photo_clip(photo_path, area_width, area_height, duration):
    """Cria um clip da foto com pan/zoom suave dentro da área visual."""
    photo = Image.open(photo_path).convert("RGB")
    photo_w, photo_h = photo.size

    # Escalar foto para cobrir a área com margem para animação
    scale_base = max(area_width / photo_w, area_height / photo_h) * 1.2
    scaled_w = int(photo_w * scale_base)
    scaled_h = int(photo_h * scale_base)
    photo_scaled = photo.resize((scaled_w, scaled_h), Image.LANCZOS)
    photo_array = np.array(photo_scaled)

    # Margem disponível para pan
    margin_x = scaled_w - area_width
    margin_y = scaled_h - area_height

    def make_frame(t):
        progress = t / duration if duration > 0 else 0

        # Zoom sutil: 1.0 → 1.08
        zoom = 1.0 + 0.08 * progress

        # Pan suave
        pan_x = int(margin_x * 0.3 * progress)
        pan_y = int(margin_y * 0.2 * progress)

        # Aplicar zoom
        zoomed_w = int(scaled_w * zoom)
        zoomed_h = int(scaled_h * zoom)

        zoomed = np.array(
            Image.fromarray(photo_array).resize((zoomed_w, zoomed_h), Image.LANCZOS)
        )

        # Crop centralizado + pan
        cx = (zoomed_w - area_width) // 2 + pan_x
        cy = (zoomed_h - area_height) // 2 + pan_y

        # Clamp
        cx = max(0, min(cx, zoomed_w - area_width))
        cy = max(0, min(cy, zoomed_h - area_height))

        return zoomed[cy:cy + area_height, cx:cx + area_width]

    return VideoClip(make_frame, duration=duration).set_fps(FPS)


def generate_slide_video(slide_num):
    """Gera um vídeo para um slide específico."""
    slide_path = os.path.join(SLIDES_DIR, f"curiosidades_tech_slide_0{slide_num}.png")
    photo_path = os.path.join(PHOTOS_DIR, f"curiosidades_tech_slide_{slide_num}.jpg")
    audio_path = os.path.join(AUDIO_DIR, f"slide_{slide_num}.mp3")
    output_path = os.path.join(OUTPUT_DIR, f"curiosidades_tech_video_0{slide_num}.mp4")

    print(f"🎬 Slide {slide_num}/9...")

    # Carregar áudio e pegar duração
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Pegar área visual para este slide
    if slide_num in SPECIAL_SLIDES:
        visual_start_y = SPECIAL_SLIDES[slide_num]["visual_start_y"]
        visual_height = SPECIAL_SLIDES[slide_num]["visual_height"]
    else:
        visual_start_y = VISUAL_START_Y
        visual_height = VISUAL_HEIGHT

    # 1. Slide estático como base (header + texto + footer)
    slide_img = Image.open(slide_path).convert("RGB")
    slide_array = np.array(slide_img)

    # Criar máscara: apagar a área visual (vai ser substituída pela foto animada)
    static_array = slide_array.copy()
    # Não apaga — vamos sobrepor a foto animada na posição certa

    static_clip = ImageClip(static_array).set_duration(duration)

    # 2. Foto animada na área visual
    photo_clip = create_animated_photo_clip(
        photo_path, WIDTH, visual_height, duration
    ).set_position((0, visual_start_y))

    # 3. Compor: foto animada embaixo, slide estático em cima
    # Mas precisamos que a parte estática cubra tudo EXCETO a área visual
    # Solução: colocar foto animada primeiro, depois sobrepor as partes estáticas

    # Recortar partes estáticas (acima e abaixo da área visual)
    top_part = static_array[:visual_start_y, :, :]
    bottom_start = visual_start_y + visual_height
    bottom_part = static_array[bottom_start:, :, :]

    top_clip = ImageClip(top_part).set_duration(duration).set_position((0, 0))
    bottom_clip = ImageClip(bottom_part).set_duration(duration).set_position((0, bottom_start))

    # Compor: fundo preto → foto animada → partes estáticas
    video = CompositeVideoClip(
        [
            ImageClip(np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)).set_duration(duration),
            photo_clip,
            top_clip,
            bottom_clip,
        ],
        size=(WIDTH, HEIGHT)
    ).set_audio(audio)

    # Renderizar
    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="medium",
        bitrate="5000k",
        logger="bar"
    )

    video.close()
    audio.close()

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"   ✅ {output_path} ({size_mb:.1f} MB)")


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("🎥 GERANDO CARROSSEL DE VÍDEOS — 9 vídeos individuais")
    print(f"   📐 Formato: {WIDTH}x{HEIGHT} (carrossel Instagram)")
    print(f"   🎵 Narração: Edge TTS pt-BR")
    print(f"   🎞️ Animação: pan/zoom na área da foto")
    print("=" * 60)

    for i in range(1, 10):
        generate_slide_video(i)

    print("\n🎉 TODOS OS 9 VÍDEOS GERADOS!")
    print(f"📁 Pasta: {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
