import cv2 # use to load image, and use ORB to extract local feature
import os
import imagehash # use PHASH to extract global feature
from PIL import Image # use to convert numpy array to image object
import numpy as np
from sklearn.decomposition import PCA
import struct # use to handle float number type
import faiss # use FAISS for indexing
import random

# Create an ORB object
orb = cv2.ORB_create()

# Path to the directory containing the images
path = '''Output/_A_basket_ball_that_has_been_sprayed_with_Vanta_black'''

# Set the dimensionality of the vectors to be indexed
local_feature_dimension = 32

# Set the number of centroids to index for the IVFADC8 index
nlist = 5

# Set the number of probes to use for the IVFADC8 index
nprobe = 10

# Initialize the index
quantizer = faiss.IndexFlatL2(local_feature_dimension)
index = faiss.IndexIVFFlat(quantizer, local_feature_dimension, nlist, faiss.METRIC_L2)

nsubquantizer = 8

nbsubquantizerindex = 8

# index = faiss.IndexIVFPQ(quantizer, local_feature_dimension, nlist, nsubquantizer, nbsubquantizerindex)

# Create a dictionary to map feature indices to image file names
file_dict = {}
# Another for input
test_file_dict = {}

# Loop through all the images in the directory
for filename in os.listdir(path):
    # Check if the file is an image file
    if filename.endswith('.jpg') or filename.endswith('.png'):
        # Load the image
        img = cv2.imread(os.path.join(path, filename))
        if img is not None:
            # Convert the image to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Extract keypoints and descriptors using ORB
            keypoints, descriptors = orb.detectAndCompute(gray, None)
            # print('descriptors', type(descriptors), len(descriptors))

            # Train the index
            index.train(descriptors)
            # Add the descriptors to the index
            index.add(descriptors)

            # Add the file name to the dictionary with the index as the key
            for i in range(descriptors.shape[0]):
                file_dict[index.ntotal - descriptors.shape[0] + i] = filename

            # Add to the test dict
            test_file_dict[filename] = gray
        else:
            print(f"Skipping non-image file: {filename}")

# Optimize the index for searching
index.nprobe = nprobe

# # Search the index for the 5 nearest neighbors of a query vector
# query = np.random.rand(1, local_feature_dimension).astype('float32')
# distances, indices = index.search(query, k=5)
# print('distances', distances)
# print('indices', indices)
#
# # Map the feature indices to image file names
# most_similar_files = [file_dict[i] for i in indices[0][1:3]]
# print('most_similar_files:', most_similar_files)

# Choose a random image
query_file = random.choice(list(test_file_dict.keys()))
print('Randomly select an image to test: ', query_file)

query_img = test_file_dict[query_file]

# Extract keypoints and descriptors using ORB
query_keypoints, query_descriptors = orb.detectAndCompute(query_img, None)

# Search the index for the 5 nearest neighbors of the query vector
distances, indices = index.search(query_descriptors, k=5)

# Map the feature indices to image filenames
# most_similar_files = [list(file_dict.keys())[i] for i in indices[0][1:3]]
most_similar_files = [file_dict[i] for i in indices[0][1:3]]

# Print the filenames of the most similar images
print("Most similar images:")
for file in most_similar_files:
    print(file)