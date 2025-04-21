# main.py - Main script to run the predictive maintenance simulation and GUI

import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

import config
from data_generator import MachineSim
import model

# Train the machine learning model (or load if we had a saved model)
clf = model.train_model()

# Initialize five machine simulators
machines = [MachineSim(i+1) for i in range(5)]
# Set initial conditions for machines (optional tuning for demonstration):
machines[0].cycles = 0    # Machine 1 starts fresh
machines[1].cycles = 1300 # Machine 2 starts with very high usage (likely needs maintenance at start)
machines[2].cycles = 600  # Machine 3 moderately used
machines[3].cycles = 0    # Machine 4 fresh
machines[4].cycles = 750  # Machine 5 near maintenance threshold

# Prepare main window
root = tk.Tk()
root.title("Predictive Maintenance Dashboard")

# Create frames for each machine
machine_frames = []
status_labels = []
metric_labels = []

for m in machines:
    frame = tk.LabelFrame(root, text=f"Machine {m.id}", padx=10, pady=5)
    frame.pack(fill="x", padx=10, pady=5)
    # Metrics label
    metrics_lbl = tk.Label(frame, text="Initializing...", font=("Arial", 10))
    metrics_lbl.pack(anchor="w")
    # Status label (will be colored)
    status_lbl = tk.Label(frame, text="Status: Initializing", font=("Arial", 10, "bold"))
    status_lbl.pack(anchor="w")
    machine_frames.append(frame)
    metric_labels.append(metrics_lbl)
    status_labels.append(status_lbl)

# Log text area
log_frame = tk.LabelFrame(root, text="Event Log", padx=10, pady=5)
log_frame.pack(fill="both", expand=True, padx=10, pady=5)
log_text = ScrolledText(log_frame, height=8, state='disabled', font=("Courier", 10))
log_text.pack(fill="both", expand=True)

# Maintain last predicted status for each machine to detect changes
last_status = [0] * len(machines)  # start assuming Normal for all

def log_event(message):
    """Append a message to the log text area with a timestamp."""
    timestamp = time.strftime("%H:%M:%S")
    log_text.config(state='normal')  # enable editing
    log_text.insert(tk.END, f"[{timestamp}] {message}\n")
    log_text.yview(tk.END)  # auto-scroll to bottom
    log_text.config(state='disabled')  # disable editing back

def update_loop():
    """Periodic update loop for simulation and GUI."""
    for i, machine in enumerate(machines):
        # Get new sensor readings from simulation
        temp, vib, press, cycles = machine.update()
        # Prepare text for metrics (formatted values with units)
        metrics_text = (f"Temperature: {temp:.1f} °C\n"
                        f"Vibration: {vib:.1f} mm/s\n"
                        f"Pressure: {press:.1f} bar\n"
                        f"Cycles since maintenance: {int(cycles)}")
        metric_labels[i].config(text=metrics_text)
        # Get model prediction for the new readings
        features = [[temp, vib, press, cycles]]
        pred_class = int(clf.predict(features)[0])
        status_text = f"Status: {config.STATUS_NAMES[pred_class]}"
        status_labels[i].config(text=status_text, fg=config.STATUS_COLORS[pred_class])
        # Check for status change events to log
        if pred_class != last_status[i]:
            # If status increased in severity
            if pred_class > last_status[i]:
                if pred_class == 1:
                    # Entered Warning
                    causes = []
                    if temp >= config.TEMP_WARN: 
                        causes.append(f"Elevated Temperature ({temp:.1f}°C)")
                    if vib >= config.VIB_WARN: 
                        causes.append(f"Elevated Vibration ({vib:.1f} mm/s)")
                    if press >= config.PRESS_WARN_HIGH or press <= config.PRESS_WARN_LOW:
                        # If pressure is out of normal range
                        if press >= config.PRESS_WARN_HIGH:
                            causes.append(f"High Pressure ({press:.1f} bar)")
                        if press <= config.PRESS_WARN_LOW:
                            causes.append(f"Low Pressure ({press:.1f} bar)")
                    if cycles >= config.CYCLES_WARN:
                        causes.append(f"High Cycle Count ({int(cycles)})")
                    cause_text = ", ".join(causes) if causes else "Anomaly detected"
                    log_event(f"Machine {machine.id} - Warning: {cause_text}")
                elif pred_class == 2:
                    # Entered Failure Predicted
                    causes = []
                    if temp >= config.TEMP_FAIL:
                        causes.append(f"High Temperature ({temp:.1f}°C)")
                    elif temp >= config.TEMP_WARN:
                        causes.append(f"Elevated Temperature ({temp:.1f}°C)")
                    if vib >= config.VIB_FAIL:
                        causes.append(f"High Vibration ({vib:.1f} mm/s)")
                    elif vib >= config.VIB_WARN:
                        causes.append(f"Elevated Vibration ({vib:.1f} mm/s)")
                    if press >= config.PRESS_FAIL_HIGH:
                        causes.append(f"High Pressure ({press:.1f} bar)")
                    elif press <= config.PRESS_FAIL_LOW:
                        causes.append(f"Low Pressure ({press:.1f} bar)")
                    elif press >= config.PRESS_WARN_HIGH:
                        causes.append(f"Elevated Pressure ({press:.1f} bar)")
                    elif press <= config.PRESS_WARN_LOW:
                        causes.append(f"Low Pressure ({press:.1f} bar)")
                    if cycles >= config.CYCLES_FAIL:
                        causes.append(f"High Cycle Count ({int(cycles)})")
                    elif cycles >= config.CYCLES_WARN:
                        causes.append(f"Elevated Cycle Count ({int(cycles)})")
                    cause_text = ", ".join(causes) if causes else "Multiple anomalies"
                    log_event(f"Machine {machine.id} - Failure Predicted: {cause_text}")
            else:
                # Status decreased (machine recovered to normal)
                if pred_class == 0:
                    # Back to Normal from Warning/Failure
                    if last_status[i] == 2:
                        log_event(f"Machine {machine.id} - Maintenance performed, back to Normal")
                    else:
                        log_event(f"Machine {machine.id} - Status back to Normal")
            # Update the last_status
            last_status[i] = pred_class

    # Schedule the next update
    root.after(config.UPDATE_INTERVAL_MS, update_loop)

# Start the update loop and run the GUI
update_loop()
root.mainloop()
