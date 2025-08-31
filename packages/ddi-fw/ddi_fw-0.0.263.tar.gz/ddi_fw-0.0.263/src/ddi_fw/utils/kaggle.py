import os
import json

def create_kaggle_dataset(base_path: str, collections: list):
    """
    This function creates metadata JSON files and uploads datasets to Kaggle from folders.

    Args:
        base_path (str): The base path containing dataset folders.
        collections (list): A list of dictionaries containing metadata about collections (e.g., model names).
        path (str): The path to your root directory (default is "/content" for Google Colab).
        
    Returns:
        None
    """

    # Step 1: Loop through each folder in base_path
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        metadata_file_path = os.path.join(folder_path, 'dataset-metadata.json')
       
        # Step 2: Get metadata for the current folder
        model_info = next((c for c in collections if c['id'] == folder_name), None)
        if model_info is None:
            raise FileNotFoundError(f"Model info for {folder_name} not exists")
            # continue  # Skip if model info is not found
        
        title = model_info['kaggle_title']
        
        if os.path.exists(metadata_file_path):
            print(f"{title} has dataset-metadata.json file")
            continue
        
        id = model_info['kaggle_id'].lower().replace(' ', '-')
        licenses = model_info['kaggle_licenses']
        description = model_info['kaggle_description']
        
        # Ensure title is between 6 and 50 characters
        if not (6 <= len(title) <= 50):
            raise ValueError(f"Title length for {title} must be between 6 and 50 characters.")
            continue  # Skip if title length is out of the expected range

        # Step 3: Define the metadata content
        metadata = {
            "title": title,
            "id": id,
            "licenses": licenses,
            "description": description,
        }

        # Step 4: Write the metadata to a JSON file in the folder
        with open(metadata_file_path, 'w') as f:
            json.dump(metadata, f, indent=4)

        print(f"Created metadata for {folder_name}: {metadata_file_path}")
    
    # Step 5: Create datasets on Kaggle using the Kaggle API
    for folder_name in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder_name)
        if os.path.isdir(folder_path):
            # Run the Kaggle dataset creation command
            os.system(f"kaggle datasets create -p {folder_path} --dir-mode zip")
            print(f"Dataset created for {folder_name}.")
