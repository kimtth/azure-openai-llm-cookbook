import os

root_dir = os.getcwd()  # or specify your root directory

for first_level in os.listdir(root_dir):
    first_level_path = os.path.join(root_dir, first_level)
    if os.path.isdir(first_level_path) and '.git' not in first_level_path:
        for second_level in os.listdir(first_level_path):
            second_level_path = os.path.join(first_level_path, second_level)
            if os.path.isdir(second_level_path):
                readme_file = os.path.join(second_level_path, "README.md")
                readme_app_file = os.path.join(second_level_path, "README.app.md")
                if os.path.exists(readme_app_file):
                    print(f"File already exists: {readme_app_file}")
                    continue
                if os.path.exists(readme_file):
                    new_file = os.path.join(second_level_path, "README.app.md")
                    if os.path.isfile(readme_file):
                        os.rename(readme_file, new_file)
                        print(f"Renamed: {new_file}")