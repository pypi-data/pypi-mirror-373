#!/usr/bin/env python
import os
import shutil

# Get the current directory (where files were generated)
project_dir = os.getcwd()

# Convert string booleans to actual booleans for reliable comparison
include_web_search = '{{ cookiecutter.include_web_search }}'.lower() == 'true'
include_ralph_commands = '{{ cookiecutter.include_ralph_commands }}'.lower() == 'true'
include_linear_integration = '{{ cookiecutter.include_linear_integration }}'.lower() == 'true'
include_agents = '{{ cookiecutter.include_agents }}'.lower() == 'true'
include_commands = '{{ cookiecutter.include_commands }}'.lower() == 'true'

# Remove files based on configuration
if not include_web_search:
    web_search_file = os.path.join(project_dir, 'agents', 'web-search-researcher.md')
    if os.path.exists(web_search_file):
        try:
            os.remove(web_search_file)
            print(f"Removed: {web_search_file}")
        except Exception as e:
            print(f"Error removing {web_search_file}: {e}")

if not include_ralph_commands:
    ralph_files = [
        os.path.join(project_dir, 'commands', 'ralph_plan.md'),
        os.path.join(project_dir, 'commands', 'ralph_impl.md'),
        os.path.join(project_dir, 'commands', 'ralph_research.md')
    ]
    for file_path in ralph_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Removed: {file_path}")
            except Exception as e:
                print(f"Error removing {file_path}: {e}")

if not include_linear_integration:
    linear_file = os.path.join(project_dir, 'commands', 'linear.md')
    if os.path.exists(linear_file):
        try:
            os.remove(linear_file)
            print(f"Removed: {linear_file}")
        except Exception as e:
            print(f"Error removing {linear_file}: {e}")

# Clean up empty directories
for root, dirs, files in os.walk(project_dir, topdown=False):
    for dir_name in dirs:
        dir_path = os.path.join(root, dir_name)
        if not os.listdir(dir_path):
            os.rmdir(dir_path)

print("Template generation complete!")