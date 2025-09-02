"""PDF report generation."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Tuple
from scipy import signal
import librosa


def generate_cleaning_report(cleaning_data: List[Dict], report_path: str, config: Dict[str, Any]) -> None:
    """Generate a PDF report showing the cleaning process."""
    # Create output directory
    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with PdfPages(report_path) as pdf:
        # Title page with summary statistics and config settings
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.9, 'BirdCount Cleaning Report', 
                ha='center', va='center', fontsize=24, fontweight='bold')
        
        # Calculate statistics
        total_calls = sum(len(data['call_times']) for data in cleaning_data)
        files_with_calls = sum(1 for data in cleaning_data if len(data['call_times']) > 0)
        
        # Statistics
        stats_text = f"Processing Statistics:\n\n"
        stats_text += f"• Total files processed: {len(cleaning_data)}\n"
        stats_text += f"• Files with detected calls: {files_with_calls}\n"
        stats_text += f"• Total calls detected: {total_calls}\n"
        stats_text += f"• Average calls per file: {total_calls/len(cleaning_data):.1f}\n"
        
        ax.text(0.5, 0.65, stats_text, ha='center', va='center', fontsize=14,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.7))
        
        # Configuration summary
        config_text = "Configuration Settings:\n\n"
        config_text += f"• Bandpass filter: {config.get('bandpass', {}).get('freq_min')}-{config.get('bandpass', {}).get('freq_max')} Hz\n"
        config_text += f"• Call detection: MAD multiplier = {config.get('detection', {}).get('mad_multiplier')}\n"
        config_text += f"• Call cropping: padding = {config.get('cropping', {}).get('padding')}s\n"
        config_text += f"• Noise reduction: factor = {config.get('spectral_subtraction', {}).get('noise_factor')}"
        
        ax.text(0.5, 0.35, config_text, ha='center', va='center', fontsize=12,
               bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgreen", alpha=0.7))
    
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        pdf.savefig(fig)
        plt.close()
        
        # Process files in groups of 5 per page
        clips_per_page = 5
        for page_start in range(0, len(cleaning_data), clips_per_page):
            page_end = min(page_start + clips_per_page, len(cleaning_data))
            page_data = cleaning_data[page_start:page_end]
            
            # Create page with rows (one per clip), 4 columns (one per processing step)
            fig, axes = plt.subplots(len(page_data), 4, figsize=(24, 5 * len(page_data)))
            
            # Handle single row case
            if len(page_data) == 1:
                axes = axes.reshape(1, -1)
            
            # Calculate consistent vmin/vmax across all rows for this page
            page_vmin, page_vmax = None, None
            for data in page_data:
                original_audio = data['original_audio']
                sr = data['sample_rate']
                frequencies, times, Sxx = signal.spectrogram(original_audio, sr, nperseg=1024, noverlap=512)
                Sxx_db = librosa.power_to_db(Sxx, ref=np.max)
                
                if page_vmin is None:
                    page_vmin, page_vmax = np.min(Sxx_db), np.max(Sxx_db)
                else:
                    page_vmin = min(page_vmin, np.min(Sxx_db))
                    page_vmax = max(page_vmax, np.max(Sxx_db))
            
            for row_idx, data in enumerate(page_data):
                filename = data['filename']
                original_audio = data['original_audio']
                filtered_audio = data['filtered_audio']
                call_times = data['call_times']
                cropped_calls = data['cropped_calls']
                denoised_calls = data['denoised_calls']
                sr = data['sample_rate']
                
                # Column 1: Original audio spectrogram (filename as title, show frequency labels)
                ax1 = axes[row_idx, 0]
                plot_spectrogram(original_audio, sr, ax1, filename, show_ylabel=True, show_colorbar=False, vmin=page_vmin, vmax=page_vmax)
                
                # Column 2: Bandpass filtered audio spectrogram
                ax2 = axes[row_idx, 1]
                plot_spectrogram(filtered_audio, sr, ax2, 'Bandpass Filtered', show_ylabel=False, show_colorbar=False, vmin=page_vmin, vmax=page_vmax)
                if call_times:
                    highlight_calls(ax2, call_times, 'orange')
                
                # Column 3: Call detection and cropping (show first detected call)
                ax3 = axes[row_idx, 2]
                if cropped_calls:
                    plot_spectrogram(cropped_calls[0], sr, ax3, 'Detected Call #1', show_ylabel=False, show_colorbar=False, vmin=page_vmin, vmax=page_vmax)
                else:
                    ax3.text(0.5, 0.5, 'No calls detected', 
                            ha='center', va='center', transform=ax3.transAxes, fontsize=12)
                    ax3.set_title('Detected Call #1', fontsize=10, fontweight='bold')
                    ax3.set_ylabel('')
                
                # Column 4: Final denoised call (show colorbar only on this column)
                ax4 = axes[row_idx, 3]
                if denoised_calls:
                    plot_spectrogram(denoised_calls[0], sr, ax4, 'Denoised Call', show_ylabel=False, show_colorbar=True, vmin=page_vmin, vmax=page_vmax)
                else:
                    ax4.text(0.5, 0.5, 'No calls detected', 
                            ha='center', va='center', transform=ax4.transAxes, fontsize=12)
                    ax4.set_title('Denoised Call', fontsize=10, fontweight='bold')
                    ax4.set_ylabel('')
            
            plt.tight_layout(pad=2.0)
            pdf.savefig(fig, bbox_inches='tight', dpi=100)
            plt.close()


def generate_clustering_report(cluster_results: Dict, embeddings_data: Dict, report_path: str, config: Dict[str, Any]) -> None:
    """Generate a PDF report showing clustering results."""
    # Create output directory
    report_file = Path(report_path)
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    embeddings_2d = cluster_results['embeddings_2d']
    cluster_labels = cluster_results['cluster_labels']
    file_names = cluster_results['file_names']
    audio_files = cluster_results['audio_files']
    
    with PdfPages(report_path) as pdf:
        # Title page
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.8, 'BirdCount Clustering Report', 
                ha='center', va='center', fontsize=24, fontweight='bold')
        ax.text(0.5, 0.6, f'Processed {len(audio_files)} files', 
                ha='center', va='center', fontsize=16)
        ax.text(0.5, 0.5, f'Found {cluster_results["n_clusters"]} clusters', 
                ha='center', va='center', fontsize=16)
        ax.text(0.5, 0.4, f'Generated on: {Path().absolute()}', 
                ha='center', va='center', fontsize=12)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        pdf.savefig(fig)
        plt.close()
        
        # UMAP visualization
        fig, ax = plt.subplots(figsize=(12, 8))
        scatter = ax.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], 
                           c=cluster_labels, cmap='tab20', alpha=0.7, s=50)
        ax.set_xlabel('UMAP 1')
        ax.set_ylabel('UMAP 2')
        ax.set_title('UMAP Visualization of Clusters')
        plt.colorbar(scatter, ax=ax, label='Cluster')
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()
        
        # Cluster statistics
        fig, ax = plt.subplots(figsize=(12, 6))
        unique_labels, counts = np.unique(cluster_labels, return_counts=True)
        
        # Remove noise label (-1) for plotting
        plot_labels = unique_labels[unique_labels != -1]
        plot_counts = counts[unique_labels != -1]
        
        bars = ax.bar(range(len(plot_labels)), plot_counts, alpha=0.7)
        ax.set_xlabel('Cluster')
        ax.set_ylabel('Number of Files')
        ax.set_title('Cluster Sizes')
        ax.set_xticks(range(len(plot_labels)))
        ax.set_xticklabels([f'Cluster {l}' for l in plot_labels])
        
        # Add count labels on bars
        for bar, count in zip(bars, plot_counts):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                   str(count), ha='center', va='bottom')
        
        plt.tight_layout()
        pdf.savefig(fig)
        plt.close()
        
        # Spectrograms organized by cluster
        # Group files by cluster
        cluster_groups = {}
        for i, label in enumerate(cluster_labels):
            if label not in cluster_groups:
                cluster_groups[label] = []
            cluster_groups[label].append(i)
        
        # Create spectrogram pages for each cluster
        for cluster_id, file_indices in cluster_groups.items():
            if cluster_id == -1:  # Skip noise
                continue
                
            cluster_name = f"Cluster {cluster_id}"
            
            # Limit to first 12 files per cluster to keep pages manageable
            file_indices = file_indices[:12]
            
            # Calculate grid size
            n_files = len(file_indices)
            cols = min(3, n_files)
            rows = (n_files + cols - 1) // cols
            
            fig, axes = plt.subplots(rows, cols, figsize=(15, 5*rows))
            fig.suptitle(f'{cluster_name} - {len(file_indices)} files', fontsize=16, fontweight='bold')
            
            # Flatten axes for easier indexing
            if rows == 1:
                axes = [axes] if cols == 1 else axes
            else:
                axes = axes.flatten()
            
            for i, file_idx in enumerate(file_indices):
                if i >= len(axes):
                    break
                    
                ax = axes[i]
                audio_file = audio_files[file_idx]
                filename = file_names[file_idx]
                
                try:
                    # Load and plot audio
                    from . import audio
                    audio_data, sr = audio.load_audio(str(audio_file))
                    plot_spectrogram(audio_data, sr, ax, filename, show_ylabel=True, show_colorbar=False)
                    
                except Exception as e:
                    ax.text(0.5, 0.5, f'Error loading {filename}', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(filename)
            
            # Hide unused subplots
            for i in range(len(file_indices), len(axes)):
                axes[i].axis('off')
            
            plt.tight_layout()
            pdf.savefig(fig)
            plt.close()
        
        # Summary page
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.text(0.5, 0.8, 'Clustering Summary', 
                ha='center', va='center', fontsize=20, fontweight='bold')
        
        summary_text = f"Total files: {len(audio_files)}\n"
        summary_text += f"Number of clusters: {cluster_results['n_clusters']}\n"
        summary_text += f"Noise points: {cluster_results['n_noise']}\n"
        summary_text += f"Clustering algorithm: HDBSCAN\n"
        summary_text += f"Embedding model: Google Perch"
        
        ax.text(0.5, 0.5, summary_text, ha='center', va='center', fontsize=14)
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        pdf.savefig(fig)
        plt.close()


def plot_spectrogram(audio: np.ndarray, sr: int, ax: plt.Axes, title: str, 
                    show_ylabel: bool = True, show_colorbar: bool = False, 
                    vmin: float = None, vmax: float = None) -> Tuple[float, float]:
    """Plot spectrogram on given axes."""
    frequencies, times, Sxx = signal.spectrogram(audio, sr, nperseg=1024, noverlap=512)
    Sxx_db = librosa.power_to_db(Sxx, ref=np.max)
    
    # Use provided vmin/vmax or calculate them
    if vmin is None or vmax is None:
        vmin, vmax = np.min(Sxx_db), np.max(Sxx_db)
    
    im = ax.pcolormesh(times, frequencies, Sxx_db, shading='gouraud', cmap='viridis', vmin=vmin, vmax=vmax)
    
    if show_ylabel:
        ax.set_ylabel('Frequency (Hz)', fontsize=10)
    else:
        ax.set_ylabel('')
        ax.set_yticklabels([])
    
    ax.set_xlabel('Time (seconds)', fontsize=10)
    ax.set_title(title, fontsize=10, fontweight='bold', pad=10)
    
    # Add colorbar if requested
    if show_colorbar:
        plt.colorbar(im, ax=ax, label='Power (dB)', shrink=0.8)
    
    # Clean up tick labels
    ax.tick_params(axis='both', which='major', labelsize=8)
    
    return vmin, vmax


def highlight_calls(ax: plt.Axes, call_times: List[Tuple[float, float]], color: str) -> None:
    """Highlight detected calls on spectrogram."""
    for start, end in call_times:
        rect = patches.Rectangle((start, 0), end - start, ax.get_ylim()[1], 
                               linewidth=2, edgecolor=color, facecolor=color, alpha=0.3)
        ax.add_patch(rect)