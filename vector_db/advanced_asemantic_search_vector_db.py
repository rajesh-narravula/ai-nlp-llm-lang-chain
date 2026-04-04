import pandas as pd
import pinecone
from sentence_transformers import SentenceTransformer
from sentence_transformers import SentenceTransformer
import config
from pinecone import ServerlessSpec, Pinecone


files = pd.read_csv('course_section_descriptions.csv', encoding = "ANSI")

files["unique_id"] = files["course_id"].astype(str) + '-' + files["section_id"].astype(str)

files["metadata"] = files.apply(lambda row: {
    "course_name": row["course_name"],
    "section_name": row["section_name"],
    "section_description": row["section_description"],
}, axis = 1)

model = SentenceTransformer('all-MiniLM-L6-v2')

def create_embeddings(row):
    combined_text = f'''{row["course_name"]} {row["course_technology"]}
                        {row["course_description"]} {row["section_name"]}{row["section_description"]}'''
    return model.encode(combined_text, show_progress_bar = False)


files["embedding"] = files.apply(create_embeddings, axis = 1)

pc = Pinecone(api_key=config.api_key, environment=config.environment)

index_name = "gcp-starter"
dimension = 384
metric = "cosine"

if index_name in [index.name for index in pc.list_indexes()]:
    pc.delete_index(index_name)
    print(f"{index_name} succesfully deleted.")
else:
     print(f"{index_name} not in index list.")

pc.create_index(name=index_name, 
                dimension=dimension, 
                metric=metric, 
                spec=ServerlessSpec(cloud='aws', region='us-east-1'))
index = pc.Index(index_name)

vectors_to_upsert = [(row["unique_id"], row["embedding"].tolist(), row["metadata"]) for index, row in files.iterrows()  ]

index.upsert(vectors=vectors_to_upsert)

print('Course descriptions upserted to Pinecone index.')

query = "regression in Python"
query_embedding = model.encode(query, show_progress_bar=False).tolist()

query_results = index.query(
    vector = [query_embedding],
    top_k = 12,
    include_metadata=True
)

score_threshold = 0.4

# Assuming query_results are fetched and include metadata
for match in query_results['matches']:
    if match['score'] >= score_threshold:
        course_details = match.get('metadata', {})
        course_name = course_details.get('course_name', 'N/A')
        section_name = course_details.get('section_name', 'N/A')
        section_description = course_details.get('section_description', 'No description available')
        
        print(f"Matched item ID: {match['id']}, Score: {match['score']}")
        print(f"Course: {course_name} \nSection: {section_name} \nDescription: {section_description} \n\n")


