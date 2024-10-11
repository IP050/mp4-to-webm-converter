import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import re
import platform

class VideoConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("MP4 to WebM Converter")
        master.geometry("800x900")
        master.resizable(True, True)  # Allow resizing

        # Initialize variables
        self.input_files = []
        self.output_folder = ""
        self.quality = tk.IntVar(value=10)  # 0 (best) to 63 (worst) for libvpx
        self.target_size = tk.StringVar()
        self.include_audio = tk.BooleanVar(value=True)
        self.target_resolution = tk.StringVar()
        self.additional_params = tk.StringVar()
        self.audio_bitrate = tk.StringVar(value="160")  # Default audio bitrate in kb/s
        self.min_video_bitrate = 50  # kb/s, adjustable based on needs

        # Create GUI components
        self.create_widgets()

    def create_widgets(self):
        padding_options = {'padx': 10, 'pady': 5}

        # Input Files Selection
        input_frame = tk.LabelFrame(self.master, text="Input MP4 Files")
        input_frame.pack(fill='x', **padding_options)

        browse_button = tk.Button(input_frame, text="Browse Files", command=self.browse_input)
        browse_button.pack(pady=5)

        self.files_listbox = tk.Listbox(input_frame, selectmode=tk.MULTIPLE, width=100, height=5)
        self.files_listbox.pack(pady=5)

        remove_button = tk.Button(input_frame, text="Remove Selected", command=self.remove_selected_files)
        remove_button.pack(pady=5)

        # Video Information Display
        info_frame = tk.LabelFrame(self.master, text="Selected Video Information")
        info_frame.pack(fill='x', **padding_options)

        self.info_text = tk.Text(info_frame, height=5, state='disabled')
        self.info_text.pack(fill='x', padx=5, pady=5)

        # Output Files Selection
        output_frame = tk.LabelFrame(self.master, text="Output WebM Files")
        output_frame.pack(fill='x', **padding_options)

        browse_output_button = tk.Button(output_frame, text="Set Output Folder", command=self.browse_output_folder)
        browse_output_button.pack(pady=5)

        self.output_folder_label = tk.Label(output_frame, text="No output folder selected.", fg="red")
        self.output_folder_label.pack(pady=5)

        # Quality Selection
        quality_frame = tk.LabelFrame(self.master, text="Quality Settings")
        quality_frame.pack(fill='x', **padding_options)

        quality_label = tk.Label(quality_frame, text="Quality (0-63):")
        quality_label.pack(side='left', padx=5)

        quality_slider = tk.Scale(quality_frame, from_=0, to=63, orient='horizontal', variable=self.quality)
        quality_slider.pack(side='left', fill='x', expand=True, padx=5)

        # Target Size
        size_frame = tk.LabelFrame(self.master, text="Target File Size")
        size_frame.pack(fill='x', **padding_options)

        size_label = tk.Label(size_frame, text="Target Size per File (KB):")
        size_label.pack(side='left', padx=5)

        size_entry = tk.Entry(size_frame, textvariable=self.target_size, width=20)
        size_entry.pack(side='left', padx=5)

        # Target Resolution
        resolution_frame = tk.LabelFrame(self.master, text="Resolution Settings")
        resolution_frame.pack(fill='x', **padding_options)

        resolution_label = tk.Label(resolution_frame, text="Target Resolution (e.g., 640x360):")
        resolution_label.pack(side='left', padx=5)

        resolution_entry = tk.Entry(resolution_frame, textvariable=self.target_resolution, width=20)
        resolution_entry.pack(side='left', padx=5)

        # Audio Bitrate
        audio_bitrate_frame = tk.LabelFrame(self.master, text="Audio Settings")
        audio_bitrate_frame.pack(fill='x', **padding_options)

        audio_bitrate_label = tk.Label(audio_bitrate_frame, text="Audio Bitrate (kb/s):")
        audio_bitrate_label.pack(side='left', padx=5)

        audio_bitrate_entry = tk.Entry(audio_bitrate_frame, textvariable=self.audio_bitrate, width=10)
        audio_bitrate_entry.pack(side='left', padx=5)

        # Include Audio
        audio_frame = tk.Frame(self.master)
        audio_frame.pack(fill='x', **padding_options)

        audio_check = tk.Checkbutton(audio_frame, text="Include Audio", variable=self.include_audio)
        audio_check.pack(side='left', padx=5)

        # Additional FFmpeg Parameters
        advanced_frame = tk.LabelFrame(self.master, text="Advanced FFmpeg Parameters")
        advanced_frame.pack(fill='x', **padding_options)

        advanced_label = tk.Label(advanced_frame, text="Additional Parameters:")
        advanced_label.pack(anchor='w', padx=5)

        advanced_entry = tk.Entry(advanced_frame, textvariable=self.additional_params, width=80)
        advanced_entry.pack(padx=5, pady=5)

        # Convert Button
        self.convert_button = tk.Button(
            self.master,
            text="Convert",
            command=self.start_conversion,
            bg="green",
            fg="white",
            font=("Helvetica", 12, "bold")
        )
        self.convert_button.pack(pady=20)

        # Progress Bar
        progress_frame = tk.LabelFrame(self.master, text="Conversion Progress")
        progress_frame.pack(fill='x', **padding_options)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=10, pady=10)

        # Status Label
        self.status_label = tk.Label(self.master, text="", fg="blue")
        self.status_label.pack(pady=10)

        # Open Output Folder Button
        self.open_folder_button = tk.Button(
            self.master,
            text="Open Output Folder",
            command=self.open_output_folder,
            state='disabled',
            bg="blue",
            fg="white",
            font=("Helvetica", 12, "bold")
        )
        self.open_folder_button.pack(pady=10)

    def browse_input(self):
        files = filedialog.askopenfilenames(
            title="Select MP4 Files",
            filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
        )
        if files:
            for file in files:
                if file not in self.input_files:
                    self.input_files.append(file)
                    self.files_listbox.insert(tk.END, file)
            self.fetch_videos_info()

    def remove_selected_files(self):
        selected_indices = list(self.files_listbox.curselection())
        selected_indices.reverse()  # Remove from the end to avoid index shifting
        for index in selected_indices:
            self.input_files.pop(index)
            self.files_listbox.delete(index)
        self.fetch_videos_info()

    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self.output_folder_label.config(text=folder, fg="green")
            self.open_folder_button.config(state='normal')

    def fetch_videos_info(self):
        if not self.input_files:
            self.info_text.config(state='normal')
            self.info_text.delete('1.0', tk.END)
            self.info_text.config(state='disabled')
            return

        self.info_text.config(state='normal')
        self.info_text.delete('1.0', tk.END)
        for file in self.input_files:
            info = self.get_video_info(file)
            self.info_text.insert(tk.END, f"File: {os.path.basename(file)}\n")
            if info:
                self.info_text.insert(tk.END, f"  Duration: {info.get('Duration', 'Unknown')}\n")
                self.info_text.insert(tk.END, f"  Bitrate: {info.get('Bitrate', 'Unknown')} kb/s\n")
                self.info_text.insert(tk.END, f"  Resolution: {info.get('Resolution', 'Unknown')}\n")
            else:
                self.info_text.insert(tk.END, "  Could not retrieve information.\n")
            self.info_text.insert(tk.END, "\n")
        self.info_text.config(state='disabled')

    def get_video_info(self, file_path):
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries",
                   "format=duration:stream=bit_rate,width,height",
                   "-of", "default=noprint_wrappers=1", file_path]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            output, _ = process.communicate()

            duration = self.parse_duration(output)
            bitrate = self.parse_bitrate(output)
            resolution = self.parse_resolution(output)

            return {
                'Duration': duration,
                'Bitrate': bitrate,
                'Resolution': resolution
            }
        except Exception as e:
            print(f"Error fetching info for {file_path}: {e}")
            return None

    def parse_duration(self, ffprobe_output):
        match = re.search(r'duration=([\d\.]+)', ffprobe_output)
        if match:
            total_seconds = float(match.group(1))
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:05.2f}"
        else:
            return "Unknown"

    def parse_bitrate(self, ffprobe_output):
        match = re.search(r'bit_rate=(\d+)', ffprobe_output)
        if match:
            return int(match.group(1)) // 1000  # Convert from bps to kbps
        else:
            return "Unknown"

    def parse_resolution(self, ffprobe_output):
        match_width = re.search(r'width=(\d+)', ffprobe_output)
        match_height = re.search(r'height=(\d+)', ffprobe_output)
        if match_width and match_height:
            return f"{match_width.group(1)}x{match_height.group(1)}"
        else:
            return "Unknown"

    def start_conversion(self):
        if not self.input_files:
            messagebox.showerror("Error", "Please select at least one input MP4 file.")
            return

        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        if not self.target_size.get().isdigit():
            messagebox.showerror("Error", "Please enter a valid target size in KB.")
            return

        # Optionally disable widgets here

        self.progress_var.set(0)
        self.status_label.config(text="Starting conversion...", fg="blue")
        self.master.update_idletasks()

        # Start conversion in a new thread
        thread = threading.Thread(target=self.convert_files)
        thread.start()

    def convert_files(self):
        total_files = len(self.input_files)
        for idx, input_path in enumerate(self.input_files, start=1):
            try:
                # Calculate target bitrate based on desired size
                target_size_kb = int(self.target_size.get())
                video_info = self.get_video_info(input_path)
                duration_str = video_info.get('Duration', "00:00:00.00")
                duration_sec = self.duration_to_seconds(duration_str)
                if duration_sec <= 0:
                    self.update_status(f"Invalid duration for {os.path.basename(input_path)}. Skipping.", "red")
                    continue

                total_bitrate = (target_size_kb * 8) / duration_sec  # in kb/s

                # Calculate video bitrate
                if self.include_audio.get():
                    try:
                        audio_bitrate = int(self.audio_bitrate.get())
                    except ValueError:
                        self.update_status("Invalid audio bitrate. Skipping conversion.", "red")
                        continue
                else:
                    audio_bitrate = 0

                video_bitrate = total_bitrate - audio_bitrate

                # Check if video bitrate is above minimum
                if video_bitrate < self.min_video_bitrate:
                    # Attempt to reduce resolution by 20%
                    current_resolution = video_info.get('Resolution', "640x360")
                    width, height = map(int, current_resolution.lower().split('x'))
                    new_width = int(width * 0.8)
                    new_height = int(height * 0.8)
                    target_resolution = f"{new_width}x{new_height}"

                    # Set video bitrate to minimum
                    video_bitrate = self.min_video_bitrate
                    self.update_status(f"Reducing resolution for {os.path.basename(input_path)} to meet target size.", "orange")
                else:
                    target_resolution = self.target_resolution.get()
                    if target_resolution and not re.match(r'^\d{3,4}x\d{3,4}$', target_resolution):
                        self.update_status(f"Invalid resolution format for {os.path.basename(input_path)}. Skipping.", "red")
                        continue

                # Build FFmpeg command
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output files without asking
                    "-i", input_path,
                    "-vcodec", "libvpx",
                    "-cpu-used", "5",  # Faster encoding
                    "-deadline", "realtime"
                ]

                if video_bitrate > 0:
                    cmd += ["-b:v", f"{int(video_bitrate)}k"]
                    cmd += ["-crf", str(self.quality.get())]  # Adjust as needed
                else:
                    # Default quality-based encoding
                    cmd += ["-crf", str(self.quality.get()), "-b:v", "0"]

                # Apply resolution scaling if needed
                if target_resolution:
                    cmd += ["-vf", f"scale={target_resolution}"]

                # Apply audio options
                if self.include_audio.get():
                    cmd += ["-c:a", "libvorbis", "-b:a", f"{self.audio_bitrate.get()}k"]
                else:
                    cmd += ["-an"]

                # Apply additional parameters if any
                additional = self.additional_params.get().strip()
                if additional:
                    cmd += additional.split()

                # Set output file path
                base_name = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(self.output_folder, f"{base_name}.webm")
                cmd += [output_path]

                # Print the command for debugging
                print(f"Executing command: {' '.join(cmd)}")

                # Execute FFmpeg command
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

                total_duration = duration_sec
                # Read from stderr
                while True:
                    line = process.stderr.readline()
                    if not line:
                        break
                    print(line.strip())  # Debug: print FFmpeg output

                    # Extract current time
                    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2}\.\d{2})', line)
                    if time_match and total_duration > 0:
                        hours = int(time_match.group(1))
                        minutes = int(time_match.group(2))
                        seconds = float(time_match.group(3))
                        current_time = hours * 3600 + minutes * 60 + seconds
                        progress = (current_time / total_duration) * 100
                        progress = min(progress, 100)
                        self.progress_var.set(progress)
                        self.master.update_idletasks()

                process.wait()

                if process.returncode != 0:
                    # Read any remaining error output
                    error_output = process.stderr.read()
                    print(f"FFmpeg error output: {error_output}")
                    self.update_status(f"Conversion failed for {os.path.basename(input_path)}.", "red")
                    continue  # Skip to the next file
                else:
                    self.update_status(f"Conversion successful for {os.path.basename(input_path)}.", "green")

                # Update overall progress bar
                file_progress = (idx / total_files) * 100
                self.progress_var.set(file_progress)
                self.master.update_idletasks()

            except Exception as e:
                self.update_status(f"Error converting {os.path.basename(input_path)}: {e}", "red")
                continue  # Continue with the next file

    # Optionally re-enable widgets here

        # Optionally re-enable widgets here

    def duration_to_seconds(self, duration_str):
        try:
            parts = duration_str.split(':')
            hours = float(parts[0])
            minutes = float(parts[1])
            seconds = float(parts[2])
            total_seconds = hours * 3600 + minutes * 60 + seconds
            return total_seconds
        except:
            return 0

    def update_status(self, message, color):
        self.status_label.config(text=message, fg=color)
        self.master.update_idletasks()

    def open_output_folder(self):
        if self.output_folder:
            if platform.system() == "Windows":
                os.startfile(self.output_folder)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.output_folder])
            else:
                subprocess.Popen(["xdg-open", self.output_folder])
        else:
            messagebox.showerror("Error", "No output folder selected.")

def main():
    root = tk.Tk()
    app = VideoConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
