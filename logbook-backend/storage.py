import os
import shutil
from fastapi import UploadFile
from pathlib import Path
import datetime

# Root path for all Logbook storage — reads from env var, defaults to ./uploads
BASE_STORAGE_PATH = Path(os.environ.get("UPLOAD_DIR", "./uploads"))

def ensure_experiment_directories(experiment_id: str) -> Path:
    """
    Creates the necessary directory structure for an experiment.
    Returns the base experiment directory path.
    """
    exp_dir = BASE_STORAGE_PATH / "experiments" / experiment_id
    
    # Subdirectories
    subdirs = ["datasets", "sample_images", "notes", "reflections"]
    
    for subdir in subdirs:
        (exp_dir / subdir).mkdir(parents=True, exist_ok=True)
        
    return exp_dir

def save_uploaded_file(upload_file: UploadFile, experiment_id: str, category: str) -> str:
    """
    Saves an uploaded file to the appropriate category folder.
    Categories: 'datasets', 'sample_images', 'notes', 'reflections'
    Returns the relative path string (relative to BASE_STORAGE_PATH).
    """
    exp_dir = ensure_experiment_directories(experiment_id)
    category_dir = exp_dir / category
    
    # Basic sanitization and timestamping to avoid overwrites
    original_filename = upload_file.filename if upload_file.filename else "unnamed_file"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{original_filename.replace(' ', '_')}"
    
    file_path = category_dir / safe_filename
    
    # Write the file
    upload_file.file.seek(0) # Ensure we are at start of file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
        
    # Return path relative to BASE_STORAGE_PATH for portability
    return str(file_path.relative_to(BASE_STORAGE_PATH))
