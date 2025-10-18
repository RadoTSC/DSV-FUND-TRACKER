# dsv_system.py
# STEP 1: Core investment tracking engine - deterministic, no Discord/Twitter dependencies
# This file processes investment data, validates tweets, and calculates portfolio rankings

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple

# File paths
LEDGER_FILE = "dsv_investments.json"
BACKUP_FILE = "dsv_investments_backup.json"

# Complete subnet reference (0-128)
SUBNET_NAMES = {
    0: "Root", 1: "Apex", 2: "Omron", 3: "Templar", 4: "Targon", 5: "Hone", 6: "Infinite Games", 7: "SubVortex",
    8: "Proprietary Trading Network", 9: "iota", 10: "Swap", 11: "Dippy Studio", 12: "Compute Horde",
    13: "Data Universe", 14: "TAOHash", 15: "BitQuant", 16: "BitKoop", 17: "404—GEN", 18: "Zeus", 19: "Nineteen.ai",
    20: "Bounty Hunter", 21: "OMEGA Any-to-Any", 22: "Desearch", 23: "Nuance", 24: "OMEGA Labs", 25: "Mainframe",
    26: "Kinitro", 27: "Neural Internet", 28: "Unknown", 29: "Coldint", 30: "Bettensor", 31: "CANDLES", 32: "ItsAI",
    33: "ReadyAI", 34: "BitMind", 35: "Cartha", 36: "Autoppia", 37: "Aurelius", 38: "Distributed Training",
    39: "basilica",
    40: "Chunking", 41: "Sportstensor", 42: "Gopher", 43: "Graphite", 44: "Score", 45: "Coming SOON!",
    46: "RESI", 47: "Reboot", 48: "Quantum Compute", 49: "Polaris Cloud", 50: "Synth", 51: "lium.io",
    52: "Dojo", 53: "EfficientFrontier", 54: "Yanez MIID", 55: "Precog", 56: "Gradients", 57: "Gaia",
    58: "Parked (focused on SN11)", 59: "Babebit", 60: "BitBosai", 61: "RedTeam", 62: "Ridges", 63: "Quantum Innovate",
    64: "Chutes", 65: "TAO Private Network", 66: "Oceans", 67: "tenex", 68: "NOVA", 69: "Unknown",
    70: "Vericore", 71: "Kora", 72: "StreetVision by NATIX", 73: "MetaHash", 74: "Unknown", 75: "Hippius",
    76: "Safe Scan", 77: "Liquidity", 78: "Unknown", 79: "Taos", 80: "TaoQuant", 81: "grail",
    82: "Unknown", 83: "CliqueAI", 84: "ChipForge (Tatsu)", 85: "Vidaio", 86: "MIAO", 87: "CheckerChain",
    88: "Investing", 89: "InfiniteHash", 90: "brain", 91: "tensorprox", 92: "ReinforcedAI", 93: "Bitcast",
    94: "Eastworld", 95: "Unknown", 96: "Flock OFF", 97: "FlamWire", 98: "Creator", 99: "Neza",
    100: "Signal", 101: "Unknown", 102: "BetterTherapy", 103: "HappyAI", 104: "for sale (burn to uidt)",
    105: "SoundShelf", 106: "VoidAI", 107: "Tiger ALPHA", 108: "Internet of Intelligence", 109: "Taoillium",
    110: "Rich Kids of TAO", 111: "oneoneone", 112: "minotaur", 113: "taonado", 114: "Level 114",
    115: "SoulX", 116: "TaoLend", 117: "BrainPlay", 118: "Unknown", 119: "Unknown", 120: "affine",
    121: "sundae_bar", 122: "Bitrecs", 123: "MANTIS", 124: "Swarm", 125: "Unknown", 126: "Tiger Beta",
    127: "Astrid Intelligence", 128: "ByteLeap",
}

# Subnet category mapping - FILL THIS IN BY HAND
SUBNET_CATEGORIES = {
    1: "Agents",
    2: "Cryptography",
    3: "Training",
    4: "Inference",
    5: "Training",
    6: "Prediction",
    7: "Infrastructure",
    8: "Trading",
    9: "Training",
    10: "Defi",
    11: "Training",
    12: "Compute",
    13: "Data",
    14: "Compute",
    15: "Defi",
    16: "Marketing",
    17: "3D",
    18: "DeSci",
    19: "NOT_SPECIFIED",
    20: "Agents",
    21: "Multimodal",
    22: "Data",
    23: "Marketing",
    24: "Data",
    25: "DeSci",
    26: "Data",
    27: "Compute",
    28: "NOT_SPECIFIED",
    29: "Training",
    30: "Prediction",
    31: "Prediction",
    32: "Detection",
    33: "Agents",
    34: "Detection",
    35: "Trading",
    36: "Agents",
    37: "Data",
    38: "Training",
    39: "Inference",
    40: "Data",
    41: "Prediction",
    42: "Data",
    43: "Inference",
    44: "Detection",
    45: "Code",
    46: "Prediction",
    47: "Hardware",
    48: "Prediction",
    49: "Compute",
    50: "Defi",
    51: "Compute",
    52: "Data",
    53: "Trading",
    54: "Detection",
    55: "Defi",
    56: "Training",
    57: "DeSci",
    58: "Inference",
    59: "Agents",
    60: "Detection",
    61: "Detection",
    62: "Agents",
    63: "Compute",
    64: "Compute",
    65: "Infrastructure",
    66: "Trading",
    67: "Trading",
    68: "DeSci",
    69: "NOT_SPECIFIED",
    70: "Inference",
    71: "Agents",
    72: "3D",
    73: "Trading",
    74: "NOT_SPECIFIED",
    75: "Storage",
    76: "DeSci",
    77: "Trading",
    78: "NOT_SPECIFIED",
    79: "Trading",
    80: "Trading",
    81: "Training",
    82: "NOT_SPECIFIED",
    83: "NOT_SPECIFIED",
    84: "NOT_SPECIFIED",
    85: "Inference",
    86: "Inference",
    87: "NOT_SPECIFIED",
    88: "Trading",
    89: "Compute",
    90: "Prediction",
    91: "Detection",
    92: "Detection",
    93: "Marketing",
    94: "Agents",
    95: "NOT_SPECIFIED",
    96: "Training",
    97: "Infrastructure",
    98: "3D",
    99: "NOT_SPECIFIED",
    100: "NOT_SPECIFIED",
    101: "NOT_SPECIFIED",
    102: "Inference",
    103: "Inference",
    104: "NOT_SPECIFIED",
    105: "Inference",
    106: "Trading",
    107: "Data",
    108: "NOT_SPECIFIED",
    109: "Agents",
    110: "NOT_SPECIFIED",
    111: "Marketing",
    112: "Trading",
    113: "Privacy",
    114: "Gaming",
    115: "Trading",
    116: "NOT_SPECIFIED",
    117: "NOT_SPECIFIED",
    118: "NOT_SPECIFIED",
    119: "NOT_SPECIFIED",
    120: "NOT_SPECIFIED",
    121: "Agents",
    122: "Prediction",
    123: "NOT_SPECIFIED",
    124: "NOT_SPECIFIED",
    125: "NOT_SPECIFIED",
    126: "NOT_SPECIFIED",
    127: "NOT_SPECIFIED",
    128: "NOT_SPECIFIED"
}


class DSVParser:
    """Extract and validate investment data from tweets - deterministic only"""

    INVESTMENT_KEYWORDS = [
        "invest", "invested", "investing",
        "allocation", "allocated", "allocating",
        "otc", "backing", "backed",
        "buy", "buying", "bought",
        "completed", "complete",
    ]

    @staticmethod
    def extract_first_amount(text: str) -> Optional[int]:
        """Extract FIRST dollar amount only from text. Ignore all subsequent amounts."""
        if not text:
            return None

        # Match: $100,000 or $100k or $1.5M or $100000
        match = re.search(r'\$\s*([\d,]+(?:\.\d{1,2})?)\s*([KMB])?', text, re.IGNORECASE)
        if not match:
            return None

        num_str = match.group(1).replace(",", "")
        suffix = (match.group(2) or "").upper()

        try:
            num = float(num_str)
            multipliers = {"K": 1000, "M": 1000000, "B": 1000000000}
            return int(num * multipliers.get(suffix, 1))
        except:
            return None

    @staticmethod
    def extract_subnet_number(text: str) -> Optional[int]:
        """Extract subnet number from text. Returns int 0-128 or None."""
        if not text:
            return None

        # Match: SN75, SN 75, Subnet 75, (Subnet 75)
        match = re.search(r'[Ss](?:ubnet)?\s*(\d{1,3})', text)
        if match:
            num = int(match.group(1))
            if 0 <= num <= 128:
                return num

        return None

    @staticmethod
    def is_valid_investment_tweet(tweet_text: str) -> bool:
        """Check if tweet contains all 4 required elements of a real investment announcement"""
        if not tweet_text:
            return False

        text_lower = tweet_text.lower()

        # Check 1: Must contain investment keyword
        has_investment_keyword = any(kw in text_lower for kw in DSVParser.INVESTMENT_KEYWORDS)
        if not has_investment_keyword:
            return False

        # Check 2: Must have subnet identifier
        has_subnet = DSVParser.extract_subnet_number(tweet_text) is not None
        if not has_subnet:
            return False

        # Check 3: Must have dollar amount
        has_amount = DSVParser.extract_first_amount(tweet_text) is not None
        if not has_amount:
            return False

        # Check 4: Original tweet only (not handled here - checked before calling this)

        return True


class DSVLedger:
    """Manage investment ledger - load, save, backup, update"""

    def __init__(self):
        self.ledger = self.load()

    def load(self) -> List[Dict]:
        """Load ledger from JSON file"""
        if os.path.exists(LEDGER_FILE):
            try:
                with open(LEDGER_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading ledger: {e}")
                return []
        return []

    def save(self):
        """Save ledger to JSON file"""
        try:
            with open(LEDGER_FILE, "w") as f:
                json.dump(self.ledger, f, indent=2)
        except Exception as e:
            print(f"Error saving ledger: {e}")

    def create_backup(self):
        """Create backup before modifying ledger"""
        try:
            with open(BACKUP_FILE, "w") as f:
                json.dump(self.ledger, f, indent=2)
        except Exception as e:
            print(f"Error creating backup: {e}")

    def restore_from_backup(self) -> bool:
        """Restore ledger from backup (for !dsv_undo)"""
        if not os.path.exists(BACKUP_FILE):
            print("No backup file found")
            return False

        try:
            with open(BACKUP_FILE, "r") as f:
                self.ledger = json.load(f)
            self.save()
            return True
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False

    def is_duplicate(self, subnet_number: int, amount_usd: int, date: str) -> bool:
        """Check if investment already exists (same subnet, amount, date)"""
        for entry in self.ledger:
            if (entry.get("subnet_number") == subnet_number and
                    entry.get("amount_usd") == amount_usd and
                    entry.get("date") == date):
                return True
        return False

    def add_investment(self, subnet_number: int, amount_usd: int, date: str,
                       tweet_text: str) -> Tuple[bool, str]:
        """Add new investment to ledger. Returns (success, message)"""

        # Validate
        if subnet_number < 0 or subnet_number > 128:
            return False, f"Invalid subnet: {subnet_number}"
        if amount_usd <= 0:
            return False, f"Invalid amount: ${amount_usd}"
        if self.is_duplicate(subnet_number, amount_usd, date):
            return False, f"Duplicate: SN{subnet_number} ${amount_usd:,} on {date}"

        subnet_name = SUBNET_NAMES.get(subnet_number, f"SN{subnet_number}")

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "subnet_number": subnet_number,
            "subnet_name": subnet_name,
            "amount_usd": amount_usd,
            "date": date,
            "source": "X",
            "raw_text": tweet_text[:300],
        }

        self.ledger.append(entry)
        self.save()
        return True, f"✅ Added: SN{subnet_number} ({subnet_name}) - ${amount_usd:,}"

    def get_portfolio(self) -> Dict:
        """Calculate current portfolio from ledger"""
        portfolio = {}

        for entry in self.ledger:
            sn = entry.get("subnet_number")
            if sn not in portfolio:
                portfolio[sn] = {
                    "name": entry.get("subnet_name", f"SN{sn}"),
                    "total": 0,
                    "count": 0,
                    "investments": []
                }

            amount = entry.get("amount_usd", 0)
            portfolio[sn]["total"] += amount
            portfolio[sn]["count"] += 1
            portfolio[sn]["investments"].append({
                "date": entry.get("date"),
                "amount": amount,
            })

        # Sort by total USD descending
        ranked = sorted(portfolio.items(), key=lambda x: x[1]["total"], reverse=True)

        total_usd = sum(p["total"] for _, p in portfolio.items())

        return {
            "total_usd": total_usd,
            "subnet_count": len(portfolio),
            "entry_count": len(self.ledger),
            "subnets": dict(ranked)
        }


class DSVFormatter:
    """Format portfolio data for Discord posting"""

    @staticmethod
    def format_portfolio_text(ledger: DSVLedger) -> str:
        """Generate portfolio rankings + category breakdown"""
        portfolio = ledger.get_portfolio()
        total_usd = portfolio["total_usd"]

        lines = []
        lines.append("📊 **DSV FUND PORTFOLIO - LIVE RANKINGS**")
        lines.append("")

        # Rankings by subnet
        for rank, (sn, data) in enumerate(portfolio["subnets"].items(), 1):
            pct = (data["total"] / total_usd * 100) if total_usd > 0 else 0
            inv_count = data["count"]
            lines.append(f"{rank}. **SN{sn} ({data['name'].upper()})**: ${data['total']:,} ({pct:.1f}%)")

        lines.append("")
        lines.append(f"🎯 **TOTAL INVESTED: ${total_usd:,}**")
        lines.append(f"📈 **Total entries: {portfolio['entry_count']}**")

        # Category breakdown
        category_totals = {}
        for sn, data in portfolio["subnets"].items():
            category = SUBNET_CATEGORIES.get(sn, "Uncategorized")
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += data["total"]

        # Sort by total descending
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)

        lines.append("")
        lines.append("📂 **ALLOCATION BY CATEGORY**")
        for category, amount in sorted_categories:
            pct = (amount / total_usd * 100) if total_usd > 0 else 0
            lines.append(f"  {category}: {pct:.1f}%")

        return "\n".join(lines)


# Test function
def test_system():
    """Test that system loads and works correctly"""
    print("\n🧪 Testing DSV System...\n")

    ledger = DSVLedger()
    portfolio = ledger.get_portfolio()

    print(f"✅ Loaded {portfolio['entry_count']} investments")
    print(f"✅ Total USD: ${portfolio['total_usd']:,}")
    print(f"✅ Subnets: {portfolio['subnet_count']}")
    print("\n" + DSVFormatter.format_portfolio_text(ledger))


if __name__ == "__main__":
    test_system()

