from .utilss.classes.score_calculator import ScoreCalculator
from .utilss.photos_utils import preprocess_loaded_image

def get_adversarial_score(image, model, full_z, class_names, top_k=5):
    """
    Calculate the adversarial score for a given image using the provided model and score calculator.

    Parameters:
    - image: Preprocessed image ready for model prediction
    - model: The neural network model used for predictions
    - full_z: The full Z matrix from hierarchical clustering
    - class_names: List of class names corresponding to model outputs
    """

    score_calculator = ScoreCalculator(full_z, class_names)
    processed_img, _ = preprocess_loaded_image(model, image)
    predictions = model.predict(processed_img, verbose=0)[0]
    score = score_calculator.calculate_adversarial_score(predictions, top_k=top_k)
    return score
