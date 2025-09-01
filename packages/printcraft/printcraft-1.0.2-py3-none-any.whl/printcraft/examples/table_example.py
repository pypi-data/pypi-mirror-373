"""
Example: Print tables using Printcraft
"""

from printcraft import ptable, export_markdown, export_html

data = [
    {"id": 1, "name": "Khan", "role": "Developer"},
    {"id": 2, "name": "Maya", "role": "Chemist"},
    {"id": 3, "name": "Jimmy", "role": "Engineer"},
]

print("Terminal table:")
ptable(data)

print("\nMarkdown table:")
print(export_markdown(data))

print("\nHTML table:")
print(export_html(data))
