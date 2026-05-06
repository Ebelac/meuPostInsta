import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from "remotion";

export const SlideVideo: React.FC<{ slideNumber: number }> = ({
  slideNumber,
}) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // --- Animação da foto ---

  // Zoom suave (entra em 1.05 e vai pra 1.15 ao longo do vídeo)
  const scale = interpolate(frame, [0, durationInFrames], [1.05, 1.15], {
    extrapolateRight: "clamp",
  });

  // Pan lento horizontal (cada slide alterna direção)
  const panDirection = slideNumber % 2 === 0 ? 1 : -1;
  const panX = interpolate(
    frame,
    [0, durationInFrames],
    [0, 30 * panDirection],
    { extrapolateRight: "clamp" }
  );

  // Pan vertical sutil
  const panY = interpolate(frame, [0, durationInFrames], [0, -15], {
    extrapolateRight: "clamp",
  });

  // Fade in inicial
  const fadeIn = interpolate(frame, [0, 20], [0, 1], {
    extrapolateRight: "clamp",
  });

  // Fade out final
  const fadeOut = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Foto animada fullscreen */}
      <AbsoluteFill
        style={{
          opacity,
          overflow: "hidden",
        }}
      >
        <Img
          src={staticFile(`images/photo_${slideNumber}.jpg`)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale}) translate(${panX}px, ${panY}px)`,
          }}
        />
      </AbsoluteFill>

      {/* Áudio narração */}
      <Audio src={staticFile(`audio/slide_${slideNumber}.mp3`)} />
    </AbsoluteFill>
  );
};
