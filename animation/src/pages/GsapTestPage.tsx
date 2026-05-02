import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import gsap from "gsap";
import { MotionPathPlugin } from "gsap/MotionPathPlugin";
import ScrollTrigger from "gsap/ScrollTrigger";
import { useGSAP } from "@gsap/react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

gsap.registerPlugin(useGSAP, ScrollTrigger, MotionPathPlugin);

function DemoClickBox() {
  const boxRef = useRef<HTMLDivElement>(null);

  const nudge = () => {
    const el = boxRef.current;
    if (!el) return;
    gsap.killTweensOf(el);
    gsap.fromTo(
      el,
      { x: 0, rotation: 0 },
      {
        x: 120,
        rotation: 360,
        duration: 0.7,
        ease: "power2.inOut",
        yoyo: true,
        repeat: 1,
      }
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>1. Click → gsap.to / fromTo</CardTitle>
        <CardDescription>
          One-off tweens on a ref. Uses{" "}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">fromTo</code> so
          each click starts from the same baseline.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button type="button" onClick={nudge}>
          Run tween
        </Button>
        <div ref={boxRef} className="lab-box lab-box--accent" />
      </CardContent>
    </Card>
  );
}

function DemoStaggerEnter() {
  const scope = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      if (!scope.current) return;
      const cards = scope.current.querySelectorAll(".lab-card");
      gsap.from(cards, {
        opacity: 0,
        y: 28,
        scale: 0.96,
        stagger: 0.1,
        duration: 0.55,
        ease: "power3.out",
      });
    },
    { scope }
  );

  return (
    <div ref={scope}>
      <Card>
        <CardHeader>
          <CardTitle>2. useGSAP + stagger</CardTitle>
          <CardDescription>
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">useGSAP</code>{" "}
            with <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">scope</code>{" "}
            reverts child tweens on cleanup (Strict Mode safe). Cards animate in on mount.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="lab-cards">
            {[1, 2, 3].map((n) => (
              <div key={n} className="lab-card lab-box">
                {n}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

function DemoTimeline() {
  const aRef = useRef<HTMLDivElement>(null);
  const bRef = useRef<HTMLDivElement>(null);
  const cRef = useRef<HTMLDivElement>(null);

  const play = () => {
    const a = aRef.current;
    const b = bRef.current;
    const c = cRef.current;
    if (!a || !b || !c) return;
    gsap.killTweensOf([a, b, c]);
    gsap.set([a, b, c], { clearProps: "all" });

    const tl = gsap.timeline();
    tl.to(a, { x: 100, backgroundColor: "#7c3aed", duration: 0.35, ease: "power2.out" })
      .to(b, { y: 48, borderRadius: "50%", duration: 0.4, ease: "back.out(1.4)" }, "-=0.1")
      .to(c, { rotation: 180, scale: 1.15, duration: 0.45, ease: "elastic.out(1, 0.5)" });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>3. Timeline</CardTitle>
        <CardDescription>
          Chained tweens with offsets. Purple shift → middle morphs → right spins/scales.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button type="button" onClick={play}>
          Play timeline
        </Button>
        <div className="lab-timeline-row">
          <div ref={aRef} className="lab-box lab-box--sm" />
          <div ref={bRef} className="lab-box lab-box--sm lab-box--mid" />
          <div ref={cRef} className="lab-box lab-box--sm" />
        </div>
      </CardContent>
    </Card>
  );
}

function DemoElasticReset() {
  const ballRef = useRef<HTMLDivElement>(null);

  const punch = () => {
    const el = ballRef.current;
    if (!el) return;
    gsap.killTweensOf(el);
    gsap.set(el, { transformOrigin: "50% 50%" });
    const tl = gsap.timeline();
    tl.to(el, { x: 120, duration: 0.35, ease: "power3.out" })
      .to(el, { scale: 1.28, duration: 0.12, ease: "power2.out" }, "-=0.08")
      .to(el, { scale: 1, duration: 0.18, ease: "bounce.out" })
      .to(el, { x: 0, duration: 0.55, ease: "elastic.out(1, 0.4)" });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>4. Timeline: slide + punch + return</CardTitle>
        <CardDescription>
          One{" "}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">timeline()</code>{" "}
          chains X motion, a scale bump, and an elastic slide home.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button type="button" onClick={punch}>
          Punch + slide
        </Button>
        <div className="lab-track">
          <div ref={ballRef} className="lab-ball" />
        </div>
      </CardContent>
    </Card>
  );
}

/** ScrollTrigger scrub — progress tied to scroll (GSAP-only superpower) */
function DemoScrollScrub() {
  const scope = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const scroller = scope.current?.querySelector("[data-scroller]");
      const fill = scope.current?.querySelector("[data-fill]");
      const track = scope.current?.querySelector("[data-track]");
      if (!(scroller instanceof HTMLElement) || !(fill instanceof HTMLElement) || !(track instanceof HTMLElement))
        return;

      gsap.set(fill, { scaleX: 0, transformOrigin: "left center" });
      const tween = gsap.to(fill, {
        scaleX: 1,
        ease: "none",
        scrollTrigger: {
          scroller,
          trigger: track,
          start: "top top",
          end: "bottom bottom",
          scrub: 0.35,
        },
      });

      return () => {
        tween.scrollTrigger?.kill();
        tween.kill();
      };
    },
    { scope }
  );

  return (
    <div ref={scope}>
      <Card>
        <CardHeader>
          <CardTitle>5. ScrollTrigger scrub</CardTitle>
          <CardDescription>
            Tie animation progress to scroll with{" "}
            <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">scrub</code>.
            Scroll inside the box — the bar is the timeline.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div
            data-scroller
            className="relative h-52 overflow-y-auto rounded-lg border border-border bg-muted/40"
          >
            <div
              className="sticky top-0 z-10 border-b border-border bg-card/95 px-3 py-2 backdrop-blur-sm"
            >
              <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                <div
                  data-fill
                  className="h-full w-full rounded-full bg-primary"
                />
              </div>
              <p className="mt-1.5 text-[0.65rem] text-muted-foreground">Scrub value follows scroll</p>
            </div>
            <div data-track className="min-h-[520px] space-y-3 px-4 py-4">
              {Array.from({ length: 14 }, (_, i) => (
                <p key={i} className="text-xs text-muted-foreground leading-relaxed">
                  Lorem scroll fuel {i + 1} — keep going to max out the bar.
                </p>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/** MotionPathPlugin — orbit an SVG dot along a path forever */
function DemoMotionPath() {
  const dotRef = useRef<SVGCircleElement>(null);

  useGSAP(() => {
    const dot = dotRef.current;
    if (!dot) return;

    const tween = gsap.to(dot, {
      duration: 3.2,
      repeat: -1,
      ease: "none",
      motionPath: {
        path: "#gsap-demo-motion-path",
        align: "#gsap-demo-motion-path",
        alignOrigin: [0.5, 0.5],
        autoRotate: true,
      },
    });

    return () => tween.kill();
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>6. MotionPath + autoRotate</CardTitle>
        <CardDescription>
          Free{" "}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">MotionPathPlugin</code>{" "}
          makes UI feel “alive” — great for loaders, badges, and playful accents.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mx-auto max-w-xs rounded-xl border border-border bg-muted/30 p-4">
          <svg viewBox="0 0 240 140" className="h-36 w-full text-muted-foreground" aria-hidden>
            <path
              id="gsap-demo-motion-path"
              d="M20,70 C60,10 120,10 160,70 S220,130 220,70"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeDasharray="6 6"
            />
            <circle
              ref={dotRef}
              r={7}
              className="fill-primary drop-shadow-[0_0_10px_rgba(124,58,237,0.9)]"
            />
          </svg>
        </div>
      </CardContent>
    </Card>
  );
}

/** Radial burst — random stagger + physics-y eases */
function DemoBurst() {
  const rootRef = useRef<HTMLDivElement>(null);

  const burst = () => {
    const root = rootRef.current;
    if (!root) return;
    const dots = root.querySelectorAll<HTMLElement>(".gs-burst-dot");
    gsap.killTweensOf(dots);
    gsap.set(dots, { clearProps: "transform,opacity" });

    gsap.fromTo(
      dots,
      { x: 0, y: 0, opacity: 1, scale: 1, rotation: 0 },
      {
        x: (i) => Math.cos((i / dots.length) * Math.PI * 2) * (72 + Math.random() * 56),
        y: (i) => Math.sin((i / dots.length) * Math.PI * 2) * (72 + Math.random() * 56),
        rotation: () => gsap.utils.random(-220, 220),
        opacity: 0,
        scale: 0,
        duration: () => 0.55 + Math.random() * 0.35,
        ease: "power4.out",
        stagger: { amount: 0.18, from: "center" },
      }
    );
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>7. Staggered “firework” burst</CardTitle>
        <CardDescription>
          Function-based randomness + radial offsets + stagger — click again to replay from center.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button type="button" onClick={burst}>
          Burst
        </Button>
        <div
          ref={rootRef}
          className="relative flex h-44 items-center justify-center overflow-hidden rounded-lg border border-border bg-linear-to-b from-violet-950/25 to-background"
        >
          {Array.from({ length: 14 }).map((_, i) => (
            <div
              key={i}
              className="gs-burst-dot pointer-events-none absolute left-1/2 top-1/2 size-2.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-linear-to-br from-amber-300 to-orange-500 shadow-sm"
            />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/** 3D flip — perspective + rotationY */
function DemoFlip3d() {
  const wrapRef = useRef<HTMLDivElement>(null);
  const [flipped, setFlipped] = useState(false);

  const flip = () => {
    const el = wrapRef.current;
    if (!el) return;
    const next = !flipped;
    setFlipped(next);
    gsap.to(el, {
      rotationY: next ? 180 : 0,
      duration: 0.85,
      ease: "power2.inOut",
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>8. 3D card flip</CardTitle>
        <CardDescription>
          Parent <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">perspective</code>{" "}
          + <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">rotationY</code> for a
          hinge-style flip (front/back content swap).
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button type="button" variant="secondary" onClick={flip}>
          Flip card
        </Button>
        <div className="mx-auto perspective-[900px]">
          <div
            ref={wrapRef}
            className="transform-3d relative h-36 w-full max-w-sm rounded-xl border border-border bg-card shadow-md"
          >
            <div className="backface-hidden absolute inset-0 flex flex-col items-center justify-center gap-1 rounded-xl bg-linear-to-br from-cyan-500/20 to-primary/25 p-4">
              <span className="text-sm font-semibold">Front</span>
              <span className="text-xs text-muted-foreground">GSAP drives the hinge</span>
            </div>
            <div className="backface-hidden absolute inset-0 flex flex-col items-center justify-center gap-1 rounded-xl bg-linear-to-br from-fuchsia-600/90 to-violet-800 p-4 text-primary-foreground transform-[rotateY(180deg)]">
              <span className="text-sm font-semibold">Back</span>
              <span className="text-xs opacity-90">Surprise panel</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export function GsapTestPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 px-5 py-8">
      <Card>
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1">
            <CardTitle className="text-xl font-semibold tracking-tight">GSAP test lab</CardTitle>
            <CardDescription className="max-w-prose text-sm leading-relaxed">
              Small patterns you can copy into real screens. Open DevTools → watch inline transforms
              update.
            </CardDescription>
          </div>
          <Button variant="link" className="h-auto shrink-0 self-start p-0" asChild>
            <Link to="/">← Photo screen</Link>
          </Button>
        </CardHeader>
      </Card>

      <DemoClickBox />
      <DemoStaggerEnter />
      <DemoTimeline />
      <DemoElasticReset />
      <DemoScrollScrub />
      <DemoMotionPath />
      <DemoBurst />
      <DemoFlip3d />
    </div>
  );
}
