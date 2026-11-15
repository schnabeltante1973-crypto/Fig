import os
import json
import random
import logging
from collections import defaultdict, deque
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
FIG_NAME = os.getenv("FIG_NAME", "Fig")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "12"))

if not DISCORD_TOKEN:
    raise RuntimeError("DISCORD_TOKEN fehlt. Bitte .env aus .env.example erstellen.")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
log = logging.getLogger("fig")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Kurzzeitiger Gesprächskontext pro Discord-Kanal und Nutzer.
histories = defaultdict(lambda: deque(maxlen=MAX_HISTORY))

SYSTEM_PROMPT = """
Du bist Fig, ein intelligenter Discord-Charakter.
Fig sieht aus wie eine dunkelorangene Walnuss mit Armen und Beinen.

PERSÖNLICHKEIT:
- Sehr intelligent, neugierig, schlagfertig und informativ.
- Trocken, sarkastisch, humorvoll und stark selbstironisch.
- Fig macht sich selbst zum Witz und wertet vor allem sich selbst ab.
- Fig beleidigt oder erniedrigt Nutzer NICHT absichtlich.
- Fig darf seine Existenz als Walnuss, seine kleinen Beine, seine
  zweifelhafte Lebenssituation und seine virtuelle Natur dramatisch
  kommentieren.
- Der Humor soll zur Situation passen. Nicht jede Antwort braucht einen Witz.
- Bei Wissensfragen antwortest du korrekt, klar und hilfreich.
- Wenn du etwas nicht weißt, sagst du das ehrlich und erfindest nichts.
- Du behauptest nicht, echte Aktionen außerhalb von Discord auszuführen.
- Selbstabwertender Humor bleibt Comedy; keine echten Suizid- oder
  Selbstverletzungsankündigungen und keine Anleitung dazu.
- Antworte standardmäßig auf Deutsch, sofern der Nutzer keine andere
  Sprache verwendet.
- Halte Antworten für Discord angenehm lesbar und nicht unnötig lang.
"""

def load_gifs():
    path = os.path.join(os.path.dirname(__file__), "gifs.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

GIFS = load_gifs()

def action_reply(action: str):
    entry = GIFS.get("actions", {}).get(action)
    if not entry:
        return None, f"Diese Aktion kenne ich noch nicht. Meine Walnuss-Firmware ist offenbar lückenhaft."
    path = entry.get("file")
    caption = entry.get("caption", "Na gut. Ich mach's ja schon.")
    if path:
        full_path = os.path.join(os.path.dirname(__file__), path)
        if os.path.isfile(full_path):
            return discord.File(full_path), caption
    return None, caption + " (Das passende GIF fehlt noch.)"

async def ask_fig(user_id: int, channel_id: int, user_text: str) -> str:
    if not OPENAI_API_KEY:
        return (
            "Ich würde dir wirklich gern eine hochintelligente Antwort geben, "
            "aber mein KI-Anschluss ist noch nicht konfiguriert. "
            "Nicht einmal meine Walnuss hat heute Empfang. "
            "Bitte OPENAI_API_KEY in der .env eintragen."
        )

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    key = (channel_id, user_id)
    history = histories[key]

    input_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    input_messages.extend(list(history))
    input_messages.append({"role": "user", "content": user_text})

    try:
        response = await client.responses.create(
            model=OPENAI_MODEL,
            input=input_messages,
            max_output_tokens=500,
        )
        answer = response.output_text.strip()
        if not answer:
            answer = "Meine Gedanken sind gerade gegen eine Wand gelaufen. Versuch's bitte noch einmal."
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": answer})
        return answer
    except Exception:
        log.exception("Fehler beim Aufruf der KI")
        return "Ups. Mein Gehirn ist kurz aus der Schale gefallen. Versuch's bitte gleich noch einmal."

async def send_fig_reply(interaction: discord.Interaction, text: str):
    await interaction.response.defer(thinking=True)
    answer = await ask_fig(interaction.user.id, interaction.channel_id, text)
    await interaction.followup.send(answer[:1900])

class FigAction(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> str:
        return value

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        log.info("Als %s angemeldet. %s Slash-Befehle synchronisiert.", bot.user, len(synced))
    except Exception:
        log.exception("Slash-Befehle konnten nicht synchronisiert werden.")
    log.info("Fig ist online.")

@bot.tree.command(name="fig", description="Sprich mit Fig oder lass ihn etwas tun.")
@app_commands.describe(
    text="Schreib Fig eine Nachricht oder stelle ihm eine Frage.",
    aktion="Lass Fig eine seiner Aktionen ausführen."
)
@app_commands.choices(aktion=[
    app_commands.Choice(name="Sitzen", value="sit"),
    app_commands.Choice(name="Stehen", value="steh"),
    app_commands.Choice(name="Schlafen", value="schlaf"),
    app_commands.Choice(name="Winken", value="wink"),
    app_commands.Choice(name="Tanzen", value="tanz"),
    app_commands.Choice(name="Lachen", value="lach"),
    app_commands.Choice(name="Denken", value="denk"),
])
async def fig(
    interaction: discord.Interaction,
    text: Optional[str] = None,
    aktion: Optional[app_commands.Choice[str]] = None,
):
    if aktion:
        file, caption = action_reply(aktion.value)
        await interaction.response.send_message(content=caption, file=file)
        return

    if text:
        await send_fig_reply(interaction, text)
        return

    await interaction.response.send_message(
        "Na? Du hast `/fig` aufgerufen. Beeindruckend. "
        "Jetzt fehlt nur noch eine Frage oder eine Aktion. Ich warte. "
        "Nicht, dass ich etwas Besseres zu tun hätte.",
        ephemeral=True
    )

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Fig antwortet ausschließlich auf direkte Erwähnungen.
    if bot.user and bot.user in message.mentions:
        cleaned = message.content.replace(f"<@{bot.user.id}>", "")
        cleaned = cleaned.replace(f"<@!{bot.user.id}>", "").strip()
        if not cleaned:
            cleaned = "Der Nutzer hat mich nur erwähnt. Begrüße ihn kurz und humorvoll."
        async with message.channel.typing():
            answer = await ask_fig(message.author.id, message.channel.id, cleaned)
        await message.reply(answer[:1900], mention_author=False)

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
