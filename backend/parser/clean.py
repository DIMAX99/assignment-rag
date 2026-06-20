import re
from pathlib import Path

input_path = Path("data/parsed/markdown/ConceptsofBiology-WEB-19-602.md")
output_path = Path("data/parsed/markdown/ConceptsofBiology-cleaned.md")

markdown = input_path.read_text(encoding="utf-8")

# Remove <!-- image -->
markdown = re.sub(
    r"<!--\s*image\s*-->",
    "",
    markdown,
    flags=re.IGNORECASE,
)

# Remove HTML tables: <table>...</table>
markdown = re.sub(
    r"<table\b.*?</table>",
    "",
    markdown,
    flags=re.IGNORECASE | re.DOTALL,
)

# Remove Markdown pipe tables
markdown = re.sub(
    r"^[ \t]*\|.*\|[ \t]*\n^[ \t]*\|[ \t:.-]+\|[ \t:|.-]*\n(?:^[ \t]*\|.*\|[ \t]*\n?)*",
    "",
    markdown,
    flags=re.MULTILINE,
)

# Clean extra blank lines
markdown = re.sub(r"[ \t]+$", "", markdown, flags=re.MULTILINE)
markdown = re.sub(r"\n{3,}", "\n\n", markdown)

output_path.write_text(markdown.strip() + "\n", encoding="utf-8")

print("Done:", output_path)