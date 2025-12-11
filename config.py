"""Configuration file for FitNotes to Hevy conversion."""

# ============================================================================
# FILE PATHS
# ============================================================================
# Path to your FitNotes CSV export file
FIT_NOTES_PATH = './files/input/FitNotes_Export_2025_11_19_10_20_01.csv'

# ============================================================================
# WORKOUT DEFAULTS
# ============================================================================
# Default time to append to workout dates (HH:MM:SS format)
# This is the time you want workouts to appear in Hevy (in your local timezone)
DEFAULT_TRAINING_TIME = '07:00:00'

# Timezone offset from UTC (in hours)
# Hevy interprets CSV timestamps as UTC, so we need to adjust for your timezone
# Examples: 
#   UTC+10 (Sydney/Melbourne): 10
#   UTC-8 (Los Angeles): -8
#   UTC+0 (London): 0
#   UTC+1 (Paris): 1
TIMEZONE_OFFSET_HOURS = 10

# Default workout name for all workouts
DEFAULT_WORKOUT_NAME = 'Workout'

# Default workout duration (format: '60m' for minutes or '3600s' for seconds)
DEFAULT_DURATION = '60m'

# ============================================================================
# EXERCISE SETTINGS
# ============================================================================
# Default distance value for all exercises (Hevy requires this field)
DEFAULT_DISTANCE = 0

# Default workout notes (set to empty string '' to disable)
DEFAULT_WORKOUT_NOTES = 'Imported from FitNotes'

# Uncomment and set to rename unmapped exercises (e.g., 'Other')
# By default, unmapped exercises keep their original FitNotes names
# DEFAULT_EXERCISE_NAME = None
