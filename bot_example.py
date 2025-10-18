# bot_example.py
# Minimal Discord bot with ONLY DSV tracker functionality
# Copy this as your starting point

import os
import json
import asyncio
import random
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

# ========== CONFIG ==========
BASE_DIR = os.path.dirname(__file__)
DSV_CHANNEL_ID = 1234567890  # ← CHANGE THIS to your Discord channel ID

# ========== BOT SETUP ==========
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
TOKEN = os.getenv("DISCORD_TOKEN")

# ========== DSV SIGNAL WATCHER ==========
@tasks.loop(seconds=5)
async def dsv_signal_watcher():
    """Check for dsv_signal.txt every 5 seconds"""
    from dsv_system import DSVLedger, DSVFormatter, SUBNET_NAMES
    
    signal_file = "dsv_signal.txt"
    
    if not os.path.exists(signal_file):
        return
    
    try:
        with open(signal_file, "r") as f:
            signal_data = json.load(f)
        
        subnet_num = signal_data["subnet_number"]
        amount = signal_data["amount_usd"]
        
        ledger = DSVLedger()
        subnet_name = SUBNET_NAMES.get(subnet_num, f"SN{subnet_num}")
        
        announcement = (
            f"🚨 **DSV FUND JUST INVESTED ${amount:,} "
            f"in Subnet {subnet_num} ({subnet_name.upper()})**\n\n"
        )
        
        rankings = DSVFormatter.format_portfolio_text(ledger)
        
        channel = bot.get_channel(DSV_CHANNEL_ID) or await bot.fetch_channel(DSV_CHANNEL_ID)
        await channel.send(announcement + rankings)
        
        os.remove(signal_file)
        print(f"✅ Posted DSV investment to Discord")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            os.remove(signal_file)
        except:
            pass

# ========== BOT STARTUP ==========
@bot.event
async def on_ready():
    print(f"✅ Bot ready: {bot.user}")
    
    # Start DSV monitor subprocess
    DSV_MONITOR_EXE = os.path.join(BASE_DIR, ".scrape311", "Scripts", "python.exe")
    DSV_MONITOR_SCRIPT = os.path.join(BASE_DIR, "dsv_monitor.py")
    
    try:
        dsv_process = await asyncio.create_subprocess_exec(
            DSV_MONITOR_EXE,
            DSV_MONITOR_SCRIPT,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print(f"✅ DSV monitor started (PID: {dsv_process.pid})")
    except Exception as e:
        print(f"❌ Failed to start monitor: {e}")
        return
    
    # Start signal watcher
    if not dsv_signal_watcher.is_running():
        dsv_signal_watcher.start()
        print("✅ Signal watcher started (checks every 5s)")

# ========== OPTIONAL COMMANDS ==========

@bot.command(name="dsv_now")
async def dsv_now(ctx):
    """Show current DSV portfolio"""
    from dsv_system import DSVLedger, DSVFormatter
    
    ledger = DSVLedger()
    rankings = DSVFormatter.format_portfolio_text(ledger)
    await ctx.send(f"📊 **CURRENT DSV PORTFOLIO**\n\n{rankings}")

@bot.command(name="dsv_undo")
async def dsv_undo(ctx):
    """Revert last investment (admin only)"""
    ADMIN_ID = 123456789  # ← CHANGE THIS to your Discord user ID
    
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only")
        return
    
    from dsv_system import DSVLedger, DSVFormatter
    
    ledger = DSVLedger()
    if ledger.restore_from_backup():
        rankings = DSVFormatter.format_portfolio_text(ledger)
        channel = bot.get_channel(DSV_CHANNEL_ID) or await bot.fetch_channel(DSV_CHANNEL_ID)
        await channel.send(f"🔄 **PORTFOLIO CORRECTED**\n\n{rankings}")
        await ctx.send("✅ Reverted to backup")
    else:
        await ctx.send("❌ No backup found")

# ========== RUN BOT ==========
bot.run(TOKEN)
