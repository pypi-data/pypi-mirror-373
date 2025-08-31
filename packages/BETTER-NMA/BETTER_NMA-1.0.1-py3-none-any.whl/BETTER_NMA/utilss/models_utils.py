import numpy as np

def get_top_k_predictions(model, image, class_names, top_k=5):
    # Get predictions from the model
    predictions = model.predict(image)

    # Flatten the predictions array if it's 2D (e.g., shape (1, num_classes))
    if len(predictions.shape) == 2:
        predictions = predictions[0]  # Extract the first (and only) batch

    # Get the indices of the top-k predictions
    top_indices = np.argsort(predictions)[-top_k:][::-1]

    # Get the top-k probabilities and corresponding labels
    top_probs = predictions[top_indices]
    top_labels = [class_names[i] for i in top_indices]

    return list(zip(top_labels, top_probs))