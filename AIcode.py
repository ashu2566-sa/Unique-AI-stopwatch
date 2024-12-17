import tkinter as tk
from tkinter import font, filedialog, messagebox
import time
import speech_recognition as sr
import pyttsx3
from random import choice
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import csv
import datetime
import random

class UniqueAIStopwatch:
    def __init__(self, root):
        self.root = root
        self.root.title("Unique AI Stopwatch with Hands-Free Features")
        self.root.geometry("1000x1000")
        self.root.config(bg="#1e1e1e")

        # Fonts
        self.large_font = font.Font(family="Helvetica", size=20, weight="bold")
        self.medium_font = font.Font(family="Helvetica", size=14)
        self.small_font = font.Font(family="Helvetica", size=10)

        # Stopwatch Variables
        self.running = False
        self.start_time = 0
        self.elapsed_time = 0
        self.laps = []
        self.productivity_score = 0

        # Speech Engine
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.listening = True

        # Stopwatch UI
        self.time_label = tk.Label(self.root, text="00:00:00", font=self.large_font, fg="white", bg="#1e1e1e")
        self.time_label.pack(pady=10)

        # Graph Dashboard
        self.graph_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.graph_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Controls
        control_frame = tk.Frame(self.root, bg="#1e1e1e")
        control_frame.pack(pady=10)

        self.start_button = tk.Button(control_frame, text="Start", font=self.small_font, command=self.start, bg="#4CAF50", fg="white")
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(control_frame, text="Stop", font=self.small_font, command=self.stop, bg="#f44336", fg="white", state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.reset_button = tk.Button(control_frame, text="Reset", font=self.small_font, command=self.reset, bg="#2196F3", fg="white")
        self.reset_button.grid(row=0, column=2, padx=5)

        self.lap_button = tk.Button(control_frame, text="Lap", font=self.small_font, command=self.record_lap, bg="#FF9800", fg="white")
        self.lap_button.grid(row=0, column=3, padx=5)

        self.voice_button = tk.Button(control_frame, text="Voice Control", font=self.small_font, command=self.voice_command, bg="#8A2BE2", fg="white")
        self.voice_button.grid(row=0, column=4, padx=5)

        self.export_button = tk.Button(control_frame, text="Export Data", font=self.small_font, command=self.export_data, bg="#FF5722", fg="white")
        self.export_button.grid(row=0, column=5, padx=5)

        self.analysis_button = tk.Button(control_frame, text="Analyze Productivity", font=self.small_font, command=self.analyze_productivity, bg="#00C853", fg="white")
        self.analysis_button.grid(row=0, column=6, padx=5)

        # Insights Section
        self.insights_label = tk.Label(self.root, text="Advanced Productivity Insights", font=self.large_font, fg="white", bg="#1e1e1e")
        self.insights_label.pack(pady=10)
        self.insights_text = tk.Text(self.root, font=self.small_font, height=8, bg="#2e2e2e", fg="white")
        self.insights_text.pack(pady=5, fill=tk.BOTH, expand=True)

        # Start listening thread
        self.voice_thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        self.voice_thread.start()

    def update_time(self):
        """Update stopwatch time and visualize progress."""
        if self.running:
            self.elapsed_time = time.time() - self.start_time
            hours, remainder = divmod(int(self.elapsed_time), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.time_label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}")
            self.root.after(100, self.update_time)

    def start(self):
        """Start the stopwatch."""
        if not self.running:
            self.running = True
            self.start_time = time.time() - self.elapsed_time
            self.update_time()
            self.speak("Stopwatch started")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop(self):
        """Stop the stopwatch."""
        if self.running:
            self.running = False
            self.speak("Stopwatch stopped")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def reset(self):
        """Reset the stopwatch and clear laps."""
        self.running = False
        self.elapsed_time = 0
        self.start_time = 0
        self.time_label.config(text="00:00:00")
        self.speak("Stopwatch reset")
        self.laps.clear()
        self.update_graph()
        self.insights_text.delete(1.0, tk.END)

    def record_lap(self):
        """Record a lap and add it to the insights."""
        if self.running:
            lap_time = self.elapsed_time - sum(self.laps)
            self.laps.append(lap_time)
            self.update_graph()
            self.insights_text.insert(tk.END, f"Lap {len(self.laps)}: {lap_time:.2f} seconds\n")

    def voice_command(self):
        """Handle voice commands."""
        self.speak("Listening for a voice command...")
        with sr.Microphone() as source:
            try:
                audio = self.recognizer.listen(source, timeout=5)
                command = self.recognizer.recognize_google(audio).lower()
                self.process_command(command)
            except:
                self.speak("Sorry, I couldn't understand that.")

    def process_command(self, command):
        """Process a recognized voice command."""
        if "start" in command:
            self.start()
        elif "stop" in command:
            self.stop()
        elif "reset" in command:
            self.reset()
        elif "lap" in command:
            self.record_lap()
        elif "analyze" in command:
            self.analyze_productivity()
        else:
            self.speak("Command not recognized.")

    def speak(self, text):
        """Text-to-speech feedback."""
        self.engine.say(text)
        self.engine.runAndWait()

    def update_graph(self):
        """Update the lap progress graph."""
        self.ax.clear()
        if self.laps:
            self.ax.plot(range(1, len(self.laps) + 1), self.laps, marker='o', label="Lap Times")
            self.ax.set_title("Lap Times")
            self.ax.set_xlabel("Lap Number")
            self.ax.set_ylabel("Time (s)")
            self.ax.legend()
        self.canvas.draw()

    def export_data(self):
        """Export lap data to a CSV file."""
        if not self.laps:
            messagebox.showwarning("No Data", "No lap data to export!")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Lap Number", "Time (s)", "Timestamp"])
                for i, lap in enumerate(self.laps, start=1):
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    writer.writerow([i, lap, timestamp])
            self.speak("Data exported successfully.")

    def analyze_productivity(self):
        """Analyze productivity based on lap data."""
        if not self.laps:
            self.insights_text.insert(tk.END, "No laps recorded. Start the stopwatch and record laps to analyze productivity.\n")
            return

        total_time = sum(self.laps)
        average_lap = total_time / len(self.laps)
        self.productivity_score = random.randint(70, 100)  # Simulated productivity score

        self.insights_text.insert(tk.END, f"Total Time: {total_time:.2f} seconds\n")
        self.insights_text.insert(tk.END, f"Average Lap Time: {average_lap:.2f} seconds\n")
        self.insights_text.insert(tk.END, f"Productivity Score: {self.productivity_score}/100\n")
        self.speak(f"Your productivity score is {self.productivity_score} out of 100.")

    def listen_for_commands(self):
        """Continuously listen for voice commands in a background thread."""
        while self.listening:
            with sr.Microphone() as source:
                try:
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=5)
                    command = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized command: {command}")  # For debugging
                    self.process_command(command)
                except Exception as e:
                    print(f"Error recognizing voice command: {e}")  # For debugging

# Run the unique AI stopwatch program
if __name__ == "__main__":
    root = tk.Tk()
    app = UniqueAIStopwatch(root)
    root.mainloop()
