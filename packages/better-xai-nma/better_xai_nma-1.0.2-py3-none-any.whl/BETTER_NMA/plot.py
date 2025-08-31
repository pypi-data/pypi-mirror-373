from re import sub
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as sch
import numpy as np
from .utilss.classes.dendrogram import Dendrogram


def extract_sub_dendrogram(Z_full, labels, selected_labels):
    """Extract a sub-dendrogram from the full Z matrix for only the selected labels."""
    original_label_to_idx = {name: i for i, name in enumerate(labels)}

    for label in selected_labels:
        if label not in original_label_to_idx:
            raise ValueError(
                f"Label '{label}' not found in original class names")

    selected_indices = [original_label_to_idx[label]
                        for label in selected_labels]
    Z_sub = []
    selected_indices_set = set(selected_indices)
    cluster_size = {i: 1 for i in range(len(selected_indices))}

    new_positions = {original: new for new,
                     original in enumerate(selected_indices)}
    active_nodes = selected_indices.copy()
    next_id = len(selected_indices)

    for i, (left, right, height, _) in enumerate(Z_full):
        left, right = int(left), int(right)
        left_in_active = left in active_nodes
        right_in_active = right in active_nodes

        if left_in_active and right_in_active:
            new_left = new_positions[left]
            new_right = new_positions[right]
            new_size = cluster_size.get(
                new_left, 1) + cluster_size.get(new_right, 1)

            if new_left > new_right:
                new_left, new_right = new_right, new_left

            Z_sub.append([new_left, new_right, height, new_size])

            active_nodes.remove(left)
            active_nodes.remove(right)
            active_nodes.append(len(labels) + i)
            new_positions[len(labels) + i] = next_id
            cluster_size[next_id] = new_size
            next_id += 1

        elif left_in_active:
            active_nodes.remove(left)
            active_nodes.append(len(labels) + i)
            new_positions[len(labels) + i] = new_positions[left]

        elif right_in_active:
            active_nodes.remove(right)
            active_nodes.append(len(labels) + i)
            new_positions[len(labels) + i] = new_positions[right]

    if Z_sub:
        Z_sub = np.array(Z_sub)
        max_idx = len(selected_indices) - 1
        for i, row in enumerate(Z_sub):
            if row[0] > max_idx:
                Z_sub[i, 0] = max_idx
            if row[1] > max_idx:
                Z_sub[i, 1] = max_idx
            max_idx += 1
    else:
        Z_sub = np.empty((0, 4))

    return Z_sub, selected_labels


def plot_sub_dendrogram(Z, labels, selected_labels, title, figsize):

    Z_sub, selected_labels = extract_sub_dendrogram(Z, labels, selected_labels)
    """Plot the sub-dendrogram."""
    if len(Z_sub) == 0:
        raise ValueError(
            "No clustering relationships found among selected labels.")

    plt.figure(figsize=figsize)
    sch.dendrogram(
        Z_sub,
        labels=selected_labels,
        leaf_rotation=0,
        leaf_font_size=10,
        orientation='right',
    )
    plt.title(title)
    plt.xlabel("Distance")
    plt.ylabel("Elements")
    plt.tight_layout()
    plt.show()


def plot(nma_instance, sub_labels, title, figsize, **kwargs):
    if nma_instance.dendrogram_object.Z is None:
        raise ValueError("No linkage matrix (z) found in NMA instance")

    if sub_labels is None:
        sub_labels = nma_instance.labels
        
    filtered_dendrogram_json = nma_instance.dendrogram_object.get_sub_dendrogram_formatted(
        sub_labels)
    print("Filtered dendrogram structure:")
    print(filtered_dendrogram_json)

    if hasattr(nma_instance, 'labels'):
        plot_sub_dendrogram(nma_instance.dendrogram_object.Z,
                            nma_instance.labels, sub_labels, title, figsize)

    print(nma_instance.dendrogram_object.Z)

    # plt.figure(figsize=(20, 15))
    # sch.dendrogram(
    #     nma_instance.z,
    #     leaf_rotation=0,
    #     leaf_font_size=10,
    #     orientation='right',
    #     color_threshold=85,
    #     **kwargs
    # )
    # plt.title('NMA Hierarchical Clustering Dendrogram')
    # plt.xlabel('Elements')
    # plt.ylabel('Distance')
    # plt.tight_layout()
    # plt.show()

