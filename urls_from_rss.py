import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import time
from dateutil import parser

# fmt: off

# URL of the XML file
podcasts = [
    {
        "url": "https://anchor.fm/s/1d7d70a4/podcast/rss",
        "podcast_name": "Speak Chinese Naturally",
        "description": "Speak Chinese Naturally -Learn Chinese (Mandarin)"
    },
    {
        "url": "https://feed.firstory.me/rss/user/ckq9bl3vd660p0805d1apvgrd",
        "podcast_name": "Huimin Mandarin",
        "description": "Learn Mandarin in Mandarin with Huimin"
    },
    {
        "url": "https://anchor.fm/s/5caa7664/podcast/rss",
        "podcast_name": "Haike Mandarin",
        "description": "還可中文 Haike Mandarin"
    },
    {
        "url": "https://feeds.soundcloud.com/users/soundcloud:users:688207190/sounds.rss",
        "podcast_name": "One Call Awaw",
        "description": "打個電話給你 One Call Awaw"
    },
    {
        "url": "https://feed.firstory.me/rss/user/cko0g8j5m1toy0984t6s7mqtk",
        "podcast_name": "Convo Chinese",
        "description": "瞎扯学中文 Convo Chinese"
    },
    {
        "url": "https://teatimechinese.libsyn.com/rss",
        "podcast_name": "TeaTime Chinese",
        "description": "TeaTime Chinese"
    },
]  # fmt: on


# Define the namespaces used in the RSS feed (if any)
namespaces = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}


def format_duration(duration):
    parts = duration.split(":")
    if len(parts) == 2:  # Format mm:ss
        hours = "00"
        minutes, seconds = parts
    elif len(parts) == 3:  # Format hh:mm:ss
        hours, minutes, seconds = parts
    else:
        return "00:00:00"  # Default to 00:00:00 for unknown formats

    return f"{hours.zfill(2)}:{minutes.zfill(2)}:{seconds.zfill(2)}"


def seconds_to_hours_minutes_seconds(total_seconds):
    hours = total_seconds // 3600
    remaining_seconds = total_seconds % 3600
    minutes = remaining_seconds // 60
    seconds = remaining_seconds % 60
    return str(hours), str(minutes), str(seconds)


# Function to format duration
def format_duration(duration):
    parts = duration.split(":")
    if len(parts) == 2:  # Format mm:ss
        hours = "00"
        minutes, seconds = parts
    elif len(parts) == 3:  # Format hh:mm:ss
        hours, minutes, seconds = parts
    elif len(parts) == 1:  # Format hh:mm:ss
        hours, minutes, seconds = seconds_to_hours_minutes_seconds(int(duration))
    else:
        return "00:00:00"  # Default to 00:00:00 for unknown formats

    return f"{hours.zfill(2)}:{minutes.zfill(2)}:{seconds.zfill(2)}"


def convert_to_unix_timestamp(pub_date_str):
    # Parse the date string into a datetime object
    pub_date = parser.parse(pub_date_str)
    # Convert the datetime object to a Unix timestamp
    return pub_date.strftime("%Y-%m-%dT%H:%M:%SZ")


# Save titles and enclosure urls to urls.txt
# podcast_name = "convo_chinese"
# filename = f"{podcast_name}_urls.txt"
filename = f"all_urls.txt"

with open(f"./downloads/{filename}", "w", encoding="utf-8") as file:
    file.write("# URLs to download. Add a tab and then the Filename if needed\n")

    for podcast in podcasts:
        # Fetch the RSS feed

        url = podcast["url"]
        podcast_name = podcast["podcast_name"]
        response = requests.get(url)
        rss_content = response.content

        # Parse the RSS feed
        root = ET.fromstring(rss_content)

        count = 0
        # Iterate over each item (episode) in the feed
        for item in root.findall(".//item"):
            title = item.find("title").text
            enclosure = item.find("enclosure")
            pubDate = item.find("pubDate").text
            audio_url = enclosure.get("url") if enclosure is not None else "N/A"

            duration = item.find("itunes:duration", namespaces)
            duration_text = format_duration(duration.text)
            line = f'{audio_url},{convert_to_unix_timestamp(pubDate)},"{podcast_name} - {title}",{format_duration(duration_text)}\n'

            file.write(line)
            count += 1

        print(
            f"{podcast_name} {count} Titles and enclosure URLs have been saved to {filename}"
        )
