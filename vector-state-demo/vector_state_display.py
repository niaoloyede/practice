from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass

import moderngl
import pygame


MODE_CONFIG = {
    "STARTUP": {"key": pygame.K_1, "label": "Startup"},
    "IDLE": {"key": pygame.K_2, "label": "Idle"},
    "TASK": {"key": pygame.K_3, "label": "Task"},
    "TELEOP": {"key": pygame.K_4, "label": "Teleop"},
    "ERROR_MINOR": {"key": pygame.K_5, "label": "Minor error"},
    "ERROR_MAJOR": {"key": pygame.K_6, "label": "Major error"},
    "PAUSED": {"key": pygame.K_7, "label": "Paused"},
    "SHUTDOWN": {"key": pygame.K_0, "label": "Shutdown"},
}


@dataclass(frozen=True)
class StateStyle:
    bg: tuple[float, float, float]
    fg: tuple[float, float, float]
    accent: tuple[float, float, float]
    speed: float
    intensity: float
    symbol: int


@dataclass(frozen=True)
class GLProfile:
    name: str
    major: int
    minor: int
    profile: int
    require: int
    version_line: str
    precision_line: str


STATE_STYLE = {
    "STARTUP": StateStyle((0.02, 0.03, 0.06), (0.86, 0.93, 1.0), (0.30, 0.82, 1.0), 0.75, 0.65, 0),
    "IDLE": StateStyle((0.00, 0.00, 0.00), (0.92, 0.96, 1.0), (0.42, 0.90, 0.76), 0.35, 0.28, 0),
    "TASK": StateStyle((0.02, 0.04, 0.08), (0.82, 0.93, 1.0), (0.18, 0.48, 1.0), 1.15, 0.80, 1),
    "TELEOP": StateStyle((0.00, 0.09, 0.18), (0.90, 0.98, 1.0), (0.22, 0.77, 1.0), 1.00, 0.70, 2),
    "ERROR_MINOR": StateStyle((0.06, 0.04, 0.00), (1.00, 0.92, 0.35), (1.00, 0.68, 0.16), 1.50, 0.90, 3),
    "ERROR_MAJOR": StateStyle((0.68, 0.00, 0.00), (0.02, 0.00, 0.00), (1.00, 0.92, 0.92), 2.40, 1.00, 3),
    "PAUSED": StateStyle((0.01, 0.01, 0.015), (0.65, 0.70, 0.78), (0.48, 0.54, 0.64), 0.18, 0.18, 4),
    "SHUTDOWN": StateStyle((0.00, 0.00, 0.00), (0.45, 0.48, 0.54), (0.30, 0.34, 0.40), 0.22, 0.25, 5),
}


VERTEX_SHADER_TEMPLATE = """#version __VERSION_LINE__
in vec2 in_pos;
out vec2 v_uv;

void main() {
    v_uv = in_pos * 0.5 + 0.5;
    gl_Position = vec4(in_pos, 0.0, 1.0);
}
"""


FRAGMENT_SHADER_TEMPLATE = """#version __VERSION_LINE__
__PRECISION_LINE__

uniform vec2 resolution;
uniform float time;
uniform vec3 bg_color;
uniform vec3 fg_color;
uniform vec3 accent_color;
uniform float speed;
uniform float intensity;
uniform int symbol;

in vec2 v_uv;
out vec4 fragColor;

float circle(vec2 p, float r) {
    return length(p) - r;
}

float ring(vec2 p, float r, float w) {
    return abs(length(p) - r) - w;
}

float box_sdf(vec2 p, vec2 b) {
    vec2 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
}

float triangle_sdf(vec2 p) {
    const float k = 1.7320508;
    p.x = abs(p.x) - 0.42;
    p.y = p.y + 0.22;
    if (p.x + k * p.y > 0.0) {
        p = vec2(p.x - k * p.y, -k * p.x - p.y) / 2.0;
    }
    p.x -= clamp(p.x, -0.84, 0.0);
    return -length(p) * sign(p.y);
}

float stroke(float d, float width) {
    return 1.0 - smoothstep(width, width + 0.008, abs(d));
}

float fill(float d) {
    return 1.0 - smoothstep(0.0, 0.008, d);
}

mat2 rot(float a) {
    float s = sin(a);
    float c = cos(a);
    return mat2(c, -s, s, c);
}

void main() {
    vec2 uv = v_uv;
    vec2 p = (uv - 0.5) * vec2(resolution.x / resolution.y, 1.0);
    float t = time * speed;
    float breathe = 0.5 + 0.5 * sin(t * 6.28318);

    vec3 color = bg_color;

    // Soft radial glow shared by all states.
    float glow = exp(-dot(p, p) * (4.0 - intensity * 1.6));
    color += accent_color * glow * (0.12 + 0.18 * intensity * breathe);

    if (symbol == 0) {
        // Breathing orb + orbit ring.
        float orb = fill(circle(p, 0.12 + 0.035 * intensity * breathe));
        float outer = stroke(ring(p, 0.28 + 0.025 * breathe, 0.010), 0.010);
        vec2 q = rot(t * 2.0) * p;
        float comet = fill(circle(q - vec2(0.28, 0.0), 0.026));
        color = mix(color, fg_color, orb);
        color = mix(color, accent_color, max(outer * 0.8, comet));
    } else if (symbol == 1) {
        // Task flow: sliding bars plus center core.
        float core = fill(circle(p, 0.095 + 0.012 * breathe));
        color = mix(color, fg_color, core);
        for (int i = 0; i < 5; i++) {
            float fi = float(i);
            vec2 q = p;
            q.x += 0.65 - mod(t * 0.55 + fi * 0.22, 1.3);
            q.y += (fi - 2.0) * 0.055;
            float bar = fill(box_sdf(q, vec2(0.13, 0.010 + 0.004 * intensity)));
            color = mix(color, accent_color, bar * (0.45 + 0.1 * fi));
        }
    } else if (symbol == 2) {
        // Teleop: directional crosshair and rotating sweep.
        float cross = stroke(box_sdf(p, vec2(0.012, 0.28)), 0.010);
        cross = max(cross, stroke(box_sdf(p, vec2(0.28, 0.012)), 0.010));
        vec2 q = rot(t * 2.4) * p;
        float sweep = fill(box_sdf(q - vec2(0.16, 0.0), vec2(0.16, 0.012)));
        float center = fill(circle(p, 0.055));
        color = mix(color, fg_color, max(cross * 0.45, center));
        color = mix(color, accent_color, sweep * 0.8);
    } else if (symbol == 3) {
        // Warning / critical: triangle, ping ring, flashing core.
        float tri = stroke(triangle_sdf(p), 0.018);
        float ping = stroke(ring(p, 0.22 + 0.12 * breathe, 0.012), 0.008);
        float flash = smoothstep(0.35, 1.0, breathe) * intensity;
        color = mix(color, fg_color, tri);
        color = mix(color, accent_color, max(ping, flash * fill(circle(p, 0.045))));
    } else if (symbol == 4) {
        // Paused: two calm bars.
        float left_bar = fill(box_sdf(p - vec2(-0.06, 0.0), vec2(0.026, 0.14)));
        float right_bar = fill(box_sdf(p - vec2(0.06, 0.0), vec2(0.026, 0.14)));
        float halo = stroke(ring(p, 0.22, 0.010), 0.006);
        color = mix(color, fg_color, max(left_bar, right_bar));
        color = mix(color, accent_color, halo * (0.25 + 0.25 * breathe));
    } else {
        // Shutdown: shrinking dot and dim ring.
        float dot = fill(circle(p, 0.08 - 0.025 * breathe));
        float dim = stroke(ring(p, 0.18, 0.010), 0.006) * (0.25 + 0.25 * (1.0 - breathe));
        color = mix(color, fg_color, dot);
        color = mix(color, accent_color, dim);
    }

    fragColor = vec4(color, 1.0);
}
"""


DESKTOP_PROFILE = GLProfile(
    name="desktop OpenGL 3.3",
    major=3,
    minor=3,
    profile=pygame.GL_CONTEXT_PROFILE_CORE,
    require=330,
    version_line="330",
    precision_line="",
)

GLES_PROFILE = GLProfile(
    name="OpenGL ES 3.0",
    major=3,
    minor=0,
    profile=pygame.GL_CONTEXT_PROFILE_ES,
    require=300,
    version_line="300 es",
    precision_line="precision mediump float;",
)


def build_shaders(profile: GLProfile) -> tuple[str, str]:
    return (
        VERTEX_SHADER_TEMPLATE.replace("__VERSION_LINE__", profile.version_line),
        FRAGMENT_SHADER_TEMPLATE.replace("__VERSION_LINE__", profile.version_line).replace(
            "__PRECISION_LINE__",
            profile.precision_line,
        ),
    )


class VectorAnimationManager:
    def __init__(self, ctx: moderngl.Context, size: tuple[int, int], profile: GLProfile):
        self.ctx = ctx
        self.size = size
        self.mode = "STARTUP"
        self.style = STATE_STYLE[self.mode]

        vertex_shader, fragment_shader = build_shaders(profile)
        self.program = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        vertices = (-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0)
        self.vbo = ctx.buffer(data=array("f", vertices).tobytes())
        self.vao = ctx.vertex_array(self.program, [(self.vbo, "2f", "in_pos")])
        self.program["resolution"].value = size

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.style = STATE_STYLE[mode]

    def render(self, now_secs: float) -> None:
        s = self.style
        self.program["time"].value = now_secs
        self.program["bg_color"].value = s.bg
        self.program["fg_color"].value = s.fg
        self.program["accent_color"].value = s.accent
        self.program["speed"].value = s.speed
        self.program["intensity"].value = s.intensity
        self.program["symbol"].value = s.symbol
        self.vao.render(moderngl.TRIANGLE_STRIP)


class VectorStateDisplay:
    def __init__(self, *, window_size: tuple[int, int], target_fps: int, prefer_gles: bool = False):
        self.window_size = window_size
        self.target_fps = target_fps
        self.prefer_gles = prefer_gles
        self.key_to_mode = {config["key"]: mode_name for mode_name, config in MODE_CONFIG.items()}
        self.current_mode = "STARTUP"
        self.running = False

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption("State-driven vector animation demo")

        ctx, profile = self._create_gl_context()
        print(f"GL context: {profile.name}")
        renderer = VectorAnimationManager(ctx, self.window_size, profile)
        clock = pygame.time.Clock()
        timer_offset = pygame.time.get_ticks()
        self.running = True

        print("Keys: 1 STARTUP, 2 IDLE, 3 TASK, 4 TELEOP, 5 ERROR_MINOR, 6 ERROR_MAJOR, 7 PAUSED, 0 SHUTDOWN, Esc quit")
        pygame.display.set_caption(f"State-driven vector animation demo - {self.current_mode}")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key in self.key_to_mode:
                        self.current_mode = self.key_to_mode[event.key]
                        renderer.set_mode(self.current_mode)
                        pygame.display.set_caption(f"State-driven vector animation demo - {self.current_mode}")
                        print(f"mode -> {self.current_mode}")

            ctx.screen.use()
            ctx.clear(0.0, 0.0, 0.0, 1.0)
            renderer.render((pygame.time.get_ticks() - timer_offset) / 1000.0)
            pygame.display.flip()
            clock.tick(self.target_fps)

        pygame.quit()

    def _create_gl_context(self) -> tuple[moderngl.Context, GLProfile]:
        profiles = [GLES_PROFILE, DESKTOP_PROFILE] if self.prefer_gles else [DESKTOP_PROFILE, GLES_PROFILE]
        errors: list[str] = []

        for profile in profiles:
            try:
                pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, profile.major)
                pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, profile.minor)
                pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, profile.profile)
                pygame.display.set_mode(self.window_size, pygame.OPENGL | pygame.DOUBLEBUF)
                ctx = moderngl.create_context(require=profile.require)
                return ctx, profile
            except (pygame.error, moderngl.Error) as exc:
                errors.append(f"{profile.name}: {exc}")
                pygame.display.quit()
                pygame.display.init()

        raise RuntimeError("Could not create an OpenGL context. Tried: " + " | ".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="State-driven vector animation prototype")
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=420)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument(
        "--gles",
        action="store_true",
        help="Prefer OpenGL ES 3.0 first (useful on embedded targets). Desktop OpenGL is tried first by default.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    VectorStateDisplay(window_size=(args.width, args.height), target_fps=args.fps, prefer_gles=args.gles).run()


if __name__ == "__main__":
    main()
