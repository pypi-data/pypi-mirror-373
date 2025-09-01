from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

class YoutubeTranscriptExtractor:
    def __init__(self,url,language="en"):
        self.url=url
        self.language=language
    def extract_youtube_video_id(self):
        """Extract YouTube video ID from URL"""
        try:
            parsed_url = urlparse(self.url)
            if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
                query = parse_qs(parsed_url.query)
                return query.get("v", [None])[0]
            elif parsed_url.hostname == "youtu.be":
                return parsed_url.path[1:]
            return None
        except Exception as e:
            return f"Error extracting video ID: {e}"
    def extract_transcript(self):
        try:
            video_id = self.extract_youtube_video_id()
            ytt = YouTubeTranscriptApi()
            transcript = ytt.fetch(video_id)
            return transcript
        except Exception as e:
            return f"Error extracting transcript: {e}"
    def clean_transcript(self):
        try:
            transcript = self.extract_transcript()
            cleaned_transcript = []
            for item in transcript.snippets:
                cleaned_transcript.append(
                    {
                        "text": item.text,
                        "start": item.start,
                        "duration": item.duration,
                        "end":item.start + item.duration

                    }
                )
            return cleaned_transcript
        except Exception as e:
            return f"Error cleaning transcript:{e}"
    def get_transcript_text(self):
        try:
            transcript = self.extract_transcript()
            transcript_text = ""
            for item in transcript.snippets:
                transcript_text += item.text + " "
            return transcript_text
        except Exception as e:
            return f"Error getting transcript text: {e}"