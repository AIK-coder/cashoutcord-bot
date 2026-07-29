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
# AVATAR DOWNLOAD
# ==========================================

async def download_avatar(member):

    url = member.display_avatar.replace(size=512).url

    async with aiohttp.ClientSession() as session:

        async with session.get(url) as response:

            data = await response.read()

    return Image.open(BytesIO(data)).convert("RGBA")


# ==========================================
# CIRCLE CROP
# ==========================================

def circle_crop(image):

    image = image.resize((AVATAR_SIZE, AVATAR_SIZE))

    mask = Image.new("L", (AVATAR_SIZE, AVATAR_SIZE), 0)

    draw = ImageDraw.Draw(mask)

    draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)

    output = Image.new("RGBA", (AVATAR_SIZE, AVATAR_SIZE))

    output.paste(image, (0, 0), mask)

    return output


# ==========================================
# GLOW
# ==========================================

def draw_glow(canvas, centre, colour):

    glow = Image.new("RGBA", canvas.size, (0,0,0,0))

    draw = ImageDraw.Draw(glow)

    radius = RING_SIZE // 2

    for i in range(GLOW_STRENGTH):

        alpha = max(0, 170 - i * 3)

        draw.ellipse(

            (
                centre[0]-radius-i,
                centre[1]-radius-i,
                centre[0]+radius+i,
                centre[1]+radius+i,
            ),

            outline=colour + (alpha,),
            width=8,
        )

    glow = glow.filter(ImageFilter.GaussianBlur(16))

    canvas.alpha_composite(glow)


# ==========================================
# RING
# ==========================================

def draw_ring(canvas, centre, colour):

    draw = ImageDraw.Draw(canvas)

    radius = RING_SIZE // 2

    draw.ellipse(

        (
            centre[0]-radius,
            centre[1]-radius,
            centre[0]+radius,
            centre[1]+radius,
        ),

        outline=colour,
        width=RING_THICKNESS,
    )


# ==========================================
# SHADOW TEXT
# ==========================================

def draw_shadow_text(draw, position, text, font, fill, shadow=(0, 0, 0), offset=4):

    x, y = position

    draw.text(
        (x + offset, y + offset),
        text,
        font=font,
        fill=shadow,
        anchor="mm"
    )

    draw.text(
        (x, y),
        text,
        font=font,
        fill=fill,
        anchor="mm"
    )


# ==========================================
# WELCOME CARD
# ==========================================

async def create_welcome_card(member):

    background = Image.open(BACKGROUND).convert("RGBA")

    background = background.resize((CARD_WIDTH, CARD_HEIGHT))

    theme = get_theme_colour()

    avatar = await download_avatar(member)

    avatar = circle_crop(avatar)

    centre_x = CARD_WIDTH // 2
    centre_y = 310

    draw_glow(
        background,
        (centre_x, centre_y),
        theme
    )

    draw_ring(
        background,
        (centre_x, centre_y),
        theme
    )

    avatar_x = centre_x - AVATAR_SIZE // 2
    avatar_y = centre_y - AVATAR_SIZE // 2

    background.alpha_composite(
        avatar,
        (avatar_x, avatar_y)
    )

    draw = ImageDraw.Draw(background)

    title_font = ImageFont.truetype(
        TITLE_FONT,
        82
    )

    username_font = ImageFont.truetype(
        TEXT_FONT,
        42
    )

    member_font = ImageFont.truetype(
        TEXT_FONT,
        30
    )


    username = member.display_name

    heading = "JUST JOINED THE SERVER"

    member_count = f"Member #{member.guild.member_count}"

    draw_shadow_text(
        draw,
        (CARD_WIDTH // 2, 690),
        heading,
        title_font,
        TEXT_COLOUR
    )

    draw_shadow_text(
        draw,
        (CARD_WIDTH // 2, 785),
        username,
        username_font,
        (235, 235, 235)
    )

    draw_shadow_text(
        draw,
        (CARD_WIDTH // 2, 845),
        member_count,
        member_font,
        SUBTEXT_COLOUR
    )

    # Small highlight ring

    highlight = Image.new("RGBA", background.size, (0, 0, 0, 0))

    hd = ImageDraw.Draw(highlight)

    r = RING_SIZE // 2

    hd.ellipse(

        (

            centre_x - r,

            centre_y - r,

            centre_x + r,

            centre_y + r,

        ),

        outline=(255, 255, 255, 130),

        width=4

    )

    highlight = highlight.filter(ImageFilter.GaussianBlur(2))

    background.alpha_composite(highlight)

    # Sharpen slightly

    background = background.filter(ImageFilter.SHARPEN)

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    output = os.path.join(

        OUTPUT_FOLDER,

        f"{member.id}.png"

    )

    background.save(output, quality=100)

    return output