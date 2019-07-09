# Network-based-Recommender

Amazon Book Recommendation with Social Network Analysis based on co-purchase data.

### Data Set Information
This project will use Amazon Meta-Data Set maintained on the Stanford Network Analysis Project (SNAP) website.
This data set is comprised of product and review metadata on 548,552 different products. The data was collected in 2006 by crawling the Amazon website. 
Data : http://snap.stanford.edu/data/amazon-meta.html

### Data Format

1. **Product ID:** numeric values (0,1,2….,548,551)
2. **ASIN:** Amazon Standard Identification Number is a 10-character alphanumeric
UID assigned by Amazon for product identification.
3. **Title:** Name of the Product.
4. **Group:** Product type, could be books, music CDs, DVDs and VHS video tapes.
5. **SalesRank:** Representation of the sales of that product compared to the others in
its category.
6. **Similar:** ASINs of co-purchased products i.e., people who buy A also buy B.
7. **Categories:** Gives the specification of the product’s category hierarchy, e.g., genre
etc. (separated by |, category id in [ ]).
8. **Reviews:** Product’s review information -
- Total Number of Reviews
- Average Rating

### Preprocessing
Before jumping into the social network analysis, some preprocess is required to read the file as Relational Data Base Management System (RDBMS) to use ASIN as the key and the others as the metadata associated with ASIN.
- **ID:** the Product ID in the dataset.
-	**ASIN:** directly from the dataset.
-	**Title:** directly from the dataset.
-	**Categories:** Concatenation of all categories of that ASIN, then preprocessed as: conversion to lowercase, then stemmed, removal of: punctuation, digits, stop words, retention of unique words.
-	**Copurchased:** List of ASINs that were present in “similar” in the dataset and have metadata associated to them.
-	**SalesRank:** directly from the dataset.
-	**TotalReviews:** directly as the total number of reviews under “reviews” in the dataset.
-	**AvgRating:** directly as the average rating under “reviews” in the dataset.

####  Filter amazonProducts Dictionary down to only Group=Book, and write filtered data to amazonBooks Dictionary.

### Graph Structure
Now we can use the co-purchase data in amazonBooks Dictionary to create the copurchaseGraph Structure as follows:

- **Nodes**: the ASINs are Nodes in the Graph.
- **Edges**: an Edge exists between two Nodes (ASINs) if the two ASINs were co-purchased.
- **Edge Weight** (based on Category Similarity): since we are attempting to make book recommendations based on co-purchase information, it would be nice to have some measure of Similarity for each ASIN (Node) pair that was co-purchased (existence of Edge between the Nodes). 
- We can then use the Similarity measure as the Edge Weight between the Node pair that was co-purchased. 
- We can potentially create such a Similarity measure by using the “Categories” data, where the Similarity measure between any two ASINs that were co-purchased is calculated as follows:
**Similarity** = (Number of words that are common between Categories of connected Nodes)/ (Total Number of words in both Categories of connected Nodes) 
- The Similarity ranges from 0 (most dissimilar) to 1 (most similar)


Also, add graph-related measures for each ASIN to the amazonBooks Dictionary:
- **DegreeCentrality**: associated with each Node (ASIN)
- **ClusteringCoeff**: associated with each Node (ASIN)

### Recommendation
Using the ASIN (0875421210), we can obtain the metadata associated with that book. 
We get the degree-1 ego network by taking the books that have been co-purchased with this one previously. 
Then we proceed to narrow it further down to the most similar books. This is done by using the island method on the degree-1 graph. 
Only the edges with threshold>= 0.5 are retained. And hence we obtain the trimmed graph which contains neighbors of the node with ASIN (0875421210).

Finally, Top Five Recommendations are then taken based on the similarity measures that are associated with the neighbors in this trimmed graph. 
In this example, The similarity metrics used is a composite measure.

