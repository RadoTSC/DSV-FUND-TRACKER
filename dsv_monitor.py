# dsv_monitor.py
# PURPOSE: Monitor @dsvfund for NEW investment tweets (quiet mode)

from __future__ import annotations
import json
import datetime as dt
from typing import Any, Optional
from twikit import Client
import asyncio
import random
import sys

from dsv_system import DSVParser, DSVLedger

# ========== CONFIG ==========
COOKIES_FILE = "cookies.json"
DSV_HANDLE = "dsvfund"
SIGNAL_FILE = "dsv_signal.txt"
CHECK_INTERVAL_MIN = 55
CHECK_INTERVAL_MAX = 65

last_seen_tweet_id: Optional[str] = None


# ========== HELPER FUNCTIONS ==========

def get_created_at_dt(t: Any) -> dt.datetime | None:
    d = getattr(t, "created_at_datetime", None)
    if isinstance(d, dt.datetime):
        return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)

    s = getattr(t, "created_at", None)
    if not isinstance(s, str):
        return None
    s = s.strip()

    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except:
        pass

    try:
        return dt.datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
    except:
        return None


def create_signal(subnet_number: int, amount_usd: int, date: str):
    signal_data = {
        "subnet_number": subnet_number,
        "amount_usd": amount_usd,
        "date": date,
        "timestamp": dt.datetime.utcnow().isoformat()
    }

    with open(SIGNAL_FILE, "w") as f:
        json.dump(signal_data, f, indent=2)


# ========== MAIN MONITORING ==========

async def check_dsvfund_investments(client: Client, user_id: str):
    global last_seen_tweet_id

    try:
        tweets = await client.get_user_tweets(user_id, "Tweets", count=10)
        ledger = DSVLedger()
        new_investments = []

        for tweet in tweets:
            tweet_id = str(getattr(tweet, "id", ""))

            # First run: set starting point
            if last_seen_tweet_id is None:
                last_seen_tweet_id = tweet_id
                return

            # Stop at last seen
            if tweet_id == last_seen_tweet_id:
                break

            # Get tweet data
            created_dt = get_created_at_dt(tweet)
            tweet_text = getattr(tweet, "full_text", None) or getattr(tweet, "text", "") or ""

            # Skip RT/replies
            is_rt = bool(getattr(tweet, "is_retweet", False))
            is_reply = bool(getattr(tweet, "in_reply_to_status_id", None))

            if is_rt or is_reply:
                continue

            # Check if investment tweet
            if not DSVParser.is_valid_investment_tweet(tweet_text):
                continue

            # Extract data
            subnet_number = DSVParser.extract_subnet_number(tweet_text)
            amount_usd = DSVParser.extract_first_amount(tweet_text)
            date_str = created_dt.strftime("%Y-%m-%d") if created_dt else dt.datetime.now().strftime("%Y-%m-%d")

            if not subnet_number or not amount_usd:
                continue

            # Check duplicate
            if ledger.is_duplicate(subnet_number, amount_usd, date_str):
                continue

            # NEW INVESTMENT!
            new_investments.append({
                "subnet_number": subnet_number,
                "amount_usd": amount_usd,
                "date": date_str,
                "tweet_text": tweet_text,
                "tweet_id": tweet_id
            })

        # Update last seen
        if tweets and last_seen_tweet_id is not None:
            first_tweet_id = str(getattr(tweets[0], "id", ""))
            if first_tweet_id:
                last_seen_tweet_id = first_tweet_id

        # Process new investments
        for inv in reversed(new_investments):
            ledger.create_backup()

            success, message = ledger.add_investment(
                inv["subnet_number"],
                inv["amount_usd"],
                inv["date"],
                inv["tweet_text"]
            )

            if success:
                # ONLY print when investment found
                print(f"\n🚨 NEW INVESTMENT DETECTED")
                print(f"   Subnet: {inv['subnet_number']}")
                print(f"   Amount: ${inv['amount_usd']:,}")
                print(f"   Date: {inv['date']}")
                print(f"   ✅ Added to ledger")
                print(f"   🔔 Signal created\n")

                create_signal(
                    inv["subnet_number"],
                    inv["amount_usd"],
                    inv["date"]
                )

    except Exception as e:
        # Only print errors
        print(f"❌ Error: {e!r}")


# ========== MAIN LOOP ==========

async def monitor_loop():
    print("🚀 DSV Monitor starting...")

    client = Client(language="en-US")
    client.load_cookies(COOKIES_FILE)

    try:
        user = await client.get_user_by_screen_name(DSV_HANDLE)
        user_id = user.id
        print(f"✅ Monitoring @{DSV_HANDLE}")
        print(f"⏰ Check interval: {CHECK_INTERVAL_MIN}-{CHECK_INTERVAL_MAX}s")
        print(f"🔕 Quiet mode: will only print when investment found\n")
    except Exception as e:
        print(f"❌ Failed to start: {e!r}")
        return

    while True:
        await check_dsvfund_investments(client, user_id)
        delay = random.uniform(CHECK_INTERVAL_MIN, CHECK_INTERVAL_MAX)
        await asyncio.sleep(delay)


# ========== RUN ==========

if __name__ == "__main__":
    try:
        asyncio.run(monitor_loop())
    except KeyboardInterrupt:
        print("\n⏹️  Monitor stopped")
    except Exception as e:
        print(f"\n❌ Monitor crashed: {e!r}")
