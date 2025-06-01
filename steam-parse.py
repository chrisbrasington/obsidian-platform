import os
import json
import subprocess
from bs4 import BeautifulSoup

# Constants
HTML_PATH = 'account.html'
GAMES_DIR = '/home/chris/obsidian/brain/03 - Resources/Video Games'
TITLES_JSON = 'titles.json'
PROGRESS_JSON = 'progress.json'

def copy_to_clipboard(text):
    """Copy text to clipboard - supports both Wayland and X11"""
    # Try Wayland clipboard first (wl-clipboard)
    try:
        subprocess.run(['wl-copy'], input=text.encode(), check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback to X11 clipboard utilities
    try:
        subprocess.run(['xclip', '-selection', 'clipboard'], 
                      input=text.encode(), check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Final fallback to xsel
    try:
        subprocess.run(['xsel', '--clipboard', '--input'], 
                      input=text.encode(), check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def focus_obsidian_and_search():
    """Focus Obsidian window and perform search"""
    import time
    
    try:
        # Focus Obsidian window (assuming it contains "Obsidian" in the title)
        subprocess.run(['swaymsg', '[title=".*Obsidian.*"] focus'], check=True)
        time.sleep(0.2)  # Small delay to ensure window is focused
        
        # Send Ctrl+Space (game search)
        subprocess.run(['wtype', '-M', 'ctrl', '-k', 'space'], check=True)
        time.sleep(0.1)
        
        # Send Ctrl+V (paste)
        subprocess.run(['wtype', '-M', 'ctrl', '-k', 'v'], check=True)
        time.sleep(0.1)
        
        # Send Enter (search)
        subprocess.run(['wtype', '-k', 'Return'], check=True)
        
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def extract_titles():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    titles = []
    for row in soup.find_all('tr'):
        if 'demo' in row.get_text().to_lower():
            continue
        if 'benchmark' in row.get_text().to_lower():
            continue
        
        tds = row.find_all('td')
        if len(tds) >= 2:
            title = tds[1].get_text(strip=True)
            title = title.replace('Remove', '').strip()
            if title:
                titles.append(title)
    
    return titles

def load_or_create_titles():
    if os.path.exists(TITLES_JSON):
        with open(TITLES_JSON, 'r') as f:
            return json.load(f)
    
    titles = extract_titles()
    with open(TITLES_JSON, 'w') as f:
        json.dump(titles, f, indent=2)
    
    return titles

def load_progress():
    if os.path.exists(PROGRESS_JSON):
        with open(PROGRESS_JSON, 'r') as f:
            return json.load(f).get('index', 0)
    return 0

def save_progress(index):
    with open(PROGRESS_JSON, 'w') as f:
        json.dump({'index': index}, f)

def main():
    titles = load_or_create_titles()
    start_index = load_progress()
    
    for i in range(start_index, len(titles)):
        title = titles[i]
        title = title.replace('™', '')
        
        # Check for matching file
        if not any(title in fname for fname in os.listdir(GAMES_DIR)):
            search_term = title.replace(' ', '+')
            print(f'https://store.steampowered.com/search/?term={search_term}')
            
            # Copy title to clipboard and trigger Obsidian search
            if copy_to_clipboard(title):

                bar_length = 30  # length of the loading bar
                progress = (i + 1) / len(titles)
                percent = round(progress * 100)
                filled_length = round(bar_length * progress)
                bar = '#' * filled_length + '-' * (bar_length - filled_length)

                print(f"\n[{bar}] {percent}%", end=' ')
                print(f"[{i + 1}]/[{len(titles)}]\n{title}\n")
                
                auto_search = input("Auto-search in Obsidian? (y/n/[number], default=y): ").strip().lower()

                if auto_search == 'q':
                    save_progress(i)
                    return
                elif auto_search == 'n':
                    pass  # Do nothing, just continue
                else:
                    # Check if input is a number
                    if auto_search.isdigit():
                        n = int(auto_search)
                        words = title.split()
                        if n > 0 and n < len(words):
                            search_phrase = ' '.join(words[:n])
                        else:
                            search_phrase = title
                    else:
                        search_phrase = title  # default to full title for 'y' or empty input

                    if copy_to_clipboard(search_phrase):
                        print(f"🔍 Searching for: {search_phrase}")
                        if focus_obsidian_and_search():
                            print("✅ Obsidian search triggered")
                        else:
                            print("❌ Failed to trigger Obsidian search")

            #response = input("Continue? ")
            #if response.lower() == 'q':
            #    print("Progress saved. Exiting.")
            #    save_progress(i)
            #    return
        else:
            print(f'FOUND {title}')

        # Save progress after each title
        save_progress(i + 1)
    
    print("✅ Done checking all titles!")

if __name__ == "__main__":
    main()
