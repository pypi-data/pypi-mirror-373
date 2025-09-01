"""
Example: Pretty-print JSON using Printcraft
"""

from printcraft import pjson, pcraft

# Python dict
data_dict = {"name": "Khan", "age": 23, "skills": ["Python", "C++", "AI"]}
print("Pretty-print dict as JSON:")
pjson(data_dict)

# JSON string
data_json = '{"company": "OpenAI", "employees": 1000, "remote": true}'
print("\nPretty-print JSON string:")
pjson(data_json)

# Using auto-detection
print("\nUsing pcraft auto-detection:")
pcraft(data_dict)
pcraft(data_json)
