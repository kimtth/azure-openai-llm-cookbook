import os
import re
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from openai import AzureOpenAI


AZURE_OPENAI_API_KEY = "your-api-key"  # Replace with your OpenAI API key
AZURE_OPENAI_MODEL_NAME = "your-model-name"  # Vision model for image analysis
AZURE_OPENAI_API_VERSION = "your-api-version"  # API version for OpenAI
AZURE_OPENAI_ENDPOINT = "your-endpoint"  # Azure endpoint for OpenAI


def extract_video_id(youtube_url):
    """Extract video ID from YouTube URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, youtube_url)
    if match:
        return match.group(1)
    return None


def get_transcript(video_id):
    """Get transcript from YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None


def get_video_title(youtube_url):
    """Get the title of the YouTube video."""
    try:
        yt = YouTube(youtube_url)
        return yt.title
    except Exception as e:
        print(f"Error getting video title: {e}")
        return "Unknown Video Title"


def summarize_with_azure_openai(text):
    """Summarize text using Azure OpenAI API."""
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY") or AZURE_OPENAI_API_KEY, 
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", AZURE_OPENAI_API_VERSION),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", AZURE_OPENAI_ENDPOINT)
        )
        
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", AZURE_OPENAI_MODEL_NAME)

        # Handle long transcripts by chunking
        if len(text) > 4000:
            chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
            summaries = []

            for chunk in chunks:
                response = client.chat.completions.create(
                    model=deployment_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that summarizes YouTube video transcripts.",
                        },
                        {
                            "role": "user",
                            "content": f"Please summarize the following transcript:\n\n{chunk}",
                        },
                    ],
                    max_tokens=500,
                    temperature=0.5,
                )
                summaries.append(response.choices[0].message.content.strip())

            # Combine the summaries
            combined_summary = " ".join(summaries)

            # Generate final summary
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that creates concise summaries.",
                    },
                    {
                        "role": "user",
                        "content": f"Please create a concise summary of these combined summaries:\n\n{combined_summary}",
                    },
                ],
                max_tokens=500,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
        else:
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes YouTube video transcripts.",
                    },
                    {
                        "role": "user",
                        "content": f"Please summarize the following transcript:\n\n{text}",
                    },
                ],
                max_tokens=500,
                temperature=0.5,
            )
            return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error in Azure OpenAI API call: {e}")
        return None


def main():
    """Main function to run the YouTube video summarizer."""
    youtube_url = input("Enter YouTube URL: ")

    video_id = extract_video_id(youtube_url)
    if not video_id:
        print("Invalid YouTube URL.")
        return

    title = get_video_title(youtube_url)
    print(f"Video Title: {title}")

    print("Fetching transcript...")
    transcript = get_transcript(video_id)
    if not transcript:
        print("Failed to retrieve transcript.")
        return

    print("Generating summary...")
    summary = summarize_with_azure_openai(transcript)
    if not summary:
        print("Failed to generate summary.")
        return

    print("\n--- SUMMARY ---")
    print(summary)
    print("---------------")


if __name__ == "__main__":
    main()
