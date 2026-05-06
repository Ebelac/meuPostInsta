#!/bin/bash
# Renderiza os 9 vídeos individuais do carrossel
cd "$(dirname "$0")"
mkdir -p out

for i in $(seq 1 9); do
  echo "🎬 Renderizando slide ${i}/9..."
  npx remotion render src/index.ts "Slide${i}" "out/curiosidades_tech_video_0${i}.mp4" --codec h264
  echo "✅ Slide ${i} concluído!"
  echo ""
done

echo "🎉 Todos os 9 vídeos renderizados em out/"
ls -lh out/curiosidades_tech_video_*.mp4
