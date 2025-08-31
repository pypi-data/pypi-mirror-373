import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from .utilss.classes.whitebox_testing import WhiteBoxTesting
from .utilss.classes.edges_dataframe import EdgesDataframe
from .utilss.photos_utils import encode_image_to_base64

def visualize_problematic_images(x_train, problematic_imgs_dict, max_display=5):
    count = 0
    for image_id, matches in problematic_imgs_dict.items():
        if count >= max_display:
            break

        image = x_train[image_id]

        plt.figure(figsize=(8, 6))
        plt.imshow(image.astype("uint8"))
        plt.title(f"Image ID: {image_id}")
        plt.axis('off')
        plt.show()

        print(f"Image ID: {image_id}")
        print("Matches:")
        for match in matches:
            print(f"  {match[0]} -> {match[1]}: {match[2]:.8f}")
        print("-" * 30)

        count += 1

def analyze_white_box_results(problematic_imgs_dict, x_train=None, encode_images=True):
    results = []

    for image_id, matches in problematic_imgs_dict.items():
        result_item = {
            "image_id": str(image_id),
            "matches": matches,
            "num_matches": len(matches)
        }

        if encode_images and x_train is not None and isinstance(image_id, int) and image_id < len(x_train):
            img = x_train[image_id]
            if img.max() <= 1.0:
                img = (img * 255).astype(np.uint8)

            result_item["image"] = encode_image_to_base64(img)

        results.append(result_item)

    return results

def get_white_box_analysis(edges_df_path, model_filename, dataset_str, source_labels, target_labels, x_train=None, get_image_by_id_func=None):
    if not edges_df_path or not model_filename or not source_labels or not target_labels:
        raise ValueError("Missing required parameters")

    edges_data = EdgesDataframe(model_filename, edges_df_path)
    edges_data.load_dataframe()
    df = edges_data.get_dataframe()

    whitebox_testing = WhiteBoxTesting(model_filename)
    problematic_imgs_dict = whitebox_testing.find_problematic_images(
        source_labels, target_labels, df, dataset_str)

    imgs_list = []

    for image_id, matches in problematic_imgs_dict.items():
        try:
            if x_train is not None and isinstance(image_id, int) and image_id < len(x_train):
                img = x_train[image_id]
                image_filename = str(image_id)
            elif get_image_by_id_func is not None:
                img, image_filename = get_image_by_id_func(image_id, dataset_str)
            else:
                print(f"Cannot retrieve image {image_id}: no data source provided")
                continue

            if img.max() <= 1.0:
                img = (img * 255).astype(np.uint8)

            original_image_base64 = encode_image_to_base64(img)

            imgs_list.append({
                "image": original_image_base64,
                "image_id": image_filename,
                "matches": matches,
            })
        except Exception as e:
            print(f"Error processing image {image_id}: {str(e)}")

    return imgs_list

def save_white_box_results(results, output_path):
    import json
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to: {output_path}")

def load_white_box_results(input_path):
    import json
    with open(input_path, 'r') as f:
        return json.load(f)