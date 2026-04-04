from pinecone import Pinecone, ServerlessSpec
from datasets import load_dataset
import os
from sentence_transformers import SentenceTransformer

import config

pc = Pinecone(api_key=config.api_key, environment=config.environment)
index_name = "text"

fw = load_dataset("HuggingFaceFW/fineweb", name = "sample-10BT", split = "train", streaming = True)

model = SentenceTransformer('all-MiniLM-L6-v2')

pc.create_index(name=index_name, 
                dimension=model.get_sentence_embedding_dimension(),
                  metric="cosine", 
                  spec=ServerlessSpec(cloud='aws', region='us-east-1'))


index = pc.Index(index_name)

# Define the number of items you want to process (subset size)
subset_size = 10000  # For example, take only 10,000 items

# Iterate over the dataset and prepare data for upserting
vectors_to_upsert = []
for i, item in enumerate(fw):
    if i >= subset_size:
        break

    text = item['text']
    unique_id = str(item['id'])
    language = item['language']

    # Create an embedding for the text
    embedding = model.encode(text, show_progress_bar=False).tolist()

    # Prepare metadata
    metadata = {'language': language}

    # Append the tuple (id, embedding, metadata) to the list
    vectors_to_upsert.append((unique_id, embedding, metadata))

# Upsert data to Pinecone in batches
batch_size = 1000  # Adjust based on your environment and dataset size
for i in range(0, len(vectors_to_upsert), batch_size):
    batch = vectors_to_upsert[i:i + batch_size]
    index.upsert(vectors=batch)

print("Subset of data upserted to Pinecone index.")