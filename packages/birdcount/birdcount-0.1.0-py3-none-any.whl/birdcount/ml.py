"""Machine learning functionality."""

import numpy as np
import umap
from sklearn.cluster import HDBSCAN
from typing import Dict, List, Optional, Union, Tuple
import pickle
import logging
from tqdm import tqdm
import warnings
import librosa
from pathlib import Path
warnings.filterwarnings('ignore')

# TensorFlow imports
try:
    import tensorflow as tf
    import tensorflow_hub as hub
    PERCH_AVAILABLE = True
except ImportError:
    print("Warning: TensorFlow and TensorFlow Hub not available.")
    print("Install with: pip install tensorflow tensorflow-hub")
    PERCH_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerchEmbedder:
    """
    Simple embedder for short bird audio clips.
    
    Assumes clips are already preprocessed and short (≤3 seconds).
    Generates one embedding per clip by padding/truncating to 5 seconds.
    """
    
    def __init__(self, 
                 hub_url: str = "https://www.kaggle.com/models/google/bird-vocalization-classifier/TensorFlow2/bird-vocalization-classifier/2",
                 sample_rate: int = 32000,
                 target_duration: float = 5.0,
                 normalize: bool = True):
        """
        Initialize the embedder.
        
        Args:
            hub_url: TensorFlow Hub URL for the Perch model
            sample_rate: Sample rate (must be 32000 for Perch)
            target_duration: Target duration in seconds (5.0 for Perch)
            normalize: Whether to normalize audio amplitude
        """
        self.hub_url = hub_url
        self.sample_rate = sample_rate
        self.target_duration = target_duration
        self.normalize = normalize
        
        # Calculate target length in samples
        self.target_length = int(target_duration * sample_rate)  # 160,000 samples
        
        # Model
        self.model = None
        
        # Initialize model
        if PERCH_AVAILABLE:
            self._load_model()
        else:
            logger.warning("TensorFlow not available. Install required packages.")
    
    def _load_model(self):
        """Load the Perch model from TensorFlow Hub."""
        try:
            logger.info("Loading Perch model from TensorFlow Hub...")
            self.model = hub.load(self.hub_url)
            logger.info(f"Successfully loaded model from {self.hub_url}")
                
        except Exception as e:
            logger.error(f"Failed to load model from TensorFlow Hub: {e}")
            self.model = None
    
    def preprocess_audio(self, audio_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        Load and preprocess a single audio file for Perch.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Preprocessed audio array or None if failed
        """
        try:
            # Load audio at target sample rate
            audio, sr = librosa.load(audio_path, sr=self.sample_rate)
            
            # Pad or truncate to target length
            if len(audio) < self.target_length:
                # Pad with zeros if too short
                audio = np.pad(audio, (0, self.target_length - len(audio)))
            else:
                # Truncate if too long
                audio = audio[:self.target_length]
            
            # Normalize if requested
            if self.normalize and np.max(np.abs(audio)) > 0:
                audio = audio / np.max(np.abs(audio))
            
            # Add batch dimension for model input
            audio = audio.reshape(1, -1).astype(np.float32)
            
            return audio
            
        except Exception as e:
            logger.error(f"Error preprocessing {audio_path}: {e}")
            return None
    
    def extract_embedding(self, audio_array: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract embedding from preprocessed audio.
        
        Args:
            audio_array: Preprocessed audio array (1, 160000)
            
        Returns:
            Embedding vector or None if failed
        """
        if self.model is None:
            logger.error("Model not loaded")
            return None
        
        try:
            # Convert to tensor
            audio_tensor = tf.constant(audio_array)
            
            # Run inference using the serving signature
            result = self.model.signatures['serving_default'](inputs=audio_tensor)
            
            # Extract the embedding (output_1 is the 1280-dim embedding)
            embedding = result['output_1'].numpy()
            
            # Convert from (1, 1280) to (1280,)
            return embedding.flatten()
            
        except Exception as e:
            logger.error(f"Error extracting embedding: {e}")
            return None
    
    def embed_single_file(self, audio_path: Union[str, Path]) -> Dict:
        """
        Process a single audio file and return embedding with metadata.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with embedding and metadata
        """
        audio_path = Path(audio_path)
        
        # Preprocess audio
        audio_array = self.preprocess_audio(audio_path)
        if audio_array is None:
            return {
                'file_path': str(audio_path),
                'file_name': audio_path.name,
                'embedding': None,
                'success': False,
                'error': 'Preprocessing failed'
            }
        
        # Extract embedding
        embedding = self.extract_embedding(audio_array)
        
        return {
            'file_path': str(audio_path),
            'file_name': audio_path.name,
            'embedding': embedding,
            'success': embedding is not None,
            'error': None if embedding is not None else 'Embedding extraction failed'
        }
    
    def embed_batch(self, 
                   audio_paths: List[Union[str, Path]], 
                   labels: Optional[List[str]] = None) -> Dict:
        """
        Process a batch of audio files.
        
        Args:
            audio_paths: List of paths to audio files
            labels: Optional list of labels for each file
            
        Returns:
            Dictionary with embeddings, labels, and metadata
        """
        embeddings = []
        file_names = []
        successful_labels = []
        failed_files = []
        
        for i, audio_path in enumerate(tqdm(audio_paths, desc="Generating embeddings")):
            result = self.embed_single_file(audio_path)
            
            if result['success']:
                embeddings.append(result['embedding'])
                file_names.append(result['file_name'])
                
                if labels:
                    successful_labels.append(labels[i])
            else:
                failed_files.append({
                    'file_path': result['file_path'],
                    'error': result['error']
                })
        
        # Convert to numpy arrays
        embeddings_array = np.array(embeddings) if embeddings else np.array([])
        labels_array = np.array(successful_labels) if successful_labels else None
        
        return {
            'embeddings': embeddings_array,
            'file_names': file_names,
            'labels': labels_array,
            'num_successful': len(embeddings),
            'num_failed': len(failed_files),
            'failed_files': failed_files,
            'embedding_dim': embeddings_array.shape[1] if embeddings_array.size > 0 else 0
        }
    
    def save_embeddings(self, 
                       embeddings_data: Dict,
                       output_path: Union[str, Path]):
        """
        Save embeddings to pickle file.
        
        Args:
            embeddings_data: Dictionary from embed_batch or embed_folder
            output_path: Path to save embeddings
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            pickle.dump(embeddings_data, f)
        
        logger.info(f"Saved {embeddings_data['num_successful']} embeddings to {output_path}")
    
    def load_embeddings(self, input_path: Union[str, Path]) -> Dict:
        """
        Load embeddings from pickle file.
        
        Args:
            input_path: Path to embeddings file
            
        Returns:
            Dictionary with embeddings and metadata
        """
        with open(input_path, 'rb') as f:
            return pickle.load(f)


def cluster_audio(embeddings: np.ndarray, config: Dict) -> Dict:
    """Run UMAP + HDBSCAN clustering."""
    # UMAP dimensionality reduction
    umap_reducer = umap.UMAP(
        n_neighbors=config.get('umap_n_neighbors', 15),
        min_dist=config.get('umap_min_dist', 0.1),
        n_components=2,
        random_state=42
    )
    embeddings_2d = umap_reducer.fit_transform(embeddings)
    
    # HDBSCAN clustering
    clusterer = HDBSCAN(
        min_cluster_size=config.get('min_cluster_size', 3),
        min_samples=config.get('min_samples', 2),
        metric=config.get('metric', 'euclidean')
    )
    cluster_labels = clusterer.fit_predict(embeddings)
    
    return {
        'embeddings': embeddings,
        'embeddings_2d': embeddings_2d,
        'cluster_labels': cluster_labels,
        'n_clusters': len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0),
        'n_noise': list(cluster_labels).count(-1)
    } 