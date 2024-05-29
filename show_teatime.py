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


# URL of the XML file
url = "https://teatimechinese.libsyn.com/rss"

# Extract titles and enclosure urls
titles_and_enclosure_urls = extract_titles_and_enclosure_urls_from_xml(url)

# Save titles and enclosure urls to urls.txt
with open("./downloads/urls.txt", "w", encoding="utf-8") as file:
    file.write("# URLs to download. Add a tab and then the Filename if needed\n")
    for title, enclosure_url in titles_and_enclosure_urls:
        file.write(f"{enclosure_url}\t{title}\n")

print("Titles and enclosure URLs have been saved to urls.txt")
