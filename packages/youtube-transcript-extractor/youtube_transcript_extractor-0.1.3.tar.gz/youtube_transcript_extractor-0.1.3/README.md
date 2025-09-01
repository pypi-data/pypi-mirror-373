# Youtube Transcript Extractor

A lightweight Python package to **extract and process YouTube video transcripts** using the [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/).

---

## Features

- Extract YouTube **video ID** from a URL (`youtu.be` or `youtube.com`).
- Fetch raw **transcripts** from YouTube videos.
- Clean transcripts into a structured format (text, start, duration, end).
- Get **plain transcript text** for analysis or processing.

---

## Installation

Install directly from PyPI:

```bash
pip install youtube-transcript-extractor
```

Or install from source (development mode):

```bash
git clone https://github.com/your-username/Youtube-Transcript-Extractor.git
cd Youtube-Transcript-Extractor
pip install -e .
```

---

## Usage

### Import the package
```python
from youtube_transcript_extractor import YoutubeTranscriptExtractor
```

### Example

```python
# Initialize with a YouTube URL
yt = YoutubeTranscriptExtractor("https://youtu.be/dQw4w9WgXcQ")

# 1. Extract video ID
print(yt.extract_youtube_video_id())
# Output: dQw4w9WgXcQ

# 2. Get raw transcript
print(yt.extract_transcript()[:2])
# Output:
# [
#   {'text': "We're no strangers to love", 'start': 7.58, 'duration': 4.12},
#   {'text': "You know the rules and so do I", 'start': 11.70, 'duration': 4.26}
# ]

# 3. Get cleaned transcript
print(yt.clean_transcript()[:2])
# Output:
# [
#   {'text': "We're no strangers to love", 'start': 7.58, 'duration': 4.12, 'end': 11.70},
#   {'text': "You know the rules and so do I", 'start': 11.70, 'duration': 4.26, 'end': 15.96}
# ]

# 4. Get transcript as plain text
print(yt.get_transcript_text()[:100])
# Output: "We're no strangers to love You know the rules and so do I ..."
```

---

## Requirements

- Python >= 3.9
- Dependencies:
  - `youtube-transcript-api`
  - `urllib3`
  - `requests`

---

## Project Links

- **Source Code:** [GitHub](https://github.com/your-username/Youtube-Transcript-Extractor)  
- **PyPI:** [Youtube Transcript Extractor](https://pypi.org/project/youtube-transcript-extractor/)  

---

## License

MIT License © 2025 54gO