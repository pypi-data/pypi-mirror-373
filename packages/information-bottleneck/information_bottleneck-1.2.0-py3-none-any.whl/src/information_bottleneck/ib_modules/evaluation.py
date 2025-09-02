"""
📊 Information Bottleneck Evaluation and Visualization Module
===========================================================

Author: Benedict Chen (benedict@benedictchen.com)

This module contains evaluation and visualization tools for analyzing Information Bottleneck results.
It provides the famous Information Bottleneck visualizations that reveal the fundamental trade-offs
between compression and prediction in learned representations.

🎯 Key Features:
- Information Bottleneck curve generation and plotting
- Information plane trajectory visualization 
- Cluster analysis and purity metrics
- Comprehensive theoretical interpretation tools

🔬 Theoretical Background:
The Information Bottleneck curve shows the fundamental trade-off between:
- I(X;Z): Compression (how much input information is preserved)  
- I(Z;Y): Prediction (how much relevant information for the task is kept)

The information plane trajectory reveals how representations evolve during training,
often showing distinct phases of fitting and compression that explain generalization.

Based on: Tishby, Pereira & Bialek (1999) "The Information Bottleneck Method"
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple, Optional, List, Any
from scipy.stats import entropy
import warnings


class EvaluationMixin:
    """
    Mixin class providing evaluation and visualization capabilities for Information Bottleneck models.
    
    This mixin extends Information Bottleneck classes with comprehensive analysis tools including:
    - Information curve generation and visualization
    - Information plane trajectory plotting  
    - Cluster structure analysis
    - Theoretical interpretation utilities
    
    The mixin assumes the host class has the following attributes:
    - self.n_clusters: Number of clusters/bottleneck size
    - self.beta: Trade-off parameter
    - self.max_iter: Maximum iterations
    - self.tolerance: Convergence tolerance
    - self.training_history: Dict with training trajectory data
    - self.p_z_given_x: Learned conditional probabilities P(Z|X)
    """
    
    def get_information_curve(self, beta_values: List[float], X: np.ndarray, Y: np.ndarray) -> Dict[str, List]:
        """
        Generate the Information Bottleneck curve by training models with different β values.
        
        This produces the famous Information Bottleneck curve showing the fundamental trade-off
        between compression I(X;Z) and prediction I(Z;Y). Each point on the curve represents
        an optimal solution for a given β value, revealing the Pareto frontier of representations.
        
        🔬 Theory:
        The Information Bottleneck curve is the solution to the optimization problem:
        
            min_{P(Z|X)} [I(X;Z) - β·I(Z;Y)]
            
        For different β values, we get different optimal trade-offs:
        - β → 0: Maximum compression, minimal prediction (trivial solution Z=constant)
        - β → ∞: Maximum prediction, minimal compression (Z preserves all of X)
        - Intermediate β: Balanced solutions that extract only task-relevant information
        
        Args:
            beta_values: List of β parameters to explore the trade-off curve
            X: Input data matrix [n_samples, n_features]  
            Y: Target/relevance variable [n_samples,]
            
        Returns:
            Dict containing:
                - 'beta_values': The β parameters used
                - 'compression': I(X;Z) values for each β
                - 'prediction': I(Z;Y) values for each β  
                - 'models': Trained InformationBottleneck models for each β
                
        🎯 Usage:
            # Generate curve for β ∈ [0.1, 1.0, 10.0]
            curve = model.get_information_curve([0.1, 1.0, 10.0], X, Y)
            
            # Analyze the compression-prediction trade-off
            plt.plot(curve['compression'], curve['prediction'], 'o-')
            plt.xlabel('I(X;Z) - Compression')
            plt.ylabel('I(Z;Y) - Prediction')
        """
        
        print(f"🎯 Generating Information Bottleneck curve for β ∈ {beta_values}")
        print("   This reveals the fundamental compression-prediction trade-off...")
        
        results = {
            'beta_values': [],
            'compression': [],  # I(X;Z) - How much input information is preserved
            'prediction': [],   # I(Z;Y) - How much task-relevant information is kept
            'models': []       # Trained models for further analysis
        }
        
        # Import here to avoid circular dependencies
        from .information_bottleneck_core import InformationBottleneck
        
        for i, beta in enumerate(beta_values):
            print(f"\n   [{i+1}/{len(beta_values)}] Training with β = {beta}...")
            
            # Create new model with current beta value
            ib_model = InformationBottleneck(
                n_clusters=self.n_clusters,
                beta=beta,
                max_iter=self.max_iter,
                tolerance=self.tolerance,
                random_seed=42  # Fixed seed for reproducible curves
            )
            
            # Train the model
            try:
                train_results = ib_model.fit(X, Y, use_annealing=True)
                
                # Store results
                results['beta_values'].append(beta)
                results['compression'].append(train_results['final_compression'])
                results['prediction'].append(train_results['final_prediction'])
                results['models'].append(ib_model)
                
                print(f"      ✓ I(X;Z) = {train_results['final_compression']:.4f} bits")
                print(f"        I(Z;Y) = {train_results['final_prediction']:.4f} bits")
                
            except Exception as e:
                print(f"      ⚠️  Training failed for β={beta}: {str(e)}")
                # Continue with other β values
                continue
        
        if len(results['beta_values']) == 0:
            raise ValueError("No models converged successfully. Try different β values or check data.")
            
        print(f"\n✅ Successfully generated curve with {len(results['beta_values'])} points")
        return results
    
    def plot_information_curve(self, beta_values: List[float], X: np.ndarray, Y: np.ndarray,
                             figsize: Tuple[int, int] = (14, 10), save_path: Optional[str] = None):
        """
        Plot comprehensive Information Bottleneck analysis including the famous IB curve.
        
        This creates a multi-panel visualization showing:
        1. The Information Bottleneck curve I(Z;Y) vs I(X;Z) - the main theoretical result
        2. Information terms vs β showing how compression and prediction vary  
        3. Compression efficiency revealing optimal operating points
        4. IB objective function values for optimization verification
        
        🔬 Theoretical Interpretation:
        
        Panel 1 - Information Bottleneck Curve:
        The curve shows the Pareto frontier of optimal representations. Each point represents
        the best possible trade-off between compression and prediction for a given β.
        - Steep regions: Small changes in β cause large changes in the trade-off
        - Flat regions: Trade-off is insensitive to β (phase transitions)
        - Concave shape: Diminishing returns - gaining prediction requires exponentially more compression
        
        Panel 2 - Information vs β:  
        Shows how I(X;Z) and I(Z;Y) change with the trade-off parameter β.
        - Low β: Dominates compression, I(X;Z) is minimized
        - High β: Dominates prediction, I(Z;Y) is maximized
        - Critical β: Phase transitions where behavior changes dramatically
        
        Args:
            beta_values: List of β parameters to explore
            X: Input data matrix [n_samples, n_features]
            Y: Target variable [n_samples,]  
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save the figure
            
        🎯 Usage:
            # Comprehensive analysis with multiple β values
            betas = np.logspace(-2, 2, 10)  # β from 0.01 to 100
            model.plot_information_curve(betas, X, Y)
            
            # Focus on specific β range where interesting behavior occurs
            model.plot_information_curve([0.1, 0.5, 1.0, 2.0, 5.0], X, Y)
        """
        
        # Generate the information curve data
        print("🎨 Creating comprehensive Information Bottleneck visualization...")
        curve_results = self.get_information_curve(beta_values, X, Y)
        
        # Create the multi-panel figure
        fig = plt.figure(figsize=figsize)
        
        # Create a 2x2 grid with improved spacing
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])  
        ax3 = fig.add_subplot(gs[1, 0])
        ax4 = fig.add_subplot(gs[1, 1])
        
        # Panel 1: The Famous Information Bottleneck Curve
        ax1.plot(curve_results['compression'], curve_results['prediction'], 'o-', 
                linewidth=3, markersize=10, alpha=0.8, color='darkblue',
                markerfacecolor='lightblue', markeredgecolor='darkblue', markeredgewidth=2)
        
        # Annotate β values on the curve
        for i, beta in enumerate(curve_results['beta_values']):
            ax1.annotate(f'β={beta}', 
                        (curve_results['compression'][i], curve_results['prediction'][i]),
                        xytext=(8, 8), textcoords='offset points', fontsize=9,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', color='black', alpha=0.6))
        
        ax1.set_xlabel('I(X;Z) - Compression (bits) →', fontsize=12, fontweight='bold')
        ax1.set_ylabel('I(Z;Y) - Prediction (bits) →', fontsize=12, fontweight='bold')  
        ax1.set_title('🏆 Information Bottleneck Curve\n(The Pareto Frontier of Representations)', 
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#f8f9fa')
        
        # Panel 2: Information Terms vs β
        ax2.semilogx(curve_results['beta_values'], curve_results['compression'], 
                    'b-o', label='I(X;Z) - Compression', alpha=0.8, linewidth=2, markersize=8)
        ax2.semilogx(curve_results['beta_values'], curve_results['prediction'], 
                    'r-o', label='I(Z;Y) - Prediction', alpha=0.8, linewidth=2, markersize=8)
        
        ax2.set_xlabel('β (log scale) →', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Mutual Information (bits)', fontsize=12, fontweight='bold')
        ax2.set_title('📊 Information Terms vs Trade-off Parameter', fontsize=14, fontweight='bold')
        ax2.legend(frameon=True, fancybox=True, shadow=True)
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#f8f9fa')
        
        # Panel 3: Compression Efficiency Analysis
        max_compression = max(curve_results['compression']) if curve_results['compression'] else 1
        compression_ratios = [max_compression / comp if comp > 1e-10 else float('inf') 
                            for comp in curve_results['compression']]
        
        ax3.semilogx(curve_results['beta_values'], compression_ratios, 'g-o', 
                    alpha=0.8, linewidth=2, markersize=8, color='darkgreen',
                    markerfacecolor='lightgreen', markeredgecolor='darkgreen')
        
        ax3.set_xlabel('β (log scale) →', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Compression Ratio', fontsize=12, fontweight='bold')
        ax3.set_title('🗜️  Compression Efficiency Analysis', fontsize=14, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.set_facecolor('#f8f9fa')
        
        # Panel 4: Information Bottleneck Objective Function
        objectives = [comp - beta * pred for comp, pred, beta in 
                     zip(curve_results['compression'], curve_results['prediction'], curve_results['beta_values'])]
        
        ax4.semilogx(curve_results['beta_values'], objectives, 'm-o', 
                    alpha=0.8, linewidth=2, markersize=8, color='purple',
                    markerfacecolor='plum', markeredgecolor='purple')
        
        ax4.set_xlabel('β (log scale) →', fontsize=12, fontweight='bold')
        ax4.set_ylabel('IB Objective: I(X;Z) - β·I(Z;Y)', fontsize=12, fontweight='bold')
        ax4.set_title('🎯 Information Bottleneck Objective', fontsize=14, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.set_facecolor('#f8f9fa')
        
        # Add overall figure title
        fig.suptitle('Information Bottleneck Analysis: The Theory That Explains Representation Learning', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"💾 Figure saved to: {save_path}")
        
        plt.show()
        
        # Print comprehensive analysis
        print(f"\n📊 Information Bottleneck Curve Analysis:")
        print(f"   🎯 β range explored: {min(curve_results['beta_values']):.3f} → {max(curve_results['beta_values']):.3f}")
        
        if compression_ratios:
            max_ratio_idx = np.argmax([r for r in compression_ratios if r != float('inf')] or [0])
            print(f"   🗜️  Maximum compression: {max(compression_ratios):.2f}x at β={curve_results['beta_values'][max_ratio_idx]}")
        
        max_pred_idx = np.argmax(curve_results['prediction'])
        print(f"   🎯 Maximum prediction: {max(curve_results['prediction']):.4f} bits at β={curve_results['beta_values'][max_pred_idx]}")
        print(f"   ⚖️  Balanced trade-off: I(X;Z)={np.mean(curve_results['compression']):.3f}, I(Z;Y)={np.mean(curve_results['prediction']):.3f}")
        
        # Identify critical β values (phase transitions)
        if len(curve_results['beta_values']) > 2:
            compression_changes = np.diff(curve_results['compression'])
            prediction_changes = np.diff(curve_results['prediction'])
            critical_indices = np.where(np.abs(compression_changes) > np.std(compression_changes))[0]
            
            if len(critical_indices) > 0:
                print(f"   ⚡ Critical β values (potential phase transitions): {[curve_results['beta_values'][i] for i in critical_indices]}")
        
        print(f"   ✨ Curve reveals the fundamental limits of representation learning!")
        
        return curve_results
    
    def plot_information_plane(self, figsize: Tuple[int, int] = (14, 8), save_path: Optional[str] = None):
        """
        Plot the information plane trajectory showing how representations evolve during training.
        
        This creates the famous information plane plot that reveals the learning dynamics
        in the I(X;Z) vs I(Z;Y) space. The trajectory shows how the representation moves
        through different phases during optimization, often revealing distinct fitting
        and compression phases that explain generalization.
        
        🔬 Theoretical Significance:
        
        The information plane trajectory reveals fundamental insights about learning:
        
        1. **Fitting Phase**: Early training increases both I(X;Z) and I(Z;Y)
           - Network learns to represent input patterns
           - Both compression and prediction improve simultaneously
        
        2. **Compression Phase**: Later training may reduce I(X;Z) while maintaining I(Z;Y)  
           - Network "forgets" irrelevant information
           - Generalization through compression of non-predictive features
           
        3. **Phase Transitions**: Abrupt changes in trajectory direction
           - Critical points where learning dynamics change
           - Often correspond to changes in generalization behavior
           
        The shape and phases of this trajectory explain why networks generalize well
        and provide insights into optimal stopping criteria and architecture design.
        
        Args:
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save the figure
            
        Returns:
            None (displays plot)
            
        🎯 Usage:
            # Plot trajectory after training
            model.fit(X, Y)
            model.plot_information_plane()
            
            # Save for analysis
            model.plot_information_plane(save_path='info_plane_trajectory.png')
            
        ⚠️  Requires:
            - self.training_history with 'mutual_info_xz' and 'mutual_info_zy' keys
            - Model must be trained before calling this method
        """
        
        if not hasattr(self, 'training_history') or not self.training_history:
            raise ValueError("No training history found. Model must be trained before plotting information plane.")
        
        required_keys = ['mutual_info_xz', 'mutual_info_zy']
        missing_keys = [key for key in required_keys if key not in self.training_history]
        if missing_keys:
            raise ValueError(f"Training history missing required keys: {missing_keys}")
        
        print("🎨 Creating Information Plane trajectory visualization...")
        print("   This shows how representations evolve during training in I(X;Z) vs I(Z;Y) space...")
        
        # Create figure with two panels  
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Extract trajectory data
        I_XZ = self.training_history['mutual_info_xz']
        I_ZY = self.training_history['mutual_info_zy']
        
        if len(I_XZ) == 0 or len(I_ZY) == 0:
            raise ValueError("Empty training trajectory. Ensure training history is properly recorded.")
        
        # Panel 1: Information Plane Trajectory
        # Plot the trajectory line
        ax1.plot(I_XZ, I_ZY, '-', alpha=0.6, linewidth=2, color='darkblue', label='Training trajectory')
        
        # Mark key points
        ax1.scatter(I_XZ[0], I_ZY[0], color='green', s=150, marker='o', 
                   label='Start', zorder=5, edgecolors='darkgreen', linewidth=2)
        ax1.scatter(I_XZ[-1], I_ZY[-1], color='red', s=150, marker='s', 
                   label='End', zorder=5, edgecolors='darkred', linewidth=2)
        
        # Add intermediate milestone markers
        n_points = len(I_XZ)
        if n_points > 10:
            milestone_indices = np.linspace(1, n_points-2, min(5, n_points-2), dtype=int)
            ax1.scatter([I_XZ[i] for i in milestone_indices], [I_ZY[i] for i in milestone_indices],
                       color='orange', s=50, alpha=0.7, zorder=4, marker='o')
        
        # Add directional arrows to show trajectory flow
        arrow_step = max(1, len(I_XZ) // 8)  # Show ~8 arrows max
        for i in range(0, len(I_XZ)-1, arrow_step):
            if i + arrow_step < len(I_XZ):
                dx = I_XZ[i + arrow_step] - I_XZ[i]
                dy = I_ZY[i + arrow_step] - I_ZY[i]
                
                # Only draw arrow if movement is significant
                if np.sqrt(dx**2 + dy**2) > 1e-6:
                    ax1.arrow(I_XZ[i], I_ZY[i], dx*0.3, dy*0.3,
                             head_width=0.01, head_length=0.01, 
                             fc='blue', ec='blue', alpha=0.6, zorder=3)
        
        ax1.set_xlabel('I(X;Z) - Compression (bits) →', fontsize=12, fontweight='bold')
        ax1.set_ylabel('I(Z;Y) - Prediction (bits) →', fontsize=12, fontweight='bold')
        ax1.set_title(f'🌌 Information Plane Trajectory\n(β = {self.beta}, Learning Dynamics)', 
                     fontsize=14, fontweight='bold')
        ax1.legend(frameon=True, fancybox=True, shadow=True)
        ax1.grid(True, alpha=0.3)
        ax1.set_facecolor('#f8f9fa')
        
        # Panel 2: Training Curves Over Time
        iterations = range(len(I_XZ))
        
        # Create twin axes for different scales
        ax2_twin = ax2.twinx()
        
        # Plot both information terms
        line1 = ax2.plot(iterations, I_XZ, 'b-', label='I(X;Z) - Compression', 
                        alpha=0.8, linewidth=2)
        line2 = ax2_twin.plot(iterations, I_ZY, 'r-', label='I(Z;Y) - Prediction', 
                             alpha=0.8, linewidth=2)
        
        # Style the axes
        ax2.set_xlabel('Training Iteration →', fontsize=12, fontweight='bold')
        ax2.set_ylabel('I(X;Z) - Compression (bits)', color='blue', fontsize=12, fontweight='bold')
        ax2_twin.set_ylabel('I(Z;Y) - Prediction (bits)', color='red', fontsize=12, fontweight='bold')
        ax2.set_title('📈 Information Evolution Over Training\n(Fitting vs Compression Phases)', 
                     fontsize=14, fontweight='bold')
        
        # Color the y-axis labels to match the lines
        ax2.tick_params(axis='y', labelcolor='blue')
        ax2_twin.tick_params(axis='y', labelcolor='red')
        
        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax2.legend(lines, labels, loc='upper right', frameon=True, fancybox=True, shadow=True)
        
        ax2.grid(True, alpha=0.3)
        ax2.set_facecolor('#f8f9fa')
        
        # Add phase annotations if clear phases are detected
        if len(I_XZ) > 10:
            # Simple phase detection: look for compression phase (decreasing I(X;Z))
            compression_changes = np.diff(I_XZ)
            compression_phase_start = None
            
            # Find where compression starts decreasing consistently
            for i in range(len(compression_changes) - 5):
                if np.mean(compression_changes[i:i+5]) < -0.001:  # Consistent decrease
                    compression_phase_start = i
                    break
            
            if compression_phase_start and compression_phase_start > len(I_XZ) // 3:
                ax2.axvline(x=compression_phase_start, color='purple', linestyle='--', alpha=0.7, linewidth=2)
                ax2.text(compression_phase_start + 1, max(I_XZ) * 0.9, 'Compression\nPhase?', 
                        fontsize=10, color='purple', fontweight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='lavender', alpha=0.8))
        
        # Overall figure formatting
        fig.suptitle('Information Plane Analysis: The Learning Journey in Information Space', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"💾 Figure saved to: {save_path}")
        
        plt.show()
        
        # Print comprehensive trajectory analysis
        print(f"\n📊 Information Plane Trajectory Analysis:")
        print(f"   🎯 Training iterations: {len(I_XZ)}")
        print(f"   🏁 Final state: I(X;Z) = {I_XZ[-1]:.4f} bits, I(Z;Y) = {I_ZY[-1]:.4f} bits")
        print(f"   📐 Trade-off parameter: β = {self.beta}")
        
        # Analyze compression and prediction changes
        compression_change = I_XZ[-1] - I_XZ[0]
        prediction_change = I_ZY[-1] - I_ZY[0]
        
        # Calculate compression ratio and prediction improvement
        compression_ratio = I_XZ[0] / I_XZ[-1] if I_XZ[-1] > 1e-10 else float('inf')
        prediction_improvement = I_ZY[-1] / I_ZY[0] if I_ZY[0] > 1e-10 else float('inf')
        
        print(f"   📉 Compression change: {compression_change:+.4f} bits")
        print(f"   📈 Prediction change: {prediction_change:+.4f} bits")
        
        if compression_ratio != float('inf'):
            print(f"   🗜️  Final compression ratio: {compression_ratio:.2f}x")
        else:
            print(f"   🗜️  Final compression ratio: ∞ (perfect compression)")
            
        if prediction_improvement != float('inf'):
            print(f"   🎯 Prediction improvement: {prediction_improvement:.2f}x")
        else:
            print(f"   🎯 Prediction improvement: ∞ (from zero baseline)")
        
        # Detect learning phases
        if len(I_XZ) > 5:
            early_compression = np.mean(I_XZ[:len(I_XZ)//3])
            late_compression = np.mean(I_XZ[2*len(I_XZ)//3:])
            
            early_prediction = np.mean(I_ZY[:len(I_ZY)//3])  
            late_prediction = np.mean(I_ZY[2*len(I_ZY)//3:])
            
            if late_compression < early_compression * 0.9 and late_prediction > early_prediction * 1.1:
                print(f"   ⚡ Detected fitting → compression phase transition!")
                print(f"      Early: I(X;Z)={early_compression:.3f}, I(Z;Y)={early_prediction:.3f}")
                print(f"      Late:  I(X;Z)={late_compression:.3f}, I(Z;Y)={late_prediction:.3f}")
            elif compression_change > 0 and prediction_change > 0:
                print(f"   📊 Fitting phase: Both compression and prediction increased")
            elif compression_change < 0 and prediction_change > 0:
                print(f"   🔄 Compression phase: Reduced compression while improving prediction")
        
        print(f"   ✨ Trajectory reveals the fundamental dynamics of representation learning!")
    
    def analyze_clusters(self, X: np.ndarray, Y: np.ndarray, detailed: bool = True):
        """
        Analyze the learned cluster structure and provide comprehensive cluster statistics.
        
        This function provides detailed analysis of the learned discrete representation Z,
        including cluster sizes, purity metrics, and information-theoretic properties.
        The analysis helps understand how the Information Bottleneck partitions the input
        space and whether the clusters capture meaningful structure for the prediction task.
        
        🔬 Theoretical Background:
        
        In the Information Bottleneck, the learned representation Z acts as a discrete
        clustering of the input space X. The quality of this clustering determines both:
        - Compression I(X;Z): How much input information is preserved
        - Prediction I(Z;Y): How much task-relevant information is captured
        
        Key metrics:
        - **Cluster Purity**: How homogeneous each cluster is w.r.t. target labels
        - **Cluster Balance**: Whether clusters have similar sizes (affects compression)
        - **Information Content**: How much information each cluster contains
        
        Args:
            X: Input data matrix [n_samples, n_features]
            Y: Target variable [n_samples,] 
            detailed: Whether to print detailed per-cluster statistics
            
        Returns:
            Dict containing cluster analysis results
            
        🎯 Usage:
            # Basic cluster analysis
            analysis = model.analyze_clusters(X, Y)
            
            # Detailed per-cluster breakdown  
            analysis = model.analyze_clusters(X, Y, detailed=True)
            
            # Access specific metrics
            print(f"Average purity: {analysis['average_purity']:.3f}")
            print(f"Cluster balance: {analysis['balance_score']:.3f}")
        """
        
        if not hasattr(self, 'p_z_given_x') or self.p_z_given_x is None:
            raise ValueError("Model must be trained before analyzing clusters. Call fit() first.")
        
        print("🔍 Analyzing learned cluster structure...")
        print("   This reveals how the Information Bottleneck partitions the input space...")
        
        # Get hard cluster assignments
        hard_assignments = np.argmax(self.p_z_given_x, axis=1)
        n_samples = len(hard_assignments)
        
        # Basic cluster statistics
        cluster_sizes = np.bincount(hard_assignments, minlength=self.n_clusters)
        non_empty_clusters = np.sum(cluster_sizes > 0)
        
        print(f"\n📊 Cluster Structure Overview:")
        print(f"   🎯 Number of clusters (K): {self.n_clusters}")
        print(f"   ✅ Active clusters: {non_empty_clusters}/{self.n_clusters}")
        print(f"   📏 Total samples: {n_samples}")
        print(f"   📊 Cluster sizes: {cluster_sizes.tolist()}")
        
        # Calculate cluster balance (entropy of cluster size distribution)
        cluster_probs = cluster_sizes / n_samples
        cluster_probs = cluster_probs[cluster_probs > 0]  # Remove empty clusters
        balance_entropy = entropy(cluster_probs, base=2)
        max_balance_entropy = np.log2(non_empty_clusters) if non_empty_clusters > 1 else 1
        balance_score = balance_entropy / max_balance_entropy if max_balance_entropy > 0 else 1
        
        print(f"   ⚖️  Cluster balance score: {balance_score:.3f} (1.0 = perfectly balanced)")
        
        # Analyze cluster purity w.r.t. target labels
        unique_labels = np.unique(Y)
        n_labels = len(unique_labels)
        
        cluster_purities = []
        cluster_entropies = []
        cluster_info = []
        
        print(f"\n🎯 Cluster Purity Analysis (w.r.t. {n_labels} target classes):")
        
        for z in range(self.n_clusters):
            cluster_mask = (hard_assignments == z)
            cluster_size = np.sum(cluster_mask)
            
            if cluster_size == 0:
                if detailed:
                    print(f"   📭 Cluster {z}: Empty cluster")
                cluster_purities.append(0.0)
                cluster_entropies.append(0.0)
                cluster_info.append({
                    'size': 0,
                    'purity': 0.0,
                    'entropy': 0.0,
                    'dominant_label': None,
                    'label_distribution': {}
                })
                continue
            
            # Analyze label distribution in this cluster
            cluster_labels = Y[cluster_mask]
            label_counts = np.bincount(cluster_labels, minlength=n_labels)
            label_probs = label_counts / cluster_size
            
            # Calculate purity (fraction of dominant class)
            dominant_label_idx = np.argmax(label_counts)
            purity = np.max(label_counts) / cluster_size
            
            # Calculate cluster entropy
            cluster_entropy = entropy(label_probs[label_probs > 0], base=2)
            
            cluster_purities.append(purity)
            cluster_entropies.append(cluster_entropy)
            
            # Store detailed info
            label_dist = {int(unique_labels[i]): int(label_counts[i]) for i in range(n_labels) if label_counts[i] > 0}
            cluster_info.append({
                'size': int(cluster_size),
                'purity': purity,
                'entropy': cluster_entropy,
                'dominant_label': int(unique_labels[dominant_label_idx]),
                'label_distribution': label_dist
            })
            
            if detailed:
                print(f"   🏷️  Cluster {z}: {cluster_size:4d} samples, purity={purity:.3f}, "
                      f"entropy={cluster_entropy:.3f}, dominant_class={unique_labels[dominant_label_idx]}")
                if cluster_size <= 20:  # Show distribution for small clusters
                    print(f"        Label distribution: {label_dist}")
        
        # Overall purity statistics
        valid_purities = [p for p in cluster_purities if p > 0]
        if valid_purities:
            avg_purity = np.mean(valid_purities)
            weighted_avg_purity = np.average(cluster_purities, weights=cluster_sizes)
        else:
            avg_purity = weighted_avg_purity = 0.0
            
        valid_entropies = [e for e in cluster_entropies if e >= 0]
        avg_entropy = np.mean(valid_entropies) if valid_entropies else 0.0
        
        print(f"\n📈 Overall Cluster Quality:")
        print(f"   🎯 Average purity: {avg_purity:.3f} (higher is better)")
        print(f"   ⚖️  Weighted average purity: {weighted_avg_purity:.3f}")
        print(f"   📊 Average cluster entropy: {avg_entropy:.3f} bits (lower is better)")
        print(f"   🎲 Maximum possible entropy: {np.log2(n_labels):.3f} bits")
        
        # Information-theoretic analysis of clustering
        if n_samples > 0:
            # Calculate mutual information between clusters and labels
            cluster_label_contingency = np.zeros((self.n_clusters, n_labels))
            for z in range(self.n_clusters):
                for y_idx, y_val in enumerate(unique_labels):
                    cluster_label_contingency[z, y_idx] = np.sum(
                        (hard_assignments == z) & (Y == y_val)
                    )
            
            # Normalize to get joint probabilities
            P_zy = cluster_label_contingency / n_samples
            P_z = np.sum(P_zy, axis=1)  # Marginal cluster probabilities
            P_y = np.sum(P_zy, axis=0)  # Marginal label probabilities
            
            # Calculate I(Z;Y) empirically from contingency table
            I_zy_empirical = 0.0
            for z in range(self.n_clusters):
                for y in range(n_labels):
                    if P_zy[z, y] > 0 and P_z[z] > 0 and P_y[y] > 0:
                        I_zy_empirical += P_zy[z, y] * np.log2(P_zy[z, y] / (P_z[z] * P_y[y]))
            
            print(f"   🔗 I(Z;Y) from clustering: {I_zy_empirical:.4f} bits")
            print(f"   📊 Clustering efficiency: {I_zy_empirical/np.log2(n_labels)*100:.1f}% of max possible")
        
        # Compile results
        analysis_results = {
            'n_clusters': self.n_clusters,
            'active_clusters': non_empty_clusters,
            'cluster_sizes': cluster_sizes.tolist(),
            'balance_score': balance_score,
            'cluster_purities': cluster_purities,
            'cluster_entropies': cluster_entropies,
            'average_purity': avg_purity,
            'weighted_average_purity': weighted_avg_purity,
            'average_entropy': avg_entropy,
            'cluster_info': cluster_info,
            'mutual_info_zy_empirical': I_zy_empirical if 'I_zy_empirical' in locals() else None
        }
        
        print(f"   ✨ Clustering reveals the learned discrete representation structure!")
        
        return analysis_results
    
    def plot_cluster_visualization(self, X: np.ndarray, Y: np.ndarray, 
                                 method: str = 'pca', figsize: Tuple[int, int] = (12, 8),
                                 save_path: Optional[str] = None):
        """
        Visualize the learned clusters in 2D space using dimensionality reduction.
        
        This creates a comprehensive visualization showing:
        1. Data points colored by learned clusters
        2. Data points colored by true labels  
        3. Cluster boundaries and statistics
        
        Args:
            X: Input data matrix [n_samples, n_features]
            Y: Target variable [n_samples,]
            method: Dimensionality reduction method ('pca', 'tsne', 'umap')
            figsize: Figure size (width, height) in inches
            save_path: Optional path to save the figure
        """
        
        if not hasattr(self, 'p_z_given_x') or self.p_z_given_x is None:
            raise ValueError("Model must be trained before visualizing clusters. Call fit() first.")
        
        print(f"🎨 Creating cluster visualization using {method.upper()}...")
        
        # Dimensionality reduction for visualization
        if method.lower() == 'pca':
            from sklearn.decomposition import PCA
            reducer = PCA(n_components=2, random_state=42)
        elif method.lower() == 'tsne':
            from sklearn.manifold import TSNE
            reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(X)-1))
        elif method.lower() == 'umap':
            try:
                import umap
                reducer = umap.UMAP(n_components=2, random_state=42)
            except ImportError:
                print("⚠️  UMAP not available, falling back to PCA")
                from sklearn.decomposition import PCA
                reducer = PCA(n_components=2, random_state=42)
                method = 'pca'
        else:
            raise ValueError(f"Unknown dimensionality reduction method: {method}")
        
        # Fit and transform data
        X_2d = reducer.fit_transform(X)
        
        # Get cluster assignments
        hard_assignments = np.argmax(self.p_z_given_x, axis=1)
        
        # Create visualization
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=figsize)
        
        # Panel 1: Clusters colored by learned assignments
        scatter1 = ax1.scatter(X_2d[:, 0], X_2d[:, 1], c=hard_assignments, 
                              cmap='tab10', alpha=0.7, s=50)
        ax1.set_title(f'Learned Clusters (K={self.n_clusters})\n{method.upper()} Projection', 
                     fontsize=12, fontweight='bold')
        ax1.set_xlabel(f'{method.upper()}_1')
        ax1.set_ylabel(f'{method.upper()}_2')
        ax1.grid(True, alpha=0.3)
        plt.colorbar(scatter1, ax=ax1, label='Cluster ID')
        
        # Panel 2: Points colored by true labels
        scatter2 = ax2.scatter(X_2d[:, 0], X_2d[:, 1], c=Y, 
                              cmap='viridis', alpha=0.7, s=50)
        ax2.set_title(f'True Labels\n{method.upper()} Projection', 
                     fontsize=12, fontweight='bold')
        ax2.set_xlabel(f'{method.upper()}_1')
        ax2.set_ylabel(f'{method.upper()}_2')
        ax2.grid(True, alpha=0.3)
        plt.colorbar(scatter2, ax=ax2, label='True Label')
        
        # Panel 3: Cluster-label agreement visualization
        # Create a combined color scheme showing cluster-label agreement
        unique_labels = np.unique(Y)
        n_labels = len(unique_labels)
        
        agreement_colors = []
        for i, (cluster, label) in enumerate(zip(hard_assignments, Y)):
            # Find dominant label for this cluster
            cluster_mask = (hard_assignments == cluster)
            if np.sum(cluster_mask) > 0:
                cluster_labels = Y[cluster_mask]
                dominant_label = np.bincount(cluster_labels).argmax()
                
                # Color based on whether point agrees with cluster's dominant label
                if label == dominant_label:
                    agreement_colors.append(1.0)  # Agreement
                else:
                    agreement_colors.append(0.0)  # Disagreement
            else:
                agreement_colors.append(0.5)  # Neutral
        
        scatter3 = ax3.scatter(X_2d[:, 0], X_2d[:, 1], c=agreement_colors, 
                              cmap='RdYlGn', alpha=0.7, s=50, vmin=0, vmax=1)
        ax3.set_title(f'Cluster-Label Agreement\n{method.upper()} Projection', 
                     fontsize=12, fontweight='bold')
        ax3.set_xlabel(f'{method.upper()}_1')
        ax3.set_ylabel(f'{method.upper()}_2')
        ax3.grid(True, alpha=0.3)
        
        # Custom colorbar for agreement
        cbar3 = plt.colorbar(scatter3, ax=ax3)
        cbar3.set_label('Agreement')
        cbar3.set_ticks([0, 1])
        cbar3.set_ticklabels(['Disagree', 'Agree'])
        
        # Overall figure formatting
        fig.suptitle(f'Information Bottleneck Cluster Analysis (β={self.beta})', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"💾 Figure saved to: {save_path}")
        
        plt.show()
        
        # Print visualization summary
        agreement_score = np.mean(agreement_colors)
        print(f"\n📊 Cluster Visualization Analysis:")
        print(f"   🎯 Dimensionality reduction: {method.upper()}")
        print(f"   ✅ Cluster-label agreement: {agreement_score:.3f} (1.0 = perfect)")
        print(f"   📊 Visualization reveals spatial cluster structure!")