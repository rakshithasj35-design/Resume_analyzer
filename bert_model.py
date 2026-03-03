from sentence_transformers import SentenceTransformer, util
import torch

# Load pretrained BERT model
model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_similarity(resume_text, job_description):
    # Convert text into embeddings
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_description, convert_to_tensor=True)

    # Compute cosine similarity
    similarity_score = util.pytorch_cos_sim(resume_embedding, job_embedding)

    return float(similarity_score[0][0])