#!/usr/bin/env python3
"""Gera narração com Edge TTS para cada slide do carrossel curiosidades_tech"""
import asyncio
import edge_tts
import os
import json

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "public", "audio")

# Texto de narração para cada slide (versão falada, sem formatação visual)
narrations = {
    1: "Você usa tecnologia todo dia e não sabe dessas 8 coisas. Tem ouro dentro do seu celular. Sua impressora te vigia. E a internet inteira pesa menos que uma fruta. A número 6 vai te dar calafrio.",
    2: "Toda a internet pesa 50 gramas. Isso é o peso de um morango. Um físico maluco resolveu pesar todos os elétrons que fazem a internet funcionar. O resultado? Tudo que você já viu, leu e assistiu online pesa menos que uma fruta na sua mão.",
    3: "O primeiro mouse do mundo era feito de madeira. Uma caixinha de madeira. Com duas rodinhas. Em 1963. Ninguém levou a sério. O inventor, Douglas Engelbart, ouviu que aquilo era inútil. Hoje não existe computador sem um.",
    4: "O Windows quase se chamou Interface Manager. Imagina ligar o computador e ver: Bem-vindo ao Interface Manager 11. Era esse o nome que Bill Gates queria. Mudaram de última hora. Uma decisão que ajudou a criar uma empresa de 3 trilhões de dólares.",
    5: "A primeira selfie tem 187 anos. Em 1839, Robert Cornelius ficou imóvel na frente de uma câmera por vários minutos. O resultado foi a primeira foto que alguém tirou de si mesmo. 180 anos antes do Instagram existir, o cara já era influencer.",
    6: "Sua impressora te espiona. Toda impressora colorida imprime pontinhos amarelos invisíveis em cada folha que sai. Esses pontos registram a data, a hora e o número de série da máquina. A olho nu você não vê nada. Mas está tudo ali, escondido no papel.",
    7: "O erro 404 veio de uma porta de verdade. O primeiro servidor da internet ficava na sala 404 do CERN, na Suíça. Quando alguém pedia algo que não existia, a resposta era: Room 404, not found. O erro mais visto do mundo nasceu de um número na porta.",
    8: "Tem ouro dentro do seu celular velho. Ouro, prata, paládio. Todo celular tem metais preciosos. Só nos Estados Unidos, mais de 60 milhões de dólares em ouro vão pro lixo todo ano dentro de celulares descartados. Antes de jogar o seu fora, pense duas vezes.",
    9: "A senha mais usada do mundo ainda é 123456. Milhões de pessoas usam. A segunda? password. Em pleno 2026. Se a sua é uma dessas duas, para tudo e muda agora. Qual fato mais te chocou? Comenta o número! Siga arroba calebe digital pra mais!",
}

VOICE = "pt-BR-AntonioNeural"  # Voz masculina brasileira natural

async def generate_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    durations = {}

    for slide_num, text in narrations.items():
        output_file = os.path.join(OUTPUT_DIR, f"slide_{slide_num}.mp3")
        print(f"🎙️ Gerando narração slide {slide_num}...")

        communicate = edge_tts.Communicate(text, VOICE, rate="-5%")
        await communicate.save(output_file)

        # Verificar duração com ffprobe se disponível
        size = os.path.getsize(output_file)
        print(f"   ✅ {output_file} ({size // 1024} KB)")

    # Salvar metadados
    meta_file = os.path.join(OUTPUT_DIR, "metadata.json")
    # Usar ffprobe para pegar durações
    for slide_num in narrations:
        mp3_path = os.path.join(OUTPUT_DIR, f"slide_{slide_num}.mp3")
        try:
            import subprocess
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", mp3_path],
                capture_output=True, text=True
            )
            info = json.loads(result.stdout)
            durations[slide_num] = float(info["format"]["duration"])
        except Exception:
            durations[slide_num] = 8.0  # fallback

    with open(meta_file, "w") as f:
        json.dump({"durations": {str(k): v for k, v in durations.items()}}, f, indent=2)

    print(f"\n📊 Durações: {durations}")
    total = sum(durations.values())
    print(f"⏱️ Duração total: {total:.1f}s")

if __name__ == "__main__":
    asyncio.run(generate_all())
