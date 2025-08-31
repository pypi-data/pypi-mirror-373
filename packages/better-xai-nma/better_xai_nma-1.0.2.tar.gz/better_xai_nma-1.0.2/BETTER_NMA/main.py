import tempfile
import os
from .nma_creator import preprocessing
from .plot import plot, plot_sub_dendrogram
from .train_adversarial_detector import create_logistic_regression_detector
from .utilss.classes.whitebox_testing import WhiteBoxTesting
from .detect_attack import detect_adversarial_image
from .query_image import query_image
from .utilss.verbal_explanation import get_verbal_explanation
from .white_box_testing import analyze_white_box_results, get_white_box_analysis
from .adversarial_score import get_adversarial_score
from .find_lca import get_lca

class NMA:
    def __init__(self, x_train, y_train, labels, model, explanation_method, top_k=4, min_confidence=0.8, infinity=None, threshold=1e-6, save_connections=False, batch_size=32):
        """
        Initializes the NMA object with training data, model, and parameters.

        Inputs:
        - x_train: Training images (e.g., NumPy array).
        - y_train: Training labels (e.g., list or array).
        - labels: List of class labels (e.g., ['cat', 'dog']).
        - model: Pre-trained model for predictions.
        - explanation_method: Method for generating explanations.
        - top_k: Number of top predictions to consider (default: 4).
        - min_confidence: Minimum confidence threshold (default: 0.8).
        - infinity: Value for infinity in calculations, usually the labels count (default: None).
        - threshold: Threshold for clustering, depends on the model (default: 1e-6).
        - save_connections: Whether to save edges dataframe, use True for white box testing (default: False).
        - batch_size: Batch size for processing (default: 32).

        Outputs: None (initializes the object).

        Explanation: Sets up the dendrogram (visual explanation) and edges dataframe using preprocessing.
        """
        self.model = model
        self.explanation_method = explanation_method
        self.top_k = top_k
        self.labels = labels
        self.min_confidence = min_confidence
        self.infinity = infinity
        self.threshold = threshold
        self.save_connections = save_connections
        self.batch_size = batch_size
        self.labels = labels
        self.detector = None

        self.dendrogram_object, self.edges_df = preprocessing(x_train, y_train, labels, model, explanation_method, top_k, min_confidence, infinity, threshold, save_connections, batch_size)
        print("NMA initialized")

    ## plot functions: ##

    def plot(self, sub_labels=None, title="Sub Dendrogram", figsize=(12, 8), **kwargs):
        """
        Plots the dendrogram.

        Inputs:
        - sub_labels (optional, if not defined, uses all labels): List of labels to highlight (e.g., ['cat', 'dog']).
        - title (optional): Plot title (default: "Sub Dendrogram").
        - figsize (optional): Figure size (default: (12, 8)).
        - **kwargs: Additional arguments for plotting.

        Outputs: None (displays plot).

        Explanation: Visualizes the full dendrogram or highlights sub-labels. includes json representation of the dendrogram.
        """
        plot(self, sub_labels, title=title, figsize=figsize, **kwargs)

    def plot_sub_dendrogram(self, sub_labels, title="Sub Dendrogram", figsize=(12, 8)):
        """
        Plots a sub-dendrogram for specific labels.

        Inputs:
        - sub_labels: List of labels to include (e.g., ['apple', 'banana']).
        - title (optional): Plot title (default: "Sub Dendrogram").
        - figsize (optional): Figure size (default: (12, 8)).

        Outputs: None (displays plot).

        Explanation: Renders a subset of the dendrogram based on provided labels.
        """
        plot_sub_dendrogram(self.dendrogram_object.Z, self.labels, sub_labels, title=title, figsize=figsize)

    ## white box testing functions: ##

    def white_box_testing(self, source_labels, target_labels, analyze_results=False, x_train=None, encode_images=True):
        """
        Performs white-box testing to find problematic images.

        Inputs:
        - source_labels: List of source labels (e.g., ['cat']).
        - target_labels: List of target labels (e.g., ['dog']).
        - analyze_results (optional): Whether to analyze results (default: False).
        - x_train (optional): Training images for analysis.
        - encode_images (optional): Whether to encode images (default: True).

        Outputs: Dictionary of problematic images or analyzed results.

        Explanation: Finds images that could be misclassified using edges dataframe.
        """
        if self.edges_df is None:
            raise ValueError("White box testing requires edges_df. Initialize NMA with save_connections=True")

        whitebox = WhiteBoxTesting(self.model.name if hasattr(self.model, 'name') else "model")
        problematic_imgs_dict = whitebox.find_problematic_images(
            source_labels, target_labels, self.edges_df, self.explanation_method)

        if analyze_results:
            return analyze_white_box_results(problematic_imgs_dict, x_train, encode_images)

        return problematic_imgs_dict

    def get_white_box_analysis(self, source_labels, target_labels, x_train=None):
        if self.edges_df is None:
            raise ValueError("White box testing requires edges_df. Initialize NMA with save_connections=True")


        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
            self.edges_df.to_csv(temp_path, index=False)

        try:
            results = get_white_box_analysis(
                edges_df_path=temp_path,
                model_filename=self.model.name if hasattr(self.model, 'name') else "model",
                dataset_str=str(self.explanation_method),
                source_labels=source_labels,
                target_labels=target_labels,
                x_train=x_train
            )
            return results
        finally:
            os.unlink(temp_path)

    ## adversarial detection functions: ##

    def train_adversarial_detector(self, authentic_images, attacked_images):
        """
        Trains an adversarial detector.

        Inputs:
        - authentic_images: Array of clean images.
        - attacked_images: Array of adversarial images.

        Outputs: Trained detector model.

        Explanation: Trains a logistic regression detector using dendrogram data.
        """
        if self.dendrogram_object is None:
            raise ValueError("NMA must be initialized with dendrogram data for adversarial detection")

        self.detector = create_logistic_regression_detector(
            self.dendrogram_object.Z,
            self.model,
            authentic_images,
            attacked_images,
            self.labels
        )
        return self.detector

    def detect_attack(self, image, plot_result=False):
        """
        Detects if an image is adversarial.

        Inputs:
        - image: Image to analyze.
        - plot_result (optional): Whether to plot results (default: False).

        Outputs: Detection result (e.g., boolean and scores).

        Explanation: Uses trained detector to check for adversarial attacks.
        """
        if self.detector is None:
            raise ValueError("Adversarial detector not trained. Call train_adversarial_detector first.")

        return detect_adversarial_image(
            self.model,
            image,
            self.detector,
            self.dendrogram_object.Z,
            self.labels,
            plot_result=plot_result
        )
    
    def find_lca(self, label1, label2):
        """
        Finds the lowest common ancestor of two labels.

        Inputs:
        - label1: First label (e.g., 'cat').
        - label2: Second label (e.g., 'dog').

        Outputs: LCA cluster or label.

        Explanation: Determines the LCA in the dendrogram hierarchy.
        """
        lca = get_lca(label1, label2, self.dendrogram_object, self.labels)
        return lca

    def adversarial_score(self, image, top_k=5):
        """
        Computes adversarial score for an image.

        Inputs:
        - image: Image to score.
        - top_k (optional): Number of top predictions (default: 5).

        Outputs: Adversarial score.

        Explanation: Calculates score based on predictions and dendrogram.
        """
        score = get_adversarial_score(image, self.model, self.dendrogram_object.Z, self.labels, top_k=top_k)
        return score

    ## query and explanation functions: ##

    def query_image(self, image, top_k=5):
        """
        Queries the model for predictions and explanations.

        Inputs:
        - image: Image to query.
        - top_k (optional): Number of top predictions (default: 5).

        Outputs: Tuple of predictions and explanations.

        Explanation: Predicts and explains using dendrogram and verbal explanation of the dendrogram.
        """
        if self.dendrogram_object is None:
            raise ValueError("NMA must be initialized with dendrogram data to query images")
        
        if self.labels is None or len(self.labels) == 0:
            raise ValueError("NMA must be initialized with labels to query images")
        
        if self.model is None:
            raise ValueError("NMA must be initialized with a model to query images")

        return query_image(image, self.model, self.labels, self.dendrogram_object, top_k=top_k)

    def verbal_explanation(self, image):
        """
        Generates a verbal explanation for an image.

        Inputs:
        - image: Image to explain.

        Outputs: Verbal explanation.

        Explanation: Calls query_image and returns the explanation.
        """
        if self.dendrogram_object is None:
            raise ValueError("NMA must be initialized with dendrogram data to query images")
        
        if self.labels is None or len(self.labels) == 0:
            raise ValueError("NMA must be initialized with labels to query images")
        
        if self.model is None:
            raise ValueError("NMA must be initialized with a model to query images")
        
        result = self.query_image(image)
        if result is None:
            return None
        predictions, explanation = result
        return explanation
    
    def change_cluster_name(self, cluster_id, new_name):
        """
        Renames a cluster in the dendrogram.

        Inputs:
        - cluster_id: ID of the cluster to rename.
        - new_name: New name for the cluster.

        Outputs: None (prints success or raises error).

        Explanation: Updates the cluster name if valid.
        """
        if self.dendrogram_object is None:
            raise ValueError("NMA must be initialized with dendrogram data to change cluster names")

        result = self.dendrogram_object.rename_cluster(cluster_id, new_name)
        if not result:
            raise ValueError(f"Failed to rename cluster: {cluster_id}")
        
        print(f"Cluster {cluster_id} renamed to {new_name}")
