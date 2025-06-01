import os
import yaml

folder_path = "/home/chris/obsidian/brain/03 - Resources/Video Games"
changed_files = []

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not content.strip().startswith('---'):
        return  # No YAML frontmatter

    parts = content.split('---')
    if len(parts) < 3:
        return  # Invalid or no YAML frontmatter

    yaml_part = parts[1]
    body = '---'.join(parts[2:])

    try:
        data = yaml.safe_load(yaml_part)
    except yaml.YAMLError:
        return  # Invalid YAML

    if not isinstance(data, dict) or 'tags' not in data:
        return

    tags = data['tags']
    if not isinstance(tags, list):
        return

    if 'mediaDB/wiki' in tags and 'mediaDB/game' not in tags:
        tags.append('mediaDB/game')
        data['tags'] = tags
        new_yaml = yaml.dump(data, sort_keys=False, allow_unicode=True).strip()
        new_content = f"---\n{new_yaml}\n---\n{body.lstrip()}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        changed_files.append(filepath)

for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith('.md'):
            process_file(os.path.join(root, file))

print("Changed files:")
for file in changed_files:
    print(file)

