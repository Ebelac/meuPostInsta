import React from "react";
import {
  AbsoluteFill,
  Img,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
  random,
} from "remotion";
import {
  TransitionSeries,
  linearTiming,
} from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { BRAND } from "./brandConfig";

// ─── Paleta ───
const C = {
  bg: "#030303",
  red: "#E5173F",
  redDim: "rgba(229,23,63,0.6)",
  redGlow: "rgba(229,23,63,0.25)",
  white: "#F0F0F0",
  gray: "rgba(240,240,240,0.5)",
  faint: "rgba(240,240,240,0.15)",
};

// ─── Slides ───
const SLIDES = [
  {
    tag: "MANIFESTO",
    headline: "22 pontos.\n33 milhoes\nde views.",
    body: "A empresa que trabalha com o Pentagono e a CIA publicou um manifesto no X. Ninguem esperava o que estava escrito ali dentro.",
    source: BRAND.handle,
  },
  {
    tag: "PONTO 1",
    headline: "O Vale do\nSilicio deve\nao pais.",
    body: "Segundo a Palantir, as big techs tem uma divida moral com os EUA. Devem trabalhar pela defesa nacional. Nao so vender anuncios.",
    source: "The Technological Republic",
  },
  {
    tag: "PONTO 5",
    headline: "Quem aperta\no botao\nprimeiro?",
    body: "Armas com inteligencia artificial vao existir querendo ou nao. A unica pergunta e quem vai construir primeiro. Quem ficar de fora nao escolhe as regras.",
    source: "Palantir Manifesto, X",
  },
  {
    tag: "PONTO 6",
    headline: "Todo mundo\ndeveria ir\npra guerra.",
    body: "A Palantir quer a volta do alistamento obrigatorio nos EUA. A logica: se o filho de todo mundo pode morrer, as guerras diminuem.",
    source: "Palantir Manifesto, X",
  },
  {
    tag: "PONTO 2",
    headline: "Seu celular\ne uma\nprisao.",
    body: "A propria empresa de tecnologia diz que estamos presos numa tirania dos apps. O iPhone e mesmo a maior conquista da humanidade?",
    source: "Palantir Manifesto, X",
  },
  {
    tag: "PONTOS 21-22",
    headline: "Nem toda\ncultura\nmerece\nrespeito.",
    body: "Esse foi o ponto que incendiou tudo. O manifesto diz que algumas culturas sao regressivas e que o pluralismo pode ser vazio e oco.",
    source: "Palantir Manifesto, X",
  },
  {
    tag: "REACOES",
    headline: "Chamaram\nde tecno-\nfascismo.",
    body: "Filosofos, economistas e politicos reagiram. Um disse que e ameaca a humanidade. Outra comparou ao discurso de um supervilao de filme.",
    source: "Coeckelbergh, Varoufakis",
  },
  {
    tag: "MERCADO",
    headline: "Wall Street\nnem piscou.",
    body: "A acao caiu 0,34% no dia. Subiu 4% no seguinte. A receita cresceu 70% no trimestre. Pro mercado, contratos de defesa valem mais que polemica.",
    source: "Bloomberg, Yahoo Finance",
  },
  {
    tag: "VOCE DECIDE",
    headline: "Lideranca\nde pensamento\nou ameaca?",
    body: "Uma empresa de vigilancia e IA militar quer ditar os rumos da civilizacao. Isso te assusta ou te convence?",
    source: BRAND.handle,
    cta: true,
  },
];

const SLIDE_DURATION = 300;
const TRANSITION_DURATION = 18;
const FONT = "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif";
const MONO = "'SF Mono', 'Courier New', monospace";

// ─────────────────────────────────────────
// IMAGEM FULLSCREEN COM PARALLAX 3D
// ─────────────────────────────────────────
const FullscreenImage: React.FC<{
  slideIndex: number;
  frame: number;
  durationInFrames: number;
}> = ({ slideIndex, frame, durationInFrames }) => {
  // Reveal: escala de 1.4 → 1.05 (slam in)
  const entryProgress = interpolate(frame, [0, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.exp),
  });
  const entryScale = interpolate(entryProgress, [0, 1], [1.5, 1.05], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Drift lento contínuo
  const driftScale = interpolate(frame, [25, durationInFrames], [1.05, 1.18], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = frame < 25 ? entryScale : driftScale;

  // Parallax 3D: perspectiva + rotação sutil
  const rotY = interpolate(
    frame,
    [0, durationInFrames],
    [slideIndex % 2 === 0 ? -1.5 : 1.5, slideIndex % 2 === 0 ? 1.5 : -1.5],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const translateZ = interpolate(frame, [0, durationInFrames], [0, -30], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Opacity
  const imgOpacity = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        bottom: 300,
        left: 0,
        right: 0,
        height: "42%",
        overflow: "hidden",
        perspective: 1200,
        opacity: imgOpacity,
      }}
    >
      <Img
        src={staticFile(`palantir/slide_${slideIndex + 1}.jpg`)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) rotateY(${rotY}deg) translateZ(${translateZ}px)`,
          filter: "saturate(0.5) brightness(0.7) contrast(1.15)",
          willChange: "transform",
        }}
      />
      {/* Gradiente: funde com o preto do topo */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: "45%",
          background: `linear-gradient(to bottom, ${C.bg} 0%, transparent 100%)`,
        }}
      />
      {/* Gradiente embaixo pro footer */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: "35%",
          background: `linear-gradient(to top, rgba(3,3,3,0.7) 0%, transparent 100%)`,
        }}
      />
      {/* Tint vermelho sutil */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 50% 50%, rgba(229,23,63,0.06) 0%, transparent 70%)`,
        }}
      />
    </div>
  );
};

// ─────────────────────────────────────────
// HEADLINE — mask reveal + 3D perspective
// ─────────────────────────────────────────
const Headline: React.FC<{
  lines: string[];
  frame: number;
  fps: number;
}> = ({ lines, frame, fps }) => {
  return (
    <div style={{ perspective: 800 }}>
      {lines.map((line, li) => {
        const delay = 5 + li * 4;

        // Clip mask reveal (text "prints" left to right)
        const clipReveal = interpolate(frame, [delay, delay + 14], [0, 100], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });

        // 3D tilt in
        const rotX = interpolate(frame, [delay, delay + 18], [12, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });
        const opacity = interpolate(frame, [delay, delay + 8], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const y = interpolate(frame, [delay, delay + 14], [25, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });

        return (
          <div
            key={li}
            style={{
              fontFamily: FONT,
              fontSize: 98,
              fontWeight: 900,
              color: C.white,
              lineHeight: 0.95,
              letterSpacing: "-0.04em",
              clipPath: `inset(0 ${100 - clipReveal}% 0 0)`,
              opacity,
              transform: `rotateX(${rotX}deg) translateY(${y}px)`,
              transformOrigin: "left bottom",
              willChange: "transform, opacity, clip-path",
            }}
          >
            {line}
          </div>
        );
      })}
    </div>
  );
};

// ─────────────────────────────────────────
// BODY — word-by-word com blur resolve
// ─────────────────────────────────────────
const BodyText: React.FC<{
  text: string;
  frame: number;
  fps: number;
  startFrame: number;
}> = ({ text, frame, fps, startFrame }) => {
  const words = text.split(" ");

  return (
    <div
      style={{
        fontFamily: FONT,
        fontSize: 54,
        color: C.gray,
        lineHeight: 1.5,
        fontWeight: 400,
        letterSpacing: "-0.01em",
      }}
    >
      {words.map((word, wi) => {
        const wordDelay = startFrame + wi * 1.5;
        const progress = interpolate(frame, [wordDelay, wordDelay + 10], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });
        const wordOpacity = interpolate(progress, [0, 0.5], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const blur = interpolate(progress, [0, 1], [12, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const y = interpolate(progress, [0, 1], [8, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <span
            key={wi}
            style={{
              display: "inline-block",
              opacity: wordOpacity,
              filter: `blur(${blur}px)`,
              transform: `translateY(${y}px)`,
              marginRight: "0.28em",
              willChange: "transform, opacity, filter",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

// ─────────────────────────────────────────
// GLITCH v2 — chromatic aberration + slice displacement
// ─────────────────────────────────────────
const ChromaGlitch: React.FC<{
  frame: number;
  seed: string;
  children: React.ReactNode;
}> = ({ frame, seed, children }) => {
  // Glitch em 3 momentos
  const g =
    (frame >= 2 && frame <= 4) ||
    (frame >= 60 && frame <= 62) ||
    (frame >= 160 && frame <= 162);
  if (!g) return <>{children}</>;

  const ox = (random(`${seed}-${frame}-x`) - 0.5) * 20;
  const oy = (random(`${seed}-${frame}-y`) - 0.5) * 8;

  // Horizontal slice displacement
  const sliceY = random(`${seed}-${frame}-sy`) * 80 + 10;
  const sliceH = random(`${seed}-${frame}-sh`) * 40 + 10;
  const sliceOx = (random(`${seed}-${frame}-sox`) - 0.5) * 40;

  return (
    <div style={{ position: "relative" }}>
      {/* Red channel */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${ox}px, ${oy}px)`,
          opacity: 0.6,
          mixBlendMode: "screen",
        }}
      >
        <div style={{ color: "#FF0040" }}>{children}</div>
      </div>
      {/* Cyan channel */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${-ox * 0.6}px, ${-oy * 0.6}px)`,
          opacity: 0.4,
          mixBlendMode: "screen",
        }}
      >
        <div style={{ color: "#00FFCC" }}>{children}</div>
      </div>
      {/* Main */}
      <div style={{ position: "relative" }}>{children}</div>
      {/* Slice displacement */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: `${sliceY}%`,
          height: sliceH,
          overflow: "hidden",
          transform: `translateX(${sliceOx}px)`,
          opacity: 0.7,
        }}
      >
        {children}
      </div>
    </div>
  );
};

// ─────────────────────────────────────────
// SLIDE
// ─────────────────────────────────────────
const ManifestoSlide: React.FC<{ slideIndex: number }> = ({ slideIndex }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const s = SLIDES[slideIndex];
  const headlineLines = s.headline.split("\n");

  // Progress
  const progress = interpolate(frame, [0, durationInFrames], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Footer entry
  const footerEntry = spring({
    fps,
    frame: frame - 15,
    config: { damping: 40, mass: 0.5 },
  });

  // Tag
  const tagReveal = interpolate(frame, [2, 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // Red accent
  const accentW = interpolate(frame, [14, 35], [0, 140], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.exp),
  });

  // Vignette breathing
  const breathe = interpolate(
    frame % 90,
    [0, 45, 90],
    [0.06, 0.12, 0.06],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // Grain
  const grainSeed = Math.floor(frame / 2);

  // Body start frame
  const bodyStart = 20 + headlineLines.length * 4;

  return (
    <AbsoluteFill style={{ backgroundColor: C.bg }}>
      {/* ── IMAGEM FULLSCREEN ── */}
      <FullscreenImage
        slideIndex={slideIndex}
        frame={frame}
        durationInFrames={durationInFrames}
      />

      {/* ── Top safe zone fill ── */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          height: 250,
          backgroundColor: C.bg,
          zIndex: 10,
        }}
      />

      {/* ── Noise texture overlay ── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.035,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 512 512' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' seed='${grainSeed}' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundSize: "512px 512px",
          pointerEvents: "none",
          zIndex: 30,
          mixBlendMode: "overlay",
        }}
      />

      {/* ── Scan lines (mais finos, mais sutis) ── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.06,
          background:
            "repeating-linear-gradient(0deg, transparent 0px, transparent 3px, rgba(255,255,255,0.03) 3px, rgba(255,255,255,0.03) 4px)",
          pointerEvents: "none",
          zIndex: 28,
        }}
      />

      {/* ── TAG ── */}
      <div
        style={{
          position: "absolute",
          top: 280,
          left: 70,
          display: "flex",
          alignItems: "center",
          gap: 14,
        }}
      >
        {/* Dot com ring animado */}
        <div style={{ position: "relative", width: 14, height: 14 }}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              borderRadius: "50%",
              backgroundColor: C.red,
              opacity: Math.floor(frame / 15) % 2 === 0 ? 1 : 0.2,
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: -4,
              borderRadius: "50%",
              border: `1.5px solid ${C.red}`,
              opacity: interpolate(
                frame % 30,
                [0, 15, 30],
                [0.8, 0.2, 0.8],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
              ),
            }}
          />
        </div>
        <div
          style={{
            fontFamily: MONO,
            fontSize: 30,
            fontWeight: 700,
            color: C.red,
            letterSpacing: "0.3em",
            textTransform: "uppercase",
            clipPath: `inset(0 ${(1 - tagReveal) * 100}% 0 0)`,
          }}
        >
          {s.tag}
        </div>
      </div>

      {/* ── HEADLINE ── */}
      <ChromaGlitch frame={frame} seed={`h-${slideIndex}`}>
        <div
          style={{
            position: "absolute",
            top: 340,
            left: 70,
            right: 50,
          }}
        >
          <Headline lines={headlineLines} frame={frame} fps={fps} />
        </div>
      </ChromaGlitch>

      {/* ── Red accent ── */}
      <div
        style={{
          position: "absolute",
          top: 348 + headlineLines.length * 94,
          left: 70,
          height: 5,
          width: accentW,
          background: `linear-gradient(90deg, ${C.red} 0%, transparent 100%)`,
          borderRadius: 3,
          boxShadow: `0 0 20px ${C.redGlow}, 0 0 60px ${C.redGlow}`,
          opacity: interpolate(frame, [12, 18], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />

      {/* ── BODY ── */}
      <div
        style={{
          position: "absolute",
          top: 348 + headlineLines.length * 94 + 30,
          left: 70,
          right: 70,
        }}
      >
        <BodyText
          text={s.body}
          frame={frame}
          fps={fps}
          startFrame={bodyStart}
        />
      </div>

      {/* ── FOOTER ── */}
      <div
        style={{
          position: "absolute",
          bottom: 300,
          left: 0,
          right: 0,
          height: 200,
          padding: "0 60px",
          background: `linear-gradient(to top, rgba(3,3,3,0.95) 0%, rgba(3,3,3,0.8) 60%, rgba(3,3,3,0.4) 85%, transparent 100%)`,
          opacity: footerEntry,
          transform: `translateY(${interpolate(footerEntry, [0, 1], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
          zIndex: 15,
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          paddingBottom: 20,
        }}
      >
        {/* Linha: profile (esquerda) + source+counter (direita) */}
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            justifyContent: "space-between",
          }}
        >
          {/* Profile */}
          <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
            <Img
              src={staticFile("palantir/profile.png")}
              style={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                objectFit: "cover",
                border: `3px solid rgba(240,240,240,0.25)`,
              }}
            />
            <div style={{ fontFamily: FONT, fontSize: 36, color: C.white, fontWeight: 600, opacity: 0.85 }}>
              {BRAND.handle}
            </div>
          </div>

          {/* Source + Counter empilhados, alinhados à direita */}
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 8 }}>
            <div
              style={{
                fontFamily: MONO,
                fontSize: 22,
                color: C.white,
                letterSpacing: "0.03em",
                textAlign: "right",
                opacity: interpolate(frame, [50, 70], [0, 0.6], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              Fonte: {s.source}
            </div>
            <div style={{ fontFamily: MONO, fontSize: 36, letterSpacing: "0.08em" }}>
              <span style={{ color: C.red, fontWeight: 700 }}>
                {String(slideIndex + 1).padStart(2, "0")}
              </span>
              <span style={{ color: C.white, opacity: 0.7 }}>{" "}/ 09</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── CTA ── */}
      {s.cta && (
        <div
          style={{
            position: "absolute",
            bottom: 430,
            left: 70,
          }}
        >
          <div
            style={{
              fontFamily: FONT,
              fontSize: 38,
              fontWeight: 700,
              color: C.red,
              opacity: interpolate(frame, [200, 225], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
              transform: `translateY(${interpolate(frame, [200, 225], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
              textShadow: `0 0 30px ${C.redGlow}`,
              letterSpacing: "-0.02em",
            }}
          >
            Siga {BRAND.handle}
          </div>
        </div>
      )}

      {/* ── Progress line ── */}
      <div
        style={{
          position: "absolute",
          bottom: 300,
          left: 0,
          height: 3,
          width: `${progress}%`,
          background: `linear-gradient(90deg, ${C.red} 0%, ${C.redDim} 100%)`,
          boxShadow: `0 0 12px ${C.redGlow}`,
          zIndex: 20,
        }}
      />

      {/* ── Bottom safe zone fill ── */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 300,
          backgroundColor: C.bg,
          zIndex: 10,
        }}
      />

      {/* ── Vignette breathing ── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          boxShadow: `inset 0 0 200px rgba(229,23,63,${breathe})`,
          pointerEvents: "none",
          zIndex: 18,
        }}
      />
    </AbsoluteFill>
  );
};

// ─── Composição ───
export const PalantirManifesto: React.FC = () => {
  return (
    <TransitionSeries>
      {SLIDES.map((_, i) => (
        <React.Fragment key={i}>
          <TransitionSeries.Sequence durationInFrames={SLIDE_DURATION}>
            <ManifestoSlide slideIndex={i} />
          </TransitionSeries.Sequence>
          {i < SLIDES.length - 1 && (
            <TransitionSeries.Transition
              timing={linearTiming({ durationInFrames: TRANSITION_DURATION })}
              presentation={fade()}
            />
          )}
        </React.Fragment>
      ))}
    </TransitionSeries>
  );
};
