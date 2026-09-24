import requests
from bs4 import BeautifulSoup
import os

# used to extract clean text for our knowledge base
urls = {
    "skilled_worker_appendix": "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-skilled-worker",
    "graduate_appendix": "https://www.gov.uk/guidance/immigration-rules/immigration-rules-appendix-graduate",
}

os.makedirs("data/rulebook", exist_ok=True)

for name, url in urls.items():
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.content, "html.parser")

    # Each accordion section is its own gem-c-govspeak div
    sections = soup.find_all("div", {"class": "gem-c-govspeak"})

    if not sections:
        print(f"Could not find any content sections for {name} — check the page structure")
        continue
    # gov.uk's page can render the same section more than once in the HTML
    # (e.g. collapsed + expanded states). Without this, duplicate content
    # gets saved into the text file and later duplicated again in every chunk.
    seen = set()
    unique_texts = []
    for section in sections:
        section_text = section.get_text(separator="\n", strip=True)
        if section_text not in seen:
            seen.add(section_text)
            unique_texts.append(section_text)

    text = "\n\n".join(unique_texts)
    
    filepath = f"data/rulebook/{name}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Saved {name}: {len(sections)} raw sections -> {len(unique_texts)} unique sections, {len(text.split())} words -> {filepath}")