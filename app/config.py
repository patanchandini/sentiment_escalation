from datetime import time

BUSINESS_START = time(9, 0)
BUSINESS_END   = time(18, 0)
BUSINESS_DAYS  = {0, 1, 2, 3, 4}   # Mon–Fri

UNRESOLVED_NEGATIVE_MINUTES = 15
REPEATED_NEGATIVE_WINDOW    = 5
REPEATED_NEGATIVE_THRESHOLD = 3

# Confidence floor — below this, we don't trust the classifier
MIN_CONFIDENCE = 0.35