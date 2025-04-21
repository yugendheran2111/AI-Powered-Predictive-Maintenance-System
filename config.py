# config.py - Configuration constants for the predictive maintenance system

# Threshold values for sensor metrics (used for data generation and classification logic)
TEMP_WARN = 85.0       # Temperature (°C) above this is considered a warning sign
TEMP_FAIL = 100.0      # Temperature (°C) above this indicates failure likely

VIB_WARN = 6.0         # Vibration level (mm/s) above this is a warning
VIB_FAIL = 12.0        # Vibration above this indicates likely failure

PRESS_WARN_LOW = 90.0   # Pressure (bar) below this is a warning (too low)
PRESS_WARN_HIGH = 160.0 # Pressure (bar) above this is a warning (too high)
PRESS_FAIL_LOW = 80.0   # Pressure (bar) below this indicates failure likely
PRESS_FAIL_HIGH = 170.0 # Pressure (bar) above this indicates failure likely

CYCLES_WARN = 800      # Cycle count above this is a warning (maintenance due soon)
CYCLES_FAIL = 1200     # Cycle count above this indicates very high usage (failure risk)

# Status labels for the model predictions
STATUS_NAMES = ["Normal", "Warning", "Failure Predicted"]

# Color codes for statuses in the GUI
STATUS_COLORS = {
    0: "green",    # Normal
    1: "orange",   # Warning
    2: "red"       # Failure Predicted
}

# GUI update interval (milliseconds)
UPDATE_INTERVAL_MS = 1000  # 1 second updates
