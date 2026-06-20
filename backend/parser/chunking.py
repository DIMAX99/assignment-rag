from pathlib import Path
import json
import time
import sys

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.db import get_vector_store


input_path = Path("data/parsed/markdown/ConceptsofBiology-cleaned.md")

jsonl_output_path = Path("data/parsed/chunks/chunks_1.jsonl")
md_output_path = Path("data/parsed/chunks/chunks_preview_1.md")

jsonl_output_path.parent.mkdir(parents=True, exist_ok=True)

markdown = input_path.read_text(encoding="utf-8")


# Step 1: Split markdown by headings
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=True,
)

section_docs = markdown_splitter.split_text(markdown)

print("Section docs:", len(section_docs))


# Step 2: Recursively chunk large sections
recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)

raw_chunks = recursive_splitter.split_documents(section_docs)

print("Raw chunks:", len(raw_chunks))


# Step 3: Clean chunks, enrich with headers, add metadata
chunks = []

for chunk in raw_chunks:
    if len(chunk.page_content.strip()) < 30:
        continue

    context_headers = []

    if "Header 1" in chunk.metadata:
        context_headers.append(f"# {chunk.metadata['Header 1']}")

    if "Header 2" in chunk.metadata:
        context_headers.append(f"## {chunk.metadata['Header 2']}")

    if "Header 3" in chunk.metadata:
        context_headers.append(f"### {chunk.metadata['Header 3']}")

    header_string = "\n".join(context_headers)

    enriched_content = (
        f"{header_string}\n\n{chunk.page_content}"
        if header_string
        else chunk.page_content
    )

    chunk.metadata["chunk_id"] = len(chunks)
    chunk.metadata["source"] = str(input_path)
    chunk.metadata["chunk_size_chars"] = len(enriched_content)

    chunk.page_content = enriched_content
    chunks.append(chunk)

print("Final chunks:", len(chunks))


# Step 4: Save chunks as JSONL for viewing/debugging
with jsonl_output_path.open("w", encoding="utf-8") as f:
    for chunk in chunks:
        row = {
            "chunk_id": chunk.metadata["chunk_id"],
            "content": chunk.page_content,
            "metadata": chunk.metadata,
        }

        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print("Saved JSONL:", jsonl_output_path)


# Step 5: Save readable markdown preview
with md_output_path.open("w", encoding="utf-8") as f:
    for chunk in chunks:
        f.write("\n\n---\n\n")
        f.write(f"# Chunk {chunk.metadata['chunk_id']}\n\n")

        f.write("Metadata:\n\n")
        f.write("```json\n")
        f.write(json.dumps(chunk.metadata, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")

        f.write(chunk.page_content)

print("Saved Markdown preview:", md_output_path)


# Step 6: Store chunks in Supabase PGVector
# This automatically creates embeddings using your get_google_embedding()
vector_store = get_vector_store()

BATCH_SIZE = 10
SLEEP_SECONDS = 8

for start in range(1900, len(chunks), BATCH_SIZE):
    end = min(start + BATCH_SIZE, len(chunks))
    batch = chunks[start:end]

    ids = [
        f"concepts_biology_chunk_{chunk.metadata['chunk_id']}"
        for chunk in batch
    ]

    print(f"Storing chunks {start} to {end - 1}")

    vector_store.add_documents(
        documents=batch,
        ids=ids,
    )

    time.sleep(SLEEP_SECONDS)

print("All chunks embedded and stored in Supabase PGVector")


# # Step 7: Quick test retrieval
# query = "What is overharvesting?"

# results = vector_store.similarity_search(query, k=3)

# print("\nTest search results:")
# for i, doc in enumerate(results):
#     print("\n====================")
#     print("Result:", i + 1)
#     print("Metadata:", doc.metadata)
#     print(doc.page_content[:500])