# Naive Bayes Module

This module implements a Naive Bayes classifier for predicting whether to play golf based on weather conditions.

## Features

- Calculates probability tables for weather features including:

  - Outlook (Sunny, Overcast, Rainy)
  - Temperature (Hot, Mild, Cool)
  - Humidity (High, Normal)
  - Wind (True, False)

- Provides functions for:
  - Calculating frequency tables for each feature
  - Computing log-likelihood ratios
  - Generating random training data
  - Making predictions on new weather conditions

## Example Usage

The module can be used to:

1. Train a Naive Bayes model on weather data to predict if conditions are suitable for playing golf

2. Generate random training data or use predefined example data

3. Calculate probability tables and log-likelihood ratios for each weather feature

4. Make predictions on new weather conditions by combining the probabilities

## Input Features

The model uses the following weather features:

- **Outlook**: Sunny, Overcast, or Rainy
- **Temperature**: Hot, Mild, or Cool
- **Humidity**: High or Normal
- **Wind**: True or False

## Output

The model predicts a binary outcome:

- "Yes" - Conditions are suitable for playing golf
- "No" - Conditions are not suitable for playing golf

## Implementation Details

The implementation uses:

- Pandas for data manipulation and frequency calculations
- Log-likelihood ratios to combine probabilities
- Laplace smoothing to handle zero probabilities
- Frequency tables to store conditional probabilities
