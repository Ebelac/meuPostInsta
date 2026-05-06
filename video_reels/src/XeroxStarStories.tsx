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
  springTiming,
} from "@remotion/transitions";
import { slide } from "@remotion/transitions/slide";
import { BRAND } from "./brandConfig";

// ─── Dados ───
const SLIDES = [
  {
    hook: "1981",
    headline: "A maquina que\ninventou o futuro",
    body: "A Xerox apresentou ao mundo o computador mais avancado que ja existiu. Mouse, interface grafica, pastas, icones, e-mail, impressora a laser. Tudo que voce usa hoje nasceu nessa maquina.",
    source: BRAND.handle,
  },
  {
    hook: "XEROX PARC",
    headline: "O laboratorio\nlendario",
    body: "Palo Alto, California. Os engenheiros mais brilhantes do mundo reunidos num laboratorio. Eles nao melhoraram o computador. Eles reinventaram como humanos interagem com maquinas.",
    source: "Computer History Museum",
  },
  {
    hook: "ANTES",
    headline: "Tela preta.\nTexto verde.",
    body: "Voce digitava comandos e torcia pra nao errar. O Xerox Star trouxe janelas, icones, menus e um dispositivo apontador chamado mouse. Voce clicava nas coisas. Arrastava arquivos. Era magia.",
    source: "Xerox Star Wikipedia",
  },
  {
    hook: "$16,500",
    headline: "O erro\nfatal",
    body: "Corrigindo pela inflacao, sao mais de 55 mil dolares hoje. Vendido so pra empresas. Nenhuma pessoa comum podia comprar. O marketing era pessimo. A Xerox nao entendia o que tinha nas maos.",
    source: "History of Information",
  },
  {
    hook: "1979",
    headline: "Steve Jobs\nvisitou o PARC",
    body: "Ele viu o mouse, a interface grafica e as janelas. Ficou maluco. Disse que era a coisa mais incrivel que ja tinha visto. Voltou pra Apple e mandou o time copiar tudo. Em 1984, nasceu o Macintosh.",
    source: "Computer History Museum",
  },
  {
    hook: "QUOTE",
    headline: '"Nos dois roubamos\nda Xerox."',
    body: "Bill Gates lancou o Windows em 1985. Jobs acusou Gates de roubar a ideia. A resposta de Gates e a frase mais honesta da historia da tecnologia.",
    source: "Walter Isaacson",
  },
  {
    hook: "TRILHOES",
    headline: "A Xerox perdeu.\nApple e Microsoft\nganharam.",
    body: "A Xerox continuou vendendo impressoras. Enquanto isso, duas empresas construiram imperios de trilhoes de dolares usando ideias que nasceram dentro do laboratorio da Xerox.",
    source: "Microsoft History, CHM",
  },
  {
    hook: "LEGADO",
    headline: "Voce usa\nisso todo dia",
    body: "Toda vez que voce clica num icone, arrasta um arquivo, usa um mouse ou toca numa tela. Ideia de 1981. O Xerox Star original esta no Smithsonian. Uma maquina que mudou tudo e que quase ninguem conhece.",
    source: "Smithsonian",
  },
  {
    hook: "MORAL",
    headline: "Inventar nao\ne suficiente",
    body: "A Xerox inventou o mouse, a interface grafica, as janelas e o e-mail comercial. A Apple e a Microsoft ficaram com o credito e com o dinheiro. Voce precisa saber vender o futuro tambem.",
    source: BRAND.handle,
    cta: true,
  },
];

const SLIDE_DURATION = 300;
const TRANSITION_DURATION = 20;

// ─── Glitch effect helper ───
const Glitch: React.FC<{
  frame: number;
  seed: string;
  children: React.ReactNode;
}> = ({ frame, seed, children }) => {
  // Glitch em momentos específicos (frames 5-8, 45-47)
  const isGlitching =
    (frame >= 3 && frame <= 6) || (frame >= 50 && frame <= 52);

  if (!isGlitching) return <>{children}</>;

  const offsetX = (random(`${seed}-x-${frame}`) - 0.5) * 12;
  const offsetY = (random(`${seed}-y-${frame}`) - 0.5) * 4;
  const skewX = (random(`${seed}-sk-${frame}`) - 0.5) * 3;

  return (
    <div style={{ position: "relative" }}>
      {/* Camada red offset */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${offsetX}px, ${offsetY}px) skewX(${skewX}deg)`,
          color: "rgba(255,0,0,0.4)",
          mixBlendMode: "screen",
        }}
      >
        {children}
      </div>
      {/* Camada cyan offset */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${-offsetX}px, ${-offsetY}px) skewX(${-skewX}deg)`,
          color: "rgba(0,255,255,0.4)",
          mixBlendMode: "screen",
        }}
      >
        {children}
      </div>
      {/* Camada principal */}
      <div style={{ position: "relative" }}>{children}</div>
    </div>
  );
};

// ─── Scan lines overlay ───
const ScanLines: React.FC<{ opacity: number }> = ({ opacity }) => {
  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        opacity,
        pointerEvents: "none",
        background:
          "repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.08) 3px, rgba(0,0,0,0.08) 4px)",
        zIndex: 20,
      }}
    />
  );
};

// ─── Word-by-word reveal ───
const WordReveal: React.FC<{
  text: string;
  frame: number;
  fps: number;
  startFrame: number;
  fontSize: number;
  color: string;
  fontWeight?: number;
  lineHeight?: number;
}> = ({
  text,
  frame,
  fps,
  startFrame,
  fontSize,
  color,
  fontWeight = 400,
  lineHeight = 1.5,
}) => {
  const words = text.split(" ");
  const FRAMES_PER_WORD = 2; // cada palavra aparece a cada 2 frames

  return (
    <div
      style={{
        fontSize,
        fontFamily: "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif",
        color,
        fontWeight,
        lineHeight,
        letterSpacing: "-0.02em",
      }}
    >
      {words.map((word, wi) => {
        const wordDelay = startFrame + wi * FRAMES_PER_WORD;
        const wordSpring = spring({
          fps,
          frame: frame - wordDelay,
          config: { damping: 30, mass: 0.3, stiffness: 300 },
        });
        const wordOpacity = interpolate(wordSpring, [0, 0.6], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const wordY = interpolate(wordSpring, [0, 1], [18, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <span
            key={wi}
            style={{
              display: "inline-block",
              opacity: wordOpacity,
              transform: `translateY(${wordY}px)`,
              marginRight: "0.3em",
              willChange: "transform, opacity",
            }}
          >
            {word}
          </span>
        );
      })}
    </div>
  );
};

// ─── Slide individual ───
const StorySlide: React.FC<{ slideIndex: number }> = ({ slideIndex }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const s = SLIDES[slideIndex];

  // ── Imagem: clip-path reveal + parallax ──
  const imgReveal = spring({
    fps,
    frame: frame - 5,
    config: { damping: 50, mass: 0.8, stiffness: 100 },
  });
  const clipRight = interpolate(imgReveal, [0, 1], [100, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const imgScale = interpolate(frame, [0, durationInFrames], [1.15, 1.3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const imgY = interpolate(frame, [0, durationInFrames], [0, -40], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const imgX = interpolate(
    frame,
    [0, durationInFrames],
    [slideIndex % 2 === 0 ? -10 : 10, slideIndex % 2 === 0 ? 20 : -20],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  // ── Hook number/label: entra grande e encolhe ──
  const hookScale = spring({
    fps,
    frame: frame - 2,
    config: { damping: 25, mass: 0.5, stiffness: 200 },
  });
  const hookScaleVal = interpolate(hookScale, [0, 1], [3, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const hookOpacity = interpolate(hookScale, [0, 0.3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ── Headline: cada linha com stagger ──
  const headlineLines = s.headline.split("\n");

  // ── Progress ring ──
  const progressAngle = interpolate(frame, [0, durationInFrames], [0, 360], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // ── Profile entry ──
  const profileSpring = spring({
    fps,
    frame: frame - 15,
    config: { damping: 40, mass: 0.4 },
  });

  // ── Grain noise (sutil) ──
  const grainSeed = Math.floor(frame / 2);

  return (
    <AbsoluteFill style={{ backgroundColor: "#0A0A0A", overflow: "hidden" }}>
      {/* ── Imagem com clip-path reveal ── */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: "48%",
          overflow: "hidden",
          clipPath: `inset(0 ${clipRight}% 0 0)`,
        }}
      >
        <Img
          src={staticFile(`xerox_star/slide_${slideIndex + 1}.jpg`)}
          style={{
            width: "120%",
            height: "120%",
            objectFit: "cover",
            marginLeft: "-10%",
            marginTop: "-10%",
            transform: `scale(${imgScale}) translate(${imgX}px, ${imgY}px)`,
            willChange: "transform",
            filter: "contrast(1.1) brightness(0.85)",
          }}
        />
        {/* Gradiente escuro no topo da imagem */}
        <div
          style={{
            position: "absolute",
            top: 0,
            left: 0,
            right: 0,
            height: "40%",
            background:
              "linear-gradient(to bottom, #0A0A0A 0%, rgba(10,10,10,0.7) 50%, transparent 100%)",
          }}
        />
        {/* Gradiente escuro embaixo */}
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: 0,
            right: 0,
            height: "30%",
            background:
              "linear-gradient(to top, rgba(10,10,10,0.6) 0%, transparent 100%)",
          }}
        />
      </div>

      {/* ── Scan lines ── */}
      <ScanLines opacity={0.15} />

      {/* ── Hook (numero/label grande) ── */}
      <Glitch frame={frame} seed={`hook-${slideIndex}`}>
        <div
          style={{
            position: "absolute",
            top: 80,
            left: 70,
            fontFamily:
              "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif",
            fontSize: 28,
            fontWeight: 900,
            color: "#1DA1F2",
            letterSpacing: "0.3em",
            textTransform: "uppercase",
            opacity: hookOpacity,
            transform: `scale(${hookScaleVal})`,
            transformOrigin: "left center",
            willChange: "transform",
          }}
        >
          {s.hook}
        </div>
      </Glitch>

      {/* ── Headline com stagger por linha ── */}
      <div
        style={{
          position: "absolute",
          top: 130,
          left: 70,
          right: 70,
        }}
      >
        {headlineLines.map((line, li) => {
          const lineDelay = 8 + li * 6;
          const lineSpring = spring({
            fps,
            frame: frame - lineDelay,
            config: { damping: 30, mass: 0.5, stiffness: 180 },
          });
          const lineOpacity = interpolate(lineSpring, [0, 0.4], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const lineX = interpolate(lineSpring, [0, 1], [80, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          return (
            <div
              key={li}
              style={{
                fontFamily:
                  "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif",
                fontSize: 72,
                fontWeight: 900,
                color: "#FFFFFF",
                lineHeight: 1.05,
                letterSpacing: "-0.03em",
                opacity: lineOpacity,
                transform: `translateX(${lineX}px)`,
                willChange: "transform, opacity",
              }}
            >
              {line}
            </div>
          );
        })}

        {/* ── Accent bar abaixo do headline ── */}
        <div
          style={{
            marginTop: 20,
            height: 5,
            backgroundColor: "#1DA1F2",
            borderRadius: 3,
            width: interpolate(frame, [20, 45], [0, 180], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            }),
            opacity: interpolate(frame, [18, 25], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        />
      </div>

      {/* ── Body text: word-by-word reveal ── */}
      <div
        style={{
          position: "absolute",
          top: headlineLines.length <= 2 ? 390 : 440,
          left: 70,
          right: 70,
          bottom: "50%",
        }}
      >
        <WordReveal
          text={s.body}
          frame={frame}
          fps={fps}
          startFrame={30}
          fontSize={38}
          color="rgba(255,255,255,0.85)"
          fontWeight={400}
          lineHeight={1.55}
        />
      </div>

      {/* ── Profile badge (canto inferior) ── */}
      <div
        style={{
          position: "absolute",
          bottom: 25,
          left: 70,
          display: "flex",
          alignItems: "center",
          gap: 14,
          opacity: profileSpring,
          transform: `translateY(${interpolate(profileSpring, [0, 1], [20, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
        }}
      >
        <Img
          src={staticFile("xerox_star/profile.png")}
          style={{
            width: 48,
            height: 48,
            borderRadius: "50%",
            objectFit: "cover",
            border: "2px solid rgba(255,255,255,0.3)",
          }}
        />
        <div
          style={{
            fontFamily:
              "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif",
            fontSize: 24,
            color: "rgba(255,255,255,0.6)",
            fontWeight: 500,
          }}
        >
          {BRAND.handle}
        </div>
      </div>

      {/* ── Slide counter + progress ring ── */}
      <div
        style={{
          position: "absolute",
          bottom: 30,
          right: 70,
          width: 60,
          height: 60,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {/* Progress ring SVG */}
        <svg
          width={60}
          height={60}
          style={{ position: "absolute", transform: "rotate(-90deg)" }}
        >
          <circle
            cx={30}
            cy={30}
            r={26}
            fill="none"
            stroke="rgba(255,255,255,0.1)"
            strokeWidth={3}
          />
          <circle
            cx={30}
            cy={30}
            r={26}
            fill="none"
            stroke="#1DA1F2"
            strokeWidth={3}
            strokeDasharray={2 * Math.PI * 26}
            strokeDashoffset={
              2 * Math.PI * 26 * (1 - progressAngle / 360)
            }
            strokeLinecap="round"
          />
        </svg>
        <div
          style={{
            fontFamily:
              "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif",
            fontSize: 20,
            fontWeight: 700,
            color: "#FFFFFF",
          }}
        >
          {slideIndex + 1}
        </div>
      </div>

      {/* ── Fonte (sutil) ── */}
      <div
        style={{
          position: "absolute",
          bottom: 85,
          right: 70,
          fontFamily:
            "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif",
          fontSize: 18,
          color: "rgba(255,255,255,0.25)",
          fontWeight: 400,
          textAlign: "right",
          opacity: interpolate(frame, [60, 80], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        {s.source}
      </div>

      {/* ── CTA especial no último slide ── */}
      {s.cta && (
        <div
          style={{
            position: "absolute",
            bottom: 100,
            left: 70,
            right: 70,
          }}
        >
          <div
            style={{
              fontFamily:
                "'SF Pro Display', 'Helvetica Neue', Helvetica, sans-serif",
              fontSize: 32,
              fontWeight: 700,
              color: "#1DA1F2",
              opacity: interpolate(frame, [180, 210], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
              transform: `translateY(${interpolate(frame, [180, 210], [15, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
            }}
          >
            Siga {BRAND.handle}
          </div>
        </div>
      )}

      {/* ── Film grain overlay ── */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          opacity: 0.04,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' seed='${grainSeed}' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundSize: "256px 256px",
          pointerEvents: "none",
          zIndex: 25,
        }}
      />
    </AbsoluteFill>
  );
};

// ─── Composição principal ───
export const XeroxStarStories: React.FC = () => {
  return (
    <TransitionSeries>
      {SLIDES.map((_, i) => (
        <React.Fragment key={i}>
          <TransitionSeries.Sequence durationInFrames={SLIDE_DURATION}>
            <StorySlide slideIndex={i} />
          </TransitionSeries.Sequence>
          {i < SLIDES.length - 1 && (
            <TransitionSeries.Transition
              timing={springTiming({
                config: { damping: 200 },
                durationInFrames: TRANSITION_DURATION,
                durationRestThreshold: 0.001,
              })}
              presentation={slide({ direction: "from-right" })}
            />
          )}
        </React.Fragment>
      ))}
    </TransitionSeries>
  );
};
