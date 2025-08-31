import pandas as pd
import os

class EdgesDataframe:
    def __init__(self, model_filename, edges_df_path):
        """
        Initialize EdgeDataframe handler.
        
        Args:
            model_filename: Name/path of the model
            edges_df_path: Path to the edges dataframe CSV file
        """
        self.model_filename = model_filename
        self.edges_df_path = edges_df_path
        self.dataframe = None
        
    def load_dataframe(self):
        """Load the edges dataframe from CSV file."""
        if not os.path.exists(self.edges_df_path):
            raise FileNotFoundError(f"Edges dataframe not found at {self.edges_df_path}")
        
        self.dataframe = pd.read_csv(self.edges_df_path)
        return self.dataframe
    
    def get_dataframe(self):
        """Get the loaded dataframe."""
        if self.dataframe is None:
            raise ValueError("Dataframe not loaded. Call load_dataframe() first.")
        return self.dataframe
    
    def save_dataframe(self, path=None):
        """Save the dataframe to CSV."""
        if self.dataframe is None:
            raise ValueError("No dataframe to save.")
        
        save_path = path or self.edges_df_path
        self.dataframe.to_csv(save_path, index=False)
        return save_path
    
    def filter_by_labels(self, source_labels=None, target_labels=None):
        """Filter dataframe by source and/or target labels."""
        if self.dataframe is None:
            raise ValueError("Dataframe not loaded.")
        
        filtered_df = self.dataframe.copy()
        
        if source_labels:
            filtered_df = filtered_df[filtered_df['source'].isin(source_labels)]
        
        if target_labels:
            filtered_df = filtered_df[filtered_df['target'].isin(target_labels)]
        
        return filtered_df
