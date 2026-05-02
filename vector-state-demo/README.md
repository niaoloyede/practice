# State-Driven Vector Animation Demo

This is a small prototype for the robot display idea:

- one renderer
- many robot states
- no video per state
- no SVG runtime parsing
- no browser
- no GSAP / Framer Motion
- Python chooses variants; the GPU draws animated vector-like shapes

It uses the same broad runtime model as the `HeadDisplay` code you shared:

```text
pygame window/context
-> moderngl shader
-> per-state uniforms
-> one frame loop
```

## Run

```bash
cd vector-state-demo
python3 vector_state_display.py
```

By default the demo tries desktop OpenGL first, which works better on laptops.
On embedded targets that expose OpenGL ES, use:

```bash
python3 vector_state_display.py --gles
```

Keys:

| Key | Mode |
| --- | --- |
| `1` | `STARTUP` |
| `2` | `IDLE` |
| `3` | `TASK` |
| `4` | `TELEOP` |
| `5` | `ERROR_MINOR` |
| `6` | `ERROR_MAJOR` |
| `7` | `PAUSED` |
| `0` | `SHUTDOWN` |
| `Esc` | quit |

## Slack-Like Icon Options Demo

This tries three ways to replicate and animate a Slack-like SVG icon:

```bash
python3 slack_logo_options.py
```

The window has three columns:

| Column | Approach |
| --- | --- |
| Left | Pure shader SDF capsules. Best runtime path for embedded GPU rendering. |
| Middle | Rasterized once into a texture, then animated as a quad. Easiest path for static SVG fidelity. |
| Right | SVG-coordinate-derived segments, animated independently. Best for state variants. |

On embedded OpenGL ES targets:

```bash
python3 slack_logo_options.py --gles
```

## Simplified Robot Avatar

There are two robot files:

| File | Purpose |
| --- | --- |
| `assets/simplified_robot.svg` | Hand-authored vector reference based on the PNG. Use this for design review/export, not runtime parsing. |
| `robot_avatar_shader.py` | Runtime demo that recreates the simplified robot procedurally in a shader. No SVG/XML parsing. |

Run the procedural runtime demo:

```bash
python3 robot_avatar_shader.py
```

Embedded OpenGL ES target:

```bash
python3 robot_avatar_shader.py --gles
```

Keys are the same as the state demo:

| Key | Mode |
| --- | --- |
| `1` | `STARTUP` |
| `2` | `IDLE` |
| `3` | `TASK` |
| `4` | `TELEOP` |
| `5` | `ERROR_MINOR` |
| `6` | `ERROR_MAJOR` |
| `7` | `PAUSED` |
| `0` | `SHUTDOWN` |
| `Esc` | quit |

The shader draws the robot with primitive SDF-ish shapes:

- head as rounded box/ellipse approximation
- torso as trapezoid
- shoulders as ellipses
- arms as rounded boxes
- red neck band as a rounded shape
- seams/highlights as strokes
- state overlays as scanlines, task progress lines, shoulder pulses, alert rings, and pause bars

## How this maps to the robot code

The important part is `STATE_STYLE`:

```python
STATE_STYLE = {
    "IDLE": StateStyle(..., speed=0.35, intensity=0.28, symbol=0),
    "ERROR_MAJOR": StateStyle(..., speed=2.40, intensity=1.00, symbol=3),
}
```

Your state machine calls:

```python
vector_animation.set_mode(self.current_mode)
```

and every frame calls:

```python
vector_animation.render(now_secs)
```

The shader receives only cheap uniforms:

- `time`
- `bg_color`
- `fg_color`
- `accent_color`
- `speed`
- `intensity`
- `symbol`

That gives you a “vector GIF with variants” without storing separate videos for every state.

## Production notes

For the real robot code, place this layer between the metaball background and notification icon rendering:

```text
metaballs
-> vector state overlay
-> notification black zone
-> notification icons
-> pygame.display.flip()
```

Do not parse SVG/XML every frame. Use SVG only as design reference, then express the motion as shader shapes, transforms, and uniforms.
