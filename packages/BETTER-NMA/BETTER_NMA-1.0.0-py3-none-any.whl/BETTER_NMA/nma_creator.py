import tensorflow as tf
import pandas as pd
from igraph import Graph
from .utilss.enums.explanation_method import ExplanationMethod
from .utilss.classes.preprocessing.batch_predictor import BatchPredictor
from .utilss.classes.preprocessing.heap_processor import HeapProcessor
from .utilss.classes.preprocessing.graph_builder import GraphBuilder
from .utilss.classes.preprocessing.hierarchical_clustering_builder import HierarchicalClusteringBuilder
from .utilss.classes.preprocessing.z_builder import ZBuilder
from .utilss.classes.dendrogram import Dendrogram

def preprocessing(x_train, y_train, labels, model, explanation_method, top_k, min_confidence, infinity, threshold, save_connections, batch_size=32):
    try:
        X = x_train
        y = y_train
        
        graph = Graph(directed=False)
        graph.add_vertices(labels)

        edges_data = []
        batch_images = []
        true_labels = []
        original_dataset_positions = [] 
        
        predictor = BatchPredictor(model, batch_size)
        builder = GraphBuilder(explanation_method, infinity)
        count = 0
        
        for i, image in enumerate(X):
            source_label = y[i]
            batch_images.append(image)
            true_labels.append(source_label)
            original_dataset_positions.append(i)
            
            if len(batch_images) == predictor.batch_size or i == len(X) - 1:
                top_predictions_batch = predictor.get_top_predictions(
                    batch_images, labels, top_k, threshold
                )
                added_labels = []
                for j, top_predictions in enumerate(top_predictions_batch):
                    current_label = true_labels[j]
                    original_index = original_dataset_positions[j]
                    seen_labels_for_image = {current_label}
                    if len(top_predictions) == 0:
                        print("Empty predictions for image", original_index)
                        continue
                    
                    if len(top_predictions[0]) < 2:
                        print("Malformed predictions for image", original_index)
                        continue
                    
                    if top_predictions[0][2] > min_confidence:
                        filtered_predictions = top_predictions

                        if filtered_predictions[0][1] != current_label:
                            continue

                        if count < 10:
                            # print(filtered_predictions)
                            count = count + 1
                        
                        for _, pred_label, pred_prob in filtered_predictions:
                            if pred_label not in labels:
                                raise ValueError(
                                    f"Prediction label '{pred_label}' not in graph labels."
                                )
                            # Add to seen labels set for this image
                            seen_labels_for_image.add(pred_label)
                            
                            if current_label != pred_label:
                                edge_data = builder.update_graph(
                                    # graph, current_label, pred_label, pred_prob, i, dataset_class
                                    graph, current_label, pred_label, pred_prob, original_index
                                )
                                # Only append edge_data if it's not None (not a self-loop)
                                if edge_data is not None:
                                    edges_data.append(edge_data)
                                    added_labels.append(pred_label)
                    
                    # Now add infinity edges for all labels not seen in THIS image
                    if explanation_method == ExplanationMethod.DISSIMILARITY.value:
                        for label in labels:
                            # if label != current_label:
                            if label not in seen_labels_for_image:                                
                                builder.add_infinity_edges(
                                    graph, added_labels, label, current_label
                                )

                batch_images = []
                true_labels = []
                original_dataset_positions = []
        
        edges_df = None
        if save_connections:
            edges_df = pd.DataFrame(edges_data)

        heap_processor = HeapProcessor(graph, explanation_method, labels)
        clustering = HierarchicalClusteringBuilder(heap_processor, labels)
        
        z_builder = ZBuilder()
        z = z_builder.create_z_matrix_from_tree(clustering, labels)
        
        dendrogram_object = Dendrogram(z)
        dendrogram = dendrogram_object.build_tree_hierarchy(z, labels)
        
        return dendrogram_object, edges_df
    except Exception as e:
        print(f"Error while preprocessing model: {str(e)}")
