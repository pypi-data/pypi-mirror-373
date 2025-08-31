from ...enums.explanation_method import ExplanationMethod

class GraphBuilder:
    def __init__(self, graph_type, infinity):
        self.graph_type = graph_type
        self.infinity = infinity
        
    def create_edge_weight(self, pred_prob):
        if self.graph_type == ExplanationMethod.DISSIMILARITY.value:
            return 1 - pred_prob
        elif self.graph_type == ExplanationMethod.COUNT.value:
            return 1
        return pred_prob
    
    def update_graph(self, graph, source_label, target_label, probability, image_id):
        if source_label == target_label:
            return None
 
        weight = self.create_edge_weight(probability)

        if graph.are_adjacent(source_label, target_label):
            edge_id = graph.get_eid(source_label, target_label)
            graph.es[edge_id]["weight"] += weight 
        else:
            graph.add_edge(source_label, target_label, weight=weight)
        
        edge_data = {
            "image_id": image_id,
            "source": source_label,
            "target": target_label,
            "target_probability": probability,
        }
        
        return edge_data
    
    
    def add_infinity_edges(self, graph, infinity_edges_labels, label, source_label):
        if label == source_label:
            return

        if label not in infinity_edges_labels:
            if graph.are_adjacent(source_label, label):
                edge_id = graph.get_eid(source_label, label)
                graph.es[edge_id]["weight"] += self.infinity
            else:
                graph.add_edge(source_label, label, weight=self.infinity) 
