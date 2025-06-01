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

def extract_titles():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    titles = []
    for row in soup.find_all('tr'):
        if 'Demo' in row.get_text():
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
        
        # Check for matching file
        if not any(title in fname for fname in os.listdir(GAMES_DIR)):
            search_term = title.replace(' ', '+')
            print(f'https://store.steampowered.com/search/?term={search_term}')
            
            # Copy title to clipboard
            if copy_to_clipboard(title):
                print(f"[{i}] Missing file for: {title} (copied to clipboard)")
            else:
                print(f"[{i}] Missing file for: {title} (clipboard copy failed)")
            
            response = input("Press Enter to continue, or 'q' to quit: ")
            if response.lower() == 'q':
                print("Progress saved. Exiting.")
                save_progress(i)
                return
        
        # Save progress after each title
        save_progress(i + 1)
    
    print("✅ Done checking all titles!")

if __name__ == "__main__":
    main()