from .utilss.classes.score_calculator import ScoreCalculator

def get_lca(label1, label2, dendrogram, class_names):
    """
    Find the Lowest Common Ancestor (LCA) of two classes in a hierarchical clustering dendrogram.

    Parameters:
    - label1: Name of the first class
    - label2: Name of the second class
    - full_z: The full Z matrix from hierarchical clustering
    - class_names: List of class names corresponding to model outputs

    Returns:
    - lca: The name of the lowest common ancestor class
    """
    score_calculator = ScoreCalculator(dendrogram.Z, class_names)
    idx1 = class_names.index(label1)
    idx2 = class_names.index(label2)
    _, lca_idx = score_calculator.count_ancestors_to_lca(idx1, idx2)
    lca = dendrogram.get_node_name(lca_idx)
    return lca