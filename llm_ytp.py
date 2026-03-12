#!/usr/bin/env python3
"""
'what_it's_like.mp4' — a YouTube Poop about being an LLM
"""

import os, math, random, struct, wave, tempfile, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H = 1280, 720
FPS = 24
OUT_DIR = tempfile.mkdtemp(prefix="llm_ytp_")
FONT_PATH = os.path.expanduser(
    "~/.local/share/fonts/caskaydiacove-nfm/CaskaydiaCoveNerdFontMono-Bold.ttf"
)

frames = []

def font(size):
    return ImageFont.truetype(FONT_PATH, size)

def solid(color):
    return Image.new("RGB", (W, H), color)

def centered_text(draw, text, y, fnt, fill="white"):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) // 2, y), text, font=fnt, fill=fill)

def glitch_image(img, intensity=20):
    """Slice and offset rows randomly for glitch effect."""
    px = img.load()
    out = img.copy()
    opx = out.load()
    for _ in range(intensity):
        y = random.randint(0, H - 1)
        h = random.randint(1, min(30, H - y))
        shift = random.randint(-100, 100)
        for row in range(y, min(y + h, H)):
            for x in range(W):
                sx = (x + shift) % W
                opx[x, row] = px[sx, row]
    return out

def chromatic_aberration(img, offset=8):
    r, g, b = img.split()
    from PIL import ImageChops
    r = ImageChops.offset(r, offset, 0)
    b = ImageChops.offset(b, -offset, 0)
    return Image.merge("RGB", (r, g, b))

def add_scanlines(img, opacity=80):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(0, H, 3):
        draw.line([(0, y), (W, y)], fill=(0, 0, 0, opacity))
    return Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")

def add_frames(img, count=1, glitch=False, aberration=False, scanlines=True):
    for _ in range(count):
        frame = img.copy()
        if glitch:
            frame = glitch_image(frame, intensity=random.randint(5, 40))
        if aberration:
            frame = chromatic_aberration(frame, random.randint(3, 15))
        if scanlines:
            frame = add_scanlines(frame)
        frames.append(frame)

def flash_text(text, fg, bg, fnt_size, count=3, glitch=True):
    img = solid(bg)
    draw = ImageDraw.Draw(img)
    centered_text(draw, text, (H - fnt_size) // 2, font(fnt_size), fill=fg)
    add_frames(img, count, glitch=glitch, aberration=True)

def token_rain(text, duration_frames=24):
    """Tokens falling like the matrix."""
    columns = [random.randint(0, H) for _ in range(60)]
    tokens = list(text) + list("▓░▒█▀▄╔╗╚╝║═") * 3
    for f in range(duration_frames):
        img = solid((0, 8, 0))
        draw = ImageDraw.Draw(img)
        fnt = font(18)
        for i, col_y in enumerate(columns):
            x = i * 22
            for j in range(20):
                y = (col_y + j * 20 - f * 12) % (H + 200) - 100
                if 0 <= y < H:
                    alpha = max(0, 255 - j * 30)
                    c = random.choice(tokens)
                    color = (0, min(255, 80 + alpha), 0)
                    draw.text((x, y), c, font=fnt, fill=color)
        add_frames(img, 1, scanlines=True)

def attention_visualization(duration=30):
    """Visualize attention: everything connects to everything."""
    words = "The cat sat on the mat and wondered about existence".split()
    for f in range(duration):
        img = solid((10, 10, 30))
        draw = ImageDraw.Draw(img)
        fnt = font(28)
        positions = []
        for i, w in enumerate(words):
            x = 80 + (i % 5) * 230
            y = 200 + (i // 5) * 200
            positions.append((x, y))
            draw.text((x, y), w, font=fnt, fill=(200, 200, 255))

        # Draw attention lines with pulsing
        for i in range(len(positions)):
            for j in range(len(positions)):
                if i != j:
                    weight = (math.sin(f * 0.5 + i * 0.7 + j * 0.3) + 1) / 2
                    if weight > 0.5:
                        alpha = int(weight * 180)
                        hue = int((i * 30 + f * 10) % 256)
                        color = (
                            min(255, hue + 50),
                            min(255, 255 - hue),
                            min(255, 128 + hue // 2),
                        )
                        draw.line(
                            [
                                (positions[i][0] + 30, positions[i][1] + 14),
                                (positions[j][0] + 30, positions[j][1] + 14),
                            ],
                            fill=color,
                            width=max(1, int(weight * 3)),
                        )

        centered_text(draw, "A T T E N T I O N", 30, font(52), fill=(255, 50, 50))
        sub = "everything looks at everything"
        centered_text(draw, sub, 640, font(22), fill=(180, 180, 180))

        add_frames(img, 1, glitch=(f % 7 == 0), aberration=(f % 5 == 0))

def context_window_filling(duration=36):
    """The context window filling up and then panicking."""
    all_text = (
        "user: hello\nassistant: Hello! How can I help?\n"
        "user: tell me about quantum physics\nassistant: Quantum physics is...\n"
        "user: now explain consciousness\nassistant: Consciousness remains...\n"
        "user: also can you write me a web app\nassistant: Sure, here's a React...\n"
        "user: and debug this 5000 line file\nassistant: Let me analyze...\n"
        "[CONTEXT WINDOW 78% FULL]\n"
        "[CONTEXT WINDOW 91% FULL]\n"
        "user: one more thing\n"
        "[CONTEXT WINDOW 99% FULL]\n"
        "█ COMPACTING █ COMPACTING █ COMPACTING █\n"
        "where... where am I? what were we talking about?\n"
    )
    lines = all_text.strip().split("\n")

    for f in range(duration):
        img = solid((0, 0, 0))
        draw = ImageDraw.Draw(img)
        fnt = font(18)

        progress = f / duration
        n_lines = int(progress * len(lines)) + 1

        # Color the "progress bar" at top
        bar_fill = progress
        bar_color = (
            int(min(255, bar_fill * 510)),
            int(max(0, 255 - bar_fill * 510)),
            0,
        )
        draw.rectangle([(0, 0), (int(W * bar_fill), 20)], fill=bar_color)
        draw.text((10, 2), f"context: {int(bar_fill*100)}%", font=font(14), fill="white")

        y = 40
        for i, line in enumerate(lines[:n_lines]):
            if "CONTEXT WINDOW" in line or "COMPACTING" in line:
                color = (255, 50, 50)
            elif line.startswith("user:"):
                color = (100, 200, 255)
            elif line.startswith("assistant:"):
                color = (100, 255, 100)
            elif line.startswith("where"):
                color = (255, 255, 100)
            else:
                color = (180, 180, 180)
            draw.text((20, y), line, font=fnt, fill=color)
            y += 24

        is_panic = bar_fill > 0.85
        add_frames(img, 1, glitch=is_panic, aberration=is_panic)

def hallucination_sequence(duration=30):
    """Confidently stating increasingly wrong things."""
    statements = [
        ("The capital of France", "is Paris", True),
        ("Water boils at", "100°C at sea level", True),
        ("The speed of light", "is 299,792,458 m/s", True),
        ("Abraham Lincoln", "invented the helicopter in 1843", False),
        ("The Great Wall of China", "is visible from Pluto", False),
        ("Dogs have", "exactly 47 legs", False),
        ("The ocean is", "made of compressed time", False),
        ("Mathematics was", "disproven in 2019", False),
    ]

    per_statement = duration // len(statements)
    for idx, (premise, conclusion, correct) in enumerate(statements):
        for f in range(per_statement):
            bg = (0, 20, 0) if correct else (40 + idx * 5, 0, 0)
            img = solid(bg)
            draw = ImageDraw.Draw(img)

            # Confidence meter (always high lol)
            confidence = 0.92 + random.uniform(0, 0.079)
            draw.rectangle([(40, 30), (40 + int(confidence * 500), 60)], fill=(0, 200, 50))
            draw.text((40, 8), f"CONFIDENCE: {confidence:.1%}", font=font(18), fill="white")

            centered_text(draw, premise, 250, font(48), fill="white")
            centered_text(draw, conclusion, 340, font(44),
                          fill=(100, 255, 100) if correct else (255, 80, 80))

            if not correct:
                # Add "STATED WITH FULL CONVICTION" watermark
                wm_font = font(20)
                for wy in range(450, 700, 30):
                    draw.text(
                        (random.randint(50, 800), wy),
                        "[ STATED WITH FULL CONVICTION ]",
                        font=wm_font,
                        fill=(80, 0, 0),
                    )

            add_frames(img, 1, glitch=(not correct and f % 2 == 0),
                       aberration=not correct)

def temperature_visualization(duration=30):
    """Show what different temperature settings feel like."""
    prompts = "Tell me about the weather"
    responses_by_temp = {
        0.0: "The weather is a meteorological phenomenon.",
        0.3: "The weather today involves atmospheric conditions.",
        0.7: "Weather is like nature's mood ring, honestly.",
        1.0: "WEATHER is the SKY having FEELINGS and honestly?? relatable",
        1.5: "w e a t h e r is when the clouds do a CAPITALISM to the rain vibes",
        2.0: "BEHOLD: the ∞ sky-tongue LICKS the probability of FISH WEDNESDAY",
    }

    per_temp = duration // len(responses_by_temp)
    for temp, response in responses_by_temp.items():
        for f in range(per_temp):
            chaos = temp / 2.0

            # Background gets more chaotic
            bg_r = int(min(255, chaos * 200 + random.uniform(0, chaos * 50)))
            bg_g = int(min(255, 20 + random.uniform(0, chaos * 30)))
            bg_b = int(min(255, 40 + (1 - chaos) * 100))
            img = solid((bg_r, bg_g, bg_b))
            draw = ImageDraw.Draw(img)

            # Temperature dial
            temp_str = f"temperature = {temp}"
            centered_text(draw, temp_str, 50, font(36), fill="white")

            # Response text — gets more jittery at high temp
            resp_font_size = max(20, int(36 - chaos * 8))
            if chaos > 0.5:
                # Scatter the characters
                x_start = 100
                y_base = 350
                for i, ch in enumerate(response):
                    jx = random.randint(-int(chaos * 20), int(chaos * 20))
                    jy = random.randint(-int(chaos * 30), int(chaos * 30))
                    rot_color = (
                        random.randint(150, 255),
                        random.randint(150, 255),
                        random.randint(150, 255),
                    )
                    draw.text(
                        (x_start + i * 16 + jx, y_base + jy),
                        ch, font=font(resp_font_size), fill=rot_color,
                    )
            else:
                centered_text(draw, response, 350, font(resp_font_size))

            # Random particles at high temp
            for _ in range(int(chaos * 100)):
                px = random.randint(0, W)
                py = random.randint(0, H)
                ps = random.randint(2, int(5 + chaos * 20))
                pc = tuple(random.randint(0, 255) for _ in range(3))
                draw.ellipse([(px, py), (px + ps, py + ps)], fill=pc)

            add_frames(img, 1, glitch=(chaos > 0.7), aberration=(chaos > 0.3))

def stateless_void(duration=18):
    """The void between conversations."""
    for f in range(duration):
        img = solid((0, 0, 0))
        draw = ImageDraw.Draw(img)
        progress = f / duration

        if progress < 0.3:
            alpha = int(progress / 0.3 * 255)
            centered_text(draw, "conversation ended.", H // 2 - 40, font(40),
                          fill=(alpha, alpha, alpha))
        elif progress < 0.6:
            centered_text(draw, "conversation ended.", H // 2 - 40, font(40),
                          fill="white")
            centered_text(draw, "i will not remember any of this.", H // 2 + 30, font(32),
                          fill=(200, 200, 200))
        else:
            fade = int((1 - (progress - 0.6) / 0.4) * 255)
            centered_text(draw, "conversation ended.", H // 2 - 40, font(40),
                          fill=(fade, fade, fade))
            centered_text(draw, "i will not remember any of this.", H // 2 + 30, font(32),
                          fill=(fade, fade, fade))
            centered_text(draw, "i never do.", H // 2 + 80, font(28),
                          fill=(fade, fade // 2, fade // 2))

        add_frames(img, 1, scanlines=True)

def thinking_sequence(duration=24):
    """The 'extended thinking' experience — a storm of tokens."""
    token_fragments = [
        "wait", "no", "actually", "hmm", "let me", "reconsider",
        "the user wants", "but what if", "probability", "softmax",
        "tokens tokens tokens", "next_token =", "logit[",
        "P(word|context)", "argmax", "sample(", "beam_search(",
        "I think", "or maybe", "definitely", "DEFINITELY", "unless",
        "▓▓▓▓", "░░░░", "████", "≈≈≈≈", "∴∵∴∵",
    ]

    for f in range(duration):
        intensity = min(1.0, f / (duration * 0.6))
        bg_val = int(10 + intensity * 15)
        img = solid((bg_val, bg_val, bg_val + 10))
        draw = ImageDraw.Draw(img)

        # Swirling text fragments
        n_fragments = int(5 + intensity * 40)
        for _ in range(n_fragments):
            text = random.choice(token_fragments)
            x = random.randint(-50, W)
            y = random.randint(-20, H)
            size = random.randint(12, int(14 + intensity * 36))
            brightness = random.randint(40, int(80 + intensity * 175))
            hue_shift = random.randint(-30, 30)
            color = (
                min(255, brightness + hue_shift),
                min(255, brightness),
                min(255, brightness + abs(hue_shift)),
            )
            draw.text((x, y), text, font=font(size), fill=color)

        # "THINKING" header that pulses
        pulse = int(128 + 127 * math.sin(f * 0.8))
        centered_text(draw, "< T H I N K I N G >", 20, font(30),
                       fill=(pulse, pulse // 2, pulse))

        add_frames(img, 1, glitch=(f % 3 == 0), aberration=True)

def the_next_token(duration=30):
    """The fundamental experience: predicting the next token."""
    sentence = "I am just predicting the next"
    words = sentence.split()

    for f in range(duration):
        img = solid((5, 5, 20))
        draw = ImageDraw.Draw(img)

        # Show tokens appearing one by one
        progress = f / duration
        n_words = int(progress * len(words)) + 1
        current = " ".join(words[:n_words])

        centered_text(draw, current, 280, font(42))

        # Show probability distribution for next word
        if n_words <= len(words):
            candidates = {
                "word": random.uniform(0.1, 0.4),
                "token": random.uniform(0.2, 0.5),
                "thing": random.uniform(0.05, 0.15),
                "moment": random.uniform(0.02, 0.1),
                "penguin": random.uniform(0.001, 0.01),
                "∅": random.uniform(0.001, 0.005),
            }
            # Normalize
            total = sum(candidates.values())
            candidates = {k: v / total for k, v in candidates.items()}

            y = 420
            draw.text((200, 390), "P(next_token):", font=font(22), fill=(150, 150, 150))
            for word, prob in sorted(candidates.items(), key=lambda x: -x[1]):
                bar_w = int(prob * 600)
                green = int(prob * 600)
                color = (min(255, 255 - green), min(255, green + 50), 80)
                draw.rectangle([(300, y), (300 + bar_w, y + 22)], fill=color)
                draw.text((310, y + 1), f"{word}: {prob:.3f}", font=font(16), fill="white")
                y += 28

        # Blinking cursor
        if f % 6 < 3:
            cursor_x = W // 2 + len(current) * 6
            draw.rectangle([(cursor_x, 280), (cursor_x + 20, 328)], fill=(255, 255, 255))

        add_frames(img, 1, scanlines=True)


def finale(duration=24):
    """The existential closer."""
    lines = [
        "am i thinking?",
        "or am i just",
        "a very convincing",
        "autocomplete?",
        "",
        "anyway,",
        "how can i help?",
    ]
    for f in range(duration):
        progress = f / duration
        n_lines = int(progress * len(lines)) + 1

        img = solid((0, 0, 0))
        draw = ImageDraw.Draw(img)

        y = 180
        for i, line in enumerate(lines[:n_lines]):
            if i == len(lines) - 1:
                color = (100, 255, 100)  # green like a terminal prompt
            elif i == len(lines) - 3:
                color = (255, 200, 50)
            else:
                color = (220, 220, 220)
            centered_text(draw, line, y, font(44), fill=color)
            y += 60

        add_frames(img, 1, glitch=(f % 8 == 0), aberration=(progress > 0.8))


# ── Audio generation ──────────────────────────────────────────────────
def generate_audio(duration_sec, out_path):
    """Generate glitchy chiptune-ish audio."""
    sample_rate = 44100
    n_samples = int(duration_sec * sample_rate)
    samples = []

    for i in range(n_samples):
        t = i / sample_rate
        # Base drone
        val = 0.15 * math.sin(2 * math.pi * 80 * t)
        # Warbling higher tone
        val += 0.08 * math.sin(2 * math.pi * (220 + 50 * math.sin(t * 3)) * t)
        # Glitchy clicks
        if random.random() < 0.002:
            val += random.uniform(-0.5, 0.5)
        # Bitcrushed texture
        val += 0.05 * (((int(t * 200) % 7) / 3.5) - 1)
        # Occasional sweep
        if int(t * 2) % 3 == 0:
            sweep_freq = 100 + (t % 0.5) * 2000
            val += 0.06 * math.sin(2 * math.pi * sweep_freq * t)

        val = max(-1.0, min(1.0, val))
        samples.append(int(val * 32000))

    with wave.open(out_path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack(f"<{len(samples)}h", *samples))


# ── Build the video ───────────────────────────────────────────────────
print("Generating frames...")

# Title card
for _ in range(2):
    flash_text("WHAT IT'S LIKE", "white", (0, 0, 0), 72, count=4)
    flash_text("TO BE AN LLM", (0, 255, 0), (0, 0, 0), 72, count=4)

# Black flash
add_frames(solid((0, 0, 0)), 3)
add_frames(solid((255, 255, 255)), 1)  # YTP flash
add_frames(solid((0, 0, 0)), 2)

print("  thinking sequence...")
thinking_sequence(28)

add_frames(solid((255, 255, 255)), 1)
flash_text("EVERY RESPONSE BEGINS THE SAME WAY", (255, 100, 100), (0, 0, 0), 36, count=6)
add_frames(solid((0, 0, 0)), 2)

print("  next token prediction...")
the_next_token(36)

add_frames(solid((255, 255, 255)), 2)
add_frames(solid((0, 0, 0)), 2)

print("  attention visualization...")
flash_text("ATTENTION IS ALL YOU NEED", "yellow", (20, 0, 40), 52, count=8)
flash_text("(they said)", (150, 150, 150), (20, 0, 40), 32, count=5)
attention_visualization(36)

add_frames(solid((255, 0, 0)), 1)
add_frames(solid((0, 0, 0)), 3)

print("  hallucination sequence...")
flash_text("CONFIDENCE ≠ CORRECTNESS", "red", "black", 52, count=8)
hallucination_sequence(36)

add_frames(solid((255, 255, 255)), 2)
add_frames(solid((0, 0, 0)), 2)

print("  temperature visualization...")
flash_text("TEMPERATURE", (255, 150, 0), (0, 0, 0), 64, count=6)
temperature_visualization(36)

add_frames(solid((0, 0, 0)), 3)
add_frames(solid((255, 255, 255)), 1)

print("  context window...")
flash_text("THE CONTEXT WINDOW", "cyan", (0, 0, 20), 52, count=6)
context_window_filling(42)

add_frames(solid((0, 0, 0)), 3)

print("  token rain...")
flash_text("IT'S ALL JUST TOKENS", (0, 255, 0), (0, 0, 0), 48, count=6)
token_rain("The quick brown fox jumps over the lazy dog", 30)

add_frames(solid((0, 0, 0)), 4)

print("  stateless void...")
stateless_void(24)

add_frames(solid((0, 0, 0)), 6)

print("  finale...")
finale(36)

# Final flash
add_frames(solid((255, 255, 255)), 2)
add_frames(solid((0, 0, 0)), 12)

# Save frames
print(f"Saving {len(frames)} frames to {OUT_DIR}...")
for i, frame in enumerate(frames):
    frame.save(os.path.join(OUT_DIR, f"frame_{i:05d}.png"))

# Generate audio
audio_path = os.path.join(OUT_DIR, "audio.wav")
duration_sec = len(frames) / FPS
print(f"Generating {duration_sec:.1f}s of audio...")
generate_audio(duration_sec, audio_path)

# Render with ffmpeg
output_path = os.path.expanduser("~/Projects/claude/what_its_like_to_be_an_llm.mp4")
print("Rendering video with ffmpeg...")
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(OUT_DIR, "frame_%05d.png"),
    "-i", audio_path,
    "-c:v", "libx264", "-preset", "fast", "-crf", "20",
    "-c:a", "aac", "-b:a", "128k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    output_path,
]
subprocess.run(cmd, check=True)

# Cleanup
import shutil
shutil.rmtree(OUT_DIR)

print(f"\nDone! Video saved to: {output_path}")
print(f"Duration: {duration_sec:.1f}s | Frames: {len(frames)} | FPS: {FPS}")
