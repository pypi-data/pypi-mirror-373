import os

PRINT_EMOJIS = os.getenv("PRINT_EMOJIS", "True").lower() in ("true", "1")
UNSUPERVISED_INTERFACE = os.getenv("UNSUPERVISED_INTERFACE", "False").lower() in ("true", "1")