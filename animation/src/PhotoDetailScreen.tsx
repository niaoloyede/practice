import { useRef, useState } from "react";
import { Link } from "react-router-dom";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

gsap.registerPlugin(useGSAP);

const ASSET = (name: string) => `/photo-inspiration/${name}`;

const SIMILAR = [
  "similar-1.png",
  "similar-2.png",
  "similar-3.png",
  "similar-4.png",
  "similar-5.png",
] as const;

export function PhotoDetailScreen() {
  const rootRef = useRef<HTMLDivElement>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const heartBgImgRef = useRef<HTMLImageElement>(null);
  const [liked, setLiked] = useState(false);

  useGSAP(
    () => {
      if (!contentRef.current) return;
      gsap.from(contentRef.current, {
        y: 28,
        opacity: 0,
        duration: 0.55,
        ease: "power3.out",
        delay: 0.12,
      });
    },
    { scope: rootRef }
  );

  const toggleHeart = () => {
    setLiked((v) => !v);
    const bgImg = heartBgImgRef.current;
    if (!bgImg) return;

    gsap.killTweensOf(bgImg);
    gsap.set(bgImg, { transformOrigin: "50% 50%" });

    const tl = gsap.timeline();
    tl.to(bgImg, {
      scale: 1.28,
      filter: "brightness(1.2)",
      duration: 0.16,
      ease: "power2.out",
    }).to(bgImg, {
      scale: 1,
      filter: "brightness(1)",
      duration: 0.52,
      ease: "elastic.out(1, 0.35)",
    });
  };

  return (
    <div
      ref={rootRef}
      className="pd-frame font-['Oxygen',ui-sans-serif,system-ui,sans-serif]"
      data-node-id="24012:739"
      data-name="Image"
    >
      <div className="pd-body">
        <div className="pd-gallery">
          <div className="pd-gallery__media" aria-hidden>
            <div className="pd-gallery__placeholder" />
            <img className="pd-gallery__img" src={ASSET("hero.png")} alt="" />
            <div className="pd-gallery__gradient" />
          </div>
        </div>

        <div ref={contentRef} className="pd-content">
          <Card className="border-0 bg-transparent py-0 shadow-none ring-0">
            <CardHeader className="gap-1 p-0 px-4">
              <CardTitle className="text-2xl font-bold leading-snug tracking-tight text-black">
                Lady, side profile
              </CardTitle>
              <CardDescription className="text-sm font-bold text-[#36947d]">
                Leslie Alexander
              </CardDescription>
            </CardHeader>
            <CardContent className="px-4 pt-0">
              <p className="pd-desc m-0 text-sm leading-normal text-foreground/75">
                Amet minim mollit non deserunt ullamco est sit aliqua dolor do amet sint.
              </p>
            </CardContent>
          </Card>

          <div className="pd-rule-wrap">
            <img className="pd-rule" src={ASSET("rule.svg")} alt="" />
          </div>

          <section className="pd-similar" aria-labelledby="similar-heading">
            <h2 id="similar-heading" className="pd-similar__heading">
              Similar photos
            </h2>
            <div className="pd-similar__strip">
              {SIMILAR.map((file) => (
                <div key={file} className="pd-thumb">
                  <img src={ASSET(file)} alt="" />
                </div>
              ))}
            </div>
          </section>

          <Card className="border-dashed border-border/60 bg-muted/20 py-3 shadow-none">
            <CardContent className="flex flex-wrap items-center justify-between gap-2 px-4 py-0">
              <Button variant="link" className="h-auto p-0 text-sm" asChild>
                <Link to="/motion-tests">Motion tests</Link>
              </Button>
              <Button variant="link" className="h-auto p-0 text-sm" asChild>
                <Link to="/gsap-tests">GSAP tests</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      <div className="pd-controls">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="pd-icon-shell relative size-8 shrink-0 rounded-full border-0 bg-transparent shadow-none hover:bg-transparent focus-visible:ring-0"
          aria-label="Back"
        >
          <span className="pd-icon-shell__bg" aria-hidden>
            <img src={ASSET("bg.svg")} alt="" />
          </span>
          <span className="pd-icon-shell__glyph" aria-hidden>
            <img src={ASSET("chevron.svg")} alt="" />
          </span>
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="icon"
          className={cn(
            "pd-icon-shell relative size-8 shrink-0 rounded-full border-0 bg-transparent shadow-none hover:bg-transparent focus-visible:ring-0",
            liked && "pd-icon-shell--liked"
          )}
          aria-label={liked ? "Unlike" : "Like"}
          aria-pressed={liked}
          onClick={toggleHeart}
        >
          <span className="pd-icon-shell__bg" aria-hidden>
            <img
              ref={heartBgImgRef}
              className="pd-icon-shell__bg-img--heart"
              src={ASSET("bg.svg")}
              alt=""
            />
          </span>
          <span className="pd-icon-shell__glyph pd-icon-shell__glyph--heart" aria-hidden>
            <img src={ASSET("heart.svg")} alt="" />
          </span>
        </Button>
      </div>
    </div>
  );
}
