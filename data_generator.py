# data_generator.py - Simulation of machine sensor data for real-time monitoring

import random
import config

class MachineSim:
    """
    Simulator for a single die casting machine's sensor readings and state.
    """
    def __init__(self, machine_id):
        self.id = machine_id
        # Initialize sensor values (within normal ranges)
        self.temp = random.uniform(60.0, 75.0)    # baseline temperature (°C)
        self.vib = random.uniform(1.0, 3.0)      # baseline vibration (mm/s)
        self.press = random.uniform(110.0, 130.0) # baseline pressure (bar)
        self.cycles = 0.0                        # cycles since last maintenance
        # State: 0 = normal, 1 = warning (degrading), 2 = failure predicted
        self.state = 0
        self.fault_type = None   # type of fault currently developing (temp/vibration/pressure)
        self.fail_time = 0       # counter for duration in failure state
        self.degrade_time = 0    # counter for duration in warning state

    def update(self):
        """
        Advance the simulation by one time step. Update sensor readings based on current state.
        Returns a tuple (temp, vib, press, cycles) of the updated readings.
        """
        # Normal state behavior
        if self.state == 0:
            # Increase cycles (each update represents one or more operation cycles)
            self.cycles += random.randint(1, 5)
            # Small random fluctuations around current values
            self.temp += random.uniform(-1.0, 1.0)
            self.vib += random.uniform(-0.2, 0.2)
            self.press += random.uniform(-2.0, 2.0)
            # Clamp some values to sensible bounds
            if self.vib < 0: 
                self.vib = 0.0
            if self.press < 0:
                self.press = 0.0
            # Check if conditions to trigger a warning state are met
            trigger = False
            # Condition 1: machine is very used (cycles beyond warning threshold)
            if self.cycles >= config.CYCLES_WARN:
                trigger = True
            # Condition 2: random fault occurrence (simulating an unexpected issue)
            if random.random() < 0.02:  # 2% chance each update
                trigger = True
            if trigger:
                # Enter warning state
                self.state = 1
                self.degrade_time = 0
                # Choose a fault type to simulate
                self.fault_type = random.choice(["temp", "vibration", "pressure_high", "pressure_low"])
                # Initialize the chosen fault metric to a warning level if not already
                if self.fault_type == "temp":
                    self.temp = max(self.temp, config.TEMP_WARN + 5.0)
                elif self.fault_type == "vibration":
                    self.vib = max(self.vib, config.VIB_WARN + 1.0)
                elif self.fault_type == "pressure_high":
                    self.press = max(self.press, config.PRESS_WARN_HIGH + 5.0)
                elif self.fault_type == "pressure_low":
                    self.press = min(self.press, config.PRESS_WARN_LOW - 5.0)
                # If cycles are extremely high (beyond fail threshold), escalate directly to failure state
                if self.cycles >= config.CYCLES_FAIL:
                    self.state = 2
                    self.fail_time = 0

        # Warning (degrading) state behavior
        elif self.state == 1:
            self.degrade_time += 1
            # Machine continues to operate, so cycles still increase
            self.cycles += random.randint(1, 5)
            # Gradually exacerbate the fault condition
            if self.fault_type == "temp":
                # Temperature increasing
                self.temp += random.uniform(1.0, 3.0)
                # Vibration might increase slightly as machine heats
                self.vib += random.uniform(0.0, 0.5)
                # Minor random pressure change
                self.press += random.uniform(-1.0, 1.0)
            elif self.fault_type == "vibration":
                # Vibration increasing
                self.vib += random.uniform(0.5, 1.5)
                # Temperature might slightly increase due to friction
                self.temp += random.uniform(0.0, 1.0)
                self.press += random.uniform(-1.0, 1.0)
            elif self.fault_type == "pressure_high":
                # Pressure increasing
                self.press += random.uniform(2.0, 5.0)
                # Slight increases in vibration/temperature due to strain
                self.vib += random.uniform(0.0, 0.3)
                self.temp += random.uniform(0.0, 1.0)
            elif self.fault_type == "pressure_low":
                # Pressure dropping
                self.press -= random.uniform(2.0, 5.0)
                if self.press < 0:
                    self.press = 0.0
                # Small fluctuations in others
                self.temp += random.uniform(-0.5, 0.5)
                self.vib += random.uniform(-0.1, 0.5)
            # Check if we've crossed into failure territory
            if (self.temp >= config.TEMP_FAIL or self.vib >= config.VIB_FAIL or 
                self.press >= config.PRESS_FAIL_HIGH or self.press <= config.PRESS_FAIL_LOW or 
                self.cycles >= config.CYCLES_FAIL or self.degrade_time >= 5):
                # Elevate to failure-predicted state
                self.state = 2
                self.fail_time = 0

        # Failure predicted state behavior
        elif self.state == 2:
            self.fail_time += 1
            # The machine is in critical state but still running; continue to increase cycles
            self.cycles += random.randint(1, 5)
            # Keep the metrics in a failing range (or worsening slightly)
            self.temp += random.uniform(0.0, 1.0)
            self.vib += random.uniform(0.0, 0.5)
            if self.fault_type == "pressure_low":
                # Pressure may continue dropping
                self.press -= random.uniform(0.0, 1.0)
                if self.press < 0:
                    self.press = 0.0
            else:
                # Other fault types: pressure might increase or fluctuate upward
                self.press += random.uniform(0.0, 2.0)
            # Simulate maintenance after a short period in failure state
            if self.fail_time >= 5 or self.cycles >= (config.CYCLES_FAIL + 100):
                # Reset machine to normal state after maintenance
                self.state = 0
                self.temp = random.uniform(60.0, 75.0)
                self.vib = random.uniform(1.0, 3.0)
                self.press = random.uniform(110.0, 130.0)
                self.cycles = 0.0
                self.fault_type = None
                self.degrade_time = 0
                self.fail_time = 0

        # Return the updated sensor readings
        return (self.temp, self.vib, self.press, self.cycles)
