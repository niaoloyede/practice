from __future__ import annotations

import argparse
import math
from array import array

import moderngl
import pygame

from vector_state_display import DESKTOP_PROFILE, GLES_PROFILE, GLProfile


# Derived from the simple 256x256 Phosphor Slack icon structure:
# eight rounded stroke segments arranged around the center.
# Coordinates are normalized: x/y in [-1, 1], y points up.
SEGMENTS = (
    ((-0.25, 0.10), (-0.25, 0.58), (0.24, 0.75, 1.00)),  # cyan vertical
    ((-0.52, 0.58), (-0.25, 0.58), (0.24, 0.75, 1.00)),  # cyan short
    ((0.10, 0.25), (0.58, 0.25), (0.25, 0.90, 0.52)),  # green horizontal
    ((0.58, 0.25), (0.58, 0.52), (0.25, 0.90, 0.52)),  # green short
    ((0.25, -0.10), (0.25, -0.58), (0.98, 0.73, 0.18)),  # amber vertical
    ((0.25, -0.58), (0.52, -0.58), (0.98, 0.73, 0.18)),  # amber short
    ((-0.58, -0.25), (-0.10, -0.25), (0.96, 0.30, 0.46)),  # rose horizontal
    ((-0.58, -0.52), (-0.58, -0.25), (0.96, 0.30, 0.46)),  # rose short
)


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

in vec2 v_uv;
out vec4 fragColor;

float capsule(vec2 p, vec2 a, vec2 b, float r) {
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

float fill_shape(float d) {
    return 1.0 - smoothstep(0.0, 0.012, d);
}

mat2 rot(float a) {
    float s = sin(a);
    float c = cos(a);
    return mat2(c, -s, s, c);
}

vec3 composite(vec3 under, vec3 over, float a) {
    return mix(under, over, clamp(a, 0.0, 1.0));
}

vec3 add_segment(vec3 color, vec2 p, vec2 a, vec2 b, vec3 seg_color, float alpha) {
    float d = capsule(p, a, b, 0.075);
    return composite(color, seg_color, fill_shape(d) * alpha);
}

vec3 add_segment_fly(vec3 color, vec2 p, vec2 a, vec2 b, vec3 seg_color, float alpha, float i) {
    float loop = mod(time * 0.34, 1.6);
    float k = smoothstep(i * 0.09, i * 0.09 + 0.36, loop);
    vec2 center = (a + b) * 0.5;
    vec2 dir = normalize(center + vec2(0.001, 0.001));
    vec2 q = p - dir * (1.0 - k) * 0.52;
    float pulse = 0.92 + 0.08 * sin(time * 4.0 + i);
    q = q / pulse;
    float d = capsule(q, a, b, 0.075);
    return composite(color, seg_color, fill_shape(d) * alpha * k);
}

vec3 slack_logo(vec2 p, float alpha) {
    vec3 color = vec3(0.0);
    color = add_segment(color, p, vec2(-0.25, 0.10), vec2(-0.25, 0.58), vec3(0.24, 0.75, 1.00), alpha);
    color = add_segment(color, p, vec2(-0.52, 0.58), vec2(-0.25, 0.58), vec3(0.24, 0.75, 1.00), alpha);
    color = add_segment(color, p, vec2(0.10, 0.25), vec2(0.58, 0.25), vec3(0.25, 0.90, 0.52), alpha);
    color = add_segment(color, p, vec2(0.58, 0.25), vec2(0.58, 0.52), vec3(0.25, 0.90, 0.52), alpha);
    color = add_segment(color, p, vec2(0.25, -0.10), vec2(0.25, -0.58), vec3(0.98, 0.73, 0.18), alpha);
    color = add_segment(color, p, vec2(0.25, -0.58), vec2(0.52, -0.58), vec3(0.98, 0.73, 0.18), alpha);
    color = add_segment(color, p, vec2(-0.58, -0.25), vec2(-0.10, -0.25), vec3(0.96, 0.30, 0.46), alpha);
    color = add_segment(color, p, vec2(-0.58, -0.52), vec2(-0.58, -0.25), vec3(0.96, 0.30, 0.46), alpha);
    return color;
}

float logo_mask(vec2 p) {
    float d = 10.0;
    d = min(d, capsule(p, vec2(-0.25, 0.10), vec2(-0.25, 0.58), 0.075));
    d = min(d, capsule(p, vec2(-0.52, 0.58), vec2(-0.25, 0.58), 0.075));
    d = min(d, capsule(p, vec2(0.10, 0.25), vec2(0.58, 0.25), 0.075));
    d = min(d, capsule(p, vec2(0.58, 0.25), vec2(0.58, 0.52), 0.075));
    d = min(d, capsule(p, vec2(0.25, -0.10), vec2(0.25, -0.58), 0.075));
    d = min(d, capsule(p, vec2(0.25, -0.58), vec2(0.52, -0.58), 0.075));
    d = min(d, capsule(p, vec2(-0.58, -0.25), vec2(-0.10, -0.25), 0.075));
    d = min(d, capsule(p, vec2(-0.58, -0.52), vec2(-0.58, -0.25), 0.075));
    return fill_shape(d);
}

vec3 flying_segments(vec2 p) {
    vec3 color = vec3(0.0);
    color = add_segment_fly(color, p, vec2(-0.25, 0.10), vec2(-0.25, 0.58), vec3(0.24, 0.75, 1.00), 1.0, 0.0);
    color = add_segment_fly(color, p, vec2(-0.52, 0.58), vec2(-0.25, 0.58), vec3(0.24, 0.75, 1.00), 1.0, 1.0);
    color = add_segment_fly(color, p, vec2(0.10, 0.25), vec2(0.58, 0.25), vec3(0.25, 0.90, 0.52), 1.0, 2.0);
    color = add_segment_fly(color, p, vec2(0.58, 0.25), vec2(0.58, 0.52), vec3(0.25, 0.90, 0.52), 1.0, 3.0);
    color = add_segment_fly(color, p, vec2(0.25, -0.10), vec2(0.25, -0.58), vec3(0.98, 0.73, 0.18), 1.0, 4.0);
    color = add_segment_fly(color, p, vec2(0.25, -0.58), vec2(0.52, -0.58), vec3(0.98, 0.73, 0.18), 1.0, 5.0);
    color = add_segment_fly(color, p, vec2(-0.58, -0.25), vec2(-0.10, -0.25), vec3(0.96, 0.30, 0.46), 1.0, 6.0);
    color = add_segment_fly(color, p, vec2(-0.58, -0.52), vec2(-0.58, -0.25), vec3(0.96, 0.30, 0.46), 1.0, 7.0);
    return color;
}

vec3 panel_background(vec2 p, float panel) {
    float vignette = exp(-dot(p, p) * 1.2);
    vec3 base = vec3(0.015, 0.018, 0.030);
    vec3 glow = panel == 0.0 ? vec3(0.04, 0.18, 0.28) : (panel == 1.0 ? vec3(0.12, 0.07, 0.20) : vec3(0.15, 0.06, 0.08));
    return base + glow * vignette;
}

void main() {
    float third = floor(v_uv.x * 3.0);
    vec2 local = vec2(fract(v_uv.x * 3.0), v_uv.y);
    float panel_aspect = (resolution.x / 3.0) / resolution.y;
    vec2 p = (local - 0.5) * vec2(panel_aspect, 1.0) * 2.2;

    vec3 color = panel_background(p, third);

    if (third < 0.5) {
        // Option 1: pure shader SDF logo, with a turbine-like breathing transform.
        vec2 q = rot(sin(time * 0.8) * 0.18) * p;
        q /= 0.88 + 0.08 * sin(time * 2.2);
        vec3 logo = slack_logo(q, 1.0);
        float mask = logo_mask(q);
        color = composite(color, logo, mask);
    } else if (third > 1.5) {
        // Option 3: SVG-coordinate-derived segments, each with its own stateful motion.
        vec3 logo = flying_segments(p);
        float mask = max(max(logo.r, logo.g), logo.b);
        color = composite(color, logo, mask);
    }

    fragColor = vec4(color, 1.0);
}
"""


TEXTURE_VERTEX_SHADER_TEMPLATE = """#version __VERSION_LINE__
in vec2 in_pos;
in vec2 in_uv;
out vec2 v_uv;

uniform vec2 center;
uniform vec2 size;
uniform float rotation;

void main() {
    vec2 p = in_pos * size;
    float s = sin(rotation);
    float c = cos(rotation);
    p = mat2(c, -s, s, c) * p;
    gl_Position = vec4(center + p, 0.0, 1.0);
    v_uv = in_uv;
}
"""


TEXTURE_FRAGMENT_SHADER_TEMPLATE = """#version __VERSION_LINE__
__PRECISION_LINE__

uniform sampler2D tex;
uniform float alpha;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    vec4 c = texture(tex, v_uv);
    fragColor = vec4(c.rgb, c.a * alpha);
}
"""


def build_shader_pair(vertex_template: str, fragment_template: str, profile: GLProfile) -> tuple[str, str]:
    vertex = vertex_template.replace("__VERSION_LINE__", profile.version_line)
    fragment = fragment_template.replace("__VERSION_LINE__", profile.version_line).replace(
        "__PRECISION_LINE__",
        profile.precision_line,
    )
    return vertex, fragment


def create_context(size: tuple[int, int], prefer_gles: bool) -> tuple[moderngl.Context, GLProfile]:
    profiles = [GLES_PROFILE, DESKTOP_PROFILE] if prefer_gles else [DESKTOP_PROFILE, GLES_PROFILE]
    errors: list[str] = []

    for profile in profiles:
        try:
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, profile.major)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, profile.minor)
            pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, profile.profile)
            pygame.display.set_mode(size, pygame.OPENGL | pygame.DOUBLEBUF)
            return moderngl.create_context(require=profile.require), profile
        except (pygame.error, moderngl.Error) as exc:
            errors.append(f"{profile.name}: {exc}")
            pygame.display.quit()
            pygame.display.init()

    raise RuntimeError("Could not create an OpenGL context. Tried: " + " | ".join(errors))


class BackgroundPanels:
    def __init__(self, ctx: moderngl.Context, profile: GLProfile, size: tuple[int, int]):
        vertex, fragment = build_shader_pair(VERTEX_SHADER_TEMPLATE, FRAGMENT_SHADER_TEMPLATE, profile)
        self.program = ctx.program(vertex_shader=vertex, fragment_shader=fragment)
        vertices = (-1.0, -1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0)
        self.vbo = ctx.buffer(array("f", vertices).tobytes())
        self.vao = ctx.vertex_array(self.program, [(self.vbo, "2f", "in_pos")])
        self.program["resolution"].value = size

    def render(self, time: float) -> None:
        self.program["time"].value = time
        self.vao.render(moderngl.TRIANGLE_STRIP)


class RasterTextureLogo:
    def __init__(self, ctx: moderngl.Context, profile: GLProfile):
        vertex, fragment = build_shader_pair(TEXTURE_VERTEX_SHADER_TEMPLATE, TEXTURE_FRAGMENT_SHADER_TEMPLATE, profile)
        self.program = ctx.program(vertex_shader=vertex, fragment_shader=fragment)
        self.program["tex"].value = 0

        # Two triangles as a textured quad; xy + uv.
        quad = (
            -1.0,
            -1.0,
            0.0,
            0.0,
            1.0,
            -1.0,
            1.0,
            0.0,
            -1.0,
            1.0,
            0.0,
            1.0,
            1.0,
            1.0,
            1.0,
            1.0,
        )
        self.vbo = ctx.buffer(array("f", quad).tobytes())
        self.vao = ctx.vertex_array(self.program, [(self.vbo, "2f 2f", "in_pos", "in_uv")])
        self.texture = ctx.texture((256, 256), 4, self._make_surface_bytes(), dtype="f1")
        self.texture.filter = (moderngl.LINEAR, moderngl.LINEAR)

    def _make_surface_bytes(self) -> bytes:
        surface = pygame.Surface((256, 256), pygame.SRCALPHA)
        width = 18
        scale = 92.0
        center = (128, 128)

        for (a, b, color) in SEGMENTS:
            rgb = tuple(int(c * 255) for c in color)
            start = (int(center[0] + a[0] * scale), int(center[1] - a[1] * scale))
            end = (int(center[0] + b[0] * scale), int(center[1] - b[1] * scale))
            pygame.draw.line(surface, rgb, start, end, width)
            pygame.draw.circle(surface, rgb, start, width // 2)
            pygame.draw.circle(surface, rgb, end, width // 2)

        return pygame.image.tostring(surface, "RGBA", True)

    def render(self, time: float) -> None:
        pulse = 0.94 + 0.05 * math.sin(time * 2.4)
        self.program["center"].value = (0.0, 0.0)
        self.program["size"].value = (0.28 * pulse, 0.50 * pulse)
        self.program["rotation"].value = math.sin(time * 0.9) * 0.25
        self.program["alpha"].value = 0.92
        self.texture.use(0)
        self.vao.render(moderngl.TRIANGLE_STRIP)


class SlackLogoOptionsDemo:
    def __init__(self, *, size: tuple[int, int], fps: int, prefer_gles: bool):
        self.size = size
        self.fps = fps
        self.prefer_gles = prefer_gles

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption("Slack-like icon animation options")
        ctx, profile = create_context(self.size, self.prefer_gles)
        ctx.enable(moderngl.BLEND)
        ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

        panels = BackgroundPanels(ctx, profile, self.size)
        raster_logo = RasterTextureLogo(ctx, profile)
        clock = pygame.time.Clock()
        start = pygame.time.get_ticks()
        print(f"GL context: {profile.name}")
        print("Left: shader SDF | Middle: rasterized once texture | Right: SVG-coordinate segments")
        print("Esc to quit")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            t = (pygame.time.get_ticks() - start) / 1000.0
            ctx.screen.use()
            ctx.clear(0.0, 0.0, 0.0, 1.0)
            panels.render(t)
            raster_logo.render(t)
            pygame.display.flip()
            clock.tick(self.fps)

        pygame.quit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Try three vector/logo animation strategies")
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=360)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--gles", action="store_true", help="Prefer OpenGL ES 3.0 first")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    SlackLogoOptionsDemo(size=(args.width, args.height), fps=args.fps, prefer_gles=args.gles).run()


if __name__ == "__main__":
    main()
