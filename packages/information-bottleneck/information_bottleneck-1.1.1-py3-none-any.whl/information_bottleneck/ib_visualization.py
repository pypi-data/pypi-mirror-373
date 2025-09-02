"""
Visualization tools for Information Bottleneck analysis
Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import seaborn as sns
try:
    from .mutual_info_core import MutualInfoCore
except ImportError:
    from mutual_info_core import MutualInfoCore


class IBVisualization:
    """Visualization tools for Information Bottleneck results"""
    
    def __init__(self):
        self.mi_estimator = MutualInfoCore()
        
        # Set up plotting style
        plt.style.use('default')
        sns.set_palette("husl")
    
    def plot_information_curve(self, beta_values: List[float], X: np.ndarray, Y: np.ndarray,
                             ib_model, title: str = "Information Bottleneck Curve", 
                             figsize: Tuple[int, int] = (12, 8)) -> Dict:
        """
        Plot the famous Information Bottleneck curve showing the trade-off
        between compression I(X;Z) and relevance I(Z;Y)
        
        This is THE plot that revolutionized deep learning theory!
        
        Args:
            beta_values: List of β values to evaluate
            X: Input data
            Y: Target data  
            ib_model: Trained IB model
            title: Plot title
            figsize: Figure size
            
        Returns:
            Dictionary with curve data
        """
        compression_values = []
        relevance_values = []
        objective_values = []
        
        print("🎨 Computing Information Bottleneck curve...")
        
        # Store original beta
        original_beta = ib_model.config.beta if hasattr(ib_model, 'config') else ib_model.beta
        
        for i, beta in enumerate(beta_values):
            print(f"   β = {beta:.3f} ({i+1}/{len(beta_values)})")
            
            # Update beta and retrain (simplified)
            if hasattr(ib_model, 'config'):
                ib_model.config.beta = beta
            else:
                ib_model.beta = beta
            
            try:
                # Get current representations
                if hasattr(ib_model, 'transform'):
                    Z = ib_model.transform(X)
                else:
                    # For discrete IB, get cluster assignments
                    Z = np.argmax(ib_model.p_z_given_x, axis=1).reshape(-1, 1)
                
                # Estimate mutual information
                i_x_z = self.mi_estimator.estimate_mutual_info_continuous(X, Z, method='adaptive')
                
                if Y.ndim == 1:
                    Y_reshaped = Y.reshape(-1, 1)
                else:
                    Y_reshaped = Y
                i_z_y = self.mi_estimator.estimate_mutual_info_continuous(Z, Y_reshaped, method='adaptive')
                
                # IB objective
                objective = i_x_z - beta * i_z_y
                
                compression_values.append(i_x_z)
                relevance_values.append(i_z_y)
                objective_values.append(objective)
                
            except Exception as e:
                print(f"⚠️  Failed for β={beta}: {e}")
                compression_values.append(np.nan)
                relevance_values.append(np.nan)
                objective_values.append(np.nan)
        
        # Restore original beta
        if hasattr(ib_model, 'config'):
            ib_model.config.beta = original_beta
        else:
            ib_model.beta = original_beta
        
        # Create the plot
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # 1. Information Plane (the famous plot!)
        ax1.scatter(compression_values, relevance_values, c=beta_values, 
                   cmap='viridis', s=60, alpha=0.8, edgecolors='black', linewidth=0.5)
        ax1.plot(compression_values, relevance_values, '--', alpha=0.5, color='gray')
        ax1.set_xlabel('Compression I(X;Z) [bits]', fontsize=12)
        ax1.set_ylabel('Relevance I(Z;Y) [bits]', fontsize=12)
        ax1.set_title('🌟 Information Plane\n(The plot that changed AI!)', fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(ax1.collections[0], ax=ax1)
        cbar.set_label('β parameter', rotation=270, labelpad=15)
        
        # 2. β vs Compression
        ax2.semilogx(beta_values, compression_values, 'o-', color='red', 
                     linewidth=2, markersize=6, alpha=0.8)
        ax2.set_xlabel('β parameter (log scale)', fontsize=12)
        ax2.set_ylabel('Compression I(X;Z) [bits]', fontsize=12)
        ax2.set_title('📊 Compression vs β', fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        # 3. β vs Relevance  
        ax3.semilogx(beta_values, relevance_values, 'o-', color='blue',
                     linewidth=2, markersize=6, alpha=0.8)
        ax3.set_xlabel('β parameter (log scale)', fontsize=12)
        ax3.set_ylabel('Relevance I(Z;Y) [bits]', fontsize=12)
        ax3.set_title('🎯 Relevance vs β', fontsize=11)
        ax3.grid(True, alpha=0.3)
        
        # 4. IB Objective
        ax4.semilogx(beta_values, objective_values, 'o-', color='purple',
                     linewidth=2, markersize=6, alpha=0.8)
        ax4.set_xlabel('β parameter (log scale)', fontsize=12)
        ax4.set_ylabel('IB Objective [bits]', fontsize=12)
        ax4.set_title('⚖️ IB Objective vs β', fontsize=11)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Return the data
        curve_data = {
            'beta_values': beta_values,
            'compression': compression_values,
            'relevance': relevance_values,
            'objective': objective_values
        }
        
        print(f"✅ Information curve computed!")
        print(f"   Compression range: [{np.nanmin(compression_values):.3f}, {np.nanmax(compression_values):.3f}] bits")
        print(f"   Relevance range: [{np.nanmin(relevance_values):.3f}, {np.nanmax(relevance_values):.3f}] bits")
        
        return curve_data
    
    def plot_information_plane(self, compression_values: List[float], relevance_values: List[float],
                             beta_values: List[float] = None, figsize: Tuple[int, int] = (10, 6)):
        """
        Plot the Information Plane - the most important plot in information theory!
        
        This visualization shows the fundamental trade-off in representation learning
        and explains why deep networks generalize so well.
        """
        
        fig, ax = plt.subplots(1, 1, figsize=figsize)
        
        if beta_values is not None:
            # Color by beta values
            scatter = ax.scatter(compression_values, relevance_values, 
                               c=beta_values, cmap='plasma', s=100, 
                               alpha=0.8, edgecolors='black', linewidth=1)
            
            # Add colorbar
            cbar = plt.colorbar(scatter, ax=ax)
            cbar.set_label('β parameter', rotation=270, labelpad=20, fontsize=12)
            
            # Connect points to show path
            ax.plot(compression_values, relevance_values, '--', 
                   alpha=0.6, color='gray', linewidth=2)
        else:
            # Simple scatter plot
            ax.scatter(compression_values, relevance_values, 
                      s=100, alpha=0.8, color='blue', edgecolors='black', linewidth=1)
            ax.plot(compression_values, relevance_values, '-', 
                   alpha=0.8, color='blue', linewidth=2)
        
        ax.set_xlabel('Compression I(X;Z) [bits]', fontsize=14, fontweight='bold')
        ax.set_ylabel('Relevance I(Z;Y) [bits]', fontsize=14, fontweight='bold')
        ax.set_title('🌟 Information Bottleneck Plane\n'
                    'The Fundamental Trade-off in Learning', 
                    fontsize=16, fontweight='bold', pad=20)
        
        # Add annotations
        ax.text(0.05, 0.95, '💧 Information Bottleneck:\nOptimal Compression ↔ Relevant Prediction', 
                transform=ax.transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))
        
        # Styling
        ax.grid(True, alpha=0.4)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_linewidth(1.5)
        ax.spines['bottom'].set_linewidth(1.5)
        
        plt.tight_layout()
        plt.show()
        
        print("🎨 Information Plane plotted!")
        print("📚 This plot shows the fundamental trade-off discovered by Tishby et al. (1999)")
        print("   • Left: High compression, low relevance (β → 0)")
        print("   • Right: Low compression, high relevance (β → ∞)")
        print("   • Optimal: Find the sweet spot on the curve!")
    
    def analyze_clusters(self, X: np.ndarray, Y: np.ndarray, ib_model, 
                        figsize: Tuple[int, int] = (15, 10)) -> Dict:
        """
        Comprehensive cluster analysis for discrete Information Bottleneck
        
        Args:
            X: Input data
            Y: Target data
            ib_model: Trained IB model
            figsize: Figure size
            
        Returns:
            Dictionary with cluster analysis results
        """
        
        if not hasattr(ib_model, 'p_z_given_x'):
            print("⚠️  This analysis requires a discrete IB model with p_z_given_x")
            return {}
        
        n_clusters = ib_model.config.n_clusters
        cluster_assignments = np.argmax(ib_model.p_z_given_x, axis=1)
        
        # Analyze clusters
        cluster_stats = {}
        for z in range(n_clusters):
            cluster_mask = cluster_assignments == z
            cluster_size = np.sum(cluster_mask)
            
            if cluster_size > 0:
                cluster_x = X[cluster_mask]
                cluster_y = Y[cluster_mask]
                
                cluster_stats[z] = {
                    'size': cluster_size,
                    'fraction': cluster_size / len(X),
                    'mean_x': np.mean(cluster_x, axis=0),
                    'std_x': np.std(cluster_x, axis=0),
                    'mean_y': np.mean(cluster_y),
                    'std_y': np.std(cluster_y),
                    'y_distribution': np.bincount(cluster_y.astype(int)) / cluster_size if Y.dtype.kind in 'iu' else None
                }
        
        # Create comprehensive visualization
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Cluster sizes
        ax1 = fig.add_subplot(gs[0, 0])
        sizes = [cluster_stats[z]['size'] for z in cluster_stats.keys()]
        clusters = list(cluster_stats.keys())
        
        bars = ax1.bar(clusters, sizes, alpha=0.8, color=plt.cm.Set3(np.linspace(0, 1, len(clusters))))
        ax1.set_xlabel('Cluster ID')
        ax1.set_ylabel('Cluster Size')
        ax1.set_title('📊 Cluster Sizes')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, size in zip(bars, sizes):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.01*max(sizes),
                    f'{size}', ha='center', va='bottom', fontsize=9)
        
        # 2. Y distribution per cluster
        ax2 = fig.add_subplot(gs[0, 1])
        if Y.dtype.kind in 'iu':  # Integer/discrete Y
            y_values = sorted(np.unique(Y))
            width = 0.8 / len(cluster_stats)
            
            for i, (z, stats) in enumerate(cluster_stats.items()):
                if stats['y_distribution'] is not None:
                    x_pos = [y + i * width for y in y_values]
                    y_dist = [stats['y_distribution'][y] if y < len(stats['y_distribution']) else 0 
                             for y in y_values]
                    ax2.bar(x_pos, y_dist, width, alpha=0.8, 
                           label=f'Cluster {z}', color=plt.cm.Set3(i/len(cluster_stats)))
            
            ax2.set_xlabel('Y Value')
            ax2.set_ylabel('Probability')
            ax2.set_title('🎯 Y Distribution per Cluster')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        else:
            # Continuous Y - show means and stds
            means = [cluster_stats[z]['mean_y'] for z in cluster_stats.keys()]
            stds = [cluster_stats[z]['std_y'] for z in cluster_stats.keys()]
            
            ax2.errorbar(clusters, means, yerr=stds, fmt='o-', capsize=5, capthick=2)
            ax2.set_xlabel('Cluster ID')
            ax2.set_ylabel('Y Value')
            ax2.set_title('🎯 Y Statistics per Cluster')
            ax2.grid(True, alpha=0.3)
        
        # 3. Cluster assignment confidence
        ax3 = fig.add_subplot(gs[0, 2])
        max_probs = np.max(ib_model.p_z_given_x, axis=1)
        ax3.hist(max_probs, bins=30, alpha=0.8, color='skyblue', edgecolor='black')
        ax3.set_xlabel('Max Assignment Probability')
        ax3.set_ylabel('Count')
        ax3.set_title('🎲 Assignment Confidence')
        ax3.axvline(np.mean(max_probs), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(max_probs):.3f}')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Feature importance heatmap (if X has reasonable dimensionality)
        if X.shape[1] <= 50:
            ax4 = fig.add_subplot(gs[1, :])
            
            # Compute cluster centroids
            centroids = np.array([cluster_stats[z]['mean_x'] for z in sorted(cluster_stats.keys())])
            
            im = ax4.imshow(centroids, cmap='RdBu_r', aspect='auto')
            ax4.set_xlabel('Feature Dimension')
            ax4.set_ylabel('Cluster ID')
            ax4.set_title('🌡️ Cluster Centroids (Feature Values)')
            plt.colorbar(im, ax=ax4, shrink=0.8)
        
        # 5. Information content per cluster
        ax5 = fig.add_subplot(gs[2, 0])
        cluster_info = []
        for z in cluster_stats.keys():
            # Approximate information content using entropy
            prob_z = cluster_stats[z]['fraction']
            info_content = -np.log2(prob_z) if prob_z > 0 else 0
            cluster_info.append(info_content)
        
        bars = ax5.bar(clusters, cluster_info, alpha=0.8, color='orange')
        ax5.set_xlabel('Cluster ID')
        ax5.set_ylabel('Information Content [bits]')
        ax5.set_title('📡 Information Content per Cluster')
        ax5.grid(True, alpha=0.3)
        
        # 6. Purity analysis (if Y is discrete)
        if Y.dtype.kind in 'iu':
            ax6 = fig.add_subplot(gs[2, 1])
            purities = []
            
            for z in cluster_stats.keys():
                if cluster_stats[z]['y_distribution'] is not None:
                    # Purity = fraction of most common class
                    purity = np.max(cluster_stats[z]['y_distribution'])
                    purities.append(purity)
                else:
                    purities.append(0)
            
            bars = ax6.bar(clusters, purities, alpha=0.8, color='green')
            ax6.set_xlabel('Cluster ID')
            ax6.set_ylabel('Purity (0-1)')
            ax6.set_title('✨ Cluster Purity')
            ax6.set_ylim(0, 1)
            ax6.grid(True, alpha=0.3)
            
            # Add purity values on bars
            for bar, purity in zip(bars, purities):
                height = bar.get_height()
                ax6.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                        f'{purity:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 7. Overall statistics
        ax7 = fig.add_subplot(gs[2, 2])
        ax7.axis('off')
        
        # Compute overall metrics
        total_clusters = len(cluster_stats)
        avg_cluster_size = np.mean([stats['size'] for stats in cluster_stats.values()])
        std_cluster_size = np.std([stats['size'] for stats in cluster_stats.values()])
        avg_confidence = np.mean(max_probs)
        
        stats_text = f"""
📊 CLUSTER SUMMARY
{'='*20}
Total Clusters: {total_clusters}
Avg Size: {avg_cluster_size:.1f} ± {std_cluster_size:.1f}
Avg Confidence: {avg_confidence:.3f}

🎯 COMPRESSION ACHIEVED
Input Dim: {X.shape[1]}
Compressed to: {total_clusters} clusters
Compression Ratio: {X.shape[1]/total_clusters:.1f}x
        """
        
        ax7.text(0.1, 0.9, stats_text, transform=ax7.transAxes, fontsize=11,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
        
        plt.suptitle('🔬 Information Bottleneck Cluster Analysis', 
                    fontsize=16, fontweight='bold', y=0.98)
        plt.show()
        
        print("🔬 Cluster analysis complete!")
        print(f"   • {total_clusters} clusters found")
        print(f"   • Average assignment confidence: {avg_confidence:.3f}")
        print(f"   • Compression achieved: {X.shape[1]} → {total_clusters} ({X.shape[1]/total_clusters:.1f}x)")
        
        return {
            'cluster_stats': cluster_stats,
            'assignment_confidence': max_probs,
            'cluster_purities': purities if Y.dtype.kind in 'iu' else None,
            'total_clusters': total_clusters,
            'compression_ratio': X.shape[1] / total_clusters
        }
    
    def plot_training_history(self, history: Dict, figsize: Tuple[int, int] = (12, 4)):
        """
        Plot training history for Information Bottleneck
        
        Args:
            history: Training history dictionary
            figsize: Figure size
        """
        if not history or 'objective' not in history:
            print("⚠️  No training history available")
            return
        
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        epochs = range(1, len(history['objective']) + 1)
        
        # Plot objective
        axes[0].plot(epochs, history['objective'], 'b-', linewidth=2, alpha=0.8)
        axes[0].set_xlabel('Iteration')
        axes[0].set_ylabel('IB Objective')
        axes[0].set_title('🎯 IB Objective')
        axes[0].grid(True, alpha=0.3)
        
        # Plot compression and relevance
        if 'compression' in history and 'relevance' in history:
            axes[1].plot(epochs, history['compression'], 'r-', linewidth=2, 
                        alpha=0.8, label='Compression I(X;Z)')
            axes[1].plot(epochs, history['relevance'], 'b-', linewidth=2, 
                        alpha=0.8, label='Relevance I(Z;Y)')
            axes[1].set_xlabel('Iteration')
            axes[1].set_ylabel('Mutual Information [bits]')
            axes[1].set_title('📊 Information Components')
            axes[1].legend()
            axes[1].grid(True, alpha=0.3)
        
        # Plot beta schedule if available
        if 'beta_values' in history:
            axes[2].semilogy(epochs, history['beta_values'], 'g-', linewidth=2, alpha=0.8)
            axes[2].set_xlabel('Iteration')
            axes[2].set_ylabel('β parameter (log scale)')
            axes[2].set_title('⚖️ β Schedule')
            axes[2].grid(True, alpha=0.3)
        else:
            axes[2].axis('off')
            axes[2].text(0.5, 0.5, 'No β schedule\nrecorded', 
                        ha='center', va='center', transform=axes[2].transAxes,
                        fontsize=12, alpha=0.5)
        
        plt.tight_layout()
        plt.show()
    
    def compare_methods(self, results_dict: Dict[str, Dict], figsize: Tuple[int, int] = (12, 8)):
        """
        Compare different IB methods or parameter settings
        
        Args:
            results_dict: Dictionary with method names as keys and results as values
            figsize: Figure size
        """
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        
        methods = list(results_dict.keys())
        colors = plt.cm.Set1(np.linspace(0, 1, len(methods)))
        
        # Extract metrics
        compressions = [results_dict[method].get('compression', 0) for method in methods]
        relevances = [results_dict[method].get('relevance', 0) for method in methods]
        objectives = [results_dict[method].get('objective', 0) for method in methods]
        betas = [results_dict[method].get('beta', 1.0) for method in methods]
        
        # 1. Information plane comparison
        for i, method in enumerate(methods):
            axes[0, 0].scatter(compressions[i], relevances[i], 
                             c=[colors[i]], s=100, alpha=0.8, 
                             label=method, edgecolors='black')
        
        axes[0, 0].set_xlabel('Compression I(X;Z)')
        axes[0, 0].set_ylabel('Relevance I(Z;Y)')
        axes[0, 0].set_title('📊 Information Plane Comparison')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Compression comparison
        bars = axes[0, 1].bar(methods, compressions, alpha=0.8, color=colors)
        axes[0, 1].set_ylabel('Compression I(X;Z)')
        axes[0, 1].set_title('🗜️ Compression Comparison')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Relevance comparison
        bars = axes[1, 0].bar(methods, relevances, alpha=0.8, color=colors)
        axes[1, 0].set_ylabel('Relevance I(Z;Y)')
        axes[1, 0].set_title('🎯 Relevance Comparison')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Objective comparison
        bars = axes[1, 1].bar(methods, objectives, alpha=0.8, color=colors)
        axes[1, 1].set_ylabel('IB Objective')
        axes[1, 1].set_title('⚖️ Objective Comparison')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print("📊 Method comparison plotted!")
        print("📈 Best compression:", methods[np.argmin(compressions)])
        print("🎯 Best relevance:", methods[np.argmax(relevances)])
        print("⚖️ Best objective:", methods[np.argmin(objectives)])