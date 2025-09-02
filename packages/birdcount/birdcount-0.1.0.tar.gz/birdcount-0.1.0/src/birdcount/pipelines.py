"""Pipeline orchestration."""

import logging
import pickle
from pathlib import Path
from typing import Dict, Any, List

from . import audio, ml, reports


def clean_audio_pipeline(config: Dict[str, Any]) -> None:
    """Complete audio cleaning pipeline."""
    # Set up logging
    log_level = config.get('logging', {}).get('level', 'INFO')
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    logger = logging.getLogger(__name__)
    
    logger.info("Starting BirdCount cleaning pipeline...")
    
    # Extract configuration sections
    bandpass_config = config.get('bandpass', {})
    detection_config = config.get('detection', {})
    cropping_config = config.get('cropping', {})
    spectral_config = config.get('spectral_subtraction', {})
    report_config = config.get('report', {})
    
    # Get input/output paths
    input_dir = config.get('input_dir')
    output_dir = config.get('output_dir', 'outputs/cleaned')
    report_path = report_config.get('path', 'outputs/cleaning_report.pdf')
    
    if not input_dir:
        logger.error("No input directory specified in config")
        return
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing audio files from: {input_path}")
    logger.info(f"Output directory: {output_path}")
    
    # Find audio files
    audio_files = list(input_path.rglob("*.wav")) + list(input_path.rglob("*.mp3"))
    
    if not audio_files:
        logger.warning(f"No audio files found in {input_path}")
        return
    
    logger.info(f"Found {len(audio_files)} audio files")
    
    # Process each audio file
    processed_files = []
    cleaning_data = []  # Store data for report
    
    for audio_file in audio_files:
        logger.info(f"Processing: {audio_file.name}")
        
        try:
            # Load audio
            audio_data, sr = audio.load_audio(str(audio_file))
            
            # Apply bandpass filter
            filtered_audio = audio.bandpass_filter(
                audio_data, sr,
                freq_min=bandpass_config.get('freq_min', 1500),
                freq_max=bandpass_config.get('freq_max', 7000),
                order=bandpass_config.get('order', 6)
            )
            
            # Detect calls
            call_times = audio.detect_calls(
                filtered_audio, sr,
                frame_length=detection_config.get('frame_length', 2048),
                hop_length=detection_config.get('hop_length', 512),
                mad_multiplier=detection_config.get('mad_multiplier', 2.0),
                min_duration=detection_config.get('min_duration', 0.4),
                max_gap=detection_config.get('max_gap', 0.08)
            )
            
            if call_times:
                logger.info(f"Detected {len(call_times)} calls in {audio_file.name}")
                
                # Crop calls
                cropped_calls = audio.crop_calls(
                    filtered_audio, sr, call_times,
                    padding=cropping_config.get('padding', 0.15)
                )
                
                # Apply spectral subtraction to each call
                denoised_calls = []
                for call in cropped_calls:
                    denoised_call = audio.spectral_subtraction(
                        call, sr,
                        noise_duration=spectral_config.get('noise_duration', 0.1),
                        noise_factor=spectral_config.get('noise_factor', 2.5),
                        n_fft=spectral_config.get('n_fft', 1024),
                        hop_length=spectral_config.get('hop_length', 256)
                    )
                    denoised_calls.append(denoised_call)
                
                # Save processed calls
                call_dir = output_path / audio_file.stem / "processed_calls"
                call_dir.mkdir(parents=True, exist_ok=True)
                
                for i, (call, denoised_call) in enumerate(zip(cropped_calls, denoised_calls)):
                    call_file = call_dir / f"call_{i+1}.wav"
                    denoised_file = call_dir / f"call_{i+1}_denoised.wav"
                    
                    audio.save_audio(str(call_file), call, sr)
                    audio.save_audio(str(denoised_file), denoised_call, sr)
                
                processed_files.append({
                    'file': audio_file,
                    'calls': len(call_times),
                    'call_times': call_times
                })
                
                # Store data for report
                cleaning_data.append({
                    'filename': audio_file.name,
                    'original_audio': audio_data,
                    'filtered_audio': filtered_audio,
                    'call_times': call_times,
                    'cropped_calls': cropped_calls,
                    'denoised_calls': denoised_calls,
                    'sample_rate': sr
                })
            else:
                logger.info(f"No calls detected in {audio_file.name}")
                
        except Exception as e:
            logger.error(f"Error processing {audio_file}: {e}")
    
    logger.info(f"Successfully processed {len(processed_files)} files")
    
    # Generate cleaning report if requested
    if report_config.get('enabled', True) and cleaning_data:
        logger.info("Generating cleaning report...")
        reports.generate_cleaning_report(cleaning_data, report_path, config)
        logger.info(f"Cleaning report saved to: {report_path}")
    
    logger.info("BirdCount cleaning pipeline complete!")


def cluster_audio_pipeline(config: Dict[str, Any]) -> None:
    """Complete clustering pipeline."""
    # Set up logging
    log_level = config.get('logging', {}).get('level', 'INFO')
    logging.basicConfig(level=getattr(logging, log_level.upper()))
    logger = logging.getLogger(__name__)
    
    logger.info("Starting BirdCount clustering pipeline...")
    
    # Extract configuration sections
    embedding_config = config.get('embedding', {})
    clustering_config = config.get('clustering', {})
    report_config = config.get('report', {})
    
    # Get input/output paths
    input_dir = config.get('input_dir')
    output_dir = config.get('output_dir', 'outputs/clustered')
    report_path = report_config.get('path', 'outputs/cluster_report.pdf')
    
    if not input_dir:
        logger.error("No input directory specified in config")
        return
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing audio files from: {input_path}")
    logger.info(f"Output directory: {output_path}")
    
    # Find audio files
    audio_files = list(input_path.rglob("*.wav")) + list(input_path.rglob("*.mp3"))
    
    if not audio_files:
        logger.warning(f"No audio files found in {input_path}")
        return
    
    logger.info(f"Found {len(audio_files)} audio files")
    
    # Initialize embedder
    try:
        embedder = ml.PerchEmbedder(
            hub_url=embedding_config.get('model_url'),
            sample_rate=embedding_config.get('sample_rate', 32000),
            target_duration=embedding_config.get('target_duration', 5.0)
        )
        
        if embedder.model is None:
            logger.error("Failed to load TensorFlow model. Make sure TensorFlow is installed.")
            return
            
    except Exception as e:
        logger.error(f"Error initializing embedder: {e}")
        return
    
    # Generate embeddings
    logger.info("Generating embeddings...")
    try:
        embeddings_data = embedder.embed_batch(audio_files)
        
        # Save embeddings
        embeddings_file = output_path / "embeddings.pkl"
        embedder.save_embeddings(embeddings_data, embeddings_file)
        logger.info(f"Saved embeddings to {embeddings_file}")
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return
    
    # Perform clustering
    logger.info("Performing clustering...")
    try:
        cluster_results = ml.cluster_audio(
            embeddings_data['embeddings'], 
            clustering_config
        )
        
        # Add file information to results
        cluster_results['file_names'] = embeddings_data['file_names']
        cluster_results['audio_files'] = audio_files
        
        # Save clustering results
        cluster_file = output_path / "cluster_results.pkl"
        with open(cluster_file, 'wb') as f:
            pickle.dump(cluster_results, f)
        logger.info(f"Saved clustering results to {cluster_file}")
        
    except Exception as e:
        logger.error(f"Error during clustering: {e}")
        return
    
    # Generate clustering report if requested
    if report_config.get('enabled', True):
        logger.info("Generating clustering report...")
        reports.generate_clustering_report(cluster_results, embeddings_data, report_path, config)
        logger.info(f"Clustering report saved to: {report_path}")
    
    logger.info("BirdCount clustering pipeline complete!") 