from .utilss.verbal_explanation import get_verbal_explanation
from .utilss.photos_utils import preprocess_loaded_image
from .utilss.models_utils import get_top_k_predictions

def query_image(image, model, labels, dendrogram_object, top_k=5):
    # predict image
    try:
        preprocessed_image, pil_image = preprocess_loaded_image(model, image)
        predictions = get_top_k_predictions(
            model, preprocessed_image, labels)
        top_label = predictions[0][0]  # Top label
        top_k_predictions = predictions[:top_k]

        consistency = dendrogram_object.find_name_hierarchy(
            dendrogram_object.Z_tree_format, top_label)
        
        explanation = get_verbal_explanation(consistency)
        
        return top_k_predictions, explanation
    except Exception as e:
        print("Error occurred while querying image:", e)
        return None
