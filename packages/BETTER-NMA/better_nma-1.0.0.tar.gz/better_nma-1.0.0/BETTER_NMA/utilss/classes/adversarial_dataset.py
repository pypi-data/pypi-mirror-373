from sklearn.model_selection import train_test_split
import numpy as np
from .score_calculator import ScoreCalculator

class AdversarialDataset:
    def __init__(self, model, clear_images, adversarial_images, Z_full, labels):
        self.model = model
        self.clear_images = clear_images
        self.adversarial_images = adversarial_images
        self.score_calculator = ScoreCalculator(Z_full=Z_full, class_names=labels)

    def create_logistic_regression_dataset(self):
        scores = []
        labels = []

        print("getting preprocess function...")

        try:
            for image in self.clear_images[:50]:
                # Add batch dimension for model prediction
                image_batch = np.expand_dims(image, axis=0)
                score = self.score_calculator.calculate_adversarial_score(self.model.predict(image_batch))
                scores.append(score)
                labels.append(0)
        except Exception as e:
            print(f"Error processing clean image: {e}")
        
        # Generate features for PGD attacks
        print("Generating attack features...")
        try:
            for adv_image in self.adversarial_images[:50]:
                # Add batch dimension for model prediction
                adv_image_batch = np.expand_dims(adv_image, axis=0)
                score = self.score_calculator.calculate_adversarial_score(self.model.predict(adv_image_batch))
                scores.append(score)
                labels.append(1)
        except Exception as e:
            print(f"Error processing PGD attack on image: {e}")

        print("labels:", labels)
        print("scores:", scores)
        
        # Convert to numpy arrays
        X = np.array(scores)
        y = np.array(labels)

        # Reshape X to ensure it is 2D
        if len(X.shape) == 1:
            X = X.reshape(-1, 1)
        
        # Split into training and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=42
        )
        
        print(f"Training data shape: {X_train.shape}")
        print(f"Clean samples: {sum(y_train == 0)}, Adversarial samples: {sum(y_train == 1)}")
        print(f"Test data shape: {X_test.shape}")
        print(f"Clean samples: {sum(y_test == 0)}, Adversarial samples: {sum(y_test == 1)}")

        return X_train, y_train, X_test, y_test
