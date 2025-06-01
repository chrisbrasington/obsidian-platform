import os
import yaml
import json
import sys

# Load config.json for vault path
def load_config():
    config_path = "config.json"
    if not os.path.exists(config_path):
        print(f"Config file '{config_path}' not found.")
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error parsing config.json: {e}")
            sys.exit(1)
    if "vault_path" not in config:
        print("Config file missing 'vault_path' key.")
        sys.exit(1)
    return config["vault_path"]

# Load platforms dict number => platform string
platforms = {}

def load_platforms():
    return {}

def save_platforms():
    pass

def print_platforms():
    print("Known platforms:")
    for num, plat in sorted(platforms.items()):
        print(f"{num}. {plat}")

def get_platform_choice():
    while True:
        inp = input("Enter platform number, new platform name, or 'q' to quit: ").strip()
        if inp.lower() in ("q", "quit"):
            print("Exiting program.")
            sys.exit(0)
        if inp.isdigit():
            num = int(inp)
            if num in platforms:
                return platforms[num]
            else:
                print(f"No platform for number {num}. Please try again.")
        else:
            if inp == "":
                print("Please enter something.")
                continue
            # Check if already exists (case insensitive)
            for plat in platforms.values():
                if plat.lower() == inp.lower():
                    print(f"Platform '{plat}' already in the list, using that.")
                    return plat
            # Add new platform
            new_num = max(platforms.keys(), default=0) + 1
            platforms[new_num] = inp
            print(f"Added new platform '{inp}' as {new_num}")
            return inp

def parse_frontmatter(lines):
    if not (lines and lines[0].strip() == "---"):
        return None, None
    end_index = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_index = i
            break
    if end_index is None:
        return None, None
    frontmatter_str = "\n".join(lines[1:end_index])
    try:
        data = yaml.safe_load(frontmatter_str) or {}
    except Exception as e:
        print(f"Error parsing YAML: {e}")
        return None, None
    return data, end_index

def write_frontmatter(file_path, data, rest_of_file):
    frontmatter = "---\n" + yaml.dump(data, sort_keys=False) + "---\n"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(frontmatter)
        f.writelines(rest_of_file)

def main():
    global platforms
    base_dir = load_config()
    platforms = load_platforms()

    for root, dirs, files in os.walk(base_dir):
        for filename in files:
            if not filename.endswith(".md"):
                continue
            full_path = os.path.join(root, filename)
            print(f"Processing file: {full_path}")

            with open(full_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            frontmatter, end_idx = parse_frontmatter(lines)
            if frontmatter is None:
                print("No frontmatter or failed to parse, skipping.")
                continue

            if frontmatter.get("dataSource") == "SteamAPI":
                print("dataSource SteamAPI detected, skipping platform set.")
                continue

            current_platform = frontmatter.get("platform")

            if current_platform and current_platform not in platforms.values():
                new_num = max(platforms.keys(), default=0) + 1
                platforms[new_num] = current_platform
                print(f"Detected new platform '{current_platform}' in file, added as {new_num}. Skipping file.")
                continue

            if current_platform:
                print(f"Platform already set to '{current_platform}', skipping file.")
                continue

            print_platforms()
            new_platform = get_platform_choice()
            frontmatter["platform"] = new_platform

            rest_of_file = lines[end_idx+1:]
            write_frontmatter(full_path, frontmatter, rest_of_file)
            print(f"Platform '{new_platform}' set for {filename}\n")

    save_platforms()

if __name__ == "__main__":
    main()
