from __future__ import annotations

import argparse
from array import array
from dataclasses import dataclass

import moderngl
import pygame

from vector_state_display import DESKTOP_PROFILE, GLES_PROFILE, GLProfile


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
class RobotStateStyle:
    bg: tuple[float, float, float]
    band: tuple[float, float, float]
    glow: tuple[float, float, float]
    speed: float
    intensity: float
    effect: int


STATE_STYLE = {
    "STARTUP": RobotStateStyle((0.00, 0.00, 0.00), (0.90, 0.02, 0.02), (0.95, 0.08, 0.06), 0.70, 0.55, 0),
    "IDLE": RobotStateStyle((0.00, 0.00, 0.00), (0.86, 0.02, 0.02), (0.45, 0.52, 0.65), 0.28, 0.20, 0),
    "TASK": RobotStateStyle((0.00, 0.02, 0.05), (0.05, 0.52, 1.00), (0.10, 0.62, 1.00), 1.05, 0.75, 1),
    "TELEOP": RobotStateStyle((0.00, 0.04, 0.08), (0.08, 0.70, 1.00), (0.18, 0.80, 1.00), 0.92, 0.65, 2),
    "ERROR_MINOR": RobotStateStyle((0.05, 0.03, 0.00), (1.00, 0.58, 0.08), (1.00, 0.72, 0.10), 1.65, 0.92, 3),
    "ERROR_MAJOR": RobotStateStyle((0.26, 0.00, 0.00), (1.00, 0.00, 0.00), (1.00, 0.00, 0.00), 2.55, 1.00, 3),
    "PAUSED": RobotStateStyle((0.00, 0.00, 0.00), (0.42, 0.45, 0.52), (0.32, 0.35, 0.42), 0.20, 0.22, 4),
    "SHUTDOWN": RobotStateStyle((0.00, 0.00, 0.00), (0.24, 0.24, 0.28), (0.18, 0.20, 0.24), 0.22, 0.28, 5),
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
uniform vec3 band_color;
uniform vec3 glow_color;
uniform float speed;
uniform float intensity;
uniform int effect;

in vec2 v_uv;
out vec4 fragColor;

float sd_ellipse(vec2 p, vec2 r) {
    // Lightweight approximation good enough for a head/shoulder avatar.
    return (length(p / r) - 1.0) * min(r.x, r.y);
}

float sd_box(vec2 p, vec2 b) {
    vec2 q = abs(p) - b;
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
}

float sd_round_box(vec2 p, vec2 b, float r) {
    return sd_box(p, b - vec2(r)) - r;
}

float sd_segment(vec2 p, vec2 a, vec2 b, float r) {
    vec2 pa = p - a;
    vec2 ba = b - a;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - r;
}

float fill_shape(float d) {
    return 1.0 - smoothstep(0.0, 0.006, d);
}

float stroke_shape(float d, float w) {
    return 1.0 - smoothstep(w, w + 0.006, abs(d));
}

float trapezoid(vec2 p, float y0, float y1, float half0, float half1) {
    float k = clamp((p.y - y0) / (y1 - y0), 0.0, 1.0);
    float half_width = mix(half0, half1, k);
    float inside_y = smoothstep(y0 - 0.010, y0 + 0.010, p.y) * (1.0 - smoothstep(y1 - 0.010, y1 + 0.010, p.y));
    float inside_x = 1.0 - smoothstep(half_width - 0.010, half_width + 0.010, abs(p.x));
    return inside_x * inside_y;
}

float subtract_shape(float a, float b) {
    return clamp(a * (1.0 - b), 0.0, 1.0);
}

vec3 composite(vec3 under, vec3 over, float alpha) {
    return mix(under, over, clamp(alpha, 0.0, 1.0));
}

mat2 rot2(float a) {
    float s = sin(a);
    float c = cos(a);
    return mat2(c, -s, s, c);
}

float sd_round_box_rot(vec2 p, vec2 center, vec2 b, float r, float angle) {
    vec2 local = rot2(-angle) * (p - center);
    return sd_round_box(local, b, r);
}

void main() {
    vec2 uv = v_uv;
    vec2 p = (uv - 0.5) * vec2(resolution.x / resolution.y, 1.0);
    p *= 1.85;

    float t = time * speed;
    float breathe = 0.5 + 0.5 * sin(t * 6.28318);
    float boot = smoothstep(0.0, 1.2, time);
    float shutdown = effect == 5 ? (0.72 + 0.20 * sin(time * 1.2)) : 1.0;
    vec2 q = p;
    q.y += 0.03 * intensity * sin(t * 2.0);
    q /= shutdown;

    vec3 body_hi = vec3(0.98, 0.94, 0.94);
    vec3 body_mid = vec3(0.83, 0.78, 0.78);
    vec3 body_dark = vec3(0.36, 0.35, 0.36);
    vec3 color = bg_color;

    // Global glow behind the robot.
    float glow = exp(-dot(q - vec2(0.0, -0.02), q - vec2(0.0, -0.02)) * 2.2);
    color += glow_color * glow * (0.08 + 0.22 * intensity * breathe);

    // Torso and collar are joined first so the silhouette reads as a single shell.
    float torso = trapezoid(q, -0.95, -0.19, 0.52, 0.35);
    float chest_cap = fill_shape(sd_ellipse(q - vec2(0.0, -0.22), vec2(0.37, 0.13)));
    float neck_base = fill_shape(sd_round_box(q - vec2(0.0, -0.04), vec2(0.25, 0.14), 0.08));
    float torso_shell = max(torso, max(chest_cap * 0.78, neck_base));
    vec3 torso_color = mix(body_mid, body_hi, clamp(0.36 + 0.52 * (q.x + 0.45) + 0.16 * (q.y + 0.7), 0.0, 1.0));
    torso_color = mix(torso_color, body_dark, smoothstep(0.32, 0.55, abs(q.x)) * torso * 0.28);
    color = composite(color, torso_color, torso_shell);

    // Shoulder sockets, upper arms, and body overlap to remove separated “floating” pieces.
    float left_socket = fill_shape(sd_round_box(q - vec2(-0.46, -0.32), vec2(0.18, 0.18), 0.06));
    float right_socket = fill_shape(sd_round_box(q - vec2(0.46, -0.32), vec2(0.18, 0.18), 0.06));
    float left_shoulder = fill_shape(sd_ellipse(q - vec2(-0.62, -0.32), vec2(0.21, 0.18)));
    float right_shoulder = fill_shape(sd_ellipse(q - vec2(0.62, -0.32), vec2(0.21, 0.18)));
    float shoulder_shell = max(max(left_socket, right_socket), max(left_shoulder, right_shoulder));
    vec3 socket_color = mix(body_dark, body_mid, 0.52);
    color = composite(color, socket_color, max(left_socket, right_socket) * 0.82);
    float left_pocket = fill_shape(sd_ellipse(q - vec2(-0.51, -0.42), vec2(0.18, 0.11)));
    float right_pocket = fill_shape(sd_ellipse(q - vec2(0.51, -0.42), vec2(0.18, 0.11)));
    color = composite(color, vec3(0.015, 0.015, 0.018), max(left_pocket, right_pocket) * 0.48);
    color = composite(color, body_mid, max(left_shoulder, right_shoulder));

    float left_disc = fill_shape(sd_ellipse(q - vec2(-0.62, -0.32), vec2(0.145, 0.13)));
    float right_disc = fill_shape(sd_ellipse(q - vec2(0.62, -0.32), vec2(0.145, 0.13)));
    color = composite(color, body_hi, max(left_disc, right_disc) * 0.78);

    float left_upper_arm = fill_shape(sd_round_box_rot(q, vec2(-0.79, -0.61), vec2(0.12, 0.31), 0.040, -0.10));
    float right_upper_arm = fill_shape(sd_round_box_rot(q, vec2(0.79, -0.61), vec2(0.12, 0.31), 0.040, 0.10));
    float left_forearm_hint = fill_shape(sd_round_box_rot(q, vec2(-0.77, -0.94), vec2(0.09, 0.14), 0.030, -0.05));
    float right_forearm_hint = fill_shape(sd_round_box_rot(q, vec2(0.77, -0.94), vec2(0.09, 0.14), 0.030, 0.05));
    float arm_shell = max(max(left_upper_arm, right_upper_arm), max(left_forearm_hint, right_forearm_hint));
    color = composite(color, body_mid, arm_shell);

    float left_arm_edge = stroke_shape(sd_segment(q, vec2(-0.91, -0.47), vec2(-0.64, -0.47), 0.002), 0.005);
    float right_arm_edge = stroke_shape(sd_segment(q, vec2(0.64, -0.47), vec2(0.91, -0.47), 0.002), 0.005);
    float elbow_shadow = max(
        fill_shape(sd_round_box(q - vec2(-0.90, -0.77), vec2(0.028, 0.11), 0.014)),
        fill_shape(sd_round_box(q - vec2(0.90, -0.77), vec2(0.028, 0.11), 0.014))
    );
    color = composite(color, vec3(0.03, 0.03, 0.035), elbow_shadow * 0.58);
    float forearm_cut = max(
        stroke_shape(sd_segment(q, vec2(-0.88, -0.86), vec2(-0.69, -0.86), 0.002), 0.004),
        stroke_shape(sd_segment(q, vec2(0.69, -0.86), vec2(0.88, -0.86), 0.002), 0.004)
    );
    color = composite(color, body_dark, forearm_cut * 0.35);

    // Neck band wraps around the head/torso connection, with an underside shadow.
    float band_rect = fill_shape(sd_round_box(q - vec2(0.0, 0.050), vec2(0.310, 0.082), 0.030));
    float band_top_flat = band_rect * smoothstep(0.125, 0.110, q.y);
    float band_bottom_round = fill_shape(sd_ellipse(q - vec2(0.0, -0.035), vec2(0.285, 0.118)));
    float neck_band = max(band_top_flat, band_bottom_round * 0.82);
    float neck_shadow = fill_shape(sd_ellipse(q - vec2(0.0, -0.095), vec2(0.310, 0.105))) * (1.0 - neck_band);
    color = composite(color, body_dark, neck_shadow * 0.26);
    vec3 animated_band = band_color * (0.78 + 0.35 * breathe * intensity);
    color = composite(color, animated_band, neck_band);

    // Head: larger capsule-like shell with side rim and highlights.
    float head_outer = fill_shape(sd_round_box(q - vec2(0.0, 0.385), vec2(0.315, 0.455), 0.230));
    float head_body = fill_shape(sd_round_box(q - vec2(0.0, 0.305), vec2(0.300, 0.330), 0.145));
    float head = max(head_outer, head_body);
    float head_shade = clamp(0.37 + 0.46 * (q.x + 0.32) + 0.20 * (q.y - 0.08), 0.0, 1.0);
    head_shade -= smoothstep(0.24, 0.34, abs(q.x)) * 0.18;
    color = composite(color, mix(body_mid, body_hi, head_shade), head);

    float left_rim = stroke_shape(sd_segment(q, vec2(-0.300, 0.05), vec2(-0.300, 0.68), 0.004), 0.006) * head;
    float right_rim_shadow = stroke_shape(sd_segment(q, vec2(0.300, 0.05), vec2(0.300, 0.68), 0.004), 0.005) * head;
    float top_rim = stroke_shape(sd_segment(q, vec2(-0.09, 0.817), vec2(0.09, 0.817), 0.002), 0.004) * head;
    color = composite(color, vec3(1.0, 1.0, 1.0), left_rim * 0.25);
    color = composite(color, body_dark, right_rim_shadow * 0.12);
    color = composite(color, body_dark, top_rim * 0.18);

    float highlight = fill_shape(sd_ellipse(q - vec2(0.13, 0.58), vec2(0.15, 0.25))) * 0.26;
    float left_soft_highlight = fill_shape(sd_ellipse(q - vec2(-0.22, 0.50), vec2(0.035, 0.34))) * 0.18;
    float cheek = fill_shape(sd_ellipse(q - vec2(0.21, 0.22), vec2(0.07, 0.18))) * 0.12;
    color = composite(color, vec3(1.0, 0.96, 0.96), (highlight + cheek + left_soft_highlight) * head);
    float head_pin = fill_shape(sd_ellipse(q - vec2(0.0, 0.72), vec2(0.010, 0.010)));
    float micro_pin_l = fill_shape(sd_ellipse(q - vec2(-0.225, 0.62), vec2(0.006, 0.006)));
    float micro_pin_r = fill_shape(sd_ellipse(q - vec2(0.225, 0.62), vec2(0.005, 0.005)));
    color = composite(color, body_dark, (head_pin * 0.55 + micro_pin_l * 0.26 + micro_pin_r * 0.20) * head);

    // Seams and panel lines over the connected shell.
    float collar = stroke_shape(sd_ellipse(q - vec2(0.0, -0.095), vec2(0.315, 0.155)), 0.006);
    float collar_inner = stroke_shape(sd_ellipse(q - vec2(0.0, -0.080), vec2(0.260, 0.120)), 0.003);
    float torso_seam = stroke_shape(q.y + 0.58, 0.004) * (1.0 - smoothstep(0.50, 0.54, abs(q.x)));
    float socket_seams = stroke_shape(sd_ellipse(q - vec2(-0.62, -0.32), vec2(0.205, 0.175)), 0.004);
    socket_seams += stroke_shape(sd_ellipse(q - vec2(0.62, -0.32), vec2(0.205, 0.175)), 0.004);
    float arm_seams = left_arm_edge + right_arm_edge;
    color = composite(
        color,
        body_dark,
        clamp((collar + collar_inner * 0.45 + torso_seam + socket_seams * 0.7 + arm_seams) * 0.35, 0.0, 1.0)
    );

    // State overlays.
    if (effect == 0) {
        // Startup / idle: soft scan glow on neck and head.
        float scan_y = mix(0.82, -0.10, fract(time * 0.18));
        float scan = exp(-pow((q.y - scan_y) * 18.0, 2.0)) * head;
        color = composite(color, glow_color, scan * 0.22 * boot);
    } else if (effect == 1) {
        // Task: blue progress line across torso.
        float line_y = -0.70 + fract(time * 0.45) * 0.42;
        float line = exp(-pow((q.y - line_y) * 55.0, 2.0)) * torso;
        color = composite(color, glow_color, line * 0.55);
    } else if (effect == 2) {
        // Teleop: shoulder sweeps.
        float sweep = 0.5 + 0.5 * sin(t * 5.0);
        color = composite(color, glow_color, left_shoulder * (1.0 - sweep) * 0.45);
        color = composite(color, glow_color, right_shoulder * sweep * 0.45);
    } else if (effect == 3) {
        // Error: warning pulse ring around head.
        float ring = stroke_shape(sd_ellipse(q - vec2(0.0, 0.35), vec2(0.42 + 0.10 * breathe, 0.52 + 0.12 * breathe)), 0.014);
        float flash = smoothstep(0.55, 1.0, breathe);
        color = composite(color, glow_color, ring * 0.75 + flash * neck_band * 0.45);
    } else if (effect == 4) {
        // Pause: dim overlay and pause bars.
        color *= 0.72;
        float bar_a = fill_shape(sd_round_box(q - vec2(-0.055, 0.30), vec2(0.022, 0.11), 0.010));
        float bar_b = fill_shape(sd_round_box(q - vec2(0.055, 0.30), vec2(0.022, 0.11), 0.010));
        color = composite(color, glow_color, max(bar_a, bar_b) * 0.75);
    }

    fragColor = vec4(color, 1.0);
}
"""


def build_shaders(profile: GLProfile) -> tuple[str, str]:
    return (
        VERTEX_SHADER_TEMPLATE.replace("__VERSION_LINE__", profile.version_line),
        FRAGMENT_SHADER_TEMPLATE.replace("__VERSION_LINE__", profile.version_line).replace(
            "__PRECISION_LINE__",
            profile.precision_line,
        ),
    )


class RobotAvatarRenderer:
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
        self.program["band_color"].value = s.band
        self.program["glow_color"].value = s.glow
        self.program["speed"].value = s.speed
        self.program["intensity"].value = s.intensity
        self.program["effect"].value = s.effect
        self.vao.render(moderngl.TRIANGLE_STRIP)


class RobotAvatarDisplay:
    def __init__(self, *, window_size: tuple[int, int], fps: int, prefer_gles: bool):
        self.window_size = window_size
        self.fps = fps
        self.prefer_gles = prefer_gles
        self.current_mode = "STARTUP"
        self.key_to_mode = {config["key"]: mode for mode, config in MODE_CONFIG.items()}

    def run(self) -> None:
        pygame.init()
        pygame.display.set_caption("Robot avatar shader - STARTUP")
        ctx, profile = self._create_gl_context()
        print(f"GL context: {profile.name}")
        print("Keys: 1 STARTUP, 2 IDLE, 3 TASK, 4 TELEOP, 5 ERROR_MINOR, 6 ERROR_MAJOR, 7 PAUSED, 0 SHUTDOWN, Esc quit")
        renderer = RobotAvatarRenderer(ctx, self.window_size, profile)
        clock = pygame.time.Clock()
        timer_offset = pygame.time.get_ticks()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in self.key_to_mode:
                        self.current_mode = self.key_to_mode[event.key]
                        renderer.set_mode(self.current_mode)
                        pygame.display.set_caption(f"Robot avatar shader - {self.current_mode}")
                        print(f"mode -> {self.current_mode}")

            ctx.screen.use()
            ctx.clear(0.0, 0.0, 0.0, 1.0)
            renderer.render((pygame.time.get_ticks() - timer_offset) / 1000.0)
            pygame.display.flip()
            clock.tick(self.fps)

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
                return moderngl.create_context(require=profile.require), profile
            except (pygame.error, moderngl.Error) as exc:
                errors.append(f"{profile.name}: {exc}")
                pygame.display.quit()
                pygame.display.init()
        raise RuntimeError("Could not create an OpenGL context. Tried: " + " | ".join(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Procedural robot avatar demo - no SVG runtime parsing")
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--gles", action="store_true", help="Prefer OpenGL ES 3.0 first")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    RobotAvatarDisplay(window_size=(args.width, args.height), fps=args.fps, prefer_gles=args.gles).run()


if __name__ == "__main__":
    main()
