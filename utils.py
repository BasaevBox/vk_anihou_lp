"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         UTILITY MODULE                                       ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from datetime import datetime
from config import CONFIG

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    colors = {
        "INFO": Colors.CYAN,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.WARNING,
        "ERROR": Colors.FAIL,
        "COMMAND": Colors.BLUE,
        "ANIMATION": Colors.HEADER,
    }
    color = colors.get(level, Colors.ENDC)
    print(f"{Colors.BOLD}[{timestamp}]{Colors.ENDC} {color}[{level}]{Colors.ENDC} {message}")