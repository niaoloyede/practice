import { lazy, Suspense } from "react";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { PhotoDetailScreen } from "./PhotoDetailScreen";

const FramerMotionTestPage = lazy(() =>
  import("./pages/FramerMotionTestPage").then((module) => ({
    default: module.FramerMotionTestPage,
  }))
);
const GsapTestPage = lazy(() =>
  import("./pages/GsapTestPage").then((module) => ({
    default: module.GsapTestPage,
  }))
);

function RouteLoader() {
  return (
    <div className="flex min-h-[calc(100dvh-3.5rem)] items-center justify-center px-4 py-8 text-sm text-muted-foreground">
      Loading demo...
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Card className="rounded-none border-x-0 border-t-0 py-0 shadow-sm">
        <CardContent className="flex flex-wrap items-center justify-center gap-1 py-3">
          <Button variant="ghost" size="sm" asChild>
            <Link to="/">Photo detail</Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/gsap-tests">GSAP tests</Link>
          </Button>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/motion-tests">Motion tests</Link>
          </Button>
        </CardContent>
      </Card>
      <Suspense fallback={<RouteLoader />}>
        <Routes>
          <Route
            path="/"
            element={
              <div className="flex min-h-[calc(100dvh-3.5rem)] items-start justify-center px-4 py-8">
                <PhotoDetailScreen />
              </div>
            }
          />
          <Route path="/gsap-tests" element={<GsapTestPage />} />
          <Route path="/motion-tests" element={<FramerMotionTestPage />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
