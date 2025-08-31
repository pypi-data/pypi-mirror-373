from .utilss.classes.adversarial_detector import AdversarialDetector
from .utilss.classes.adversarial_dataset import AdversarialDataset

def _create_adversarial_dataset(Z_matrix, clean_images, adversarial_images, model, labels) -> dict:
    adversarial_dataset = AdversarialDataset(model, clean_images, adversarial_images, Z_matrix, labels)
    X_train, y_train, X_test, y_test = adversarial_dataset.create_logistic_regression_dataset()
    result = {
        "X_train": X_train,
        "y_train": y_train,
        "X_test": X_test,
        "y_test": y_test
    }   
    return result

def create_logistic_regression_detector(Z_matrix, model, clean_images, adversarial_images, labels):
    adversarial_dataset = _create_adversarial_dataset(Z_matrix, clean_images, adversarial_images, model, labels)
    adversarial_detector = AdversarialDetector(adversarial_dataset)

    print("Adversarial detector trained successfully!")

    return adversarial_detector