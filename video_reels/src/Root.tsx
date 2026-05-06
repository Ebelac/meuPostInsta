import React from "react";
import { Composition } from "remotion";
import { SlideVideo } from "./SlideVideo";
import { XeroxStarStories } from "./XeroxStarStories";
import { PalantirManifesto } from "./PalantirManifesto";

// Durações de cada slide em segundos (do Edge TTS)
const slideDurations = [16.848, 19.128, 21.72, 19.656, 20.304, 19.584, 21.84, 21.96, 27.0];
const FPS = 30;

// Xerox Star: 9 slides x 6s = 54s, minus overlapping transitions
const XEROX_SLIDES = 9;
const XEROX_SLIDE_DURATION = 300; // 10s per slide
const XEROX_TRANSITION = 30;
const XEROX_TOTAL_FRAMES =
  XEROX_SLIDES * XEROX_SLIDE_DURATION - (XEROX_SLIDES - 1) * XEROX_TRANSITION;

// Palantir: 9 slides x 10s, 18f transitions
const PALANTIR_SLIDES = 9;
const PALANTIR_SLIDE_DURATION = 300;
const PALANTIR_TRANSITION = 18;
const PALANTIR_TOTAL_FRAMES =
  PALANTIR_SLIDES * PALANTIR_SLIDE_DURATION -
  (PALANTIR_SLIDES - 1) * PALANTIR_TRANSITION;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {/* Palantir Manifesto - Tom Sombrio */}
      <Composition
        id="PalantirManifesto"
        component={PalantirManifesto}
        durationInFrames={PALANTIR_TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{}}
      />

      {/* Xerox Star Stories - Motion Graphics */}
      <Composition
        id="XeroxStarStories"
        component={XeroxStarStories}
        durationInFrames={XEROX_TOTAL_FRAMES}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{}}
      />

      {/* Slides individuais anteriores */}
      {slideDurations.map((duration, index) => {
        const slideNumber = index + 1;
        const durationInFrames = Math.ceil(duration * FPS);
        return (
          <Composition
            key={slideNumber}
            id={`Slide${slideNumber}`}
            component={SlideVideo}
            durationInFrames={durationInFrames}
            fps={FPS}
            width={1080}
            height={1440}
            defaultProps={{
              slideNumber,
            }}
          />
        );
      })}
    </>
  );
};
