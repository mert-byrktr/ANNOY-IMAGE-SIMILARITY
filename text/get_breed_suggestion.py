from sentence_transformers import SentenceTransformer, util

# Initialize the model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_breed_suggestion(breed_query, breed_list, threshold=0.7):
    """
    Given a breed query and a list of breed names, this function returns the best matching breed
    if the cosine similarity is above the threshold.
    """

    if not isinstance(breed_list, list):
        breed_list = list(breed_list)
        
    query_embedding = model.encode(breed_query, convert_to_tensor=True)
    breed_embeddings = model.encode(breed_list, convert_to_tensor=True)

    cosine_scores = util.cos_sim(query_embedding, breed_embeddings)[0]

    best_idx = cosine_scores.argmax().item()
    best_score = cosine_scores[best_idx].item()

    if best_score >= threshold:
        return breed_list[best_idx], best_score
    else:
        return None, best_score

# Example usage:
# Suppose you have a list of known breeds from your predictions.
# known_breeds = list(set(breed.lower() for breed in ['rottweiler', 'labrador', 'poodle', 'beagle']))  # Example list
# user_input = "rottwieer"  # A misspelling of 'rottweiler'

# suggested_breed, score = get_breed_suggestion(user_input.lower(), known_breeds)
# if suggested_breed:
#     print(f"Did you mean: {suggested_breed} (score: {score:.2f})?")
# else:
#     print("No suitable match found.")
