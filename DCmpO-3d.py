import tkinter as tk
from tkinter import ttk

class EnvelopeSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Envelope Segment Normalizer")

        # Variables
        self.time_val = tk.DoubleVar(value=0)
        self.attack_val = tk.DoubleVar(value=20)  # Now represents %
        self.decay_val = tk.DoubleVar(value=100)   # Now represents %
        self.norm_attack = tk.StringVar(value="0.00")
        self.norm_decay = tk.StringVar(value="0.00")

        # Clock variables
        self.clock_running = False
        self.after_id = None
        self.updating_from_clock = False
        self.interval_sec = tk.DoubleVar(value=1.0)  # Default interval

        # Time Slider
        ttk.Label(root, text="Fake Time (0-100):").grid(row=0, column=0, padx=10, pady=5)
        self.time_slider = ttk.Scale(root, from_=0, to=100, variable=self.time_val,
                                    command=self.update_envelope)
        self.time_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        ttk.Label(root, textvariable=self.time_val).grid(row=0, column=2, padx=5)

        # Attack Control (now ratio)
        ttk.Label(root, text="Attack Ratio (%):").grid(row=1, column=0, padx=10, pady=5)
        self.attack_spin = ttk.Spinbox(root, from_=0, to=100, width=8,
                                     textvariable=self.attack_val,
                                     command=self.update_envelope)
        self.attack_spin.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # Decay Control (now ratio)
        ttk.Label(root, text="Decay Ratio (%):").grid(row=2, column=0, padx=10, pady=5)
        self.decay_spin = ttk.Spinbox(root, from_=0, to=100, width=8,
                                    textvariable=self.decay_val,
                                    command=self.update_envelope)
        self.decay_spin.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # Normalized Values Display
        ttk.Label(root, text="Normalized Attack:").grid(row=3, column=0, padx=10, pady=5)
        ttk.Label(root, textvariable=self.norm_attack, width=8,
                 relief="solid").grid(row=3, column=1, padx=10, pady=5, sticky="w")

        ttk.Label(root, text="Normalized Decay:").grid(row=4, column=0, padx=10, pady=5)
        ttk.Label(root, textvariable=self.norm_decay, width=8,
                 relief="solid").grid(row=4, column=1, padx=10, pady=5, sticky="w")

        # Clock Controls
        clock_frame = ttk.Frame(root)
        clock_frame.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="ew")

        ttk.Label(clock_frame, text="Clock Interval (sec):").pack(side=tk.LEFT, padx=(0, 5))
        self.interval_spin = ttk.Spinbox(clock_frame, from_=0.1, to=10, increment=0.1, width=8,
                                        textvariable=self.interval_sec)
        self.interval_spin.pack(side=tk.LEFT, padx=5)

        self.play_btn = ttk.Button(clock_frame, text="Play", command=self.toggle_clock)
        self.play_btn.pack(side=tk.LEFT, padx=5)

        # Time value change handler
        self.time_val.trace_add('write', self.on_time_val_changed)

        # Initialize
        self.update_envelope()

    def on_time_val_changed(self, *args):
        """Stop clock if user manually changes time value"""
        if self.clock_running and not self.updating_from_clock:
            self.stop_clock()

    def toggle_clock(self):
        """Toggle play/stop state"""
        if self.clock_running:
            self.stop_clock()
        else:
            self.start_clock()

    def start_clock(self):
        """Start the clock timer"""
        if not self.clock_running:
            self.clock_running = True
            self.play_btn.config(text="Stop")
            # Reset to 0 if at end
            if self.time_val.get() >= 100:
                self.time_val.set(0)
            self.advance_clock()

    def stop_clock(self):
        """Stop the clock timer"""
        if self.clock_running:
            self.clock_running = False
            self.play_btn.config(text="Play")
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
                
                
    def advance_clock(self):
        if not self.clock_running:
            return

        current_time = self.time_val.get()
        step = 1

        if current_time < 100:
            new_time = current_time + step
            if new_time > 100:
                new_time = 100
        else:
            new_time = 0

        self.updating_from_clock = True
        self.time_val.set(new_time)
        self.updating_from_clock = False

        # Explicitly update envelope after time change
        self.update_envelope()  # ADDED THIS LINE

        interval_ms = int(self.interval_sec.get() * 1000)
        self.after_id = self.root.after(interval_ms, self.advance_clock)            
                
                
                
    def update_envelope(self, *args):
        try:
            t = self.time_val.get()
            A = self.attack_val.get()  # Already a percentage of total time
            D = self.decay_val.get()   # Already a percentage of total time

            # Attack Segment (0-1 normalized)
            if A > 0 and t <= A:
                norm_a = t / A
                self.norm_attack.set(f"{norm_a:.2f}")
                self.norm_decay.set("0.00")

            # Decay Segment (0-1 normalized)
            elif D > A and t >= A and t <= D:
                norm_d = (t - A) / (D - A)
                self.norm_attack.set("0.00")
                self.norm_decay.set(f"{norm_d:.2f}")

            # Outside segments
            else:
                self.norm_attack.set("0.00")
                self.norm_decay.set("0.00")

        except ValueError:
            pass  # Handle invalid input silently

if __name__ == "__main__":
    root = tk.Tk()
    app = EnvelopeSimulator(root)
    root.mainloop()