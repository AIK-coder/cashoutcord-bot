from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from io import BytesIO
import aiohttp
import colorgram
import os

from config import *

# ==========================================
# COLOUR DETECTION
# ==========================================

def get_theme_colour():
    colours = colorgram.extract(BACKGROUND, 8)

    best = colours[0].rgb
    highest = 0

    for c in colours:
        rgb = c.rgb
        score = rgb.r + rgb.b

        if score > highest:
            highest = score
            best = rgb

    return (best.r, best.g, best.b)


# ==========================================
# DOWNLOAD AVATAR
# ==========================================

async def download_avatar(member):

    url = member.display_avatar.replace(size=512).url

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()

    avatar = Image.open(BytesIO(data)).convert("RGBA")
    return avatar


# ==========================================
# TEXT WITH SHADOW
# ==========================================

def draw_shadow_text(draw, pos, text, font, colour):

    x, y = pos

    draw.text(
        (x + 4, y + 4),
        text,
        font=font,
        fill=(0, 0, 0, 170),
        anchor="mm"
    )

    draw.text(
        (x, y),
        text,
        font=font,
        fill=colour,
        anchor="mm"
    )


# ==========================================
# CREATE CARD
# ==========================================

async def create_welcome_card(member):

    accent = get_theme_colour()

    background = Image.open(BACKGROUND).convert("RGBA")
    background = background.resize((CARD_WIDTH, CARD_HEIGHT))

    draw = ImageDraw.Draw(background)

    # ==========================================
    # PROFILE PICTURE
    # ==========================================

    avatar = await download_avatar(member)

    avatar = ImageOps.fit(
        avatar,
        (AVATAR_SIZE, AVATAR_SIZE),
        centering=(0.5, 0.5)
    )

    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)

    ImageDraw.Draw(mask).ellipse(
        (0, 0, AVATAR_SIZE, AVATAR_SIZE),
        fill=255
    )

    avatar.putalpha(mask)

    centre_x = CARD_WIDTH // 2
    centre_y = 370

    ring = Image.new(
        "RGBA",
        (RING_SIZE, RING_SIZE),
        (0, 0, 0, 0)
    )

    rd = ImageDraw.Draw(ring)

    rd.ellipse(
        (
            RING_THICKNESS,
            RING_THICKNESS,
            RING_SIZE - RING_THICKNESS,
            RING_SIZE - RING_THICKNESS
        ),
        outline=accent,
        width=RING_THICKNESS
    )

    glow = ring.filter(
        ImageFilter.GaussianBlur(GLOW_STRENGTH)
    )

    background.alpha_composite(
        glow,
        (
            centre_x - RING_SIZE // 2,
            centre_y - RING_SIZE // 2
        )
    )

    background.alpha_composite(
        ring,
        (
            centre_x - RING_SIZE // 2,
            centre_y - RING_SIZE // 2
        )
    )

    background.alpha_composite(
        avatar,
        (
            centre_x - AVATAR_SIZE // 2,
            centre_y - AVATAR_SIZE // 2
        )
    )

    # ==========================================
    # DARK GLASS PANEL
    # ==========================================

    glass = Image.new(
        "RGBA",
        background.size,
        (0, 0, 0, 0)
    )

    gd = ImageDraw.Draw(glass)

    gd.rounded_rectangle(
        (
            250,
            620,
            CARD_WIDTH - 250,
            CARD_HEIGHT - 120
        ),
        radius=40,
        fill=(0, 0, 0, 120)
    )

    background.alpha_composite(glass)


    # ==========================================
    # FONTS
    # ==========================================

    title_font = ImageFont.truetype(
        TITLE_FONT,
        82
    )

    username_font = ImageFont.truetype(
        TEXT_FONT,
        56
    )

    member_font = ImageFont.truetype(
        TEXT_FONT,
        34
    )

    # ==========================================
    # TEXT
    # ==========================================

    username = member.display_name

    heading = "WELCOME TO CASHOUT RP"

    member_count = f"Member #{member.guild.member_count}"

    draw_shadow_text(
        draw,
        (CARD_WIDTH // 2, 705),
        heading,
        title_font,
        TEXT_COLOUR
    )

    draw_shadow_text(
        draw,
        (CARD_WIDTH // 2, 785),
        username,
        username_font,
        (245, 245, 245)
    )

    draw_shadow_text(
        draw,
        (CARD_WIDTH // 2, 845),
        member_count,
        member_font,
        SUBTEXT_COLOUR
    )

    # ==========================================
    # HIGHLIGHT RING
    # ==========================================

    highlight = Image.new(
        "RGBA",
        background.size,
        (0, 0, 0, 0)
    )

    hd = ImageDraw.Draw(highlight)

    r = RING_SIZE // 2

    hd.ellipse(
        (
            centre_x - r,
            centre_y - r,
            centre_x + r,
            centre_y + r
        ),
        outline=(255, 255, 255, 120),
        width=3
    )

    highlight = highlight.filter(
        ImageFilter.GaussianBlur(2)
    )

    background.alpha_composite(highlight)

    # ==========================================
    # SAVE IMAGE
    # ==========================================

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    output = os.path.join(
        OUTPUT_FOLDER,
        f"{member.id}.png"
    )

    background.save(
        output,
        quality=100
    )

    return output