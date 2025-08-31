
---

# NMA – Near Misses Analysis

NMA (**Near Misses Analysis**) is a Python package for analyzing machine learning models through **dendrogram-based hierarchical clustering**, **white-box testing**, and **adversarial attack detection**.

It provides visualization, explanation, and diagnostic tools to help developers and researchers understand their models’ decision boundaries, identify vulnerabilities, and detect adversarial inputs.

---

## ✨ Features

* 📊 **Dendrogram construction & visualization**

  * Build hierarchical trees from model predictions.
  * Plot full dendrograms or **sub-dendrograms** for specific labels.

* 🧪 **White-box testing**

  * Identify problematic training samples likely to cause misclassification.
  * Run structured analysis across source/target label pairs.

* 🛡 **Adversarial attack detection**

  * Train a logistic regression adversarial detector.
  * Detect adversarial images and compute adversarial scores.

* 🔎 **Model querying & explanations**

  * Query images for predictions with hierarchical context.
  * Generate **verbal explanations** of model predictions.

* 🧩 **Cluster analysis tools**

  * Find lowest common ancestors (LCA) in the dendrogram.
  * Rename clusters for more meaningful interpretation.

---

## 📦 Installation

```bash
pip install BETTER_NMA
```

---

## 🚀 Quickstart

```python
from BETTER_NMA import NMA
import numpy as np

# Example data (replace with your dataset/model)
x_train = np.random.rand(100, 32, 32, 3)
y_train = np.random.randint(0, 2, size=100)
labels = ["cat", "dog"]

# Your pre-trained model (e.g., Keras, PyTorch wrapper with predict)
model = my_model  

# Initialize NMA
nma = NMA(
    x_train=x_train,
    y_train=y_train,
    labels=labels,
    model=model,
    explanation_method="similarity", 
    save_connections=True
)

# Plot dendrogram
nma.plot(title="Model Decision Hierarchy")

# Run white-box testing
issues = nma.white_box_testing(["cat"], ["dog"], analyze_results=True)

# Train adversarial detector
nma.train_adversarial_detector(authentic_images, adversarial_images)

# Detect if a new image is adversarial
result = nma.detect_attack(test_image)

# Get verbal explanation of an image
explanation = nma.verbal_explanation(test_image)
print(explanation)
```

---

## 📚 API Overview

### Dendrogram & Visualization

* `plot(sub_labels=None, ...)` – plot full or partial dendrogram.
* `plot_sub_dendrogram(sub_labels, ...)` – zoom into specific classes.

### White-box Testing

* `white_box_testing(source_labels, target_labels, ...)` – find problematic images.
* `get_white_box_analysis(source_labels, target_labels, ...)` – detailed analysis.

### Adversarial Detection

* `train_adversarial_detector(authentic_images, attacked_images)` – train detector.
* `detect_attack(image, plot_result=False)` – detect adversarial samples.
* `adversarial_score(image, top_k=5)` – compute adversarial score.

### Query & Explanation

* `query_image(image, top_k=5)` – get predictions & explanation.
* `verbal_explanation(image)` – generate natural language explanation.

### Cluster Analysis

* `find_lca(label1, label2)` – lowest common ancestor.
* `change_cluster_name(cluster_id, new_name)` – rename clusters.

---

## 🛠 Requirements

* Python ≥ 3.8
* NumPy, Pandas, Matplotlib, Scikit-learn
* (Optional) PyTorch / TensorFlow for model support

---

## 📖 Use Cases

* **Research** – interpret model predictions via hierarchical clustering.
* **Robustness testing** – identify adversarial vulnerabilities.
* **Explainability** – provide visual + verbal explanations.
* **Debugging** – detect mislabeled or problematic training samples.

---

## 📜 License

MIT License – free to use and modify.

---

