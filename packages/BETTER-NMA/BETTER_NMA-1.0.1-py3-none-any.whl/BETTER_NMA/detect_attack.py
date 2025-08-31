from .utilss.classes.score_calculator import ScoreCalculator
from .utilss.photos_utils import preprocess_loaded_image
from .utilss.models_utils import get_top_k_predictions
import matplotlib.pyplot as plt

def plot_detection_result(detection_result, figsize=(12, 8), top_k=5):
    """
    Plot the detection result with image, predictions, and detection status.
    
    Parameters:
    - detection_result: Dictionary with keys 'image', 'predictions', 'result', 'probability'
    - figsize: Tuple for figure size
    - top_k: Number of top predictions to display
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Plot the image
    ax1.imshow(detection_result['image'])
    ax1.axis('off')
    ax1.set_title('Input Image', fontsize=14, fontweight='bold')
    
    # Plot predictions and detection result
    predictions = detection_result['predictions'][:top_k]
    
    # Handle both tuple and dictionary formats
    if predictions and isinstance(predictions[0], tuple):
        # If predictions are tuples (class_name, probability)
        classes = [pred[0] for pred in predictions]
        probabilities = [pred[1] for pred in predictions]
    else:
        # If predictions are dictionaries
        classes = [pred['class'] for pred in predictions]
        probabilities = [pred['probability'] for pred in predictions]
    
    # Create bar plot for predictions
    bars = ax2.barh(range(len(classes)), probabilities, color='skyblue')
    ax2.set_yticks(range(len(classes)))
    ax2.set_yticklabels(classes, fontsize=10)
    ax2.set_xlabel('Probability', fontsize=12)
    ax2.set_title(f'Top {top_k} Predictions', fontsize=14, fontweight='bold')
    ax2.set_xlim(0, 1)
    
    # Add probability values on bars
    for i, (bar, prob) in enumerate(zip(bars, probabilities)):
        ax2.text(prob + 0.01, i, f'{prob:.3f}', 
                va='center', fontsize=9)
    
    # Add detection result as text
    detection_status = detection_result['result']
    detection_prob = detection_result['probability']
    
    # Color based on detection result
    status_color = 'red' if detection_status == 'Adversarial' else 'green'
    
    # Add detection result text box
    textstr = f'Detection: {detection_status}\nConfidence: {detection_prob:.3f}'
    props = dict(boxstyle='round', facecolor=status_color, alpha=0.3)
    ax2.text(0.02, 0.98, textstr, transform=ax2.transAxes, fontsize=12,
            verticalalignment='top', bbox=props, fontweight='bold')
    
    plt.tight_layout()
    plt.show()

def detect_adversarial_image(model, image, detector, Z_full, labels, plot_result=False):
    """
    Detect if an image is adversarial using the trained logistic regression detector.
    
    Parameters:
    - model: The original model being attacked
    - detector: The trained logistic regression detector
    - Z_full: Hierarchical clustering data
    - labels: List of class names
    - image: The input image to check
    - plot_result: Whether to plot the detection result (default: False)
    
    Returns:
    - Dictionary with 'image', 'predictions', 'result', and 'probability'
    """
        
    image_preprocessed, pil_image = preprocess_loaded_image(model, image)
    score_calculator = ScoreCalculator(Z_full, labels)
    
    # Get predictions from the original model
    preds = model.predict(image_preprocessed, verbose=0)
    
    # Calculate the adversarial score (or other features)
    score = score_calculator.calculate_adversarial_score(preds[0])
    
    # Use the detector to classify the image
    feature = [[score]]  # Wrap the score in a 2D array
    label = detector.predict(feature)[0]  # Predict the label (0 = clean, 1 = adversarial)
    proba = detector.predict_proba(feature)[0][1]  # Probability of being adversarial
    detection_result = 'Adversarial' if label == 1 else 'Clean'

    # Get top predictions for the image
    image_predictions = get_top_k_predictions(model, image_preprocessed, labels)
    
    result = {
        "image": pil_image,
        "predictions": image_predictions,
        "result": detection_result,
        "probability": proba
    }
    
    if plot_result:
        plot_detection_result(result)
    
    return result