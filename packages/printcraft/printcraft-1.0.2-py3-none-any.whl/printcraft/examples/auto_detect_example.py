"""
Example: Auto-detect and print using pcraft
"""

from printcraft import pcraft

# Dictionary
data_dict = {"name": "Khan", "age": 23}
pcraft(data_dict)

# List of dicts -> table
data_list = [{"id": 1, "name": "Khan"}, {"id": 2, "name": "Maya"}]
pcraft(data_list)

# List -> formatted list
data_simple_list = [1, 2, 3, 4, 5]
pcraft(data_simple_list)

# Tuple
data_tuple = (10, 20, 30)
pcraft(data_tuple)

# Large dict -> preview
large_dict = {f"key{i}": i for i in range(20)}
pcraft(large_dict)
