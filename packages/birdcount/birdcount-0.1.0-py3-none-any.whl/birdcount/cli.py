"""Command-line interface for BirdCount."""

import argparse
from . import config


def clean_command(args):
    """Clean and preprocess audio files."""
    try:
        config_dict = config.load_config(args.config)
        print(f"Running birdcount clean with config: {args.config}")
        
        # Import here to avoid circular imports
        from .pipelines import clean_audio_pipeline
        clean_audio_pipeline(config_dict)
        
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
    except Exception as e:
        print(f"Error during cleaning: {e}")


def cluster_command(args):
    """Cluster audio files using embeddings."""
    try:
        config_dict = config.load_config(args.config)
        print(f"Running birdcount cluster with config: {args.config}")
        
        # Import here to avoid circular imports
        from .pipelines import cluster_audio_pipeline
        cluster_audio_pipeline(config_dict)
        
    except FileNotFoundError:
        print(f"Config file not found: {args.config}")
    except Exception as e:
        print(f"Error during clustering: {e}")


def main():
    parser = argparse.ArgumentParser(prog='birdcount')
    subparsers = parser.add_subparsers(dest='command')

    # Clean command
    clean_parser = subparsers.add_parser('clean', help='Clean and preprocess audio files')
    clean_parser.add_argument('--config', required=True, 
                             help='Path to cleaning config YAML file')
    clean_parser.set_defaults(func=clean_command)

    # Cluster command
    cluster_parser = subparsers.add_parser('cluster', help='Cluster audio files using embeddings')
    cluster_parser.add_argument('--config', required=True, 
                               help='Path to clustering config YAML file')
    cluster_parser.set_defaults(func=cluster_command)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
