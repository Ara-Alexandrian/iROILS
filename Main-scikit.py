import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tqdm import tqdm

def preprocess_data(file_path):
    # Load the spreadsheet data
    data = pd.read_excel(file_path)
    # Drop rows where '105.Narrative' is NaN
    data_cleaned = data.dropna(subset=['105.Narrative'])
    return data_cleaned

def tfidf_vectorization(data_cleaned):
    tfidf_vectorizer = TfidfVectorizer(max_df=0.85, max_features=10000, stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(data_cleaned['105.Narrative'])
    return tfidf_matrix, tfidf_vectorizer

def determine_optimal_clusters(tfidf_matrix):
    # Using the Elbow method to find the optimal number of clusters
    wcss = []
    silhouette_scores = []
    # Trying out clusters ranging from 2 to 11 (inclusive)
    for i in tqdm(range(2, 11), desc="Determining Optimal Clusters"):
        kmeans = KMeans(n_clusters=i, random_state=42)
        kmeans.fit(tfidf_matrix)
        wcss.append(kmeans.inertia_)
        silhouette_avg = silhouette_score(tfidf_matrix, kmeans.labels_)
        silhouette_scores.append(silhouette_avg)
    return wcss, silhouette_scores

def main():
    data_cleaned = preprocess_data("Events_runninglist.xlsx")
    tfidf_matrix, tfidf_vectorizer = tfidf_vectorization(data_cleaned)
    wcss, silhouette_scores = determine_optimal_clusters(tfidf_matrix)

    # Plotting results to determine optimal number of clusters
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(range(2, 11), wcss, marker='o', linestyle='--')
    plt.title('Elbow Method')
    plt.xlabel('Number of clusters')
    plt.ylabel('WCSS')

    plt.subplot(1, 2, 2)
    plt.plot(range(2, 11), silhouette_scores, marker='o', linestyle='--')
    plt.title('Silhouette Score')
    plt.xlabel('Number of clusters')
    plt.ylabel('Silhouette Score')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
