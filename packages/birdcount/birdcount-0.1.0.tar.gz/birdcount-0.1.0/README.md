# BirdCount

A Python package for processing, analyzing, and counting bird calls from audio recordings.

## Features

- **Audio Cleaning**: Bandpass filtering, call detection, cropping, and spectral subtraction
- **Call Detection**: Adaptive threshold-based detection using MAD (Median Absolute Deviation)
- **Embedding Generation**: Integration with TensorFlow Hub Perch model for bird call embeddings
- **Clustering**: HDBSCAN clustering with UMAP visualization
- **PDF Reports**: Automatic generation of cleaning and clustering reports
- **Configurable**: YAML-based configuration for easy parameter tuning

## Installation

### Basic Installation

```bash
pip install birdcount
```

### With Machine Learning Dependencies

For embedding generation (requires TensorFlow):

```bash
pip install birdcount[ml]
```

### Development Installation

```bash
git clone https://github.com/seanwrowland/birdcount.git
cd birdcount
pip install -e .
```

## Google Colab

You can use BirdCount directly in Google Colab! Here's a quick example:

```python
# Install BirdCount
!pip install birdcount[ml]

# Download sample config files
!wget https://raw.githubusercontent.com/seanwrowland/birdcount/main/clean_config.yaml
!wget https://raw.githubusercontent.com/seanwrowland/birdcount/main/cluster_config.yaml

# Upload your audio files to Colab, then run:
!birdcount clean --config clean_config.yaml
!birdcount cluster --config cluster_config.yaml
```

## Quick Start

BirdCount provides two main commands for processing bird audio:

### 1. Clean Audio Files

First, clean and preprocess your audio files:

```bash
birdcount clean --config clean_config.yaml
```

This command:
- Applies bandpass filtering to isolate bird call frequencies
- Detects individual calls using adaptive thresholds
- Crops calls with padding
- Applies spectral subtraction for noise reduction
- Generates a cleaning report PDF showing the process

### 2. Cluster Audio Files

Then, cluster the cleaned audio files:

```bash
birdcount cluster --config cluster_config.yaml
```

This command:
- Generates embeddings using Google Perch model
- Performs HDBSCAN clustering
- Creates UMAP visualizations
- Generates a clustering report PDF organized by clusters

## Configuration

### Cleaning Configuration (`clean_config.yaml`)

```yaml
# Input and output directories
input_dir: "data/raw/birds"
output_dir: "outputs/cleaned"

# Bandpass filter settings
bandpass:
  freq_min: 1500
  freq_max: 7000
  order: 6

# Call detection settings
detection:
  mad_multiplier: 2.0
  min_duration: 0.4
  max_gap: 0.08
  frame_length: 2048
  hop_length: 512

# Cropping settings
cropping:
  padding: 0.15

# Spectral subtraction settings
spectral_subtraction:
  noise_duration: 0.1
  noise_factor: 2.5
  n_fft: 1024
  hop_length: 256

# Report settings
report:
  enabled: true
  path: "outputs/cleaning_report.pdf"

# Logging settings
logging:
  level: "INFO"
```

### Clustering Configuration (`cluster_config.yaml`)

```yaml
# Input and output directories
input_dir: "outputs/cleaned"
output_dir: "outputs/clustered"

# Embedding settings
embedding:
  enabled: true
  model_url: "https://www.kaggle.com/models/google/bird-vocalization-classifier/TensorFlow2/bird-vocalization-classifier/2"
  sample_rate: 32000
  target_duration: 5.0

# Clustering settings
clustering:
  min_cluster_size: 3
  min_samples: 2
  metric: "euclidean"
  umap_n_neighbors: 15
  umap_min_dist: 0.1

# Report settings
report:
  enabled: true
  path: "outputs/cluster_report.pdf"

# Logging settings
logging:
  level: "INFO"
```

## Output Structure

```
outputs/
├── cleaned/
│   ├── audio_file_1/
│   │   └── processed_calls/
│   │       ├── call_1.wav
│   │       ├── call_1_denoised.wav
│   │       ├── call_2.wav
│   │       └── call_2_denoised.wav
│   └── cleaning_report.pdf
└── clustered/
    ├── embeddings.pkl
    ├── cluster_results.pkl
    └── cluster_report.pdf
```

## Reports

### Cleaning Report
The cleaning report (`cleaning_report.pdf`) includes:
- Before/after spectrograms for each file
- Call detection highlights
- Processing summary and statistics
- Configuration details

### Clustering Report
The clustering report (`cluster_report.pdf`) includes:
- UMAP visualization of clusters
- Cluster size statistics
- Spectrograms organized by cluster
- Summary of clustering results

## API Usage

```python
from birdcount import cleaning, clustering, config

# Load configuration
config_dict = config.load_config('clean_config.yaml')

# Run cleaning pipeline
cleaning.clean_audio_pipeline(config_dict)

# Run clustering pipeline
clustering.cluster_audio_pipeline(config_dict)
```

## Dependencies

### Core Dependencies
- numpy
- scipy
- librosa
- matplotlib
- seaborn
- hdbscan
- umap-learn
- scikit-learn
- pyyaml
- plotly
- pandas
- soundfile
- tqdm

### Optional ML Dependencies
- tensorflow
- tensorflow-hub

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
flake8 src/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Citation

If you use BirdCount in your research, please cite:

```bibtex
@software{rowland2025birdcount,
  title={BirdCount: Bird call counting and analysis tool},
  author={Rowland, Sean},
  year={2025},
  url={https://github.com/seanwrowland/birdcount}
}
```