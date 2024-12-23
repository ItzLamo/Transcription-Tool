# Meeting Transcription Tool  

## Overview  
The **Meeting Transcription Tool** is a desktop application for recording, transcribing, summarizing, and managing audio or video meeting content. It simplifies capturing and organizing meeting details for easy access and review.  

---

## Features  
- **Audio Recording**: Record meetings directly within the app.  
- **File Upload**: Import audio/video files for transcription.  
- **Transcription**: Convert speech to text using Google Speech Recognition.  
- **Summarization**: Generate concise summaries of transcripts.  
- **History Management**: Save and revisit recent transcriptions.  
- **Export Options**: Save transcripts as text files or prepare for future PDF export.  

---

## Requirements  
- Python 3.x  
- Required Python Libraries:  
  - `tkinter`  
  - `pyaudio`  
  - `wave`  
  - `speech_recognition`  
  - `moviepy`  
  - `json`  

Install dependencies with:  
```bash
pip install moviepy pyaudio speechrecognition
```  

---

## Usage  
1. **Launch the Application**: Run the script to open the tool.  
2. **Record Audio**: Click "Start Recording" to capture live audio.  
3. **Upload Files**: Use the "Browse File" button to import existing audio/video files.  
4. **Generate Transcript**: Select a file or recording and click "Generate Transcript."  
5. **Summarize Content**: Click "Generate Summary" to create a concise overview.  
6. **Save Results**: Save the transcript or export it for further use.  

---

## Upcoming Features  
- PDF Export for transcripts.  
- Advanced editing and formatting options for transcripts.  
