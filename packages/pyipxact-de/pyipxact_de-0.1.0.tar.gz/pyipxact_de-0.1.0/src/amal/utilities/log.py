import sys

from loguru import logger

LOGURU_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <light-black>│</light-black> "
    "{level.icon} {level.no} <level>{level:<8}</level> <light-black>│</light-black> "
    "{file}:<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line:<5}</cyan> - "
    "<level>{message}</level>"
)


LEVEL_ICONS = {
    "TRACE"     : "\N{LOWER RIGHT PENCIL}",      # "✎",
    "DEBUG"     : "\N{GEAR}",                    # "⚙",
    "INFO"      : "\N{INFORMATION SOURCE}",      # "ℹ",
    "SUCCESS"   : "\N{HEAVY CHECK MARK}",        # "✔",
    "WARNING"   : "\N{WARNING SIGN}",            # "⚠",
    "ERROR"     : "\N{HEAVY MULTIPLICATION X}",  # "✗",
    "CRITICAL"  : "\N{SKULL AND CROSSBONES}",    # "☠",
}

# uFE0E -> "\N{VARIATION SELECTOR-15}"
# uFE0F -> "\N{VARIATION SELECTOR-16}"

# "✎"  : "\N{LOWER RIGHT PENCIL}"
# "✏︎"  : "\N{PENCIL}\uFE0E"
# "✏️" : "\N{PENCIL}\uFE0F"

# "⚙"  : "\N{GEAR}"
# "🐞" : "\N{LADY BEETLE}"
# "🛠" : "\N{HAMMER AND WRENCH}\uFE0F"

# "ℹ︎"   : "\N{INFORMATION SOURCE}"
# "ℹ︎"   : "\N{INFORMATION SOURCE}\N{VARIATION SELECTOR-15}"
# "ℹ️" : "\N{INFORMATION SOURCE}\uFE0F"
# "ℹ️" : "\N{INFORMATION SOURCE}\N{VARIATION SELECTOR-16}"

# "✓"  : "\N{CHECK MARK}"
# "✔"  : "\N{HEAVY CHECK MARK}"
# "☑"  : "\N{BALLOT BOX WITH CHECK}"
# "✅" : "\N{WHITE HEAVY CHECK MARK}"

# "⚠"  : "\N{WARNING SIGN}\uFE0E"
# "⚠"  : "\N{WARNING SIGN}\N{VARIATION SELECTOR-15}"
# "⚠️" : "\N{WARNING SIGN}\uFE0F"
# "⚠️" : "\N{WARNING SIGN}\N{VARIATION SELECTOR-16}"

# "✖"  : "\N{HEAVY MULTIPLICATION X}"
# "✗"  : "\N{BALLOT X}"
# "✘"  : "\N{HEAVY BALLOT X}"
# "❌" : "\N{CROSS MARK}"

# "‼" : "\N{DOUBLE EXCLAMATION MARK}"
# "❗" : "\N{HEAVY EXCLAMATION MARK SYMBOL}"


# "☠"  : "\N{SKULL AND CROSSBONES}"
# "☠"  : "\N{SKULL AND CROSSBONES}\uFE0E"
# "☠"  : "\N{SKULL AND CROSSBONES}\N{VARIATION SELECTOR-15}"
# "☠️" : "\N{SKULL AND CROSSBONES}\UFE0F"
# "☠️" : "\N{SKULL AND CROSSBONES}\N{VARIATION SELECTOR-16}"



# Re-register built‑in levels with icons
for name in ["TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]:
    logger.level(name, icon=LEVEL_ICONS[name])

logger.remove(0)
logger.add(sys.stderr, format=LOGURU_FORMAT)
