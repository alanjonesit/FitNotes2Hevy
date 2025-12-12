"""Configuration settings for FitNotes to Hevy conversion."""

# Input file path (set this to your FitNotes export file)
INPUT_FILE_PATH = "data/input/FitNotes_Export_2025_11_19_10_20_01.csv"

# Workout defaults
DEFAULT_TRAINING_TIME = "07:00"
TIMEZONE_OFFSET_HOURS = 10
DEFAULT_WORKOUT_NAME = "Workout"
DEFAULT_DURATION = "60m"
DEFAULT_WORKOUT_NOTES = "Imported from FitNotes"

# Exercise conversion rules
TIME_TO_REPS_EXERCISES = [
    "Bird Dog",
    "Dead Bug",
    "Deadbug",
    "Flutter Kicks",
    "Flutter Kick",
]
TIME_TO_DISTANCE_EXERCISES = [
    "Farmers Walk",
    "Farmer Walk",
    "Farmer's Walk",
    "Farmer's Carry",
]
REPS_TO_TIME_EXERCISES = ["Warm Up"]
