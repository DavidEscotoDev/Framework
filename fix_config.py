import re
content = open("src/coding_agent/config.py", "r").read()
# Fix escaped quotes: replace \" with "
content = content.replace('\\"', '"')
content = content.replace("\\'", "'")
with open("src/coding_agent/config.py", "w") as f:
    f.write(content)
print("Fixed config.py")
import ast
ast.parse(content)
print("Syntax OK")