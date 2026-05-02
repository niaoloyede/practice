import { useState } from "react";
import { Link } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

function DemoBasic() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>1. initial / animate / transition</CardTitle>
        <CardDescription>
          Declarative state on mount.{" "}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">transition</code>{" "}
          controls duration and easing.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <motion.div
          className="lab-box lab-box--accent"
          initial={{ opacity: 0, scale: 0.85, y: 16 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ type: "spring", stiffness: 380, damping: 24 }}
        />
      </CardContent>
    </Card>
  );
}

function DemoGestures() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>2. whileHover / whileTap</CardTitle>
        <CardDescription>
          Motion reacts to pointer without manual listeners. Try hover and press.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button
          asChild
          className="h-auto rounded-xl border-0 bg-linear-to-br from-violet-600 to-violet-900 px-5 py-3 text-[15px] font-semibold text-white shadow-md hover:from-violet-600 hover:to-violet-900"
        >
          <motion.button
            type="button"
            whileHover={{ scale: 1.04, boxShadow: "0 8px 24px rgba(124, 58, 237, 0.35)" }}
            whileTap={{ scale: 0.96 }}
            transition={{ type: "spring", stiffness: 400, damping: 22 }}
          >
            Hover &amp; tap me
          </motion.button>
        </Button>
      </CardContent>
    </Card>
  );
}

const listVariants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -12 },
  show: { opacity: 1, x: 0 },
};

function DemoVariants() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>3. variants + staggerChildren</CardTitle>
        <CardDescription>
          Parent drives child states with named{" "}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">variants</code>{" "}
          and orchestrated delays.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <motion.ul
          className="m-0 flex list-none flex-col gap-2 p-0"
          variants={listVariants}
          initial="hidden"
          animate="show"
        >
          {["Alpha", "Bravo", "Charlie"].map((label) => (
            <motion.li key={label} variants={itemVariants} className="list-none">
              <Card className="border-border/80 py-0">
                <CardContent className="py-3 text-sm font-semibold">{label}</CardContent>
              </Card>
            </motion.li>
          ))}
        </motion.ul>
      </CardContent>
    </Card>
  );
}

function DemoPresence() {
  const [open, setOpen] = useState(true);

  return (
    <Card>
      <CardHeader>
        <CardTitle>4. AnimatePresence</CardTitle>
        <CardDescription>
          Wrap conditionally rendered{" "}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">motion.*</code> so
          exit animations run before removal.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button type="button" onClick={() => setOpen((v) => !v)}>
          {open ? "Hide panel" : "Show panel"}
        </Button>
        <div className="fm-presence-slot">
          <AnimatePresence mode="wait">
            {open && (
              <motion.div
                key="panel"
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.26, ease: [0.22, 1, 0.36, 1] }}
              >
                <Card>
                  <CardContent className="pt-6">
                    <p className="m-0 text-sm text-muted-foreground leading-relaxed">
                      This block animates in and out. Toggle to see{" "}
                      <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">
                        exit
                      </code>
                      .
                    </p>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}

function DemoLayout() {
  const [wide, setWide] = useState(false);

  return (
    <Card>
      <CardHeader>
        <CardTitle>5. layout (size spring)</CardTitle>
        <CardDescription>
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">layout</code>{" "}
          smooths layout-driven changes — here the pill width springs open and closed.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Button type="button" variant="secondary" onClick={() => setWide((w) => !w)}>
          Toggle width
        </Button>
        <div className="fm-layout-track">
          <motion.div
            layout
            className="fm-layout-pill"
            animate={{ width: wide ? 220 : 96 }}
            transition={{ type: "spring", stiffness: 320, damping: 28 }}
          >
            <motion.span layout className="fm-layout-pill__label">
              {wide ? "Wide" : "Narrow"}
            </motion.span>
          </motion.div>
        </div>
      </CardContent>
    </Card>
  );
}

/** Shared element crossfade — layoutId morph between trees */
function DemoSharedLayoutId() {
  const [slot, setSlot] = useState<"a" | "b">("a");

  return (
    <Card>
      <CardHeader>
        <CardTitle>6. Shared layout morph (layoutId)</CardTitle>
        <CardDescription>
          The same <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">layoutId</code>{" "}
          in two branches lets Motion interpolate position/size like magic glue.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <button
            type="button"
            onClick={() => setSlot("a")}
            className="relative flex min-h-[112px] flex-col rounded-xl border border-border bg-muted/20 p-4 text-left transition-colors hover:bg-muted/40"
          >
            <span className="text-[0.65rem] font-medium uppercase tracking-wide text-muted-foreground">
              Column A
            </span>
            {slot === "a" && (
              <motion.div
                layoutId="fm-demo-pod"
                className="mt-3 size-14 rounded-2xl bg-primary shadow-lg"
                transition={{ type: "spring", stiffness: 420, damping: 28 }}
              />
            )}
          </button>
          <button
            type="button"
            onClick={() => setSlot("b")}
            className="relative flex min-h-[112px] flex-col rounded-xl border border-border bg-muted/20 p-4 text-left transition-colors hover:bg-muted/40"
          >
            <span className="text-[0.65rem] font-medium uppercase tracking-wide text-muted-foreground">
              Column B
            </span>
            {slot === "b" && (
              <motion.div
                layoutId="fm-demo-pod"
                className="mt-3 size-14 rounded-2xl bg-primary shadow-lg"
                transition={{ type: "spring", stiffness: 420, damping: 28 }}
              />
            )}
          </button>
        </div>
        <Button type="button" variant="secondary" onClick={() => setSlot((s) => (s === "a" ? "b" : "a"))}>
          Swap column
        </Button>
      </CardContent>
    </Card>
  );
}

/** Drag with rubber-band edges */
function DemoDragElastic() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>7. Drag + elastic constraints</CardTitle>
        <CardDescription>
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">drag</code> with{" "}
          <code className="rounded bg-muted px-1 py-0.5 font-mono text-[0.65rem]">dragElastic</code>{" "}
          feels tactile — release to spring back inside the dashed arena.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative h-52 overflow-hidden rounded-xl border border-dashed border-primary/35 bg-muted/25">
          <motion.div
            drag
            dragConstraints={{ left: -80, right: 80, top: -48, bottom: 48 }}
            dragElastic={0.32}
            whileHover={{ scale: 1.04 }}
            whileTap={{ scale: 1.12, cursor: "grabbing" }}
            className="absolute left-1/2 top-1/2 size-16 -translate-x-1/2 -translate-y-1/2 cursor-grab rounded-2xl bg-linear-to-br from-pink-500 to-orange-400 shadow-[0_12px_30px_rgba(244,63,94,0.35)]"
          />
        </div>
      </CardContent>
    </Card>
  );
}

/** Scrollport reveal — declarative intersection */
function DemoInView() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>8. whileInView (scroll reveal)</CardTitle>
        <CardDescription>
          Motion watches visibility for you — great for marketing sections without reaching for
          ScrollTrigger.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="max-h-64 space-y-3 overflow-y-auto rounded-lg border border-border bg-muted/15 p-3 pr-2">
          {["Aurora", "Nebula", "Comet", "Pulsar"].map((label, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 28, rotate: -1.5, filter: "blur(6px)" }}
              whileInView={{ opacity: 1, y: 0, rotate: 0, filter: "blur(0px)" }}
              viewport={{ once: true, amount: 0.55 }}
              transition={{
                type: "spring",
                stiffness: 380,
                damping: 26,
                delay: i * 0.05,
              }}
              className="rounded-lg border border-border/80 bg-card px-4 py-3 text-sm font-medium shadow-sm"
            >
              {label} — springs in once when it crosses the inner scroller.
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function FramerMotionTestPage() {
  return (
    <div className="mx-auto max-w-3xl space-y-6 px-5 py-8">
      <Card>
        <CardHeader className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div className="space-y-1">
            <CardTitle className="text-xl font-semibold tracking-tight">
              Framer Motion test lab
            </CardTitle>
            <CardDescription className="max-w-prose text-sm leading-relaxed">
              Small declarative examples: springs, gestures, variants, exit animations, and layout.
            </CardDescription>
          </div>
          <div className="fm-header-links shrink-0">
            <Button variant="link" className="h-auto p-0" asChild>
              <Link to="/">← Photo</Link>
            </Button>
            <Button variant="link" className="h-auto p-0" asChild>
              <Link to="/gsap-tests">GSAP tests →</Link>
            </Button>
          </div>
        </CardHeader>
      </Card>

      <DemoBasic />
      <DemoGestures />
      <DemoVariants />
      <DemoPresence />
      <DemoLayout />
      <DemoSharedLayoutId />
      <DemoDragElastic />
      <DemoInView />
    </div>
  );
}
