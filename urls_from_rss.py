import requests
import xml.etree.ElementTree as ET


def extract_titles_and_enclosure_urls_from_xml(url):
    # Download XML file from the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Parse XML content
        root = ET.fromstring(response.content)

        # Find all <item> elements
        items = root.findall(".//item")

        # Extract titles and enclosure urls
        results = []
        for item in items:
            title = (
                item.find("title").text
                if item.find("title") is not None
                else "No title"
            )
            enclosure = item.find("enclosure")
            enclosure_url = (
                enclosure.get("url") if enclosure is not None else "No enclosure url"
            )
            results.append((title, enclosure_url))

        return results
    else:
        print("Failed to fetch XML content. Status code:", response.status_code)
        return []


# fmt: off

# URL of the XML file
# url, podcast_name = "https://teatimechinese.libsyn.com/rss", "TeaTime Chinese" # TeaTime Chinese
# url, podcast_name = "https://feed.firstory.me/rss/user/ckq9bl3vd660p0805d1apvgrd", "Huimin Mandarin"  # Learn Mandarin in Mandarin with Huimin
url, podcast_name = "https://anchor.fm/s/5caa7664/podcast/rss", "Haike Mandarin"  # 還可中文 Haike Mandarin
# url, podcast_name = "https://feeds.soundcloud.com/users/soundcloud:users:688207190/sounds.rss", "One Call Awaw"  # 打個電話給你 One Call Awaw
# url, podcast_name = "https://feed.firstory.me/rss/user/cko0g8j5m1toy0984t6s7mqtk","Convo Chinese" # 瞎扯学中文 Convo Chinese
# fmt: on


# Extract titles and enclosure urls
titles_and_enclosure_urls = extract_titles_and_enclosure_urls_from_xml(url)

# Save titles and enclosure urls to urls.txt
# podcast_name = "convo_chinese"
filename = f"{podcast_name}_urls.txt"
with open(f"./downloads/{filename}", "w", encoding="utf-8") as file:
    file.write("# URLs to download. Add a tab and then the Filename if needed\n")
    print(f"Found {len(titles_and_enclosure_urls)} urls")
    for title, enclosure_url in titles_and_enclosure_urls:
        file.write(f"{enclosure_url}\t{podcast_name} - {title}\n")

print(f"Titles and enclosure URLs have been saved to {filename}")
