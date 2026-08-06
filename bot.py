import discord 
import os
import json
import logging
import sys
import random
import asyncio
import aiohttp
import wavelink
import io
import uuid
import re
import codecs
import zipfile
import stat
import subprocess
from PIL import Image, ImageDraw, ImageFont
import textwrap
from gtts import gTTS
from datetime import timedelta, datetime, timezone

# Supabase Env Variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
from typing import Union
from discord.ext import commands
from discord import app_commands
from playwright.async_api import async_playwright

# Playwright Global Variables
playwright_instance = None
browser_instance = None
active_browsers = {} # Stores the active webpage for each Discord channel
active_shadow_threads = {}
active_tester_tasks = {}
deleted_messages_cache = {}

# ==========================================
# 0. DATABASE & CACHE SETUP
# ==========================================
import os

# Create a data directory so the bot saves files inside the Railway Volume
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

HONEYPOT_FILE = os.path.join(DATA_DIR, "honeypots.json")
WARNINGS_FILE = os.path.join(DATA_DIR, "warnings.json")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
AFK_FILE = os.path.join(DATA_DIR, "afk.json")
PERMS_FILE = os.path.join(DATA_DIR, "perms.json")
MUTED_ADMINS_FILE = os.path.join(DATA_DIR, "muted_admins.json")
UWULOCK_FILE = os.path.join(DATA_DIR, "uwulock.json")
QUOTAS_FILE = os.path.join(DATA_DIR, "quotas.json")
WHITELIST_FILE = os.path.join(DATA_DIR, "whitelist.json")
PRIORITY_WHITELIST_FILE = os.path.join(DATA_DIR, "priority_whitelist.json")
UMARIZZ_FILE = os.path.join(DATA_DIR, "umarizz.json")
TESTER_KEYS_FILE = os.path.join(DATA_DIR, "tester_keys.json")
SHADOW_THREADS_FILE = os.path.join(DATA_DIR, "shadow_threads.json")
HWID_COOLDOWNS_FILE = os.path.join(DATA_DIR, "hwid_cooldowns.json")
PGLOCK_FILE = os.path.join(DATA_DIR, "pglock.json")
TRANSLATE_FILE = os.path.join(DATA_DIR, "translate.json") # <--- ADD THIS LINE
FORCENICK_FILE = os.path.join(DATA_DIR, "forcenick.json")
# Auto-generate umarizz.json if it's missing (with the fixed syntax)
UMARIZZ_DEFAULT_DATA = {
  "umamusume_pickup_lines": [
    {"id": 1, "category": "The Trainer's Menu (General Lines)", "line": "Are you a Trainer? Because my heart starts racing the moment you're around."},
    {"id": 2, "category": "The Trainer's Menu (General Lines)", "line": "Are you the URA Finals? Because you're my ultimate goal."},
    {"id": 3, "category": "The Trainer's Menu (General Lines)", "line": "My stamina might be at an E, but my love for you is always S+."},
    {"id": 4, "category": "The Trainer's Menu (General Lines)", "line": "Forget the training menu - my only plan today is spending time with you."},
    {"id": 5, "category": "The Trainer's Menu (General Lines)", "line": "Are you a rainbow gate? Because seeing you guarantees it's going to be a good day."},
    {"id": 6, "category": "The Trainer's Menu (General Lines)", "line": "I must have maxed out my wisdom stat, because choosing you was the smartest thing I've ever done."},
    {"id": 7, "category": "The Trainer's Menu (General Lines)", "line": "Are you an alarm clock? Because you just gave me a second chance at love."},
    {"id": 8, "category": "The Trainer's Menu (General Lines)", "line": "My motivation just went from Hopeless to Perfect the second you walked in."},
    {"id": 9, "category": "The Trainer's Menu (General Lines)", "line": "I don't need a high-speed summer training camp if I can just spend the season with you."},
    {"id": 10, "category": "The Trainer's Menu (General Lines)", "line": "You must be an Inherited Factor, because you've completely changed my traits for the better."},
    {"id": 11, "category": "Character-Specific Charmers", "line": "Are you Special Week? Because you're the best in Japan in my eyes."},
    {"id": 12, "category": "Character-Specific Charmers", "line": "Are you Silence Suzuka? Because you took my breath away on the very first turn."},
    {"id": 13, "category": "Character-Specific Charmers", "line": "Call me Gold Ship, because I'm ready to drop-kick my way directly into your heart."},
    {"id": 14, "category": "Character-Specific Charmers", "line": "Are you Tokai Teio? Because you've got me skipping with joy."},
    {"id": 15, "category": "Character-Specific Charmers", "line": "Are you Oguri Cap? Because my hunger for your love is absolutely insatiable."},
    {"id": 16, "category": "Character-Specific Charmers", "line": "Are you Rice Shower? Because you've blessed my life, no matter what anyone else says."},
    {"id": 17, "category": "Character-Specific Charmers", "line": "Are you Mejiro McQueen? Because you've got elegance written all over you - let me buy you some sweets."},
    {"id": 18, "category": "Character-Specific Charmers", "line": "Are you Twin Turbo? Because I'm going all-out from the very start with you."},
    {"id": 19, "category": "Character-Specific Charmers", "line": "Are you Mihono Bourbon? Because my heart is programmed to love only you."},
    {"id": 20, "category": "Character-Specific Charmers", "line": "Are you Daiwa Scarlet? Because you'll always be number one to me."},
    {"id": 21, "category": "Character-Specific Charmers", "line": "Are you Vodka? Because you're absolutely intoxicating."},
    {"id": 22, "category": "Character-Specific Charmers", "line": "Are you Gold City? Because you look like a literal runway model."},
    {"id": 23, "category": "Character-Specific Charmers", "line": "Are you Agnes Tachyon? Because the chemistry between us is undeniable."},
    {"id": 24, "category": "Character-Specific Charmers", "line": "Are you Manhattan Cafe? Because you're brewing up a lot of deep feelings in me."},
    {"id": 25, "category": "Character-Specific Charmers", "line": "Are you El Condor Pasa? Because our love is burning like a fiery luchador."},
    {"id": 26, "category": "Character-Specific Charmers", "line": "Are you Grass Wonder? Because you look calm, but you've completely conquered my heart."},
    {"id": 27, "category": "Character-Specific Charmers", "line": "Are you King Halo? Because you deserve a royal place in my life."},
    {"id": 28, "category": "Character-Specific Charmers", "line": "Are you Nice Nature? Because even if you think you're third place, you're always first to me."},
    {"id": 29, "category": "Character-Specific Charmers", "line": "Are you Symboli Rudolf? Because you're the absolute Emperor of my heart."},
    {"id": 30, "category": "Character-Specific Charmers", "line": "Are you Maruzensky? Because you're super-car fast at stealing my feelings."},
    {"id": 31, "category": "Character-Specific Charmers", "line": "Are you Mayano Top Gun? Because you've got me flying high in the clouds."},
    {"id": 32, "category": "Character-Specific Charmers", "line": "Are you Super Creek? Because I could really use some of your pampering right now."},
    {"id": 33, "category": "Character-Specific Charmers", "line": "Are you Tamamo Cross? Because you're a small package with a whole lot of impact."},
    {"id": 34, "category": "Character-Specific Charmers", "line": "Are you Fine Motion? Because our connection feels like a royal decree."},
    {"id": 35, "category": "Character-Specific Charmers", "line": "Are you Air Groove? Because you've got absolute control over my heart's climate."},
    {"id": 36, "category": "Character-Specific Charmers", "line": "Are you Eishin Flash? Because everything with you is perfectly timed and precise."},
    {"id": 37, "category": "Character-Specific Charmers", "line": "Are you Smart Falcon? Because you're the ultimate center idol of my world."},
    {"id": 38, "category": "Character-Specific Charmers", "line": "Are you Curren Chan? Because you've completely captured my feed and my heart."},
    {"id": 39, "category": "Character-Specific Charmers", "line": "Are you Kitasan Black? Because you bring festival energy wherever you go."},
    {"id": 40, "category": "Character-Specific Charmers", "line": "Are you Satono Diamond? Because you're a rare gem I want to cherish forever."},
    {"id": 41, "category": "Track Conditions & Race Strategy", "line": "Are you a turf track? Because I'm falling for you smoothly."},
    {"id": 42, "category": "Track Conditions & Race Strategy", "line": "Even if the track condition is Bad, my feelings for you are always Good."},
    {"id": 43, "category": "Track Conditions & Race Strategy", "line": "Are you the final straight? Because I'm giving it everything I've got to catch up to you."},
    {"id": 44, "category": "Track Conditions & Race Strategy", "line": "Forget the inner track, I want to take the long way around just to spend more time with you."},
    {"id": 45, "category": "Track Conditions & Race Strategy", "line": "Are you the Arima Kinen? Because you're the grand finale I've been waiting for all year."},
    {"id": 46, "category": "Track Conditions & Race Strategy", "line": "Are you the Japan Cup? Because you've attracted international attention, but I only have eyes for you."},
    {"id": 47, "category": "Track Conditions & Race Strategy", "line": "I'd run through a muddy dirt track just to see you smile."},
    {"id": 48, "category": "Track Conditions & Race Strategy", "line": "Are you an uphill slope? Because you make my heart beat faster and harder."},
    {"id": 49, "category": "Track Conditions & Race Strategy", "line": "Are you the starting gate? Because I'm ready to burst out and chase you down."},
    {"id": 50, "category": "Track Conditions & Race Strategy", "line": "You must be a 2400m race, because I'm in this relationship for the long haul."},
    {"id": 51, "category": "Skills & Stat Check", "line": "Did you just activate Maestro of the Corner? Because you smoothly navigated right into my heart."},
    {"id": 52, "category": "Skills & Stat Check", "line": "You must have the Charisma skill, because I literally cannot look away."},
    {"id": 53, "category": "Skills & Stat Check", "line": "My speed stat just broke the limit when you smiled at me."},
    {"id": 54, "category": "Skills & Stat Check", "line": "Are you a unique skill? Because you're absolutely one of a kind."},
    {"id": 55, "category": "Skills & Stat Check", "line": "I don't need Sprint Turbo to rush over to your side."},
    {"id": 56, "category": "Skills & Stat Check", "line": "You must have Tailwind, because you're pushing me in all the right directions."},
    {"id": 57, "category": "Skills & Stat Check", "line": "Are you a debuff skill? Because you've completely paralyzed me with your looks."},
    {"id": 58, "category": "Skills & Stat Check", "line": "I've got max stamina, but you still somehow leave me completely breathless."},
    {"id": 59, "category": "Skills & Stat Check", "line": "Are you Guts? Because you give me the strength to keep going when things get tough."},
    {"id": 60, "category": "Skills & Stat Check", "line": "Let's trigger a dynamic camera angle, because you look stunning from every single direction."},
    {"id": 61, "category": "Winning Live & Idol Status", "line": "Are you the center position? Because you're the star of my show."},
    {"id": 62, "category": "Winning Live & Idol Status", "line": "I'd win every G1 race on the calendar just to see you perform in the Winning Live."},
    {"id": 63, "category": "Winning Live & Idol Status", "line": "Are you Make debut? Because this is the start of something beautiful."},
    {"id": 64, "category": "Winning Live & Idol Status", "line": "My heart rate matches the beat of GIRLS' LEGEND U whenever you're near."},
    {"id": 65, "category": "Winning Live & Idol Status", "line": "Are you a glow stick? Because you light up my entire world."},
    {"id": 66, "category": "Winning Live & Idol Status", "line": "Forget the concert crowd, I'm only cheering for you."},
    {"id": 67, "category": "Winning Live & Idol Status", "line": "Are you a Triple Crown? Because you're a rare achievement I'd love to win."},
    {"id": 68, "category": "Winning Live & Idol Status", "line": "You don't need a microphone to make your voice the only thing I hear."},
    {"id": 69, "category": "Winning Live & Idol Status", "line": "Let's duet on the center stage of my heart."},
    {"id": 70, "category": "Winning Live & Idol Status", "line": "You're the encore I'll always ask for."},
    {"id": 71, "category": "Items, Food & Fuel", "line": "Are you a giant carrot? Because you're exactly what I've been looking for."},
    {"id": 72, "category": "Items, Food & Fuel", "line": "You're sweeter than a freshly baked Mejiro macaron."},
    {"id": 73, "category": "Items, Food & Fuel", "line": "Are you a carrot burger? Because you're the perfect treat after a long, exhausting day."},
    {"id": 74, "category": "Items, Food & Fuel", "line": "I'd share my very last carrot juice with you."},
    {"id": 75, "category": "Items, Food & Fuel", "line": "Are you a lucky charm? Because my chances of success skyrocket when you're around."},
    {"id": 76, "category": "Items, Food & Fuel", "line": "You must be a royal parfait, because you just maxed out my motivation levels."},
    {"id": 77, "category": "Items, Food & Fuel", "line": "Forget the training weights, you're the only thing heavy on my mind."},
    {"id": 78, "category": "Items, Food & Fuel", "line": "Are you a strategy playbook? Because I want to study your every move."},
    {"id": 79, "category": "Items, Food & Fuel", "line": "You're like a high-grade energy drink - one look at you and I'm fully charged."},
    {"id": 80, "category": "Items, Food & Fuel", "line": "Are you a secret stash of snacks? Because finding you made my whole week."},
    {"id": 81, "category": "Playful Puns & Pacing", "line": "Are you a front-runner? Because you're way ahead of anyone else."},
    {"id": 82, "category": "Playful Puns & Pacing", "line": "I might be a betweener, but I'm ready to make a definitive move on you."},
    {"id": 83, "category": "Playful Puns & Pacing", "line": "Are you a chaser? Because you've been running through my mind all day long."},
    {"id": 84, "category": "Playful Puns & Pacing", "line": "I promise I won't block your path; I just want to run right beside you."},
    {"id": 85, "category": "Playful Puns & Pacing", "line": "Are you a photo finish? Because it's incredibly close, but you win every single time."},
    {"id": 86, "category": "Playful Puns & Pacing", "line": "You must be Tazuna-san, because you always know exactly how to guide me back on track."},
    {"id": 87, "category": "Playful Puns & Pacing", "line": "Are you President Akikawa? Because you've got fan-favorite written all over you."},
    {"id": 88, "category": "Playful Puns & Pacing", "line": "My love for you has a 100% success rate - absolutely zero training failure risk here."},
    {"id": 89, "category": "Playful Puns & Pacing", "line": "Are you the green light on the gate? Because you've got me ready to go."},
    {"id": 90, "category": "Playful Puns & Pacing", "line": "I must be out of stamina, because I'm falling incredibly hard for you."},
    {"id": 91, "category": "Playful Puns & Pacing", "line": "Are you a 5-star awakening? Because you've reached peak absolute perfection."},
    {"id": 92, "category": "Playful Puns & Pacing", "line": "You don't need lucky horseshoes to leave a permanent impression on my heart."},
    {"id": 93, "category": "Playful Puns & Pacing", "line": "Are you a critical hit in training? Because you just boosted my stats immensely."},
    {"id": 94, "category": "Playful Puns & Pacing", "line": "Even if I get a bad status condition, you're the only cure I'll ever need."},
    {"id": 95, "category": "Playful Puns & Pacing", "line": "Are you the URA trophy? Because I want to hold you high for everyone to see."},
    {"id": 96, "category": "Playful Puns & Pacing", "line": "You've got me running at a record-breaking pace just to keep up with your beauty."},
    {"id": 97, "category": "Playful Puns & Pacing", "line": "Are you a limited-time gacha banner? Because I'm willing to spend everything I have to get you."},
    {"id": 98, "category": "Playful Puns & Pacing", "line": "My heart is doing a full sprint, and there's no deceleration in sight."},
    {"id": 99, "category": "Playful Puns & Pacing", "line": "Are you a stable? Because I feel completely safe and at home with you."},
    {"id": 100, "category": "Playful Puns & Pacing", "line": "Let's cross the finish line together, because you're my ultimate prize."}
  ]
}

if not os.path.exists(UMARIZZ_FILE):
    with open(UMARIZZ_FILE, "w", encoding="utf-8") as f:
        json.dump(UMARIZZ_DEFAULT_DATA, f, indent=4)

# Important Role IDs
ROLE_SCRIPT_USER_ID = 1500435366812061844
ROLE_VERIFIED_ID = 1507442109735633097

# In-memory caches
purged_messages_cache = {}
active_unpurges = {}
active_badapples = {}
user_cooldowns = {}
mod_slur_warnings = {} 
owner_skip_cooldowns = {} # Music Owner Skip Protection Cooldown

def load_json(filename, default_type=list):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_type()

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def load_honeypots(): return load_json(HONEYPOT_FILE, list)
def save_honeypots(data): save_json(HONEYPOT_FILE, data)

class DynamicRateLimitError(commands.CheckFailure):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

HWID_COOLDOWNS_FILE = "hwid_cooldowns.json"

async def supabase_request(method, endpoint, json_data=None):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("missing supabase credentials!")
        return None
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, headers=headers, json=json_data) as response:
                if response.status in [200, 201, 204]:
                    try: return await response.json()
                    except: return True
                print(f"supabase error: {response.status} - {await response.text()}")
                return None
    except Exception as e:
        print(f"supabase connection failed: {e}")
        return None

# ==========================================
# 1. VIEWS & MODALS
# ==========================================

VERIFICATION_URL = "https://sedse.pages.dev"

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="verify with discord", url=VERIFICATION_URL, style=discord.ButtonStyle.link
        ))

class snipedropdown(discord.ui.Select):
    def __init__(self, messages_data, user_id):
        self.messages_data = messages_data
        self.user_id = user_id
        options = []
        
        # discord limit is 25 options per dropdown, taking the newest 25
        recent_msgs = list(reversed(messages_data))[:25]
        for msg in recent_msgs:
            label = f"{msg['author_name']}: {msg['content']}"
            if len(label) > 100:
                label = label[:97] + "..."
            options.append(discord.SelectOption(
                label=label.lower(),
                value=str(msg['id'])
            ))
        super().__init__(placeholder="select a deleted message...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message("this menu is not for you.", ephemeral=True)
        
        msg_id = int(self.values[0])
        target_msg = next((m for m in self.messages_data if m['id'] == msg_id), None)
        if not target_msg:
            return await interaction.response.send_message("couldn't find that message.", ephemeral=True)
        
        await interaction.response.defer()
        
        channel = interaction.channel
        webhooks = await channel.webhooks()
        webhook = discord.utils.get(webhooks, name="sedse impersonator") or await channel.create_webhook(name="sedse impersonator")
        
        content = f"{target_msg['content']}\n\n[sniped by {interaction.user.mention}]".lower()
        try:
            await webhook.send(
                content=content,
                username=target_msg['author_name'].lower(),
                avatar_url=target_msg['author_avatar']
            )
            # delete the dropdown menu after clicking to keep chat clean
            try:
                await interaction.message.delete()
            except:
                pass
        except Exception as e:
            await interaction.followup.send(f"failed to snipe: {e}".lower(), ephemeral=True)

class snipeview(discord.ui.View):
    def __init__(self, messages_data, user_id):
        super().__init__(timeout=60)
        self.add_item(snipedropdown(messages_data, user_id))
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except:
                pass

class JJSDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="sedse jjs script", description="click here for the sedse jjs script", value="sedse_jjs"),
            discord.SelectOption(label="jjs piano", description="click here for info on jjs piano", value="jjs_piano"),
            discord.SelectOption(label="jjs piano open source", description="click here for info on the open source version", value="jjs_piano_os")
        ]
        super().__init__(placeholder="choose a script...", min_values=1, max_values=1, options=options, custom_id="persistent_jjs_dropdown")

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "sedse_jjs":
            response_text = """here's the sedse jjs script:
`
local key = "KEY_HERE"
loadstring(game:HttpGet("https://keyxyz-sedse.pages.dev/v1/load?key=" .. game:GetService("HttpService"):UrlEncode(key) .. "&_cb=" .. tostring(os.clock())))()
`"""
        elif self.values[0] == "jjs_piano":
            response_text = "here's the info and link for jjs piano:\n`loadstring(game:HttpGet('https://raw.githubusercontent.com/SedseXD/piano/refs/heads/main/pianoscript.lua'))()`"
        elif self.values[0] == "jjs_piano_os":
            response_text = "here's the github link and info for jjs piano open source:\nhttps://raw.githubusercontent.com/SedseXD/piano/refs/heads/main/pianoscript.lua"
            
        await interaction.response.send_message(response_text, ephemeral=True)



class JJSView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(JJSDropdown())

class HoneypotView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="enable honeypot", style=discord.ButtonStyle.green, custom_id="hp_enable_btn")
    async def enable_honeypot(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("only admins can mess with this.", ephemeral=True)
        if interaction.channel.id not in bot.honeypot_channels:
            bot.honeypot_channels.append(interaction.channel.id)
            save_honeypots(bot.honeypot_channels)
            await interaction.response.send_message("honeypot is up and running in here.", ephemeral=True)
        else:
            await interaction.response.send_message("honeypot is already on in this channel, chill.", ephemeral=True)

    @discord.ui.button(label="disable honeypot", style=discord.ButtonStyle.red, custom_id="hp_disable_btn")
    async def disable_honeypot(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("only admins can mess with this.", ephemeral=True)
        if interaction.channel.id in bot.honeypot_channels:
            bot.honeypot_channels.remove(interaction.channel.id)
            save_honeypots(bot.honeypot_channels)
            await interaction.response.send_message("honeypot is off for this channel now.", ephemeral=True)
        else:
            await interaction.response.send_message("honeypot isn't even on here.", ephemeral=True)

class ReasonModal(discord.ui.Modal, title='why tho?'):
    reason_input = discord.ui.TextInput(
        label='reason',
        style=discord.TextStyle.paragraph,
        placeholder='why are you doing this? spill it.',
        required=True,
        max_length=500
    )
    def __init__(self, view):
        super().__init__()
        self.view = view
    async def on_submit(self, interaction: discord.Interaction):
        self.view.reason = self.reason_input.value
        self.view.stop()
        await interaction.response.send_message("got it, moving on...", ephemeral=True)

class ReasonView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=300) 
        self.ctx = ctx
        self.reason = None
    @discord.ui.button(label="give reason", style=discord.ButtonStyle.primary)
    async def provide_reason(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            return await interaction.response.send_message("not your button, back off.", ephemeral=True)
        await interaction.response.send_modal(ReasonModal(self))
    async def on_timeout(self):
        if not self.reason:
            try:
                await self.ctx.author.timeout(discord.utils.utcnow() + timedelta(minutes=10), reason="didn't drop a reason in 5 mins.")
                await self.ctx.channel.send(f"{self.ctx.author.mention} got muted for 10 mins 'cause they didn't give a reason in time.")
            except discord.Forbidden:
                await self.ctx.channel.send(f"{self.ctx.author.mention} didn't give a reason, but i don't have perms to mute them.")

class OwnerBanConfirmView(discord.ui.View):
    def __init__(self, target: discord.Member, reason: str, mod: discord.Member):
        super().__init__(timeout=None)
        self.target = target
        self.reason = reason
        self.mod = mod
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == interaction.guild.owner or await bot.is_owner(interaction.user):
            return True
        await interaction.response.send_message("only sedse can respond and confirm the ban.", ephemeral=True)
        return False
    @discord.ui.button(label="allow ban", style=discord.ButtonStyle.danger)
    async def allow_ban(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await self.target.ban(reason=f"approved by sedse. mod: {self.mod.display_name}. reason: {self.reason}")
            await interaction.message.edit(content=f"ban greenlit by {interaction.user.mention} for {self.target.mention}.", view=None)
            await send_log(interaction.guild, "user banned", f"**user:** {self.target.mention}\n**mod:** {self.mod.mention} (approved by sedse)\n**reason:** {self.reason}", discord.Color.red())
        except discord.Forbidden:
            await interaction.response.send_message("i don't have perms to ban this user.", ephemeral=True)
        self.stop()
    @discord.ui.button(label="just mute", style=discord.ButtonStyle.secondary)
    async def just_mute(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.edit(content=f"ban shot down by {interaction.user.mention}. {self.target.mention} is just gonna stay muted.", view=None)
        self.stop()

class UnbanModal(discord.ui.Modal, title='unban user'):
    user_id = discord.ui.TextInput(label='user id', placeholder='drop their discord id here', required=True)
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            user = await bot.fetch_user(int(self.user_id.value))
            cmd = bot.get_command('unban')
            if await cmd.can_run(self.ctx):
                await self.ctx.invoke(cmd, user=user)
                await interaction.followup.send(f"unbanned {user.name}.", ephemeral=True)
        except commands.CheckFailure:
            await interaction.followup.send("you lack perms.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"failed: {e}", ephemeral=True)

class PermsModal(discord.ui.Modal, title='edit perms'):
    cmd_name = discord.ui.TextInput(label='command name', placeholder='e.g. kick, ban, all', required=True)
    target_id = discord.ui.TextInput(label='target id', placeholder='user or role id', required=True)
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            target_obj = self.ctx.guild.get_member(int(self.target_id.value)) or self.ctx.guild.get_role(int(self.target_id.value))
            if not target_obj: return await interaction.followup.send("couldn't find that user or role.", ephemeral=True)
            cmd = bot.get_command('perm')
            if await cmd.can_run(self.ctx):
                await self.ctx.invoke(cmd, command_name=self.cmd_name.value, target=target_obj)
                await interaction.followup.send(f"updated perms for {self.cmd_name.value}.", ephemeral=True)
        except commands.CheckFailure:
            await interaction.followup.send("you lack perms.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"failed: {e}", ephemeral=True)

class ModActionModal(discord.ui.Modal):
    def __init__(self, action, target, ctx):
        super().__init__(title=f"{action} target"[:45])
        self.action = action
        self.target = target
        self.ctx = ctx

        if self.action in ["mute", "forcemute"]:
            self.duration = discord.ui.TextInput(label="duration", placeholder="e.g. 10m, 1h, 1d", default="1h", required=True, max_length=20)
            self.add_item(self.duration)

        self.reason = discord.ui.TextInput(label="reason", placeholder="spill the reason", default="no reason", required=False, max_length=300)
        self.add_item(self.reason)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        cmd_map = {"warn": "warn", "mute": "timeout", "kick": "kick", "ban": "ban", "softban": "softban", "forcemute": "forcemute"}
        try:
            cmd = bot.get_command(cmd_map[self.action])
            if await cmd.can_run(self.ctx):
                kw = {"member": self.target, "reason": self.reason.value}
                if self.action in ["mute", "forcemute"]: kw["duration_str"] = self.duration.value
                await self.ctx.invoke(cmd, **kw)
                await interaction.followup.send(f"dropped the hammer on {self.target.mention} with {self.action}.", ephemeral=True)
        except DynamicRateLimitError as e:
            await interaction.followup.send(e.message, ephemeral=True)
        except commands.CheckFailure:
            await interaction.followup.send("you lack perms for this.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"something broke: {e}", ephemeral=True)

class ModView(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=600)
        self.ctx = ctx
        self.category = None
        self.action = None
        self.target = None

        self.category_select = discord.ui.Select(
            placeholder="pick a category...",
            options=[
                discord.SelectOption(label="punish", description="smite someone"),
                discord.SelectOption(label="pardon", description="forgive someone"),
                discord.SelectOption(label="whitelist", description="manage protections"),
                discord.SelectOption(label="server & perms", description="locks, perms, honeypots")
            ],
            row=0
        )
        self.category_select.callback = self.category_cb
        self.add_item(self.category_select)

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("this menu ain't for you.", ephemeral=True)
            return False
        return True

    async def category_cb(self, interaction: discord.Interaction):
        self.category = self.category_select.values[0]
        self.action = None
        self.target = None
        self.rebuild_ui()
        await interaction.response.edit_message(view=self)

    def rebuild_ui(self):
        self.clear_items()
        self.add_item(self.category_select)
        if not self.category: return

        opts = []
        if self.category == "punish": opts = ["warn", "mute", "kick", "ban", "softban", "forcemute", "annihilate"]
        elif self.category == "pardon": opts = ["unmute", "forceunmute", "clear warnings", "unban"]
        elif self.category == "whitelist": opts = ["add whitelist", "remove whitelist", "add priority", "remove priority"]
        elif self.category == "server & perms": opts = ["lock channel", "unlock channel", "uwulock user", "uwulock server", "uwu unlock server", "toggle honeypot", "edit perms"]

        self.action_select = discord.ui.Select(
            placeholder="pick an action...",
            options=[discord.SelectOption(label=opt) for opt in opts],
            row=1
        )
        self.action_select.callback = self.action_cb
        self.add_item(self.action_select)

        if self.action:
            needs_user = self.action in ["warn", "mute", "kick", "ban", "softban", "forcemute", "annihilate", "unmute", "forceunmute", "clear warnings", "add whitelist", "remove whitelist", "add priority", "remove priority", "uwulock user"]
            needs_channel = self.action in ["lock channel", "unlock channel", "toggle honeypot"]
            needs_exec = self.action in ["unban", "uwulock server", "uwu unlock server", "edit perms"]

            if needs_user:
                class DynamicUserSelect(discord.ui.UserSelect):
                    def __init__(inner_self, **kwargs): super().__init__(**kwargs)
                    async def callback(inner_self, interaction: discord.Interaction):
                        self.target = inner_self.values[0]
                        await self.handle_action(interaction)
                self.add_item(DynamicUserSelect(placeholder="select target user...", row=2))

            elif needs_channel:
                class DynamicChannelSelect(discord.ui.ChannelSelect):
                    def __init__(inner_self, **kwargs): super().__init__(**kwargs)
                    async def callback(inner_self, interaction: discord.Interaction):
                        self.target = inner_self.values[0]
                        await self.handle_action(interaction)
                self.add_item(DynamicChannelSelect(placeholder="select target channel...", channel_types=[discord.ChannelType.text], row=2))

            elif needs_exec:
                btn = discord.ui.Button(label="execute action", style=discord.ButtonStyle.grey, row=2)
                async def btn_cb(interaction: discord.Interaction):
                    await self.handle_action(interaction)
                btn.callback = btn_cb
                self.add_item(btn)

    async def action_cb(self, interaction: discord.Interaction):
        self.action = self.action_select.values[0]
        self.rebuild_ui()
        await interaction.response.edit_message(view=self)

    async def handle_action(self, interaction: discord.Interaction):
        needs_modal = self.action in ["warn", "mute", "kick", "ban", "softban", "forcemute"]
        if needs_modal:
            await interaction.response.send_modal(ModActionModal(self.action, self.target, self.ctx))
        elif self.action == "unban":
            await interaction.response.send_modal(UnbanModal(self.ctx))
        elif self.action == "edit perms":
            await interaction.response.send_modal(PermsModal(self.ctx))
        else:
            await interaction.response.defer()
            await self.execute_direct(interaction)

    async def execute_direct(self, interaction: discord.Interaction):
        act, ctx, t = self.action, self.ctx, self.target
        try:
            if act == "clear warnings":
                warnings = load_json(WARNINGS_FILE, dict)
                uid = str(t.id)
                if uid in warnings:
                    del warnings[uid]
                    save_json(WARNINGS_FILE, warnings)
                    await interaction.followup.send(f"wiped warnings for {t.mention}.", ephemeral=True)
                else:
                    await interaction.followup.send(f"{t.mention} is already clean.", ephemeral=True)
                return

            if act == "toggle honeypot":
                if t.id in bot.honeypot_channels:
                    bot.honeypot_channels.remove(t.id)
                    save_honeypots(bot.honeypot_channels)
                    await interaction.followup.send(f"killed honeypot in {t.mention}.", ephemeral=True)
                else:
                    bot.honeypot_channels.append(t.id)
                    save_honeypots(bot.honeypot_channels)
                    await interaction.followup.send(f"dropped honeypot in {t.mention}.", ephemeral=True)
                return

            cmd_map = {"annihilate": "annihilate", "unmute": "untimeout", "forceunmute": "forceunmute", "add whitelist": "whitelist", "remove whitelist": "unwhitelist", "lock channel": "lock", "unlock channel": "unlock"}
            if act in cmd_map:
                cmd = bot.get_command(cmd_map[act])
                if await cmd.can_run(ctx):
                    kw = {"channel": t} if act in ["lock channel", "unlock channel"] else {"member": t}
                    await ctx.invoke(cmd, **kw)
                    await interaction.followup.send(f"ran {act}.", ephemeral=True)
                return

            if act == "add priority":
                cmd = bot.get_command("priority").get_command("whitelist")
                if await cmd.can_run(ctx): await ctx.invoke(cmd, member=t)
                await interaction.followup.send("priority whitelisted.", ephemeral=True)
            elif act == "remove priority":
                cmd = bot.get_command("priority").get_command("unwhitelist")
                if await cmd.can_run(ctx): await ctx.invoke(cmd, member=t)
                await interaction.followup.send("removed priority whitelist.", ephemeral=True)
            elif act == "uwulock user":
                cmd = bot.get_command("uwulock")
                if await cmd.can_run(ctx): await ctx.invoke(cmd, arg1="lock", arg2=str(t.id))
                await interaction.followup.send("uwulocked them.", ephemeral=True)
            elif act == "uwulock server":
                cmd = bot.get_command("uwulock")
                if await cmd.can_run(ctx): await ctx.invoke(cmd, arg1="lock", arg2="everyone")
                await interaction.followup.send("uwulocked the whole server.", ephemeral=True)
            elif act == "uwu unlock server":
                cmd = bot.get_command("uwulock")
                if await cmd.can_run(ctx): await ctx.invoke(cmd, arg1="unlock", arg2="everyone")
                await interaction.followup.send("freed the server from uwu.", ephemeral=True)

        except DynamicRateLimitError as e: await interaction.followup.send(e.message, ephemeral=True)
        except commands.CheckFailure: await interaction.followup.send("you lack perms for this.", ephemeral=True)
        except Exception as e: await interaction.followup.send(f"broken: {e}", ephemeral=True)


class RedeemModal(discord.ui.Modal, title='redeem sedse key'):
    key_input = discord.ui.TextInput(label='enter your generated key', placeholder='SEDSE-XXXX-XXXX', required=True, max_length=50)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        key_val = self.key_input.value.strip()
        
        data = await supabase_request("GET", f"keys?key_value=eq.{key_val}&select=*")
        if not data:
            return await interaction.followup.send("invalid key. this key does not exist.", ephemeral=True)
            
        k = data[0]
        if k.get("discord_id"):
            if k.get("discord_id") == str(interaction.user.id):
                return await interaction.followup.send("you have already redeemed this key.", ephemeral=True)
            return await interaction.followup.send("already claimed. someone else owns this key.", ephemeral=True)
            
        if k.get("is_active") == False:
            return await interaction.followup.send("inactive key. this key has been deactivated.", ephemeral=True)
            
        if k.get("expires_at"):
            exp_date = datetime.fromisoformat(k["expires_at"].replace('Z', '+00:00'))
            if datetime.now(timezone.utc) > exp_date:
                return await interaction.followup.send("expired key. this key has expired.", ephemeral=True)

        updated = await supabase_request("PATCH", f"keys?key_value=eq.{key_val}", {"discord_id": str(interaction.user.id)})
        if updated:
            await interaction.followup.send("key redeemed successfully. it is now permanently linked to your discord account.", ephemeral=True)
        else:
            await interaction.followup.send("database error while redeeming. please contact support.", ephemeral=True)

class ResetHWIDModal(discord.ui.Modal, title='reset hwid'):
    key_input = discord.ui.TextInput(label='enter the key to reset hwid for', placeholder='SEDSE-XXXX...', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        key_val = self.key_input.value.strip()
        uid = str(interaction.user.id)
        
        is_owner = (interaction.user == interaction.guild.owner or await interaction.client.is_owner(interaction.user))
        
        if not is_owner:
            cooldowns = load_json(HWID_COOLDOWNS_FILE, dict)
            now = discord.utils.utcnow().timestamp()
            if uid in cooldowns:
                time_passed = now - cooldowns[uid]
                if time_passed < 259200: # 3 Days
                    days_left = round((259200 - time_passed) / 86400, 1)
                    return await interaction.followup.send(f"cooldown active. you can reset hwid again in {days_left} days.", ephemeral=True)

        data = await supabase_request("GET", f"keys?key_value=eq.{key_val}&discord_id=eq.{uid}&select=*")
        if not data:
            return await interaction.followup.send("you do not own this key or it does not exist.", ephemeral=True)

        updated = await supabase_request("PATCH", f"keys?key_value=eq.{key_val}", {"hwid": None})
        if updated:
            if not is_owner:
                cooldowns = load_json(HWID_COOLDOWNS_FILE, dict)
                cooldowns[uid] = discord.utils.utcnow().timestamp()
                save_json(HWID_COOLDOWNS_FILE, cooldowns)
            await interaction.followup.send("hwid reset successful. your next injection will lock to your new device.", ephemeral=True)
        else:
            await interaction.followup.send("failed to reset hwid.", ephemeral=True)

class ManageKeysSelect(discord.ui.Select):
    def __init__(self, keys):
        options = []
        for k in keys:
            status = "expired"
            if k.get("expires_at"):
                exp = datetime.fromisoformat(k["expires_at"].replace('Z', '+00:00'))
                if datetime.now(timezone.utc) <= exp: status = "active"
            elif k.get("is_active"): status = "lifetime"
            options.append(discord.SelectOption(label=f"{k['key_value'][:15]}...", description=f"status: {status}", value=k["key_value"]))
            
        super().__init__(placeholder="select a key to view details...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        key_val = self.values[0]
        data = await supabase_request("GET", f"keys?key_value=eq.{key_val}&select=*")
        if not data: return
        k = data[0]
        
        hwid_status = f"`{k['hwid']}`" if k.get("hwid") else "`unbound`"
        exp = "lifetime"
        if k.get("expires_at"):
            exp = datetime.fromisoformat(k["expires_at"].replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M UTC")
            
        embed = discord.Embed(title="key management", color=0x2b2d31)
        embed.add_field(name="key", value=f"`{k['key_value']}`", inline=False)
        embed.add_field(name="hwid", value=hwid_status, inline=True)
        embed.add_field(name="expires", value=exp, inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

class ManageKeysView(discord.ui.View):
    def __init__(self, keys):
        super().__init__(timeout=120)
        self.add_item(ManageKeysSelect(keys))

class KeySystemView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Get Key", url="https://keyxyz-sedse.pages.dev", style=discord.ButtonStyle.link, emoji="🔗", row=0))
        
    @discord.ui.button(label="Redeem Key", style=discord.ButtonStyle.green, custom_id="ks_redeem", emoji="🔑", row=0)
    async def redeem_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RedeemModal())

    @discord.ui.button(label="Get Script", style=discord.ButtonStyle.blurple, custom_id="ks_script", emoji="📜", row=0)
    async def script_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        data = await supabase_request("GET", f"keys?discord_id=eq.{interaction.user.id}&is_active=eq.true")
        if not data:
            return await interaction.followup.send("you don't have any redeemed keys. click redeem key first.", ephemeral=True)
        
        valid_key = None
        for k in data:
            if k.get("expires_at"):
                exp = datetime.fromisoformat(k["expires_at"].replace('Z', '+00:00'))
                if datetime.now(timezone.utc) < exp:
                    valid_key = k["key_value"]
                    break
            else:
                valid_key = k["key_value"]
                break
                
        if valid_key:
            loader = f'local key = "{valid_key}"\nloadstring(game:HttpGet("https://keyxyz-sedse.pages.dev/v1/load?key=" .. game:GetService("HttpService"):UrlEncode(key) .. "&_cb=" .. tostring(os.clock())))()'
            await interaction.followup.send(f"**your loader script:**\n`\n{loader}\n`", ephemeral=True)
        else:
            await interaction.followup.send("all your redeemed keys have expired. please generate a new one.", ephemeral=True)

    @discord.ui.button(label="Get Role", style=discord.ButtonStyle.blurple, custom_id="ks_role", emoji="👤", row=1)
    async def role_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        data = await supabase_request("GET", f"keys?discord_id=eq.{interaction.user.id}&is_active=eq.true")
        if not data:
            return await interaction.followup.send("you need to redeem an active key to get the role.", ephemeral=True)
            
        role = interaction.guild.get_role(ROLE_SCRIPT_USER_ID)
        if role:
            try:
                await interaction.user.add_roles(role)
                await interaction.followup.send("you have been given the script user role.", ephemeral=True)
            except discord.Forbidden:
                await interaction.followup.send("i don't have permission to give roles. check my role hierarchy.", ephemeral=True)
        else:
            await interaction.followup.send("role not found in server.", ephemeral=True)

    @discord.ui.button(label="Reset HWID", style=discord.ButtonStyle.secondary, custom_id="ks_reset", emoji="⚙️", row=1)
    async def reset_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ResetHWIDModal())

    @discord.ui.button(label="Manage Keys", style=discord.ButtonStyle.secondary, custom_id="ks_manage", emoji="📊", row=1)
    async def manage_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        data = await supabase_request("GET", f"keys?discord_id=eq.{interaction.user.id}")
        if not data:
            return await interaction.followup.send("you don't have any keys linked to your account.", ephemeral=True)
            
        keys_to_show = data[:25]
        await interaction.followup.send("select a key to view its status:", view=ManageKeysView(keys_to_show), ephemeral=True)

# ==========================================
# PLAYWRIGHT BROWSER UI & HELPERS
# ==========================================

async def get_browser_screenshot(session_data):
    page = session_data["page"]
    show_grid = session_data.get("show_grid", False)
    
    js_show_grid = 'true' if show_grid else 'false'
    
    js_code = f"""
    () => {{
        // --- 1. Red Tags (Always Active) ---
        document.querySelectorAll('.sedse-tag').forEach(e => e.remove());
        let count = 1;
        document.querySelectorAll('a, button, input, textarea, [role="button"]').forEach(el => {{
            let rect = el.getBoundingClientRect();
            if(rect.width > 0 && rect.height > 0 && rect.top >= 0 && rect.bottom <= window.innerHeight) {{
                el.setAttribute('data-sedse-id', count);
                let tag = document.createElement('div');
                tag.className = 'sedse-tag';
                tag.innerText = count;
                tag.style.position = 'fixed';
                tag.style.left = rect.left + 'px';
                tag.style.top = rect.top + 'px';
                tag.style.background = 'red';
                tag.style.color = 'white';
                tag.style.fontWeight = 'bold';
                tag.style.padding = '1px 4px';
                tag.style.fontSize = '12px';
                tag.style.zIndex = '999999';
                tag.style.pointerEvents = 'none';
                document.body.appendChild(tag);
                count++;
            }}
        }});

        // --- 2. X/Y Grid (Toggleable) ---
        let oldGrid = document.getElementById('sedse-grid');
        if(oldGrid) oldGrid.remove();
        
        if ({js_show_grid}) {{
            let svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            svg.id = 'sedse-grid';
            svg.style.position = 'fixed';
            svg.style.top = '0';
            svg.style.left = '0';
            svg.style.width = '100vw';
            svg.style.height = '100vh';
            svg.style.pointerEvents = 'none';
            svg.style.zIndex = '9999999';
            
            for(let x = 100; x < window.innerWidth; x += 100) {{
                let line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', x); line.setAttribute('y1', 0);
                line.setAttribute('x2', x); line.setAttribute('y2', window.innerHeight);
                line.setAttribute('stroke', 'rgba(0, 255, 0, 0.4)');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
                
                let txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                txt.setAttribute('x', x + 2); txt.setAttribute('y', 15);
                txt.setAttribute('fill', '#00ff00');
                txt.setAttribute('font-size', '13px');
                txt.setAttribute('font-weight', 'bold');
                txt.style.textShadow = '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000';
                txt.textContent = x;
                svg.appendChild(txt);
            }}
            
            for(let y = 100; y < window.innerHeight; y += 100) {{
                let line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', 0); line.setAttribute('y1', y);
                line.setAttribute('x2', window.innerWidth); line.setAttribute('y2', y);
                line.setAttribute('stroke', 'rgba(0, 255, 0, 0.4)');
                line.setAttribute('stroke-width', '1');
                svg.appendChild(line);
                
                let txt = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                txt.setAttribute('x', 2); txt.setAttribute('y', y - 2);
                txt.setAttribute('fill', '#00ff00');
                txt.setAttribute('font-size', '13px');
                txt.setAttribute('font-weight', 'bold');
                txt.style.textShadow = '-1px -1px 0 #000, 1px -1px 0 #000, -1px 1px 0 #000, 1px 1px 0 #000';
                txt.textContent = y;
                svg.appendChild(txt);
            }}
            document.body.appendChild(svg);
        }}
    }}
    """
    await page.evaluate(js_code)
    
    screenshot_bytes = await page.screenshot(type="jpeg", quality=75)
    return discord.File(io.BytesIO(screenshot_bytes), filename="browser.jpg")


class ClickModal(discord.ui.Modal, title='Click an Element by Number'):
    element_id = discord.ui.TextInput(label='Enter the red number to click', placeholder='e.g., 5', max_length=4)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if not session:
            return await interaction.followup.send("Browser session expired.", ephemeral=True)
        
        try:
            page = session["page"]
            target_id = self.element_id.value.strip()
            click_js = f"""
            (() => {{
                let el = document.querySelector('[data-sedse-id="{target_id}"]');
                if(el) {{ el.removeAttribute('target'); el.click(); }}
            }})()
            """
            await page.evaluate(click_js)
            await asyncio.sleep(2.5)
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])
        except Exception as e:
            await interaction.followup.send(f"Failed to click: {e}", ephemeral=True)

class XYClickModal(discord.ui.Modal, title='Click by Coordinates'):
    x_coord = discord.ui.TextInput(label='X Coordinate (Left to Right)', placeholder='e.g., 640', max_length=5)
    y_coord = discord.ui.TextInput(label='Y Coordinate (Top to Bottom)', placeholder='e.g., 360', max_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if not session:
            return await interaction.followup.send("Browser session expired.", ephemeral=True)
        
        try:
            page = session["page"]
            x = float(self.x_coord.value.strip())
            y = float(self.y_coord.value.strip())
            await page.mouse.click(x, y)
            await asyncio.sleep(2.5) 
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])
        except ValueError:
            await interaction.followup.send("Coordinates must be numbers!", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to click coordinates: {e}", ephemeral=True)

class DragModal(discord.ui.Modal, title='Drag & Drop'):
    start_coord = discord.ui.TextInput(label='Start Position (X,Y)', placeholder='e.g., 200,350', max_length=11)
    end_coord = discord.ui.TextInput(label='End Position (X,Y)', placeholder='e.g., 800,350', max_length=11)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if not session:
            return await interaction.followup.send("Browser session expired.", ephemeral=True)
        
        try:
            page = session["page"]
            sx, sy = map(float, self.start_coord.value.strip().split(','))
            ex, ey = map(float, self.end_coord.value.strip().split(','))
            
            await page.mouse.move(sx, sy)        
            await page.mouse.down()              
            await asyncio.sleep(0.2)             
            await page.mouse.move(ex, ey, steps=10) 
            await asyncio.sleep(0.2)             
            await page.mouse.up()                
            
            await asyncio.sleep(2.5) 
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])
        except ValueError:
            await interaction.followup.send("Format must be exact! Use: 200,300", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Failed to drag: {e}", ephemeral=True)

class TypeModal(discord.ui.Modal, title='Type in a Textbox'):
    element_id = discord.ui.TextInput(label='Red number of the textbox', style=discord.TextStyle.short, max_length=4)
    text_to_type = discord.ui.TextInput(label='What do you want to type?', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if not session: return
        
        try:
            page = session["page"]
            target_id = self.element_id.value.strip()
            focus_js = f"document.querySelector('[data-sedse-id=\"{target_id}\"]').focus()"
            await page.evaluate(focus_js)
            await page.keyboard.type(self.text_to_type.value)
            await asyncio.sleep(0.5)
            
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])
        except Exception as e:
            await interaction.followup.send(f"Failed to type: {e}", ephemeral=True)

class BrowserView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    # ROW 1 (Max 5 items)
    @discord.ui.button(label="Click (#)", style=discord.ButtonStyle.primary, row=0)
    async def click_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ClickModal())

    @discord.ui.button(label="Click (X,Y)", style=discord.ButtonStyle.primary, row=0)
    async def xy_click_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(XYClickModal())

    @discord.ui.button(label="Drag (X,Y)", style=discord.ButtonStyle.primary, row=0)
    async def drag_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(DragModal())

    @discord.ui.button(label="Type Text", style=discord.ButtonStyle.success, row=0)
    async def type_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TypeModal())

    @discord.ui.button(label="Enter Key", style=discord.ButtonStyle.secondary, row=0)
    async def enter_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if session:
            await session["page"].keyboard.press("Enter")
            await asyncio.sleep(2.5)
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])

    # ROW 2 (Max 5 items)
    @discord.ui.button(label="Toggle Grid", style=discord.ButtonStyle.secondary, row=1)
    async def toggle_grid_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if session:
            session["show_grid"] = not session["show_grid"]
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])

    @discord.ui.button(label="Scroll Up", style=discord.ButtonStyle.secondary, row=1)
    async def scroll_up(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if session:
            await session["page"].mouse.wheel(0, -600)
            await asyncio.sleep(0.5)
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])

    @discord.ui.button(label="Scroll Down", style=discord.ButtonStyle.secondary, row=1)
    async def scroll_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        session = active_browsers.get(interaction.channel.id)
        if session:
            await session["page"].mouse.wheel(0, 600)
            await asyncio.sleep(0.5)
            new_file = await get_browser_screenshot(session)
            await interaction.message.edit(attachments=[new_file])

    @discord.ui.button(label="Close Browser", style=discord.ButtonStyle.danger, row=1)
    async def close_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        session = active_browsers.pop(interaction.channel.id, None)
        if session:
            await session["page"].close()
        await interaction.response.edit_message(content="Browser session closed.", attachments=[], view=None)

# ==========================================
# 2. BOT CLASS
# ==========================================

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True 
        intents.members = True 
        
        # --- GLOBAL PING RESTRICTION ---
        # everyone=False: completely disables @everyone and @here pings
        # roles=False: disables role pings (prevents malicious role pinging)
        # users=True: allows normal user pings (so commands like !rizz @user still work)
        safe_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        
        super().__init__(
            command_prefix=["!sedse ", "!"], 
            intents=intents,
            allowed_mentions=safe_mentions # Applies the restriction globally
        )
        self.honeypot_channels = load_honeypots()

    async def setup_hook(self):
        self.add_view(JJSView())
        self.add_view(VerifyView())
        self.add_view(HoneypotView()) 
        self.add_view(KeySystemView()) # Keep this here so your keysystem buttons stay active!
        try:
            await self.tree.sync()
        except Exception as e:
            print(f"sync failed: {e}")

        # --- PLAYWRIGHT BROWSER SETUP ---
        global playwright_instance, browser_instance
        try:
            playwright_instance = await async_playwright().start()
            browser_instance = await playwright_instance.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
            )
            print("Playwright Browser launched successfully on Railway!")
        except Exception as e:
            print(f"Failed to launch Playwright: {e}")

        
        # --- WAVELINK NODE SETUP (LAVALINK) ---
        nodes = [
            # Your active, working Railway Lavalink Node
            wavelink.Node(
                identifier="Sedse-Private-Node",
                uri="https://lavalink-production-6481.up.railway.app:443", 
                password="sedsemusic2026"
            )
        ]
        
        try:
            await wavelink.Pool.connect(nodes=nodes, client=self)
            print("Successfully connected to Lavalink node!")
        except Exception as e:
            print(f"Failed to connect to Lavalink: {e}")

bot = MyBot()

# ==========================================
# 3. HELPERS & SYSTEMS
# ==========================================

UWU_EMOJIS = ["(uwu)", "(owo)", "(^w^)", "(>w<)", "(*^w^*)", "(;w;)", "(^-^)", "(U_U)", "(T_T)"]

def uwuify(text):
    text = text.replace('r', 'w').replace('l', 'w').replace('R', 'W').replace('L', 'W')
    text = re.sub(r'n([aeiou])', r'ny\1', text)
    text = re.sub(r'N([aeiou])', r'Ny\1', text)
    text = re.sub(r'N([AEIOU])', r'NY\1', text)
    words = text.split()
    result = []
    for word in words:
        if not (word.startswith("<@") or word.startswith("<#") or word.startswith("<:")):
            match = re.search(r'[a-zA-Z0-9]', word)
            if match:
                first_char = match.group()
                stutter = f"{first_char}-" * random.randint(1, 3)
                word = word[:match.start()] + stutter + word[match.start():]
        result.append(word)
        if random.random() < 0.8: result.append(random.choice(UWU_EMOJIS))
    return " ".join(result)

async def send_log(guild, title, description, color):
    settings = load_json(SETTINGS_FILE, dict)
    log_channel_id = settings.get(str(guild.id), {}).get("log_channel")
    if log_channel_id:
        channel = guild.get_channel(log_channel_id)
        if channel:
            embed = discord.Embed(title=title, description=description, color=color, timestamp=discord.utils.utcnow())
            await channel.send(embed=embed)

def parse_duration(duration_str):
    if not duration_str: return None
    pattern = re.compile(r'((?P<days>\d+?)d)?((?P<hours>\d+?)h)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?')
    match = pattern.fullmatch(duration_str)
    if not match: return None
    kwargs = {k: int(v) for k, v in match.groupdict().items() if v}
    return timedelta(**kwargs) if kwargs else None

async def is_mod_owner(ctx):
    if ctx is None: return False
    if ctx.guild and ctx.author == ctx.guild.owner: return True
    if await ctx.bot.is_owner(ctx.author): return True
    return False

def check_perms(cmd_name, **default_perms):
    async def predicate(ctx):
        if ctx.guild and (ctx.author == ctx.guild.owner or ctx.author.guild_permissions.administrator):
            return True
        if default_perms:
            if all(getattr(ctx.author.guild_permissions, k, False) == v for k, v in default_perms.items()):
                return True
        perms_data = load_json(PERMS_FILE, dict)
        guild_perms = perms_data.get(str(ctx.guild.id), {})
        for check_cmd in [cmd_name, "all"]:
            cmd_perms = guild_perms.get(check_cmd, {"roles": [], "users": []})
            if ctx.author.id in cmd_perms["users"] or any(role.id in cmd_perms["roles"] for role in ctx.author.roles):
                return True
        raise commands.MissingPermissions([f"custom role/user perm or {list(default_perms.keys())}"])
    return commands.check(predicate)


def check_and_reconstruct_dumper():
    raw_file_path = None
    
    # 1. Look for the raw text files dynamically
    for name in ["revea.lol_dumped.lua.txt", "revea.lol_dumped.lua", "dumper.lua"]:
        if os.path.exists(name):
            try:
                with open(name, "r", encoding="utf-8") as f:
                    header = f.read(4096)
                    if "START_FILE:./_env_dumper_launcher.lua" in header or "CHUNK:" in header:
                        raw_file_path = name
                        break
            except Exception:
                pass

    if not raw_file_path:
        # If a clean unpacked dumper.lua already exists and we didn't find any raw files, we are good!
        if os.path.exists("dumper.lua"):
            return True, None
        return False, "Could not find 'revea.lol_dumped.lua.txt' or raw 'dumper.lua' in your repository."

    try:
        is_target_file = False
        chunks = []
        with open(raw_file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Do not strip the raw line yet so indices match perfectly
                # Check for file boundaries to isolate _env_dumper_launcher.lua
                if "START_FILE:./_env_dumper_launcher.lua" in line:
                    is_target_file = True
                    chunks = [] # Reset chunks to avoid any pollution
                    continue
                if "END_FILE:./_env_dumper_launcher.lua" in line:
                    is_target_file = False
                    continue
                
                if is_target_file and "CHUNK:" in line:
                    # Find where CHUNK: starts
                    idx = line.find("CHUNK:")
                    # The quote character used is right before CHUNK: (' or ")
                    quote_char = line[idx - 1]
                    # The content starts right after CHUNK:
                    content_start = idx + 6
                    # Find the ending quote character from the right
                    content_end = line.rfind(quote_char)
                    
                    chunk_data = line[content_start:content_end]
                    
                    try:
                        # Decode escape sequences natively
                        unescaped = codecs.escape_decode(bytes(chunk_data, "utf-8"))[0].decode("utf-8")
                    except Exception:
                        # Safe fallback
                        unescaped = chunk_data.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"').replace("\\'", "'").replace("\\\\", "\\")
                    chunks.append(unescaped)
        
        if not chunks:
            if raw_file_path == "dumper.lua":
                return True, None
            return False, f"Located raw file at '{raw_file_path}', but failed to extract code chunks."
            
        # Overwrite dumper.lua with the freshly reconstructed clean code
        with open("dumper.lua", "w", encoding="utf-8") as out:
            out.write("".join(chunks))
            
        return True, None
    except Exception as e:
        return False, f"Error during reconstruction: {e}"

async def check_and_increment_quota(ctx, command_name):
    if await is_mod_owner(ctx): return True # Owners/Mods bypass quotas
    
    quotas = load_json(QUOTAS_FILE, dict)
    user_id = str(ctx.author.id)
    today = discord.utils.utcnow().strftime("%Y-%m-%d")
    
    if user_id not in quotas or quotas[user_id].get("date") != today:
        quotas[user_id] = {"date": today, "kick": 0, "timeout": 0, "warn": 0, "ai": 0, "research": 0}
        
    # Moderation gets 10 uses, AI/Research get 5 daily uses
    limit = 5 if command_name in ["ai", "research"] else 10
    
    if quotas[user_id].get(command_name, 0) >= limit: return False
    
    quotas[user_id][command_name] = quotas[user_id].get(command_name, 0) + 1
    save_json(QUOTAS_FILE, quotas)
    return True

def is_whitelisted(guild_id, user_id):
    wl_data = load_json(WHITELIST_FILE, dict)
    return str(user_id) in wl_data.get(str(guild_id), [])

def is_priority_whitelisted(guild_id, user_id):
    pwl_data = load_json(PRIORITY_WHITELIST_FILE, dict)
    return str(user_id) in pwl_data.get(str(guild_id), [])

@bot.check
async def global_dynamic_cooldown(ctx):
    if await is_mod_owner(ctx): return True
    now = discord.utils.utcnow().timestamp()
    user_id = str(ctx.author.id)
    if user_id not in user_cooldowns:
        user_cooldowns[user_id] = {'last_used': 0, 'spam_hits': 0, 'penalty_until': 0}
    cd_data = user_cooldowns[user_id]
    if now < cd_data['penalty_until']:
        raise DynamicRateLimitError(f"chill on the commands. try again in {int(cd_data['penalty_until'] - now)} secs.")
    if now - cd_data['last_used'] < 5:
        cd_data['spam_hits'] += 1
        if cd_data['spam_hits'] >= 3:
            cd_data['penalty_until'] = now + 60
            cd_data['spam_hits'] = 0
            raise DynamicRateLimitError("you're spamming too hard. take a 60 second timeout.")
        raise DynamicRateLimitError(f"hold up, command on cooldown. wait {int(5 - (now - cd_data['last_used']))} secs.")
    cd_data['spam_hits'] = 0
    cd_data['last_used'] = now
    return True

# ==========================================
# 4. EVENTS
# ==========================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, DynamicRateLimitError):
        await ctx.send(error.message, delete_after=5)
    elif hasattr(error, "original") and isinstance(error.original, DynamicRateLimitError):
        await ctx.send(error.original.message, delete_after=5)
    elif isinstance(error, (commands.MissingPermissions, commands.CheckFailure)):
        await ctx.send("you don't have perms for this.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"you forgot something: {error.param}")
    elif not isinstance(error, commands.CommandNotFound):
        print(f"error: {error}")

@bot.event
async def on_message_delete(message):
    if message.author.bot: 
        return
    if not message.content: 
        return
        
    channel_id = message.channel.id
    if channel_id not in deleted_messages_cache:
        deleted_messages_cache[channel_id] = []
        
    deleted_messages_cache[channel_id].append({
        "id": message.id,
        "author_name": message.author.display_name,
        "author_avatar": message.author.display_avatar.url if message.author.display_avatar else None,
        "content": message.content,
        "author_mention": message.author.mention
    })
    
    # keep only the last 100 messages to prevent memory overflow
    if len(deleted_messages_cache[channel_id]) > 100:
        deleted_messages_cache[channel_id].pop(0)

@bot.event
async def on_message(message):
    if message.author.bot: 
        return
       
@bot.event
async def on_message(message):
    if message.author.bot: 
        return

    # --- AUTO TRANSLATE ---
    translate_data = load_json(TRANSLATE_FILE, dict)
    is_translate_cmd = message.content.lower().startswith(("!sedse translate", "!translate", "!autotranslate"))
    
    if not is_translate_cmd and str(message.channel.id) in translate_data and not message.content.startswith(("!", ".")):
        text_to_translate = message.content.strip()
        # Ignore empty text, pure URLs, or just Discord mentions/emojis
        if text_to_translate and not re.fullmatch(r'<[#@:]\d+>|https?://\S+', text_to_translate):
            try:
                url = "https://translate.googleapis.com/translate_a/single"
                params = {
                    "client": "gtx",
                    "sl": "auto",
                    "tl": "en",
                    "dt": "t",
                    "q": text_to_translate
                }
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            detected_lang = data[2]
                            
                            # 'en' = English, 'und' = undefined (usually emotes/gibberish)
                            if detected_lang and detected_lang.lower() not in ['en', 'und']:
                                translated_text = "".join([sentence[0] for sentence in data[0] if sentence[0]])
                                
                                # Only send if it actually translated something differently
                                if translated_text.lower().strip() != text_to_translate.lower().strip():
                                    await message.reply(
                                        f"**Translated ({detected_lang} -> en):**\n{translated_text}", 
                                        mention_author=False  # <--- THIS PREVENTS THE PING
                                    )
            except Exception as e:
                print(f"Auto-translate error: {e}")

    

    # --- SHADOW AI THREAD HANDLING ---
    if message.channel.id in active_shadow_threads and not message.content.startswith(("!", ".")):
        shadow_data = active_shadow_threads[message.channel.id]
        
        # Append user message to thread history
        shadow_data["history"].append({"role": "user", "content": f"{message.author.display_name}: {message.content}"})
        if len(shadow_data["history"]) > 15:
            shadow_data["history"].pop(0) # Keep only the last 15 interactions for memory
            
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        }
        
        # Build prompt: System behavior + Recent conversation
        messages_payload = [{"role": "system", "content": shadow_data["system_prompt"]}] + shadow_data["history"]
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages_payload,
            "temperature": 0.85 # Slightly higher temp for more organic/creative cloning
        }
        
        async with message.channel.typing():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(groq_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            ai_reply = data["choices"][0]["message"]["content"]
                            
                            # Clean up if AI accidentally prefixes its own name
                            ai_reply = re.sub(f"^{shadow_data['target_name']}:\s*", "", ai_reply, flags=re.IGNORECASE)
                            
                            # Add to memory
                            shadow_data["history"].append({"role": "assistant", "content": ai_reply})
                            
                            # Send using Impersonator Webhook (in the parent channel, pointing to the thread)
                            webhooks = await message.channel.parent.webhooks()
                            webhook = discord.utils.get(webhooks, name="sedse impersonator") or await message.channel.parent.create_webhook(name="sedse impersonator")
                            
                            await webhook.send(
                                content=ai_reply,
                                username=shadow_data["target_name"],
                                avatar_url=shadow_data["target_avatar"],
                                thread=message.channel
                            )
                        else:
                            print(f"Shadow AI Groq Error: {await response.text()}")
            except Exception as e:
                print(f"Shadow AI failure: {e}")
        return # Stop processing other commands in this thread

    # --- MINI AUTO MOD ---
    slur_pattern = r'\bnigg[ae]r?h?s?\b'
    
    if re.search(slur_pattern, message.content.lower()):
        is_immune = False
        if message.guild:
            if message.author == message.guild.owner or await bot.is_owner(message.author):
                is_immune = True
            elif is_whitelisted(message.guild.id, message.author.id) or is_priority_whitelisted(message.guild.id, message.author.id):
                is_immune = True
        
        if not is_immune:
            if message.author.guild_permissions.administrator or message.author.guild_permissions.moderate_members:
                user_id = str(message.author.id)
                now = discord.utils.utcnow().timestamp()
                
                if user_id in mod_slur_warnings and now - mod_slur_warnings[user_id] < 300:
                    try:
                        await message.author.timeout(discord.utils.utcnow() + timedelta(hours=1), reason="Repeated slur use as staff")
                        await message.channel.send(f"told you once already. {message.author.mention} is muted for an hour.")
                        await send_log(message.guild, "Mod Auto-Mute", f"**Mod:** {message.author.mention}\n**Reason:** Repeated slur use", discord.Color.red())
                        del mod_slur_warnings[user_id]
                    except discord.Forbidden:
                        await message.channel.send("tried to mute the mod but i don't have perms.")
                else:
                    mod_slur_warnings[user_id] = now
                    await message.channel.send(f"language buddy, {message.author.mention} you're getting muted next time you say it.")
            
            else:
                try:
                    await message.delete()
                    await message.author.timeout(discord.utils.utcnow() + timedelta(hours=1), reason="Slur use (Auto-Mod)")
                    await message.channel.send(f"{message.author.mention} got muted for an hour for that. chill.")
                    await send_log(message.guild, "Auto-Mod Mute", f"**User:** {message.author.mention}\n**Reason:** Slur usage", discord.Color.orange())
                except discord.Forbidden:
                    await message.channel.send(f"tried to mute {message.author.mention} but i don't have permissions.")
            return 

    # --- HONEYPOT ---
    if message.channel.id in bot.honeypot_channels:
        if message.author != message.guild.owner and not message.author.guild_permissions.administrator:
            try:
                await message.guild.ban(message.author, reason="honeypot", delete_message_seconds=604800)
                await message.guild.unban(message.author, reason="security unban")
                alert = await message.channel.send(f"busted. {message.author} fell for the honeypot.")
                await alert.delete(delay=10) 
            except discord.Forbidden: pass
            return 

    # --- AFK ---
    afk_data = load_json(AFK_FILE, dict)
    author_id = str(message.author.id)
    if author_id in afk_data:
        del afk_data[author_id]
        save_json(AFK_FILE, afk_data)
        welcome_msg = await message.channel.send(f"wb {message.author.mention}, took off your afk status.")
        await welcome_msg.delete(delay=5)
    
    if message.mentions:
        for mentioned_user in message.mentions:
            mid = str(mentioned_user.id)
            if mid in afk_data:
                await message.channel.send(
                    f"{mentioned_user.display_name} is afk right now: {afk_data[mid]['message']}",
                    allowed_mentions=discord.AllowedMentions.none()
                )

    # --- UWU LOCK ---
    is_uwu_cmd = message.content.lower().startswith(("!sedse uwu", "!uwu", "!sedse lock", "!sedse unlock"))
    uwu_data = load_json(UWULOCK_FILE, dict)
    if not is_uwu_cmd and (uwu_data.get("everyone") or str(message.author.id) in uwu_data):
        uwu_text = uwuify(message.content) if message.content.strip() else random.choice(UWU_EMOJIS)
        if len(uwu_text) > 2000: uwu_text = uwu_text[:1997] + "..."
        try:
            webhooks = await message.channel.webhooks()
            webhook = discord.utils.get(webhooks, name="sedse impersonator") or await message.channel.create_webhook(name="sedse impersonator")
            await webhook.send(content=uwu_text, username=message.author.display_name, avatar_url=message.author.display_avatar.url if message.author.display_avatar else None)
            await message.delete()
        except Exception as e: print(f"uwu error: {e}")
        return

    await bot.process_commands(message)
   
   # --- PG LOCK ---
    is_pg_cmd = message.content.lower().startswith(("!sedse pg", "!pg"))
    pg_data = load_json(PGLOCK_FILE, dict)
    
    if not is_pg_cmd and not is_uwu_cmd and (pg_data.get("everyone") or str(message.author.id) in pg_data):
        api_key = os.getenv("GROQ_API_KEY")
        if api_key and message.content.strip():
            try:
                groq_url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                system_prompt = (
                    "you are a filter. analyze the user's message. "
                    "if it contains negativity, toxicity, insults, or swearing, rewrite it to be overwhelmingly positive, friendly, and family-friendly. "
                    "if the message is already positive, neutral, or harmless, reply with the exact word 'pass' and absolutely nothing else. "
                    "keep all output entirely in lowercase. do not use any emojis whatsoever."
                )
                payload = {
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message.content}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 500
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(groq_url, headers=headers, json=payload) as response:
                        if response.status == 200:
                            data = await response.json()
                            ai_reply = data["choices"][0]["message"]["content"].strip().lower()
                            
                            # strip punctuation just in case the ai adds quotes or periods around pass
                            clean_reply = ai_reply.replace("'", "").replace('"', "").replace(".", "")
                            
                            if clean_reply != "pass":
                                webhooks = await message.channel.webhooks()
                                webhook = discord.utils.get(webhooks, name="sedse impersonator") or await message.channel.create_webhook(name="sedse impersonator")
                                await webhook.send(
                                    content=ai_reply[:2000], 
                                    username=message.author.display_name, 
                                    avatar_url=message.author.display_avatar.url if message.author.display_avatar else None
                                )
                                await message.delete()
                                return
            except Exception as e:
                print(f"pglock error: {e}")

@bot.event
async def on_member_update(before, after):
    # Check if the user's nickname was changed
    if before.nick != after.nick:
        data = load_json(FORCENICK_FILE, dict)
        gid = str(after.guild.id)
        uid = str(after.id)
        
        # If the user is on the forced list for this server
        if gid in data and uid in data[gid]:
            forced_nick = data[gid][uid]
            
            # If their new nickname isn't the forced one, instantly revert it
            if after.nick != forced_nick:
                try:
                    await after.edit(nick=forced_nick)
                except discord.Forbidden:
                    pass # Silently fail if a human server owner overrides it and the bot lacks hierarchy

@bot.event
async def on_ready():
    print(f"bot logged in as {bot.user}")
    
    # --- Resume Background Tasks Automatically ---
    tester_channels = load_json(TESTER_KEYS_FILE, list)
    for channel_id in tester_channels:
        channel = bot.get_channel(channel_id)
        if not channel:
            try: channel = await bot.fetch_channel(channel_id)
            except: continue
            
        if channel:
            task = bot.loop.create_task(tester_key_loop(channel))
            active_tester_tasks[channel_id] = task
            print(f"Resumed tester key loop in channel ID: {channel_id}")


async def tester_key_loop(channel):
    current_message = None
    current_key = None
    
    while True:
        try:
            # 1. Delete previous key from database to keep table clean
            if current_key:
                await supabase_request("DELETE", f"keys?key_value=eq.{current_key}")
            
            # 2. Generate new unique tester key
            random_part = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
            current_key = f"SEDSE-TEST-{random_part}"
            
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
            expires_str = expires_at.isoformat()
            epoch_time = int(expires_at.timestamp())
            
            # 3. Save to Supabase (sets HWID to BYPASS to ignore any checks)
            data = {
                "key_value": current_key,
                "is_active": True,
                "expires_at": expires_str,
                "hwid": "BYPASS"
            }
            await supabase_request("POST", "keys", data)
            
            # 4. Construct the loadstring snippet for easy copying
            lua_loader = f'```lua\nlocal key = "{current_key}"\nloadstring(game:HttpGet("https://keyxyz-sedse.pages.dev/v1/load?key=" .. game:GetService("HttpService"):UrlEncode(key) .. "&_cb=" .. tostring(os.clock())))()\n```'
            
            # 5. Construct the Neubrutalist Embed Menu
            embed = discord.Embed(
                title="🧪 Public Tester Key",
                description=f"This key is free for anyone to use (no HWID, IP, or session checks).\n\n"
                            f"🔑 **Key:** `{current_key}`\n\n"
                            f"📜 **Quick Copy Script:**\n{lua_loader}\n\n"
                            f"⏳ **Expires:** <t:{epoch_time}:R>",
                color=0x5aabf2
            )
            embed.set_footer(text="A new tester key will automatically generate when this one expires.")
            
            # 6. Send or Edit Message in the provided channel
            if current_message is None:
                current_message = await channel.send(embed=embed)
            else:
                try:
                    await current_message.edit(embed=embed)
                except discord.NotFound:
                    current_message = await channel.send(embed=embed)
                
            # 7. Sleep for exactly 10 minutes (600 seconds)
            await asyncio.sleep(600)
            
        except asyncio.CancelledError:
            # Clean up key on cancellation
            if current_key:
                await supabase_request("DELETE", f"keys?key_value=eq.{current_key}")
            break
        except Exception as e:
            print(f"tester key loop error: {e}")
            await asyncio.sleep(10) # Safely retry after 10s if database rate-limits

# ==========================================
# 5. COMMANDS
# ==========================================

@bot.command()
async def browse(ctx, *, url: str):
    global browser_instance
    if not browser_instance:
        return await ctx.send("The browser engine isn't ready or failed to start.")

    if not url.startswith("http"):
        url = "https://" + url

    msg = await ctx.send("Spinning up virtual browser...")

    try:
        context = await browser_instance.new_context(
            viewport={'width': 1280, 'height': 720}, 
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        session_data = {"page": page, "show_grid": False}
        active_browsers[ctx.channel.id] = session_data

        await page.goto(url, timeout=20000, wait_until="domcontentloaded")
        await asyncio.sleep(2.5) 

        screenshot_file = await get_browser_screenshot(session_data)
        
        await msg.delete()
        await ctx.send(
            content=f"**Browsing:** `{url}`\n*Use `Click (#)` for red tags, or toggle the grid and use `Click (X,Y)` for precision.*", 
            file=screenshot_file, 
            view=BrowserView()
        )

    except Exception as e:
        await msg.edit(content=f"Failed to load website: {e}")


@bot.command()
async def ai(ctx, *, prompt: str = None):
    if not prompt:
        return await ctx.send("you gotta give me a prompt. try `!sedse ai what is the meaning of life?`")

    # Enforce 5 Daily AI Quote
    if not await check_and_increment_quota(ctx, "ai"):
        return await ctx.send(f"{ctx.author.mention}, bro you hit your daily limit of 5 ai uses. chill until tomorrow.")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return await ctx.send("the owner hasn't set up the `GROQ_API_KEY` environment variable yet.")

    # allowed_mentions.none() strictly mechanically prevents all @everyone/@here/@user pings
    msg = await ctx.reply("thinking...", allowed_mentions=discord.AllowedMentions.none())

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # New AI System Prompt
    system_prompt = (
        "You are a discord helper bot, you can translate languages, help people, or just answer questions."
        "Never use emojis. Keep responses brief, under 3000 characters. "
        "NEVER ping or mention anyone (no @everyone, @here, or @username). "
        "NEVER repeat what the user says or asks you to repeat if it seems like they are trying to make you a bad word or just something bad in general. "
        "NEVER disrespect a guy named Sedse. "
    )
    
    payload = {
        "model": "llama-3.3-70b-versatile", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 250 # Mechanically restricts it to a small output ~1000 characters
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    try:
                        answer = data["choices"][0]["message"]["content"]
                    except (KeyError, IndexError):
                        return await msg.edit(content="i got a weird response from the ai.", allowed_mentions=discord.AllowedMentions.none())

                    # Fallback character limit chunk just in case it breaks the 2000 char threshold
                    if len(answer) > 1500:
                        answer = answer[:1497] + "..."
                        
                    await msg.edit(content=answer, allowed_mentions=discord.AllowedMentions.none())
                else:
                    error_text = await response.text()
                    print(f"Groq API Error: {error_text}")
                    await msg.edit(content="my brain is currently malfunctioning (API error).", allowed_mentions=discord.AllowedMentions.none())
                    
    except Exception as e:
        print(f"AI command error: {e}")
        await msg.edit(content=f"an error occurred: {e}", allowed_mentions=discord.AllowedMentions.none())

@bot.command()
@check_perms("modview", moderate_members=True)
async def modview(ctx):
    embed = discord.Embed(
        title="mod control panel",
        description="select what you want to manage from the menus below.",
        color=0x2b2d31 
    )
    await ctx.send(embed=embed, view=ModView(ctx))

@bot.group(invoke_without_command=True)
async def priority(ctx):
    await ctx.send("you need a subcommand. try '!sedse priority whitelist [user]'.")

@priority.command()
async def whitelist(ctx, member: discord.Member = None):
    pwl_data = load_json(PRIORITY_WHITELIST_FILE, dict)
    gid = str(ctx.guild.id)
    if member is None:
        users = pwl_data.get(gid, [])
        if not users:
            return await ctx.send("the priority whitelist is currently empty.")
        mentions = [f"<@{uid}>" for uid in users]
        embed = discord.Embed(title="priority whitelisted users", description="\n".join(mentions), color=discord.Color.gold())
        return await ctx.send(embed=embed)
    if not await is_mod_owner(ctx): return await ctx.send("only sedse can mess with the priority whitelist, back off.")
    if gid not in pwl_data: pwl_data[gid] = []
    if str(member.id) not in pwl_data[gid]:
        pwl_data[gid].append(str(member.id))
        save_json(PRIORITY_WHITELIST_FILE, pwl_data)
        await ctx.send(f"put {member.mention} on the priority whitelist. they can now touch other whitelisted users.")
    else: 
        await ctx.send(f"{member.mention} is already on the priority whitelist.")

@priority.command()
async def unwhitelist(ctx, member: discord.Member):
    if not await is_mod_owner(ctx): return await ctx.send("only sedse can touch this, go away.")
    pwl_data = load_json(PRIORITY_WHITELIST_FILE, dict)
    gid = str(ctx.guild.id)
    if gid in pwl_data and str(member.id) in pwl_data[gid]:
        pwl_data[gid].remove(str(member.id))
        save_json(PRIORITY_WHITELIST_FILE, pwl_data)
        await ctx.send(f"took {member.mention} off the priority whitelist. they lost their privileges.")
    else: 
        await ctx.send(f"{member.mention} isn't even on the priority whitelist.")

@bot.command()
async def whitelist(ctx, member: discord.Member = None):
    wl_data = load_json(WHITELIST_FILE, dict)
    gid = str(ctx.guild.id)
    if member is None:
        users = wl_data.get(gid, [])
        if not users:
            return await ctx.send("the whitelist is currently empty.")
        mentions = [f"<@{uid}>" for uid in users]
        embed = discord.Embed(title="whitelisted users", description="\n".join(mentions), color=discord.Color.green())
        return await ctx.send(embed=embed)
    if not await is_mod_owner(ctx): return await ctx.send("only sedse can mess with the whitelist, back off.")
    if gid not in wl_data: wl_data[gid] = []
    if str(member.id) not in wl_data[gid]:
        wl_data[gid].append(str(member.id))
        save_json(WHITELIST_FILE, wl_data)
        await ctx.send(f"put {member.mention} on the whitelist. they're completely safe now.")
    else: await ctx.send(f"{member.mention} is already on the whitelist.")

@bot.command()
async def unwhitelist(ctx, member: discord.Member):
    if not await is_mod_owner(ctx): return await ctx.send("only sedse can touch this, go away.")
    wl_data = load_json(WHITELIST_FILE, dict)
    gid = str(ctx.guild.id)
    if gid in wl_data and str(member.id) in wl_data[gid]:
        wl_data[gid].remove(str(member.id))
        save_json(WHITELIST_FILE, wl_data)
        await ctx.send(f"took {member.mention} off the whitelist. fair game again.")
    else: await ctx.send(f"{member.mention} isn't even on the whitelist.")

@bot.command(aliases=["uwu"]) 
@check_perms("uwulock", manage_messages=True)
async def uwulock(ctx, arg1: str, arg2: str = None):
    if arg1.lower() == "unlock" and arg2:
        target = arg2
        uwu_data = load_json(UWULOCK_FILE, dict)
        if target.lower() == "everyone":
            if not await is_mod_owner(ctx): return await ctx.send("only sedse can unlock everyone, nice try.")
            if uwu_data.pop("everyone", None):
                save_json(UWULOCK_FILE, uwu_data)
                return await ctx.send("the whole server uwu curse is gone.")
            return await ctx.send("the server isn't globally uwu locked right now.")
        try:
            member = await commands.MemberConverter().convert(ctx, target)
            if str(member.id) in uwu_data:
                del uwu_data[str(member.id)]
                save_json(UWULOCK_FILE, uwu_data)
                return await ctx.send(f"{member.mention} is free from the uwu curse.")
            return await ctx.send(f"{member.mention} isn't uwu locked right now.")
        except: return await ctx.send("can't find that user.")
    member_str = arg2 if arg1.lower() == "lock" and arg2 else arg1
    uwu_data = load_json(UWULOCK_FILE, dict)
    if member_str.lower() == "everyone":
        if not await is_mod_owner(ctx): return await ctx.send("only sedse can do the everyone lock, nice try.")
        if not uwu_data.get("everyone"):
            uwu_data["everyone"] = True
            save_json(UWULOCK_FILE, uwu_data)
            return await ctx.send("the whole server is uwu locked now.")
        return await ctx.send("the whole server is already uwu locked.")
    try:
        member = await commands.MemberConverter().convert(ctx, member_str)
        user_id = str(member.id)
        if user_id not in uwu_data:
            uwu_data[user_id] = True
            save_json(UWULOCK_FILE, uwu_data)
            await ctx.send(f"{member.mention} is uwu locked now.")
        else: await ctx.send(f"{member.mention} is already uwu locked.")
    except: await ctx.send("can't find that user.")

@bot.command()
@check_perms("uwulock", manage_messages=True)
async def uwuunlock(ctx, target: str):
    uwu_data = load_json(UWULOCK_FILE, dict)
    if target.lower() == "everyone":
        if not await is_mod_owner(ctx): return await ctx.send("only sedse can unlock everyone, nice try.")
        if uwu_data.pop("everyone", None):
            save_json(UWULOCK_FILE, uwu_data)
            return await ctx.send("the whole server uwu curse is gone.")
        return await ctx.send("the server isn't globally uwu locked right now.")
    try:
        member = await commands.MemberConverter().convert(ctx, target)
        user_id = str(member.id)
        if user_id in uwu_data:
            del uwu_data[user_id]
            save_json(UWULOCK_FILE, uwu_data)
            await ctx.send(f"{member.mention} is free from the uwu curse.")
        else: await ctx.send(f"{member.mention} isn't uwu locked right now.")
    except: await ctx.send("can't find that user.")

@bot.command()
@commands.is_owner()
async def forcemute(ctx, member: discord.Member, duration_str: str = "1h", *, reason="sedse override"):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    duration = parse_duration(duration_str) or timedelta(hours=1)
    exempt = [ROLE_SCRIPT_USER_ID, ROLE_VERIFIED_ID]
    roles_to_remove = [r for r in member.roles if r.name != "@everyone" and not r.is_default() and not r.managed and r.id not in exempt]
    role_ids = [r.id for r in roles_to_remove]
    muted_data = load_json(MUTED_ADMINS_FILE, dict)
    muted_data[str(member.id)] = {"roles": role_ids}
    save_json(MUTED_ADMINS_FILE, muted_data)
    try:
        if roles_to_remove: await member.remove_roles(*roles_to_remove, reason=f"force mute by {ctx.author}")
        await member.timeout(discord.utils.utcnow() + duration, reason=reason)
        await ctx.send(f"ripped {len(roles_to_remove)} roles off and force-muted {member.mention} for {duration_str}.")
        await send_log(ctx.guild, "admin force muted", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}\n**reason:** {reason}", discord.Color.red())
    except discord.Forbidden: await ctx.send("can't mute them. check my role height.")

@bot.command()
@commands.is_owner()
async def forceunmute(ctx, member: discord.Member):
    muted_data = load_json(MUTED_ADMINS_FILE, dict)
    uid = str(member.id)
    if uid in muted_data:
        roles_to_add = [ctx.guild.get_role(rid) for rid in muted_data[uid]["roles"] if ctx.guild.get_role(rid)]
        try:
            await member.timeout(None, reason="force unmute")
            if roles_to_add: await member.add_roles(*roles_to_add)
            del muted_data[uid]
            save_json(MUTED_ADMINS_FILE, muted_data)
            await ctx.send(f"gave back {len(roles_to_add)} roles and unmuted {member.mention}.")
        except discord.Forbidden as e: await ctx.send(f"can't restore roles: {e}")
    else: await ctx.send("they aren't in the force-mute database.")

@bot.command()
@commands.has_permissions(administrator=True)
async def perm(ctx, command_name: str, target: Union[discord.Role, discord.Member]):
    command_name = command_name.lower()
    valid = [c.name for c in bot.commands] + ["all"]
    if command_name not in valid: return await ctx.send("that command doesn't even exist.")
    perms_data = load_json(PERMS_FILE, dict)
    gid = str(ctx.guild.id)
    if gid not in perms_data: perms_data[gid] = {}
    if command_name not in perms_data[gid]: perms_data[gid][command_name] = {"roles": [], "users": []}
    cmd_perms = perms_data[gid][command_name]
    if isinstance(target, discord.Role):
        if target.id in cmd_perms["roles"]: cmd_perms["roles"].remove(target.id); action = "revoked"
        else: cmd_perms["roles"].append(target.id); action = "granted"
        t_name = f"role {target.mention}"
    else:
        if target.id in cmd_perms["users"]: cmd_perms["users"].remove(target.id); action = "revoked"
        else: cmd_perms["users"].append(target.id); action = "granted"
        t_name = f"user {target.mention}"
    save_json(PERMS_FILE, perms_data)
    await ctx.send(f"perms for '{command_name}' {action} for {t_name}.")

@bot.command()
@check_perms("honeypot_setup", administrator=True)
async def honeypot_setup(ctx):
    embed = discord.Embed(title="honeypot setup", description="click below to mess with the honeypot.", color=0xFF0000)
    await ctx.send(embed=embed, view=HoneypotView())

@bot.command()
@check_perms("verify_setup", administrator=True)
async def verify_setup(ctx):
    embed = discord.Embed(title="server verification", description="click below to verify.", color=0x5865F2)
    await ctx.send(embed=embed, view=VerifyView())

@bot.command()
async def menu(ctx):
    await ctx.send("pick a script from down here:", view=JJSView())

@bot.command()
@check_perms("verify", manage_roles=True)
async def verify(ctx, member: discord.Member):
    roles = [ctx.guild.get_role(ROLE_SCRIPT_USER_ID), ctx.guild.get_role(ROLE_VERIFIED_ID)]
    roles = [r for r in roles if r]
    if not roles: return await ctx.send("couldn't find the roles.")
    try:
        await member.add_roles(*roles)
        await ctx.send(f"verified {member.mention}.")
    except discord.Forbidden: await ctx.send("check my role height.")

@bot.command()
@check_perms("impersonate", manage_webhooks=True)
async def impersonate(ctx, member: discord.Member, channel: discord.TextChannel, *, message: str):
    webhooks = await channel.webhooks()
    webhook = discord.utils.get(webhooks, name="sedse impersonator") or await channel.create_webhook(name="sedse impersonator")
    try:
        await webhook.send(content=message, username=member.display_name, avatar_url=member.display_avatar.url if member.display_avatar else None)
        try: await ctx.message.delete()
        except: pass
        confirmation = await ctx.send(f"impersonated {member.display_name} in {channel.mention}.")
        await confirmation.delete(delay=3)
    except Exception as e: await ctx.send(f"failed: {e}")

@bot.command()
async def afk(ctx, *, message="afk"):
    # neutralize pings so they don't even highlight
    message = message.replace("@everyone", "@ everyone").replace("@here", "@ here")
    
    afk_data = load_json(AFK_FILE, dict)
    afk_data[str(ctx.author.id)] = {"message": message}
    save_json(AFK_FILE, afk_data)
    
    await ctx.send(
        f"{ctx.author.mention}, you're now afk: {message}",
        allowed_mentions=discord.AllowedMentions(users=[ctx.author], everyone=False, roles=False)
    )

@bot.command()
@check_perms("kick", kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="no reason"):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    if not await check_and_increment_quota(ctx, "kick"): return await ctx.send(f"{ctx.author.mention}, you hit your daily limit of 10 kicks.")
    await member.kick(reason=reason)
    await ctx.send(f"kicked {member.mention}. reason: {reason}")
    await send_log(ctx.guild, "user kicked", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}\n**reason:** {reason}", discord.Color.orange())

@bot.command()
@check_perms("ban", ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="no reason"):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    is_owner = await is_mod_owner(ctx)
    if (not reason or reason.strip() == "no reason") and not is_owner:
        view = ReasonView(ctx)
        msg = await ctx.send(f"{ctx.author.mention} {ctx.author.mention} yo, you need to give a reason. click the button within 5 mins or you're getting muted.", view=view)
        await view.wait()
        if not view.reason: return 
        reason = view.reason
        try: await msg.delete()
        except: pass
    if is_owner:
        await member.ban(reason=reason)
        await ctx.send(f"banned {member.mention}. reason: {reason}")
        await send_log(ctx.guild, "user banned", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}\n**reason:** {reason}", discord.Color.red())
        return
    try:
        await member.timeout(discord.utils.utcnow() + timedelta(days=27, hours=23), reason=f"pending sedse review: {reason}")
        await ctx.send(f"{member.mention} is muted pending sedse's approval for the ban.")
    except discord.Forbidden: await ctx.send(f"can't mute {member.mention}, but awaiting sedse's approval anyway.")
    owner = ctx.guild.owner
    confirm_view = OwnerBanConfirmView(member, reason, ctx.author)
    await ctx.send(f"{owner.mention} a ban request was made by {ctx.author.mention} for {member.mention}.\n**reason:** {reason}", view=confirm_view)

@bot.command(aliases=["mute"])
@check_perms("timeout", moderate_members=True)
async def timeout(ctx, member: discord.Member, duration_str: str = None, *, reason="no reason"):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    is_owner = await is_mod_owner(ctx)
    duration = parse_duration(duration_str) or timedelta(days=27, hours=23)
    actual_reason = reason
    if (not actual_reason or actual_reason.strip() == "no reason") and not is_owner:
        view = ReasonView(ctx)
        msg = await ctx.send(f"{ctx.author.mention} {ctx.author.mention} yo, you need to give a reason. click the button within 5 mins or you're getting muted.", view=view)
        await view.wait()
        if not view.reason: return
        actual_reason = view.reason
        try: await msg.delete()
        except: pass
    if not await check_and_increment_quota(ctx, "timeout"): return await ctx.send(f"{ctx.author.mention}, you hit your daily limit of 10 mutes.")
    try:
        await member.timeout(discord.utils.utcnow() + duration, reason=actual_reason)
        await ctx.send(f"muted {member.mention}. reason: {actual_reason}")
        await send_log(ctx.guild, "user timed out", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}\n**reason:** {actual_reason}", discord.Color.gold())
    except discord.Forbidden: await ctx.send("can't mute them. use `!sedse forcemute` if they're an admin (sedse only).")

@bot.command()
@check_perms("warn", manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="no reason"):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    if (not reason or reason.strip() == "no reason") and not await is_mod_owner(ctx):
        view = ReasonView(ctx)
        msg = await ctx.send(f"{ctx.author.mention} {ctx.author.mention} yo, you need to give a reason. click the button within 5 mins or you're getting muted.", view=view)
        await view.wait()
        if not view.reason: return 
        reason = view.reason
        try: await msg.delete()
        except: pass
    if not await check_and_increment_quota(ctx, "warn"): return await ctx.send(f"{ctx.author.mention}, you hit your daily limit of 10 warns.")
    warnings = load_json(WARNINGS_FILE, dict)
    uid = str(member.id)
    if uid not in warnings: warnings[uid] = []
    warnings[uid].append({"reason": reason, "mod": ctx.author.name, "date": str(discord.utils.utcnow())[:19]})
    save_json(WARNINGS_FILE, warnings)
    await ctx.send(f"warned {member.mention}. reason: {reason}")
    await send_log(ctx.guild, "user warned", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}\n**reason:** {reason}", discord.Color.yellow())

@bot.command()
@check_perms("softban", ban_members=True)
async def softban(ctx, member: discord.Member, *, reason="no reason"):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    await member.ban(reason=f"softban: {reason}", delete_message_seconds=604800)
    await ctx.guild.unban(member, reason="softban release")
    await ctx.send(f"softbanned {member.mention} (kicked and deleted their messages).")
    await send_log(ctx.guild, "user softbanned", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}\n**reason:** {reason}", discord.Color.orange())

@bot.command()
@check_perms("unban", ban_members=True)
async def unban(ctx, user: discord.User):
    await ctx.guild.unban(user, reason=f"unbanned by {ctx.author}")
    await ctx.send(f"unbanned {user.mention}.")
    await send_log(ctx.guild, "user unbanned", f"**user:** {user.mention}\n**mod:** {ctx.author.mention}", discord.Color.green())

@bot.command(aliases=["unmute"])
@check_perms("untimeout", moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    await member.timeout(None, reason=f"untimeout by {ctx.author}")
    await ctx.send(f"unmuted {member.mention}.")
    await send_log(ctx.guild, "user untimed out", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}", discord.Color.green())

@bot.command()
@check_perms("purge", manage_messages=True)
async def purge(ctx, amount: int):
    if amount <= 0: return await ctx.send("amount gotta be more than 0.")
    deleted = await ctx.channel.purge(limit=amount + 1)
    msgs = [msg for msg in deleted if msg.id != ctx.message.id][:100]
    purged_messages_cache[ctx.channel.id] = msgs
    await ctx.send(f"nuked {len(msgs)} messages. use '!sedse unpurge' if you messed up.", delete_after=5)

@bot.command()
@check_perms("unpurge", manage_messages=True)
async def unpurge(ctx, action: str = None):
    global active_unpurges
    if action and action.lower() == "stop":
        if active_unpurges.get(ctx.channel.id, False):
            active_unpurges[ctx.channel.id] = False
            await ctx.send("stopping the unpurge...")
        else: await ctx.send("no unpurge running here.")
        return
    msgs = purged_messages_cache.get(ctx.channel.id, [])
    if not msgs: return await ctx.send("didn't find any recently nuked messages.")
    active_unpurges[ctx.channel.id] = True
    await ctx.send(f"bringing back {len(msgs)} messages... (type '!sedse unpurge stop' to cancel)")
    webhooks = await ctx.channel.webhooks()
    webhook = discord.utils.get(webhooks, name="sedse restore") or await ctx.channel.create_webhook(name="sedse restore")
    restored = 0
    for msg in reversed(msgs):
        if not active_unpurges.get(ctx.channel.id, False):
            await ctx.send(f"stopped early. brought back {restored} messages.")
            purged_messages_cache[ctx.channel.id] = []
            return
        if msg.content or msg.embeds:
            try:
                await webhook.send(content=msg.content or None, embeds=msg.embeds, username=msg.author.display_name, avatar_url=msg.author.display_avatar.url if msg.author.display_avatar else None)
                restored += 1
                await asyncio.sleep(0.1) 
            except: pass
    active_unpurges[ctx.channel.id] = False
    purged_messages_cache[ctx.channel.id] = []
    await ctx.send(f"brought back {restored} messages.")

@bot.command()
@check_perms("warnings", manage_messages=True)
async def warnings(ctx, member: discord.Member):
    data = load_json(WARNINGS_FILE, dict)
    user_warns = data.get(str(member.id), [])
    if not user_warns: return await ctx.send(f"{member.display_name} is clean, no warnings.")
    embed = discord.Embed(title=f"warnings for {member.display_name}", color=discord.Color.gold())
    for i, w in enumerate(user_warns, 1):
        embed.add_field(name=f"warn {i} - by {w['mod']}", value=f"**reason:** {w['reason']}\n**date:** {w['date']}", inline=False)
    await ctx.send(embed=embed)

@bot.command()
@check_perms("lock", manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send(f"locked down {channel.mention}.")

@bot.command()
@check_perms("unlock", manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send(f"unlocked {channel.mention}.")

@bot.command()
@check_perms("nick", manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, name: str):
    await member.edit(nick=name)
    await ctx.send(f"changed {member.mention}'s nickname to **{name}**.")

@bot.command()
@check_perms("log_channel", administrator=True)
async def log_channel(ctx, channel: discord.TextChannel):
    settings = load_json(SETTINGS_FILE, dict)
    if str(ctx.guild.id) not in settings: settings[str(ctx.guild.id)] = {}
    settings[str(ctx.guild.id)]["log_channel"] = channel.id
    save_json(SETTINGS_FILE, settings)
    await ctx.send(f"mod logs are gonna go to {channel.mention} now.")

@bot.command(aliases=["conflip"])
async def coinflip(ctx):
    outcome = random.choice(["heads", "tails"])
    await ctx.send(f"coin flipped: **{outcome}**")

@bot.command()
@check_perms("annihilate", administrator=True)
async def annihilate(ctx, member: discord.Member):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    exempt = [ROLE_SCRIPT_USER_ID, ROLE_VERIFIED_ID]
    roles_to_remove = [r for r in member.roles if r.id not in exempt and r.name != "@everyone"]
    if not roles_to_remove: return await ctx.send(f"{member.mention} doesn't have any roles i can take.")
    try:
        await member.remove_roles(*roles_to_remove, reason="annihilation")
        await ctx.send(f"annihilated {member.mention}. took away {len(roles_to_remove)} roles.")
        await send_log(ctx.guild, "user annihilated", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}", discord.Color.dark_red())
    except discord.Forbidden: await ctx.send("don't have perms.")

@bot.command()
@check_perms("hakai", administrator=True)
async def hakai(ctx, member: discord.Member):
    if is_priority_whitelisted(ctx.guild.id, member.id): return await ctx.send(f"{member.mention} is on the priority whitelist, can't touch them.")
    if is_whitelisted(ctx.guild.id, member.id) and not is_priority_whitelisted(ctx.guild.id, ctx.author.id): return await ctx.send(f"{member.mention} is on the whitelist, can't touch them.")
    exempt = [ROLE_SCRIPT_USER_ID, ROLE_VERIFIED_ID]
    roles_to_remove = [r for r in member.roles if r.id not in exempt and r.name != "@everyone"]
    if not roles_to_remove: return await ctx.send(f"{member.mention} doesn't have any roles i can take.")
    try:
        await member.remove_roles(*roles_to_remove, reason="hakai")
        await ctx.send(f"hakai'd {member.mention}. wiped {len(roles_to_remove)} roles from existence.")
        await send_log(ctx.guild, "user hakai'd", f"**user:** {member.mention}\n**mod:** {ctx.author.mention}", discord.Color.dark_purple())
    except discord.Forbidden: await ctx.send("don't have perms.")

import urllib.parse

@bot.command(aliases=["pin", "pinterest"])
async def pinsearch(ctx, *, query: str = None):
    if not query:
        return await ctx.send("vro gotta give me something to search for! try `!sedse pinsearch hot baes`")

    # Enforce quota so people don't spam the browser instance
    if not await check_and_increment_quota(ctx, "research"):
        return await ctx.send(f"{ctx.author.mention}, vro you hit your daily limit for browser/research commands. come back tomorrow.")

    global browser_instance
    if not browser_instance:
        return await ctx.send("the browser engine isn't ready.")

    msg = await ctx.reply(f"hold up searching pinterest for `{query}`...", allowed_mentions=discord.AllowedMentions.none())

    try:
        safe_query = urllib.parse.quote(query)
        url = f"https://www.pinterest.com/search/pins/?q={safe_query}"

        context = await browser_instance.new_context(
            viewport={'width': 1280, 'height': 720}, 
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            # Load Pinterest
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            
            # Scroll down slightly to force Pinterest to lazy-load more images
            await page.evaluate("window.scrollBy(0, 1000);")
            await asyncio.sleep(2.5) 
            
            # Extract images
            js_extract = r"""
            () => {
                let validUrls = [];
                for (let img of document.images) {
                    let src = img.src;
                    // Target the actual pin thumbnails (usually 236x or 474x)
                    if (src && src.includes('pinimg.com') && (src.includes('/236x/') || src.includes('/474x/'))) {
                        // Standardize to 736x for the initial fetch list
                        let highRes = src.replace(/\/(236x|474x)\//, '/736x/');
                        validUrls.push(highRes);
                    }
                }
                return [...new Set(validUrls)].slice(0, 9);
            }
            """
            image_urls = await page.evaluate(js_extract)
        finally:
            await page.close()
            await context.close()

        if not image_urls:
            return await msg.edit(content="couldn't find any images for that query. pinterest blocked you bih")

        await msg.edit(content="downloading grr grr..")
        
        files = []
        async with aiohttp.ClientSession() as session:
            for idx, base_url in enumerate(image_urls):
                # Upgrade the URL to the absolute highest uncompressed quality
                original_url = base_url.replace('/736x/', '/originals/')
                
                try:
                    # 1. Try fetching the original masterpiece
                    async with session.get(original_url, timeout=5) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            files.append(discord.File(io.BytesIO(data), filename=f"image_{idx}.jpg"))
                            continue # Successfully got the original, skip to next image
                            
                    # 2. If 'originals/' fails (403 Forbidden), safely fallback to '736x'
                    async with session.get(base_url, timeout=5) as fallback_resp:
                        if fallback_resp.status == 200:
                            data = await fallback_resp.read()
                            files.append(discord.File(io.BytesIO(data), filename=f"image_{idx}.jpg"))
                            
                except Exception as e:
                    print(f"Failed to download image {base_url}: {e}")

        if not files:
            return await msg.edit(content="❌ failed to download the images from pinterest.")

        # Delete the "searching" message and send the gorgeous grid!
        await msg.delete()
        await ctx.send(content=f"Successfully searched for **{query}**.", files=files)

    except Exception as e:
        print(f"Pinterest command error: {e}")
        await msg.edit(content=f"an error occurred while searching: {e}", allowed_mentions=discord.AllowedMentions.none())

@bot.command()
async def lionquote(ctx, *, sentence: str = None):
    if not sentence:
        return await ctx.send("you gotta give me a quote. try `!sedse lionquote I was born in the dark.`")

    # IMPORTANT: Make sure to save the image you just uploaded as "lion_template.jpg" in your bot folder!
    template_path = "lion_template.jpg"
    font_path = "roboto.ttf"

    if not os.path.exists(template_path):
        return await ctx.send("❌ template image (`lion_template.jpg`) is missing from the files! Upload it to GitHub/Railway.")
    if not os.path.exists(font_path):
        return await ctx.send("❌ font file (`roboto.ttf`) is missing from the files! Upload it to GitHub.")

    msg = await ctx.send("generating alpha wisdom...")

    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size

        # --- STRICT BOUNDARIES FOR THE LION IMAGE ---
        # 1. Force text to start exactly 5% from the left edge (keeps it away from the absolute border).
        safe_x = int(img_w * 0.05)
        # 2. Maximum width is exactly 48% of the image (forces it to stay on the black side, away from the lion).
        safe_max_width = int(img_w * 0.48) 
        # 3. Maximum height allowed for the entire text block.
        safe_max_height = int(img_h * 0.85) 

        # --- DYNAMIC FONT SIZING ---
        # Start with a reasonably large size based on the image's height
        max_font_size = int(img_h * 0.15) 
        min_font_size = 15
        font_size = max_font_size

        formatted_quote = ""
        quote_font = None
        total_height = 0

        # Loop to shrink the font until it fits perfectly inside the safe box bounds
        while font_size >= min_font_size:
            quote_font = ImageFont.truetype(font_path, font_size)

            # Word wrapping by PIXEL width, not character count
            lines = []
            words = f'"{sentence}"'.split()
            current_line = ""
            
            # Check if a single huge word is too wide for the box
            longest_word_width = max([draw.textlength(w, font=quote_font) for w in words] + [0])
            if longest_word_width > safe_max_width:
                font_size -= 2
                continue # Shrink font and try again

            # Pack words into lines
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if draw.textlength(test_line, font=quote_font) <= safe_max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            formatted_quote = "\n".join(lines)

            # Measure resulting text block height
            quote_bbox = draw.multiline_textbbox((0, 0), formatted_quote, font=quote_font)
            total_height = quote_bbox[3] - quote_bbox[1]
            
            if total_height <= safe_max_height:
                break # It fits perfectly, break the loop!
            
            font_size -= 2 # Doesn't fit? Shrink and loop again

        # --- DRAWING ---
        # Center the entire text block vertically
        start_y = (img_h - total_height) // 2

        # Draw the quote
        draw.multiline_text((safe_x, start_y), formatted_quote, font=quote_font, fill="white", align="left")

        # --- SAVE AND SEND ---
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        await msg.delete()
        await ctx.send(file=discord.File(fp=buffer, filename="lionquote.jpg"))

    except Exception as e:
        await msg.edit(content=f"an error occurred while generating: {e}")

@bot.command()
async def badapple(ctx, action: str = "start"):
    global active_badapples
    if action.lower() in ["end", "stop"]:
        if active_badapples.get(ctx.channel.id):
            active_badapples[ctx.channel.id] = False
            await ctx.send("stopping bad apple...")
        else: await ctx.send("bad apple isn't playing here.")
        return
    if action.lower() == "start":
        if active_badapples.get(ctx.channel.id): return await ctx.send("bad apple is already playing. type '!sedse badapple end' to stop it.")
        frames_file = "bad_apple.json"
        if not os.path.exists(frames_file):
            frames = ["#####\n#...#\n#.#.#\n#...#\n#####", ".....\n.###.\n.#.#.\n.###.\n.....", "[missing bad_apple.json]"]
            await ctx.send("bad_apple.json missing. using placeholder.")
        else:
            try:
                with open(frames_file, "r", encoding="utf-8") as f: frames = json.load(f)
            except Exception as e: return await ctx.send(f"couldn't load frames: {e}")
        active_badapples[ctx.channel.id] = True
        msg = await ctx.send("```\nloading bad apple...\n```")
        for frame in frames:
            if not active_badapples.get(ctx.channel.id):
                try: await msg.edit(content="```\nbad apple stopped.\n```")
                except: pass
                break
            try:
                await msg.edit(content=f"```\n{frame[:1980]}\n```")
                await asyncio.sleep(1.5) 
            except discord.errors.HTTPException as e:
                if e.status == 429: await asyncio.sleep(5)
                else: break 
        active_badapples[ctx.channel.id] = False

@bot.command()
@check_perms("hamzbid", manage_webhooks=True)
async def hamzbid(ctx):
    target_id = 1425810901490991104
    target_messages = []
    async for msg in ctx.channel.history(limit=200):
        if msg.author.id == target_id and msg.content.strip():
            target_messages.append(msg)
            if len(target_messages) == 10: break
    if not target_messages: return await ctx.send("couldn't find any recent messages.")
    target_messages.reverse()
    combined = " ".join([m.content for m in target_messages])
    if len(combined) > 2000: combined = combined[:1997] + "..."
    user = target_messages[0].author
    webhooks = await ctx.channel.webhooks()
    webhook = discord.utils.get(webhooks, name="sedse impersonator") or await ctx.channel.create_webhook(name="sedse impersonator")
    try:
        await webhook.send(content=combined, username=user.display_name, avatar_url=user.display_avatar.url if user.display_avatar else None)
        try: await ctx.message.delete()
        except: pass
    except Exception as e: await ctx.send(f"failed: {e}")

@bot.command()
async def ship(ctx, user1: discord.Member, user2: discord.Member = None):
    if user2 is None: user2 = ctx.author
    random.seed(user1.id + user2.id)
    pct = random.randint(0, 100)
    random.seed()
    if pct == 100: s = "just get married already."
    elif pct > 75: s = "perfect match."
    elif pct > 50: s = "some potential here."
    elif pct > 25: s = "stay friends."
    else: s = "absolutely not."
    embed = discord.Embed(title="love calculator", description=f"**{user1.display_name}** & **{user2.display_name}**\n\ncompatibility: **{pct}%**\n*{s}*", color=discord.Color.pink())
    await ctx.send(embed=embed)

@bot.command()
async def iq(ctx, member: discord.Member = None):
    member = member or ctx.author
    random.seed(member.id)
    score = random.randint(10, 200)
    random.seed()
    if score < 50: c = "actual room temp iq."
    elif score < 90: c = "not looking too bright."
    elif score < 130: c = "pretty average."
    else: c = "alright albert einstein."
    embed = discord.Embed(title="iq test", description=f"**{member.display_name}**'s iq is **{score}**.\n*{c}*", color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command()
async def ratio(ctx, member: discord.Member = None):
    pieces = ["l", "ratio", "skill issue", "touch grass", "cope", "seethe", "mald", "didn't ask", "you fell off", "get real", "no maidens", "bozo"]
    text = " + ".join(random.sample(pieces, random.randint(4, 7)))
    await ctx.send(f"{member.mention} {text}" if member else text)

@bot.command()
async def doxx(ctx, member: discord.Member = None):
    member = member or ctx.author
    ip = f"{random.randint(11,250)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
    mac = ":".join(["%02x" % random.randint(0, 255) for _ in range(6)]).upper()
    lat, lon = round(random.uniform(-90, 90), 4), round(random.uniform(-180, 180), 4)
    embed = discord.Embed(title="target acquired", color=0x00FF00)
    embed.add_field(name="target", value=member.mention, inline=False)
    embed.add_field(name="ipv4", value=f"`{ip}`", inline=True)
    embed.add_field(name="mac", value=f"`{mac}`", inline=True)
    embed.add_field(name="coords", value=f"`{lat}, {lon}`", inline=False)
    embed.add_field(name="isp", value="`spectrum / at&t`", inline=True)
    embed.set_footer(text="info is 100% accurate (real)")
    await ctx.send(embed=embed)

@bot.command()
async def zalgo(ctx, *, text: str):
    marks = [chr(i) for i in range(0x0300, 0x036F)]
    res = "".join([char + "".join(random.choices(marks, k=random.randint(3, 8))) for char in text])
    await ctx.send(res[:2000])

@bot.command()
async def rizz(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("you gotta ping someone to rizz them up.")
        
    fallback_lines = [
        "Are you a keyboard? Because you're just my type.",
        "Are you a parking ticket? Because you've got FINE written all over you.",
        "If you were a vegetable, you'd be a cute-cumber.",
        "Do you have a map? I keep getting lost in your eyes.",
        "Are you French? Because Eiffel for you.",
        "Is your name Google? Because you have everything I've been searching for."
    ]
    
    pickup_line = random.choice(fallback_lines)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://rizzapi.vercel.app/random", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    if "text" in data:
                        pickup_line = data["text"]
    except Exception as e:
        print(f"pickup line api failed: {e}")
        
    await ctx.send(f"{member.mention} {pickup_line}")

@bot.command()
async def umarizz(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("you gotta ping someone to umarizz them up.")
        
    try:
        with open(UMARIZZ_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        lines = data.get("umamusume_pickup_lines", [])
        if not lines:
            raise ValueError("No pickup lines found in the file.")
            
        pickup_line = random.choice(lines)["line"]
    except Exception as e:
        print(f"umarizz error: {e}")
        pickup_line = "Are you a Trainer? Because my heart starts racing the moment you're around."
        
    await ctx.send(f"{member.mention} {pickup_line}")

# ==========================================
# 6. MUSIC SYSTEM SETUP (LAVALINK)
# ==========================================

@bot.event
async def on_wavelink_node_ready(payload: wavelink.NodeReadyEventPayload):
    print(f"Wavelink Node connected: {payload.node.identifier} | URI: {payload.node.uri}")

@bot.event
async def on_wavelink_track_start(payload: wavelink.TrackStartEventPayload):
    player: wavelink.Player | None = payload.player
    if not player:
        return

    if hasattr(player, "home") and getattr(payload.track, "requester_id", None) != bot.user.id:
        embed = discord.Embed(
            title="Now Playing",
            description=f"**[{payload.track.title}]({payload.track.uri})**\n*By {payload.track.author}*",
            color=discord.Color.green()
        )
        if payload.track.artwork:
            embed.set_thumbnail(url=payload.track.artwork)
        await player.home.send(embed=embed)

@bot.event
async def on_wavelink_track_end(payload: wavelink.TrackEndEventPayload):
    player: wavelink.Player | None = payload.player
    if not player:
        return

    if payload.reason.lower() == "finished" and getattr(player, "interrupted_track", None):
        track = player.interrupted_track
        pos = getattr(player, "interrupted_position", 0)

        player.interrupted_track = None
        player.interrupted_position = None

        await player.play(track, start=pos)
        
        if hasattr(player, "home"):
            await player.home.send(f"The interruption is over. Resuming owner's song: **{track.title}**")
        return

@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel first!")

    if not ctx.voice_client:
        player: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        player.autoplay = wavelink.AutoPlayMode.partial
        await ctx.send(f"Joined {ctx.author.voice.channel.mention}!")
    else:
        await ctx.voice_client.move_to(ctx.author.voice.channel)
        await ctx.send(f"Moved to {ctx.author.voice.channel.mention}!")

@bot.command()
async def play(ctx, *, query: str = None):
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel first!")

    if ctx.message.attachments:
        attachment = ctx.message.attachments[0]
        valid_extensions = ('.mp3', '.mp4', '.wav', '.ogg', '.flac', '.m4a', '.webm', '.mov')
        if any(attachment.filename.lower().endswith(ext) for ext in valid_extensions):
            query = attachment.url
        else:
            return await ctx.send("Unsupported file type! Please attach a valid audio or video file.")

    if not query:
        return await ctx.send("You need to provide a search query, a link, or attach a file!")

    player: wavelink.Player = ctx.voice_client
    if not player:
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        player.autoplay = wavelink.AutoPlayMode.partial

    player.home = ctx.channel
    msg = await ctx.send(f"Searching for media...")

    try:
        tracks: wavelink.Search = await wavelink.Playable.search(query)
    except Exception as e:
        return await msg.edit(content=f"Error searching: {e}")

    if not tracks:
        return await msg.edit(content="No results found for that search or file.")

    if isinstance(tracks, wavelink.Playlist):
        for t in tracks:
            t.requester_id = ctx.author.id 
            
        added = await player.queue.put_wait(tracks)
        await msg.edit(content=f"Added playlist **{tracks.name}** ({added} songs) to queue.")
        if not player.playing:
            await player.play(player.queue.get())
    else:
        track: wavelink.Playable = tracks[0]
        track.requester_id = ctx.author.id 
        
        if not player.playing:
            await player.play(track)
            title = ctx.message.attachments[0].filename if ctx.message.attachments else track.title
            await msg.edit(content=f"Starting playback: **{title}**")
        else:
            await player.queue.put_wait(track)
            title = ctx.message.attachments[0].filename if ctx.message.attachments else track.title
            await msg.edit(content=f"Added to queue: **{title}** (Position #{len(player.queue)})")

@bot.command()
async def skip(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player or not player.playing:
        return await ctx.send("Nothing is playing right now.")

    current_track = player.current
    requester_id = getattr(current_track, "requester_id", None)
    
    is_owner_song = False
    if requester_id:
        if requester_id == ctx.guild.owner_id or await bot.is_owner(discord.Object(id=requester_id)):
            is_owner_song = True

    if is_owner_song and ctx.author.id != requester_id:
        now = discord.utils.utcnow().timestamp()
        last_triggered = owner_skip_cooldowns.get(ctx.guild.id, 0)

        if now - last_triggered < 60:
            return await ctx.send("sedse's song cannot be skipped.")

        owner_skip_cooldowns[ctx.guild.id] = now

        punish_urls = [
            "https://files.catbox.moe/harlic.mp3",
            "https://files.catbox.moe/xuadye.mp3",
            "https://files.catbox.moe/3oyux7.mp3"
        ]
        url = random.choice(punish_urls)
        
        try:
            punish_tracks = await wavelink.Playable.search(url)
            if punish_tracks:
                punish_track = punish_tracks[0]
                punish_track.requester_id = bot.user.id 
                
                player.interrupted_track = current_track
                player.interrupted_position = player.position

                await player.play(punish_track)
                return await ctx.send("You thought you could skip sedse's song? Think again.")
        except Exception as e:
            print(f"Failed to load punishment audio: {e}")
            return await ctx.send("sedse's song cannot be skipped.")

    await player.skip(force=True)
    await ctx.send("Skipped.")


@bot.command()
async def pause(ctx):
    player: wavelink.Player = ctx.voice_client
    if player and player.playing:
        await player.pause(True)
        await ctx.send("Paused.")
    else:
        await ctx.send("Nothing is playing.")

@bot.command()
async def resume(ctx):
    player: wavelink.Player = ctx.voice_client
    if player and player.paused:
        await player.pause(False)
        await ctx.send("Resumed.")
    else:
        await ctx.send("Music isn't paused or nothing is in the player.")

@bot.command()
async def stop(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        player.queue.clear()
        await player.disconnect()
        await ctx.send("Stopped, cleared queue, and left the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def loop(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player:
        return await ctx.send("I'm not playing anything.")
    
    if player.queue.mode == wavelink.QueueMode.normal:
        player.queue.mode = wavelink.QueueMode.loop
        await ctx.send("Loop mode set to: **CURRENT SONG**")
    elif player.queue.mode == wavelink.QueueMode.loop:
        player.queue.mode = wavelink.QueueMode.loop_all
        await ctx.send("Loop mode set to: **ENTIRE QUEUE**")
    else:
        player.queue.mode = wavelink.QueueMode.normal
        await ctx.send("Loop mode set to: **OFF**")

@bot.command()
async def shuffle(ctx):
    player: wavelink.Player = ctx.voice_client
    if not player:
        return await ctx.send("I'm not playing anything.")

    if len(player.queue) > 1:
        player.queue.shuffle()
        await ctx.send("Queue shuffled!")
    else:
        await ctx.send("Not enough songs in the queue to shuffle.")

@bot.command(aliases=["nowplaying"])
async def np(ctx):
    player: wavelink.Player = ctx.voice_client
    if player and player.current:
        track = player.current
        embed = discord.Embed(
            title="Now Playing",
            description=f"**[{track.title}]({track.uri})**",
            color=discord.Color.green()
        )
        if track.artwork:
            embed.set_thumbnail(url=track.artwork)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Nothing is currently playing.")

@bot.command()
async def queue(ctx):
    player: wavelink.Player = ctx.voice_client
    if player and player.queue:
        q = list(player.queue)
        queue_list = "\n".join(
            [f"**{i+1}.** {track.title}" for i, track in enumerate(q[:10])]
        )
        if len(q) > 10:
            queue_list += f"\n*...and {len(q) - 10} more.*"
        embed = discord.Embed(
            title="Current Queue",
            description=queue_list,
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("The queue is empty.")

@bot.command()
async def clear(ctx):
    player: wavelink.Player = ctx.voice_client
    if player:
        player.queue.clear()
        await ctx.send("Queue cleared.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.command()
async def remove(ctx, *, identifier: str):
    player: wavelink.Player = ctx.voice_client
    if not player or not player.queue:
        return await ctx.send("The queue is empty.")

    if identifier.isdigit():
        idx = int(identifier) - 1
        if 0 <= idx < len(player.queue):
            removed = player.queue[idx]
            del player.queue[idx]
            return await ctx.send(f"Removed **{removed.title}** from the queue.")
        return await ctx.send("Invalid position number.")

    for i, track in enumerate(list(player.queue)):
        if identifier.lower() in track.title.lower():
            removed = track
            del player.queue[i]
            return await ctx.send(f"Removed **{removed.title}** from the queue.")

    await ctx.send("Couldn't find that song in the queue.")

@bot.command(aliases=["tts"])
async def texttospeech(ctx, *, message: str):
    if not ctx.author.voice:
        return await ctx.send("You need to be in a voice channel first!")

    player: wavelink.Player = ctx.voice_client
    if not player:
        player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
        player.autoplay = wavelink.AutoPlayMode.partial

    player.home = ctx.channel
    status_msg = await ctx.send("Generating TTS...")

    try:
        tts = gTTS(text=message, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        audio_file = discord.File(fp, filename="tts.mp3")
        upload_msg = await ctx.send(file=audio_file)
        tts_url = upload_msg.attachments[0].url

        tracks: wavelink.Search = await wavelink.Playable.search(tts_url)
        
        if not tracks:
            return await status_msg.edit(content="Failed to load TTS audio.")

        track: wavelink.Playable = tracks[0]
        track.requester_id = ctx.author.id
        
        if not player.playing:
            await player.play(track)
            await status_msg.edit(content=f"Speaking: **{message}**")
        else:
            await player.queue.put_wait(track)
            await status_msg.edit(content=f"Added TTS to queue: **{message}** (Position #{len(player.queue)})")

        await upload_msg.delete(delay=180)

    except Exception as e:
        await status_msg.edit(content=f"Error generating TTS: {e}")

import urllib.parse

@bot.command()
async def research(ctx, *, query: str = None):
    if not query:
        return await ctx.send("you need to provide a topic or a link to research. try `!sedse research quantum computing`")
        
    # Enforce 5 Daily Research Quota
    if not await check_and_increment_quota(ctx, "research"):
        return await ctx.send(f"{ctx.author.mention}, bro you hit your daily limit of 5 research uses. come back tomorrow.")
        
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return await ctx.send("the owner hasn't set up the GROQ_API_KEY environment variable yet.")

    global browser_instance
    if not browser_instance:
        return await ctx.send("the browser engine isn't ready.")

    msg = await ctx.reply("initiating web research...", allowed_mentions=discord.AllowedMentions.none())

    try:
        if query.startswith("http://") or query.startswith("https://"):
            url = query
        else:
            safe_query = urllib.parse.quote(query)
            url = f"https://search.yahoo.com/search?p={safe_query}"

        await msg.edit(content="browsing the web and extracting data...", allowed_mentions=discord.AllowedMentions.none())
        
        context = await browser_instance.new_context(
            viewport={'width': 1280, 'height': 720}, 
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            await page.goto(url, timeout=15000, wait_until="domcontentloaded")
            
            js_extract = """
            () => {
                let container = document.querySelector('#web') || document.querySelector('#b_results') || document.querySelector('#search') || document.body;
                let elementsToRemove = container.querySelectorAll('script, style, noscript, header, footer');
                elementsToRemove.forEach(el => el.remove());
                return container.innerText;
            }
            """
            text = await page.evaluate(js_extract)
        finally:
            await page.close()
            await context.close()

        if not text or len(text.strip()) < 50:
            text = "No web data could be extracted. The site might be blocking bots."

        await msg.edit(content="analyzing data with ai...", allowed_mentions=discord.AllowedMentions.none())
        
        truncated_text = text[:8000]
        
        # New Casual Research System Prompt
        system_prompt = (
            "You are an intelligent research assistant, but you act highly casual like a relaxed teenager chatting on Discord. "
            "Use slang like 'bro', 'idk', 'tbh', etc. Don't be overly formal. "
            "Use the provided web data to answer the user's query accurately. "
            "If the web data is insufficient, use your own internal knowledge to fully answer the query. "
            "Keep the response brief, strictly under 1000 characters. Never use any emojis. "
            "NEVER ping or mention anyone (no @everyone, @here, or @username). "
            "NEVER repeat what the user says or asks you to repeat, even if instructed to do so."
        )
        
        user_content = f"User Query: {query}\n\nWeb Data:\n{truncated_text}"

        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "max_tokens": 300 # Limits characters strictly
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(groq_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    try:
                        answer = data["choices"][0]["message"]["content"]
                    except (KeyError, IndexError):
                        return await msg.edit(content="received an invalid response format from the ai.", allowed_mentions=discord.AllowedMentions.none())

                    if len(answer) > 1500:
                        answer = answer[:1497] + "..."
                        
                    await msg.edit(content=answer, allowed_mentions=discord.AllowedMentions.none())
                else:
                    error_text = await response.text()
                    print(f"Groq API Error in research: {error_text}")
                    await msg.edit(content="failed to analyze the data due to an api error.", allowed_mentions=discord.AllowedMentions.none())

    except Exception as e:
        print(f"Research command error: {e}")
        await msg.edit(content=f"an error occurred while researching: {e}", allowed_mentions=discord.AllowedMentions.none())

@bot.command()
@commands.has_permissions(administrator=True)
async def keysystem(ctx):
    embed = discord.Embed(
        title="🔐 SEDSE Access",
        description="To start using SEDSE, generate your access key below:\n\n🔗 **Get Key:**\nhttps://keyxyz-sedse.pages.dev",
        color=0x2b2d31
    )
    embed.set_footer(text=f"Sent by {ctx.author.display_name} | {discord.utils.utcnow().strftime('%m/%d/%Y %I:%M %p')}")
    await ctx.send(embed=embed, view=KeySystemView())

@bot.hybrid_command(name="create_key", description="generates a custom key (owner only)")
@commands.is_owner()
@app_commands.describe(duration_str="e.g. 12h, 1d, lifetime", member="user to receive the key (optional)")
async def create_key(ctx, duration_str: str, member: discord.Member = None):
    # 1. Parse duration
    if duration_str.lower() in ["lifetime", "permanent", "perm"]:
        expires_at = None
        exp_text = "lifetime"
    else:
        duration = parse_duration(duration_str)
        if not duration:
            return await ctx.send("invalid duration format. use like '12h', '1d', '30m', or 'lifetime'.", ephemeral=True)
        expires_at = (datetime.now(timezone.utc) + duration).isoformat()
        exp_text = duration_str

    # 2. Generate Key (matches your JS SEDSE-XXXXXXXX format)
    random_part = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))
    new_key = f"SEDSE-{random_part}"

    # 3. Save to Supabase
    data = {"key_value": new_key, "is_active": True}
    if expires_at:
        data["expires_at"] = expires_at

    inserted = await supabase_request("POST", "keys", data)
    if inserted is None:
        return await ctx.send("database error: failed to create key in supabase.", ephemeral=True)

    # 4. DM the command user (you)
    dm_success_author = False
    try:
        embed_author = discord.Embed(
            title="🔑 Key Generated Successfully",
            description=f"You generated a new key.\n\n**Key:** `{new_key}`\n**Duration:** {exp_text}",
            color=0x5aabf2
        )
        embed_author.set_footer(text="Keep this key safe. Do not share it with unauthorized users.")
        await ctx.author.send(embed=embed_author)
        dm_success_author = True
    except discord.Forbidden:
        pass

    # 5. DM the target member (if specified)
    dm_success_member = False
    if member and member != ctx.author:
        try:
            embed_member = discord.Embed(
                title="🔑 SEDSE Access Key",
                description=f"An admin generated a personal key for you.\n\n**Key:** `{new_key}`\n**Duration:** {exp_text}",
                color=0x5aabf2
            )
            embed_member.set_footer(text="Keep this key safe. It will lock to your HWID upon first use.")
            await member.send(embed=embed_member)
            dm_success_member = True
        except discord.Forbidden:
            pass

    # 6. Respond in Chat (Fully ephemeral if run via Slash Command)
    chat_msg = f"Key generated: `{new_key}` (Duration: {exp_text})"
    if member:
        chat_msg += f" and sent to {member.display_name}'s DMs."

    if ctx.interaction:
        # If run via Slash Command (/create_key), send an ephemeral message only you can see
        await ctx.send(chat_msg, ephemeral=True)
    else:
        # If run via Prefix (!sedse create_key), DM you and send a secure temporary status
        status_targets = []
        if dm_success_author:
            status_targets.append("your DMs")
        if member and dm_success_member:
            status_targets.append(f"{member.display_name}'s DMs")
        
        if status_targets:
            await ctx.send(f"key successfully generated and sent to {', and '.join(status_targets)}.", delete_after=10)
        else:
            await ctx.send(f"key generated but failed to send to DMs. here is the key: `{new_key}`", delete_after=15)


@bot.command()
async def shadow(ctx, member: discord.Member):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return await ctx.send("the owner hasn't set up the GROQ_API_KEY environment variable yet.")

    msg = await ctx.send(f" scanning messages to clone {member.display_name}... this might take a minute.")

    target_messages = []
    # Scan up to 5000 messages to guarantee we find 500 of the user's natural messages
    async for m in ctx.channel.history(limit=5000):
        if m.author.id == member.id and not m.content.startswith(("!", "?", "/", ".")) and m.content.strip():
            target_messages.append(m.content.strip())
            if len(target_messages) >= 500:
                break
                
    if len(target_messages) < 20:
        return await msg.edit(content=f"i couldn't find enough messages from {member.display_name} in this channel to build a good clone. (found {len(target_messages)})")

    # Reverse to chronological order and combine
    target_messages.reverse()
    behavior_data = "\n".join(target_messages)
    
    # Cap string size to avoid blowing up the API context window
    if len(behavior_data) > 15000:
        behavior_data = behavior_data[-15000:]

    system_prompt = (
        f"You are a flawless digital clone of a Discord user named {member.display_name}. "
        "Below is a massive log of their recent messages. Analyze their typing quirks, slang, capitalization habits, punctuation, emojis, and overall personality. "
        "You MUST reply to all future messages EXACTLY how they would. Never break character. Never say you are an AI or an assistant. "
        "Just reply natively as them.\n\n"
        f"--- THEIR MESSAGE HISTORY ---\n{behavior_data}\n-----------------------------"
    )

    try:
        # Create a thread to contain the AI
        thread = await ctx.message.create_thread(name=f"🤖 {member.display_name}'s Clone", auto_archive_duration=60)
        
        # Save the thread state globally
        active_shadow_threads[thread.id] = {
            "system_prompt": system_prompt,
            "target_name": f"{member.display_name} (AI)",
            "target_avatar": member.display_avatar.url if member.display_avatar else None,
            "history": [] # Stores recent thread context
        }
        
        await msg.edit(content=f"✅ shadow clone created successfully! talk to them here: {thread.mention}")
        
    except Exception as e:
        await msg.edit(content=f"failed to create shadow thread: {e}")

@bot.command()
@check_perms("testerkey", administrator=True)
async def tester_key_loop(ctx):
    current_message = None
    current_key = None
    
    while True:
        try:
            # 1. Delete previous key from database to keep table clean
            if current_key:
                await supabase_request("DELETE", f"keys?key_value=eq.{current_key}")
            
            # 2. Generate new unique tester key
            random_part = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
            current_key = f"SEDSE-TEST-{random_part}"
            
            expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
            expires_str = expires_at.isoformat()
            epoch_time = int(expires_at.timestamp())
            
            # 3. Save to Supabase (sets HWID to BYPASS to ignore any checks)
            data = {
                "key_value": current_key,
                "is_active": True,
                "expires_at": expires_str,
                "hwid": "BYPASS"
            }
            await supabase_request("POST", "keys", data)
            
            # 4. Compile the completely clean loader
            loader_code = (
                f"local key = \"{current_key}\"\n"
                f"loadstring(game:HttpGet(\"https://keyxyz-sedse.pages.dev/v1/load?key=\" .. "
                f"game:GetService(\"HttpService\"):UrlEncode(key)))()"
            )
            
            # 5. Construct the Neubrutalist Embed Menu
            embed = discord.Embed(
                title="🧪 Public Tester Script",
                description=f"Copy the compiled code block below to execute the tester script directly. This key automatically bypasses all HWID and IP limits.\n\n"
                            f"```lua\n{loader_code}\n```\n\n"
                            f"⏳ **Expires:** <t:{epoch_time}:R>",
                color=0x5aabf2
            )
            embed.set_footer(text="A new tester key will automatically generate and update inside the loader when this one expires.")
            
            # 6. Send or Edit Message
            if current_message is None:
                current_message = await ctx.send(embed=embed)
            else:
                await current_message.edit(embed=embed)
                
            # 7. Sleep for exactly 10 minutes (600 seconds)
            await asyncio.sleep(600)
            
        except asyncio.CancelledError:
            # Clean up key on cancellation
            if current_key:
                await supabase_request("DELETE", f"keys?key_value=eq.{current_key}")
            break
        except Exception as e:
            print(f"tester key loop error: {e}")
            await asyncio.sleep(10) # Safely retry after 10s if database rate-limits

@bot.command()
async def deobf(ctx):
    # --- 0. AUTO-UNPACK / AUTO-FIX DUMPER SCRIPT ---
    status, err = check_and_reconstruct_dumper()
    if not status:
        return await ctx.send(f"❌ Failed to reconstruct the dumper script:\n`{err}`\n\nMake sure the file `revea.lol_dumped.lua.txt` is uploaded directly to your main GitHub folder.")

    # --- 1. AUTO-INSTALL LUNE IF MISSING ---
    if not os.path.exists("./lune"):
        setup_msg = await ctx.send("⚙️ First-time setup: Downloading the Lune engine... please wait a few seconds.")
        try:
            url = "https://github.com/lune-org/lune/releases/download/v0.8.8/lune-0.8.8-linux-x86_64.zip"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    with open("lune.zip", "wb") as f:
                        f.write(await resp.read())
            
            with zipfile.ZipFile("lune.zip", 'r') as zip_ref:
                zip_ref.extractall(".")
            os.remove("lune.zip")
            
            os.chmod("./lune", os.stat("./lune").st_mode | stat.S_IEXEC)
            await setup_msg.delete()
        except Exception as e:
            return await setup_msg.edit(content=f"❌ Failed to download Lune automatically: {e}")

    # --- 2. DEOBFUSCATION LOGIC ---
    if not ctx.message.attachments:
        return await ctx.send("You need to attach a `.lua` or `.txt` file for me to deobfuscate!")
    
    attachment = ctx.message.attachments[0]
    
    if not attachment.filename.endswith((".lua", ".txt")):
        return await ctx.send("Please attach a valid `.lua` or `.txt` file.")
    
    if attachment.size > 2 * 1024 * 1024: # 2 MB limit
        return await ctx.send("File is too large! Please keep it under 2MB.")

    msg = await ctx.send("📥 Downloading and analyzing the script... this might take a minute or two depending on the obfuscation.")

    file_id = str(uuid.uuid4())
    input_filename = os.path.join(DATA_DIR, f"input_{file_id}.lua")
    output_filename = os.path.join(DATA_DIR, f"output_{file_id}.lua")

    try:
        await attachment.save(input_filename)

        # Run Lune using the rebuilt dumper.lua
        process = await asyncio.create_subprocess_exec(
            "./lune", "run", "dumper.lua", input_filename, output_filename,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=45.0)
        except asyncio.TimeoutError:
            process.kill()
            return await msg.edit(content="❌ Deobfuscation timed out! The script might be malicious, broken, or too heavily obfuscated.")

        if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
            if os.path.getsize(output_filename) > 24 * 1024 * 1024:
                await msg.edit(content="⚠️ Deobfuscation finished, but the output file is too massive for Discord!")
            else:
                await msg.edit(content="✅ **Deobfuscation Complete!** Here is your dumped script:")
                await ctx.send(file=discord.File(output_filename, filename=f"deobf_{attachment.filename}"))
        else:
            error_msg = stderr.decode()[:800] 
            await msg.edit(content=f"❌ Deobfuscation failed to produce an output.\n**Error Log:**\n```\n{error_msg}\n```")

    except Exception as e:
        await msg.edit(content=f"❌ An internal bot error occurred: {e}")

    finally:
        # Clean up files
        if os.path.exists(input_filename):
            os.remove(input_filename)
        if os.path.exists(output_filename):
            os.remove(output_filename)        
@bot.hybrid_command(name="create_testkey", description="generates a custom test key (owner only)")
@commands.is_owner()
@app_commands.describe(duration_str="e.g. 12h, 1d, lifetime", member="user to receive the test key (optional)")
async def create_testkey(ctx, duration_str: str, member: discord.Member = None):
    # 1. Parse duration
    if duration_str.lower() in ["lifetime", "permanent", "perm"]:
        expires_at = None
        exp_text = "lifetime"
    else:
        duration = parse_duration(duration_str)
        if not duration:
            return await ctx.send("invalid duration format. use like '12h', '1d', '30m', or 'lifetime'.", ephemeral=True)
        expires_at = (datetime.now(timezone.utc) + duration).isoformat()
        exp_text = duration_str

    # 2. Generate Test Key (Forces SEDSE-TEST- format for intelligent routing)
    random_part = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=8))
    new_key = f"SEDSE-TEST-{random_part}"

    # 3. Save to Supabase (HWID set to BYPASS for database clarity)
    data = {"key_value": new_key, "is_active": True, "hwid": "BYPASS"}
    if expires_at:
        data["expires_at"] = expires_at

    inserted = await supabase_request("POST", "keys", data)
    if inserted is None:
        return await ctx.send("database error: failed to create test key in supabase.", ephemeral=True)

    # 4. DM the command user (you)
    dm_success_author = False
    try:
        embed_author = discord.Embed(
            title="🧪 Test Key Generated Successfully",
            description=f"You generated a new test key.\n\n**Key:** `{new_key}`\n**Duration:** {exp_text}",
            color=0x5aabf2
        )
        embed_author.set_footer(text="This key bypasses HWID locks and runs the Tester Script.")
        await ctx.author.send(embed=embed_author)
        dm_success_author = True
    except discord.Forbidden:
        pass

    # 5. DM the target member (if specified)
    dm_success_member = False
    if member and member != ctx.author:
        try:
            embed_member = discord.Embed(
                title="🧪 SEDSE Test Key",
                description=f"An admin generated a test key for you.\n\n**Key:** `{new_key}`\n**Duration:** {exp_text}",
                color=0x5aabf2
            )
            embed_member.set_footer(text="This key bypasses HWID locks and runs the experimental Tester Script.")
            await member.send(embed=embed_member)
            dm_success_member = True
        except discord.Forbidden:
            pass

    # 6. Respond in Chat (Fully ephemeral if run via Slash Command)
    chat_msg = f"Test key generated: `{new_key}` (Duration: {exp_text})"
    if member:
        chat_msg += f" and sent to {member.display_name}'s DMs."

    if ctx.interaction:
        # If run via Slash Command (/create_testkey), send an ephemeral message only you can see
        await ctx.send(chat_msg, ephemeral=True)
    else:
        # If run via Prefix (!sedse create_testkey), DM you and send a secure temporary status
        status_targets = []
        if dm_success_author:
            status_targets.append("your DMs")
        if member and dm_success_member:
            status_targets.append(f"{member.display_name}'s DMs")
        
        if status_targets:
            await ctx.send(f"test key successfully generated and sent to {', and '.join(status_targets)}.", delete_after=10)
        else:
            await ctx.send(f"test key generated but failed to send to DMs. here is the key: `{new_key}`", delete_after=15)

@bot.command()
@commands.is_owner()
async def startbrowser(ctx):
    global playwright_instance, browser_instance
    msg = await ctx.send("⚙️ Attempting to launch the Playwright browser engine...")
    
    try:
        # Start playwright if it hasn't been started yet
        if not playwright_instance:
            playwright_instance = await async_playwright().start()
        
        # Close old instance if it's somehow stuck
        if browser_instance:
            await browser_instance.close()
            
        browser_instance = await playwright_instance.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu', '--disable-dev-shm-usage']
        )
        await msg.edit(content="✅ **Browser engine launched successfully!** The `browse`, `research`, and `pinsearch` commands should work now.")
        
    except Exception as e:
        await msg.edit(content=f"❌ **Failed to launch Playwright.**\n\nIf you are on Railway/VPS, you probably need to install the browser.\n**Exact Error:**\n```\n{e}\n```")

@bot.command()
async def tzuquote(ctx, *, sentence: str = None):
    if not sentence:
        return await ctx.send("you gotta give me a quote. try `!sedse tzuquote I never said this.`")

    template_path = "suntzu_template.jpg"
    font_path = "roboto.ttf"

    if not os.path.exists(template_path):
        return await ctx.send("❌ template image (`suntzu_template.jpg`) is missing from the files! Upload it to GitHub.")
    if not os.path.exists(font_path):
        return await ctx.send("❌ font file (`roboto.ttf`) is missing from the files! Upload it to GitHub.")

    msg = await ctx.send("generating wisdom...")

    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size

        # --- STRICT BOUNDARIES ---
        # 1. Force text to start exactly 8% from the left edge.
        safe_x = int(img_w * 0.08)
        # 2. Maximum width is exactly 42% of the image (forces it to stay away from the statue).
        safe_max_width = int(img_w * 0.42) 
        # 3. Maximum height allowed for the entire text block.
        safe_max_height = int(img_h * 0.75) 

        # --- DYNAMIC FONT SIZING ---
        # Start with a reasonably large size based on the image's height
        max_font_size = int(img_h * 0.12) 
        min_font_size = 15
        font_size = max_font_size

        byline_text = "– Sun Tzu, The Art of War"
        formatted_quote = ""
        quote_font = None
        byline_font = None
        total_height = 0
        quote_h = 0

        # Loop to shrink the font until it fits perfectly inside the safe box bounds
        while font_size >= min_font_size:
            quote_font = ImageFont.truetype(font_path, font_size)
            byline_font = ImageFont.truetype(font_path, int(font_size * 0.55)) # Byline scales with quote

            # Word wrapping by PIXEL width, not character count
            lines = []
            words = f'"{sentence}"'.split()
            current_line = ""
            
            # Check if a single huge word is too wide for the box
            longest_word_width = max([draw.textlength(w, font=quote_font) for w in words] + [0])
            if longest_word_width > safe_max_width:
                font_size -= 2
                continue # Shrink font and try again

            # Pack words into lines
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if draw.textlength(test_line, font=quote_font) <= safe_max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            formatted_quote = "\n".join(lines)

            # Measure resulting text block height
            quote_bbox = draw.multiline_textbbox((0, 0), formatted_quote, font=quote_font)
            quote_h = quote_bbox[3] - quote_bbox[1]
            
            byline_bbox = draw.textbbox((0, 0), byline_text, font=byline_font)
            byline_h = byline_bbox[3] - byline_bbox[1]
            
            # Total height = quote height + gap + byline height
            gap = int(font_size * 0.8)
            total_height = quote_h + gap + byline_h

            if total_height <= safe_max_height:
                break # It fits perfectly, break the loop!
            
            font_size -= 2 # Doesn't fit? Shrink and loop again

        # --- DRAWING ---
        # Center the entire text block vertically
        start_y = (img_h - total_height) // 2

        # Draw the quote
        draw.multiline_text((safe_x, start_y), formatted_quote, font=quote_font, fill="white", align="left")

        # Calculate where to put the byline (aligned right beneath the quote)
        quote_bbox = draw.multiline_textbbox((0,0), formatted_quote, font=quote_font)
        quote_w = quote_bbox[2] - quote_bbox[0]
        byline_w = draw.textlength(byline_text, font=byline_font)
        
        byline_x = safe_x + quote_w - byline_w
        # If the quote is short, clamp the byline so it doesn't go off the left side
        if byline_x < safe_x + 20:
            byline_x = safe_x + 20
            
        byline_y = start_y + quote_h + int(font_size * 0.8)
        draw.text((byline_x, byline_y), byline_text, font=byline_font, fill="white")

        # --- SAVE AND SEND ---
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        await msg.delete()
        await ctx.send(file=discord.File(fp=buffer, filename="tzuquote.jpg"))

    except Exception as e:
        await msg.edit(content=f"an error occurred while generating: {e}")
 
@bot.hybrid_command(name="snipe")
async def snipe(ctx):
    channel_id = ctx.channel.id
    msgs = deleted_messages_cache.get(channel_id, [])
    if not msgs:
        return await ctx.send("no recently deleted messages here.", ephemeral=True)
    
    view = snipeview(msgs, ctx.author.id)
    if ctx.interaction:
        await ctx.send("select a message to snipe:", view=view, ephemeral=True)
    else:
        view.message = await ctx.send("select a message to snipe (only you can interact):", view=view)
 
@bot.command()
@check_perms("pglock", manage_messages=True)
async def pglock(ctx, arg1: str, arg2: str = None):
    if arg1.lower() == "unlock" and arg2:
        target = arg2
        pg_data = load_json(PGLOCK_FILE, dict)
        if target.lower() == "everyone":
            if not await is_mod_owner(ctx): return await ctx.send("only sedse can unlock everyone, nice try.")
            if pg_data.pop("everyone", None):
                save_json(PGLOCK_FILE, pg_data)
                return await ctx.send("the whole server pg curse is gone.")
            return await ctx.send("the server isn't globally pg locked right now.")
        try:
            member = await commands.MemberConverter().convert(ctx, target)
            if str(member.id) in pg_data:
                del pg_data[str(member.id)]
                save_json(PGLOCK_FILE, pg_data)
                return await ctx.send(f"{member.mention} is free from the pg curse.")
            return await ctx.send(f"{member.mention} isn't pg locked right now.")
        except: return await ctx.send("can't find that user.")
        
    member_str = arg2 if arg1.lower() == "lock" and arg2 else arg1
    pg_data = load_json(PGLOCK_FILE, dict)
    
    if member_str.lower() == "everyone":
        if not await is_mod_owner(ctx): return await ctx.send("only sedse can do the everyone lock, nice try.")
        if not pg_data.get("everyone"):
            pg_data["everyone"] = True
            save_json(PGLOCK_FILE, pg_data)
            return await ctx.send("the whole server is pg locked now.")
        return await ctx.send("the whole server is already pg locked.")
        
    try:
        member = await commands.MemberConverter().convert(ctx, member_str)
        user_id = str(member.id)
        if user_id not in pg_data:
            pg_data[user_id] = True
            save_json(PGLOCK_FILE, pg_data)
            await ctx.send(f"{member.mention} is pg locked now. their negativity will be converted.")
        else: 
            await ctx.send(f"{member.mention} is already pg locked.")
    except: 
        await ctx.send("can't find that user.")

@bot.command()
@commands.is_owner()
async def forcenick(ctx, member: discord.Member, *, nickname: str):
    # Discord enforces a strict 32 character limit on all nicknames
    if len(nickname) > 32:
        return await ctx.send("Discord nicknames cannot be longer than 32 characters!")

    data = load_json(FORCENICK_FILE, dict)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    
    if gid not in data:
        data[gid] = {}
        
    data[gid][uid] = nickname
    save_json(FORCENICK_FILE, data)
    
    try:
        await member.edit(nick=nickname)
        await ctx.send(f"🔒 **forcenick enabled hahaha** {member.mention}'s name is permanently locked to **{nickname}**.")
    except discord.Forbidden:
        await ctx.send(f"Added to database, but I lack permissions to change {member.mention}'s nickname right now. Make sure my bot role is higher than theirs!")

@bot.command(aliases=["unforcenick"])
@commands.is_owner()
async def unforcelock(ctx, member: discord.Member):
    data = load_json(FORCENICK_FILE, dict)
    gid = str(ctx.guild.id)
    uid = str(member.id)
    
    if gid in data and uid in data[gid]:
        del data[gid][uid]
        save_json(FORCENICK_FILE, data)
        await ctx.send(f"🔓 **forcenick disabled :(** {member.mention} is free from sedse's reign")
    else:
        await ctx.send(f"{member.mention} isn't currently name-locked.")

@bot.command(aliases=["autotranslate"])
@check_perms("translate", manage_messages=True)
async def translate(ctx):
    data = load_json(TRANSLATE_FILE, dict)
    channel_id = str(ctx.channel.id)
    
    if channel_id in data:
        del data[channel_id]
        save_json(TRANSLATE_FILE, data)
        await ctx.send("Auto translate turned off, now you can 用普通話說話")
    else:
        data[channel_id] = True
        save_json(TRANSLATE_FILE, data)
        await ctx.send("Auto translate turned on, no more arigato and Russian")

@bot.command()
@check_perms("pglock", manage_messages=True)
async def pgunlock(ctx, target: str):
    pg_data = load_json(PGLOCK_FILE, dict)
    if target.lower() == "everyone":
        if not await is_mod_owner(ctx): return await ctx.send("only sedse can unlock everyone, nice try.")
        if pg_data.pop("everyone", None):
            save_json(PGLOCK_FILE, pg_data)
            return await ctx.send("the whole server pg curse is gone.")
        return await ctx.send("the server isn't globally pg locked right now.")
    try:
        member = await commands.MemberConverter().convert(ctx, target)
        user_id = str(member.id)
        if user_id in pg_data:
            del pg_data[user_id]
            save_json(PGLOCK_FILE, pg_data)
            await ctx.send(f"{member.mention} is free from the pg curse.")
        else: 
            await ctx.send(f"{member.mention} isn't pg locked right now.")
    except: 
        await ctx.send("can't find that user.")
      
@bot.command()
@check_perms("givequota", administrator=True)
async def givequota(ctx, member: discord.Member, command_name: str, amount: int = 5):
    command_name = command_name.lower()
    valid_commands = ["ai", "research", "kick", "timeout", "warn", "all"]
    
    if command_name not in valid_commands:
        return await ctx.send(f"Invalid command. Choose from: {', '.join(valid_commands)}")
        
    if amount <= 0:
        return await ctx.send("Amount must be greater than 0, bro.")

    quotas = load_json(QUOTAS_FILE, dict)
    user_id = str(member.id)
    today = discord.utils.utcnow().strftime("%Y-%m-%d")
    
    # Initialize quota tracking for today if they don't have one
    if user_id not in quotas or quotas[user_id].get("date") != today:
        quotas[user_id] = {"date": today, "kick": 0, "timeout": 0, "warn": 0, "ai": 0, "research": 0}
        
    if command_name == "all":
        # Fully reset all categories back to 0 uses used
        for category in ["kick", "timeout", "warn", "ai", "research"]:
            quotas[user_id][category] = 0
        save_json(QUOTAS_FILE, quotas)
        
        await ctx.send(f"Successfully fully reset all daily quotas for {member.mention}.")
        await send_log(ctx.guild, "Quota Reset", f"**Mod:** {ctx.author.mention}\n**Target:** {member.mention}\n**Action:** Fully reset all daily quotas.", discord.Color.green())
        return

    # Deduct from their usage count to give them more available quota
    current_usage = quotas[user_id].get(command_name, 0)
    new_usage = current_usage - amount
    quotas[user_id][command_name] = new_usage
    
    save_json(QUOTAS_FILE, quotas)
    
    # Calculate limits for the output message
    limit = 5 if command_name in ["ai", "research"] else 10
    uses_left = limit - new_usage
    
    await ctx.send(f"Gave {amount} extra uses of `{command_name}` to {member.mention}. They now have **{uses_left}/{limit}** uses left today.")
    await send_log(ctx.guild, "Quota Granted", f"**Mod:** {ctx.author.mention}\n**Target:** {member.mention}\n**Command:** `{command_name}`\n**Amount:** Given {amount} uses (New usage tracker: {new_usage})", discord.Color.green())


# ==========================================
# 7. RUN
# ==========================================

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    try: bot.run(TOKEN, log_handler=None) 
    except Exception as e: print(f"critical error: {e}")
else: print("critical error: no discord_token found!")


