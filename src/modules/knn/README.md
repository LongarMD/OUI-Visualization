# K-Nearest Neighbors (KNN) Algorithm

### The Steps:

1. **Look at the Data**: The algorithm has a dataset of points where we know the correct classifications (training data)
2. **Get a New Point**: When we want to classify something new (test point)
3. **Find Neighbors**: The algorithm finds the K closest points to our test point
4. **Make a Decision**: Based on those neighbors, it decides which class the new point belongs to

### Classification Methods:

This implementation offers two ways to classify:

1. **Majority Voting**

   - Simply counts the most common class among the K neighbors
   - Example: If K=3 and two neighbors are Class A and one is Class B, it chooses Class A

2. **Weighted Voting**
   - Closer neighbors have more influence than farther ones
   - Uses 1/distance as the weight
   - More sophisticated than majority voting as it considers distance

## The Interactive Visualization

This tool uses the famous Iris dataset (projected into 2D) to demonstrate KNN. You can:

- Click anywhere to place a test point
- Choose how many neighbors (K) to consider
- Select between majority or weighted voting
- See the classification result and the circle containing the K nearest neighbors
