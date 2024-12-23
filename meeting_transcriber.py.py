import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import speech_recognition as sr
from moviepy import VideoFileClip
import os
import json
from datetime import datetime
import threading
import pyaudio
import wave

class EnhancedTranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meeting Transcription Tool")
        self.root.geometry("1000x600")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize variables
        self.recording = False
        self.current_recording = None
        self.recognizer = sr.Recognizer()
        self.file_path = tk.StringVar()
        self.recording_time = tk.StringVar()
        self.recording_time.set("00:00")
        self.timer_running = False
        self.elapsed_time = 0
        
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        # Style configuration
        self.configure_styles()
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Create panels
        left_panel = self.create_left_panel(main_frame)
        right_panel = self.create_right_panel(main_frame)
        
        left_panel.grid(row=0, column=0, sticky="ns", padx=(0, 10))
        right_panel.grid(row=0, column=1, sticky="nsew")
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
    def configure_styles(self):
        style = ttk.Style()
        style.configure('TButton', padding=5, font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'))
        style.configure('Timer.TLabel', font=('Helvetica', 14, 'bold'), foreground='#e74c3c')
        
    def create_left_panel(self, parent):
        panel = ttk.Frame(parent)
        
        # File selection
        file_frame = ttk.LabelFrame(panel, text="File Operations", padding="5")
        file_frame.pack(fill="x", pady=5)
        
        ttk.Label(file_frame, textvariable=self.file_path, width=30).pack(pady=5)
        ttk.Button(file_frame, text="Browse File", command=self.select_file).pack(fill="x", pady=2)
        
        # Recording controls
        record_frame = ttk.LabelFrame(panel, text="Recording", padding="5")
        record_frame.pack(fill="x", pady=5)
        
        self.record_button = ttk.Button(record_frame, text="Start Recording", command=self.toggle_recording)
        self.record_button.pack(fill="x", pady=2)
        
        self.recording_label = ttk.Label(record_frame, text="Status: Not Recording")
        self.recording_label.pack(pady=2)
        
        # Recording timer
        ttk.Label(record_frame, textvariable=self.recording_time, style='Timer.TLabel').pack(pady=2)
        
        # History section
        history_frame = ttk.LabelFrame(panel, text="Recent Transcripts", padding="5")
        history_frame.pack(fill="x", pady=5)
        
        self.history_list = tk.Listbox(history_frame, height=6)
        self.history_list.pack(fill="x", pady=2)
        self.history_list.bind('<<ListboxSelect>>', self.load_selected_history)
        
        return panel
        
    def create_right_panel(self, parent):
        panel = ttk.Frame(parent)
        
        # Transcript area
        transcript_frame = ttk.LabelFrame(panel, text="Transcription", padding="5")
        transcript_frame.pack(fill="both", expand=True)
        
        self.transcript_text = scrolledtext.ScrolledText(
            transcript_frame, 
            wrap=tk.WORD, 
            width=60, 
            height=20,
            font=('Helvetica', 10)
        )
        self.transcript_text.pack(fill="both", expand=True, pady=5)
        
        # Bottom controls
        control_frame = ttk.Frame(panel)
        control_frame.pack(fill="x", pady=5)
        
        buttons = [
            ("Generate Transcript", self.generate_transcript),
            ("Save Transcript", self.save_transcript),
            ("Generate Summary", self.generate_summary),
            ("Export to PDF", self.export_to_pdf),
            ("Clear", self.clear_transcript)
        ]
        
        for text, command in buttons:
            ttk.Button(control_frame, text=text, command=command).pack(side="left", padx=2)
        
        return panel
        
    def toggle_recording(self):
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()
            
    def start_recording(self):
        self.recording = True
        self.record_button.configure(text="Stop Recording")
        self.recording_label.configure(text="Status: Recording...")
        
        # Reset and start timer
        self.elapsed_time = 0
        self.timer_running = True
        self.update_timer()
        
        # Start recording in a separate thread
        self.record_thread = threading.Thread(target=self.record_audio)
        self.record_thread.start()
        
    def stop_recording(self):
        self.recording = False
        self.timer_running = False
        self.record_button.configure(text="Start Recording")
        self.recording_label.configure(text="Status: Not Recording")
        
    def update_timer(self):
        if self.timer_running:
            minutes = self.elapsed_time // 60
            seconds = self.elapsed_time % 60
            self.recording_time.set(f"{minutes:02d}:{seconds:02d}")
            self.elapsed_time += 1
            self.root.after(1000, self.update_timer)
        
    def record_audio(self):
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        
        p = pyaudio.PyAudio()
        
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        frames = []
        
        while self.recording:
            try:
                data = stream.read(CHUNK)
                frames.append(data)
            except Exception as e:
                print(f"Error recording audio: {e}")
                break
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if frames:  # Only save if we have recorded data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            
            try:
                wf = wave.open(filename, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                self.current_recording = filename
                self.file_path.set(filename)
                messagebox.showinfo("Success", "Recording saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save recording: {e}")
        
    def select_file(self):
        filetypes = (
            ('Audio/Video files', '*.mp4 *.avi *.mov *.mp3 *.wav'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select a file',
            filetypes=filetypes
        )
        
        if filename:
            self.file_path.set(filename)
            
    def generate_transcript(self):
        if not self.file_path.get():
            messagebox.showwarning("Warning", "Please select a file or record audio first!")
            return
            
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.insert(tk.END, f"Processing file: {self.file_path.get()}\n\n")
        self.root.update()
        
        try:
            # Handle video files
            file_path = self.file_path.get()
            if file_path.lower().endswith(('.mp4', '.avi', '.mov')):
                video = VideoFileClip(file_path)
                audio_path = "temp_audio.wav"
                video.audio.write_audiofile(audio_path)
                file_path = audio_path
            
            # Perform transcription
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                
            # Clean up temporary file
            if file_path != self.file_path.get():
                os.remove(file_path)
                
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.insert(tk.END, text)
            self.save_to_history(text)
            self.update_history_list()
            
        except Exception as e:
            messagebox.showerror("Error", f"Transcription error: {str(e)}")
            
    def save_transcript(self):
        text = self.transcript_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No transcript to save!")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write(text)
                messagebox.showinfo("Success", "Transcript saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save transcript: {e}")
            
    def generate_summary(self):
        text = self.transcript_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No transcript to summarize!")
            return
            
        # Enhanced summarization
        sentences = text.split('.')
        if len(sentences) <= 3:
            summary = text
        else:
            # Get first sentence, middle sentence, and last sentence
            summary = f"{sentences[0]}.\n\n"
            middle_idx = len(sentences) // 2
            summary += f"{sentences[middle_idx]}.\n\n"
            summary += f"{sentences[-2]}."
        
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Meeting Summary")
        summary_window.geometry("600x400")
        
        summary_text = scrolledtext.ScrolledText(
            summary_window, 
            wrap=tk.WORD, 
            width=60, 
            height=15,
            font=('Helvetica', 10)
        )
        summary_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        summary_text.insert(tk.END, summary)
        summary_text.config(state=tk.DISABLED)
        
    def export_to_pdf(self):
        text = self.transcript_text.get(1.0, tk.END).strip()
        if not text:
            messagebox.showwarning("Warning", "No transcript to export!")
            return
            
        messagebox.showinfo("Info", "PDF export feature coming soon!")
        
    def clear_transcript(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the transcript?"):
            self.transcript_text.delete(1.0, tk.END)
        
    def save_to_history(self, text):
        try:
            history = []
            if os.path.exists('transcript_history.json'):
                with open('transcript_history.json', 'r') as f:
                    history = json.load(f)
                    
            history.append({
                'timestamp': datetime.now().isoformat(),
                'text': text,
                'file': self.file_path.get()
            })
            
            with open('transcript_history.json', 'w') as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            print(f"Error saving to history: {e}")
            
    def load_history(self):
        try:
            if os.path.exists('transcript_history.json'):
                with open('transcript_history.json', 'r') as f:
                    self.history = json.load(f)
                    self.update_history_list()
        except Exception as e:
            print(f"Error loading history: {e}")
            self.history = []
            
    def update_history_list(self):
        self.history_list.delete(0, tk.END)
        for entry in reversed(self.history[-5:]):  # Show last 5 entries
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime("%Y-%m-%d %H:%M")
            self.history_list.insert(0, f"{timestamp} - {os.path.basename(entry['file'])}")
            
    def load_selected_history(self, event):
        selection = self.history_list.curselection()
        if selection:
            index = selection[0]
            history_index = len(self.history) - 1 - index
            entry = self.history[history_index]
            self.transcript_text.delete(1.0, tk.END)
            self.transcript_text.insert(tk.END, entry['text'])

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedTranscriptionApp(root)
    root.mainloop()