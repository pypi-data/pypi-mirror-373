import torch
from typing import Dict, Any, Optional, List
import torch.nn.functional as F
import numpy as np  # Import numpy for mean calculation
import logging  # Import logging
import time  # Import time
import datetime  # Import datetime

from clt.config import TrainingConfig, CLTConfig  # Ensure these are imported for type hints
from clt.models.clt import CrossLayerTranscoder

# Configure logging
logger = logging.getLogger(__name__)


# Helper function to format elapsed time
def _format_elapsed_time(seconds: float) -> str:
    """Formats elapsed seconds into HH:MM:SS or MM:SS."""
    td = datetime.timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if td.days > 0 or hours > 0:
        return f"{td.days * 24 + hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"


class CLTEvaluator:
    """Handles evaluation metrics computation for the CLT model."""

    def __init__(
        self,
        model: CrossLayerTranscoder,
        device: torch.device,
        start_time: Optional[float] = None,
        mean_tg: Optional[Dict[int, torch.Tensor]] = None,
        std_tg: Optional[Dict[int, torch.Tensor]] = None,
        normalization_method: str = "none",
        d_model: Optional[int] = None,
    ):
        """Initialize the evaluator.

        Args:
            model: The CrossLayerTranscoder model to evaluate.
            device: The device to perform computations on.
            start_time: The initial time.time() from the trainer for elapsed time logging.
            mean_tg: Optional dictionary of per-layer target means for de-normalising outputs.
            std_tg: Optional dictionary of per-layer target stds for de-normalising outputs.
            normalization_method: The normalization method being used.
            d_model: Model dimension for sqrt_d_model normalization.
        """
        self.model = model
        self.device = device
        self.start_time = start_time or time.time()  # Store start time
        # Store normalisation stats if provided
        self.mean_tg = mean_tg or {}
        self.std_tg = std_tg or {}
        
        # Validate normalization method
        valid_norm_methods = ["none", "mean_std", "sqrt_d_model"]
        if normalization_method not in valid_norm_methods:
            raise ValueError(
                f"Invalid normalization_method: {normalization_method}. "
                f"Must be one of {valid_norm_methods}"
            )
        self.normalization_method = normalization_method
        self.d_model = d_model
        self.metrics_history: List[Dict[str, Any]] = []  # For storing metrics over time if needed

    @staticmethod
    def _log_density(density: torch.Tensor, eps: float = 1e-10) -> torch.Tensor:
        """Computes log10 density, adding epsilon for numerical stability."""
        # .detach().cpu() is removed as subsequent processing might need gradients or specific device
        return torch.log10(density + eps)

    @staticmethod
    def _calculate_aggregate_metric(
        per_layer_data: Dict[str, List[float]],
    ) -> Optional[float]:
        """Helper to calculate the mean of a metric across all layers' features."""
        all_values: List[float] = []  # Type hint for clarity
        for layer_key in per_layer_data:
            all_values.extend(per_layer_data[layer_key])
        if not all_values:
            return None
        return float(np.mean(all_values))

    @staticmethod
    def _calculate_aggregate_histogram_data(
        per_layer_data: Dict[str, List[float]],
    ) -> List[float]:
        """Helper to flatten metric data from all layers for an aggregate histogram."""
        all_values: List[float] = []
        for layer_key in per_layer_data:
            all_values.extend(per_layer_data[layer_key])
        return all_values

    @torch.no_grad()
    def compute_metrics(
        self,
        inputs: Dict[int, torch.Tensor],
        targets: Dict[int, torch.Tensor],
        dead_neuron_mask: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """Compute all evaluation metrics for the given batch with structured keys.

        Args:
            inputs: Dictionary mapping layer indices to input activations.
            targets: Dictionary mapping layer indices to target activations.
            dead_neuron_mask: Optional mask indicating dead neurons based on trainer's window.

        Returns:
            Dictionary containing computed metrics structured for WandB logging.
            Metrics are organized into 'reconstruction', 'sparsity', 'dead_features',
            'layerwise'.
        """
        mem_before_eval = 0.0
        if torch.cuda.is_available() and self.device.type == "cuda":
            mem_before_eval = torch.cuda.memory_allocated(self.device) / (1024**2)
            elapsed_str = _format_elapsed_time(time.time() - self.start_time)
            logger.debug(f"Eval - Start [{elapsed_str}]. Mem: {mem_before_eval:.2f} MB")

        # Ensure data is on the correct device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        targets = {k: v.to(self.device) for k, v in targets.items()}

        # Get model outputs (reconstructions and feature activations)
        reconstructions = self.model(inputs)
        feature_activations = self.model.get_feature_activations(inputs)

        # --- Compute Metrics ---
        sparsity_metrics = self._compute_sparsity(feature_activations)
        reconstruction_metrics = self._compute_reconstruction_metrics(targets, reconstructions)
        density_metrics = self._compute_feature_density(feature_activations)
        # Compute layerwise dead features based on the provided mask
        dead_neuron_metrics = self._compute_dead_neuron_metrics(dead_neuron_mask)

        # --- Calculate Aggregate Metrics & Histograms ---
        log_feature_density_layerwise = density_metrics.get("layerwise/log_feature_density", {})
        consistent_activation_heuristic_layerwise = density_metrics.get("layerwise/consistent_activation_heuristic", {})

        # Calculate aggregate mean values
        feature_density_mean = self._calculate_aggregate_metric(log_feature_density_layerwise)
        consistent_activation_heuristic_mean = self._calculate_aggregate_metric(
            consistent_activation_heuristic_layerwise
        )

        # Calculate aggregate histogram data (flattened lists)
        log_feature_density_agg_hist_data = self._calculate_aggregate_histogram_data(log_feature_density_layerwise)
        consistent_activation_heuristic_agg_hist_data = self._calculate_aggregate_histogram_data(
            consistent_activation_heuristic_layerwise
        )

        # Add aggregate metrics to sparsity section
        if feature_density_mean is not None:
            sparsity_metrics["sparsity/feature_density_mean"] = feature_density_mean
        if consistent_activation_heuristic_mean is not None:
            sparsity_metrics["sparsity/consistent_activation_heuristic_mean"] = consistent_activation_heuristic_mean
        # Add aggregate histogram data
        if log_feature_density_agg_hist_data:
            sparsity_metrics["sparsity/log_feature_density_agg_hist"] = log_feature_density_agg_hist_data
        if consistent_activation_heuristic_agg_hist_data:
            sparsity_metrics["sparsity/consistent_activation_heuristic_agg_hist"] = (
                consistent_activation_heuristic_agg_hist_data
            )

        # Calculate total dead features from layerwise eval data
        total_dead_eval = sum(dead_neuron_metrics.get("layerwise/dead_features", {}).values())
        dead_neuron_metrics["dead_features/total_eval"] = total_dead_eval

        # --- Combine results into structured dictionary ---
        all_metrics = {
            **reconstruction_metrics,
            **sparsity_metrics,
            **density_metrics,  # Contains the layerwise density/heuristic data
            **dead_neuron_metrics,  # Contains layerwise dead features and total eval dead features
        }
        # Explicitly delete intermediate tensors to potentially free memory sooner
        del reconstructions
        del feature_activations
        # Optionally empty cache, though it has a performance cost
        # if torch.cuda.is_available():
        #     torch.cuda.empty_cache()

        if torch.cuda.is_available() and self.device.type == "cuda":
            mem_after_eval = torch.cuda.memory_allocated(self.device) / (1024**2)
            elapsed_str = _format_elapsed_time(time.time() - self.start_time)
            logger.debug(
                f"Eval - End [{elapsed_str}]. Mem: {mem_after_eval:.2f} MB (+{mem_after_eval - mem_before_eval:.2f} MB)"
            )

        return all_metrics

    def _compute_sparsity(self, activations: Dict[int, torch.Tensor]) -> Dict[str, Any]:
        """Compute L0 sparsity metrics with structured keys.

        Args:
            activations: Dictionary mapping layer indices to feature activations.

        Returns:
            Dictionary with L0 stats under 'sparsity/' and 'layerwise/l0/' keys.
        """
        if not activations or not any(v.numel() > 0 for v in activations.values()):
            if not self.model.world_size > 1 or self.model.rank == 0:
                logger.warning("Warning: Received empty activations for sparsity computation. " "Returning zeros.")
            return {
                "sparsity/total_l0": 0.0,
                "sparsity/avg_l0": 0.0,
                "sparsity/sparsity_fraction": 1.0,  # Renamed from 'sparsity'
                "layerwise/l0": {f"layer_{i}": 0.0 for i in range(self.model.config.num_layers)},
            }

        per_layer_l0_dict = {}
        total_l0 = 0.0
        num_valid_layers = 0

        for layer_idx, layer_activations in activations.items():
            # layer_activations shape: [num_tokens, num_features]
            if layer_activations.numel() == 0 or layer_activations.shape[0] == 0:
                per_layer_l0_dict[f"layer_{layer_idx}"] = 0.0
                continue

            # Count active features per token, then average across tokens
            active_count_per_token = (layer_activations != 0).float().sum(dim=-1)
            avg_active_this_layer = active_count_per_token.mean().item()

            per_layer_l0_dict[f"layer_{layer_idx}"] = avg_active_this_layer
            total_l0 += avg_active_this_layer
            num_valid_layers += 1

        avg_l0 = total_l0 / num_valid_layers if num_valid_layers > 0 else 0.0
        # Use total avg L0 across layers for sparsity fraction calculation
        total_possible_features_per_token = self.model.config.num_features
        sparsity_fraction = (
            1.0 - (avg_l0 / total_possible_features_per_token) if total_possible_features_per_token > 0 else 1.0
        )
        sparsity_fraction = max(0.0, min(1.0, sparsity_fraction))

        return {
            "sparsity/total_l0": total_l0,
            "sparsity/avg_l0": avg_l0,
            "sparsity/sparsity_fraction": sparsity_fraction,  # Renamed for clarity
            "layerwise/l0": per_layer_l0_dict,
        }

    def _compute_reconstruction_metrics(
        self,
        targets: Dict[int, torch.Tensor],
        reconstructions: Dict[int, torch.Tensor],
    ) -> Dict[str, float]:
        """Compute explained variance and MSE with structured keys.

        If normalisation statistics were provided, this method first *de-normalises*
        both the targets and reconstructions before computing metrics.

        Args:
            targets: Dictionary mapping layer indices to target activations.
            reconstructions: Dictionary mapping layer indices to reconstructed activations.

        Returns:
            Dictionary with 'reconstruction/explained_variance' and 'reconstruction/normalized_mean_reconstruction_error'.
        """
        total_explained_variance = 0.0
        total_nmse = 0.0
        num_layers = 0
        
        # For layerwise metrics
        layerwise_nmse = {}
        layerwise_explained_variance = {}

        for layer_idx, target_act in targets.items():
            if layer_idx not in reconstructions:
                continue

            recon_act = reconstructions[layer_idx]

            # --- De-normalise based on normalization method ---
            target_act_denorm = target_act
            recon_act_denorm = recon_act
            
            if self.normalization_method == "mean_std" and layer_idx in self.mean_tg and layer_idx in self.std_tg:
                # Standard denormalization: x * std + mean
                mean = self.mean_tg[layer_idx].to(recon_act.device, recon_act.dtype)
                std = self.std_tg[layer_idx].to(recon_act.device, recon_act.dtype)
                # Ensure broadcast shape
                target_act_denorm = target_act * std + mean
                recon_act_denorm = recon_act * std + mean
            elif self.normalization_method == "sqrt_d_model" and self.d_model is not None:
                # sqrt_d_model denormalization: x / sqrt(d_model)
                sqrt_d_model = (self.d_model ** 0.5)
                target_act_denorm = target_act / sqrt_d_model
                recon_act_denorm = recon_act / sqrt_d_model
            # --- End De-normalisation ---

            # Ensure shapes match (flatten if necessary) and up-cast to float32 for numerically stable metrics
            target_flat = target_act_denorm.view(-1, target_act_denorm.shape[-1]).float()
            recon_flat = recon_act_denorm.view(-1, recon_act_denorm.shape[-1]).float()

            if target_flat.shape != recon_flat.shape or target_flat.numel() == 0:
                continue

            # Calculate MSE (de-normalized)
            mse_layer = F.mse_loss(recon_flat, target_flat, reduction="mean").item()

            # Calculate Explained Variance (EV) - uses de-normalized values
            target_variance_layer = torch.var(target_flat, dim=0, unbiased=False).mean().item()
            error_variance_layer = torch.var(target_flat - recon_flat, dim=0, unbiased=False).mean().item()

            explained_variance_layer = 0.0
            if target_variance_layer > 1e-9:  # Avoid division by zero or near-zero
                explained_variance_layer = 1.0 - (error_variance_layer / target_variance_layer)
            else:
                # If target variance is zero, EV is 1 if error is also zero, else 0 or undefined.
                # Let's be consistent: if target var is ~0, EV is 1 if error var is also ~0, else 0.
                explained_variance_layer = 1.0 if error_variance_layer < 1e-9 else 0.0
            total_explained_variance += explained_variance_layer

            # Calculate NMSE for the layer (de-normalized)
            nmse_layer = 0.0
            if target_variance_layer > 1e-9:
                nmse_layer = mse_layer / target_variance_layer
            elif mse_layer < 1e-9:  # Target variance is zero and MSE is also zero
                nmse_layer = 0.0
            else:  # Target variance is zero but MSE is non-zero (implies error, NMSE is effectively infinite)
                nmse_layer = float("inf")  # Or a large number, or handle as NaN depending on preference
            total_nmse += nmse_layer
            
            # Store layerwise metrics
            layerwise_nmse[f"layer_{layer_idx}"] = nmse_layer
            layerwise_explained_variance[f"layer_{layer_idx}"] = explained_variance_layer

            num_layers += 1

        avg_explained_variance = total_explained_variance / num_layers if num_layers > 0 else 0.0
        avg_normalized_mean_reconstruction_error = total_nmse / num_layers if num_layers > 0 else 0.0

        # Clamp EV between 0 and 1 for robustness
        avg_explained_variance = max(0.0, min(1.0, avg_explained_variance))

        # avg_normalized_mean_reconstruction_error can be inf, handle this if it needs to be bounded or logged carefully.
        # For now, log as is.

        return {
            "reconstruction/explained_variance": avg_explained_variance,
            "reconstruction/normalized_mean_reconstruction_error": avg_normalized_mean_reconstruction_error,
            "layerwise/normalized_mse": layerwise_nmse,
            "layerwise/explained_variance": layerwise_explained_variance,
        }

    def _compute_feature_density(self, activations: Dict[int, torch.Tensor]) -> Dict[str, Any]:
        """Compute feature density metrics with structured keys for layerwise data.

        Args:
            activations: Dictionary mapping layer indices to feature activations.

        Returns:
            Dictionary containing per-layer dictionaries under
            'layerwise/log_feature_density' and 'layerwise/consistent_activation_heuristic'.
        """
        if not activations or not any(v.numel() > 0 for v in activations.values()):
            return {
                "layerwise/log_feature_density": {},
                "layerwise/consistent_activation_heuristic": {},
            }

        per_layer_log_density: Dict[str, list[float]] = {}
        per_layer_heuristic: Dict[str, list[float]] = {}

        for layer_idx, layer_activations in activations.items():
            # layer_activations: [batch_tokens, num_features]
            if layer_activations.numel() == 0:
                continue

            num_tokens, num_features = layer_activations.shape
            if num_tokens == 0:
                continue

            # Use a small threshold for numerical stability
            act_bool = (layer_activations > 1e-6).float()

            # Feature Density: Fraction of tokens each feature is active for
            # Shape: [num_features]
            feature_density_tensor = act_bool.mean(dim=0)
            # Apply log10 transformation
            log_feature_density_tensor = CLTEvaluator._log_density(feature_density_tensor)
            log_feature_density_this_layer = log_feature_density_tensor.tolist()
            per_layer_log_density[f"layer_{layer_idx}"] = log_feature_density_this_layer

            # Consistent Activation Heuristic:
            # [num_features], number of tokens each feature fired for
            tokens_feature_active = act_bool.sum(dim=0)  # [num_features]

            # Calculate heuristic per feature: total activations / num prompts active
            # Add small epsilon to denominator to avoid division by zero
            # Use act_bool.any(dim=0) instead of (tokens_feature_active > 0).float() for clarity
            prompts_feature_active_mask = act_bool.any(dim=0)  # Check if feature fired at least once
            denominator = prompts_feature_active_mask.float() + 1e-9  # [num_features]
            heuristic_this_layer = (tokens_feature_active / denominator).tolist()
            per_layer_heuristic[f"layer_{layer_idx}"] = heuristic_this_layer

        # Return per-layer dictionaries containing lists of per-feature values
        return {
            "layerwise/log_feature_density": per_layer_log_density,
            "layerwise/consistent_activation_heuristic": per_layer_heuristic,
        }

    def _compute_dead_neuron_metrics(self, dead_neuron_mask: Optional[torch.Tensor]) -> Dict[str, Any]:
        """Compute layerwise dead neuron metrics based on the provided mask.

        Args:
            dead_neuron_mask: Optional mask indicating dead neurons.

        Returns:
            Dictionary with 'layerwise/dead_features/layer_{i}'.
            Total count is calculated later in compute_metrics.
        """
        dead_neuron_metrics: Dict[str, Any] = {
            # "dead_features/total": 0, # Total calculated later
            "layerwise/dead_features": {},
        }
        if dead_neuron_mask is not None:
            # Ensure mask is on the correct device
            dead_neuron_mask = dead_neuron_mask.to(self.device)
            # Validate mask shape matches model config
            expected_shape = (
                self.model.config.num_layers,
                self.model.config.num_features,
            )
            if dead_neuron_mask.shape == expected_shape:
                # total_dead = dead_neuron_mask.sum().item() # No longer needed here
                # dead_neuron_metrics["dead_features/total"] = total_dead
                per_layer_dead_dict = {}
                for layer_idx in range(dead_neuron_mask.shape[0]):
                    per_layer_dead_dict[f"layer_{layer_idx}"] = dead_neuron_mask[layer_idx].sum().item()
                dead_neuron_metrics["layerwise/dead_features"] = per_layer_dead_dict
            else:
                if not self.model.world_size > 1 or self.model.rank == 0:
                    logger.warning(
                        f"Warning: Received dead_neuron_mask with unexpected shape {dead_neuron_mask.shape}. Expected {expected_shape}. Skipping dead neuron eval metrics."
                    )
        return dead_neuron_metrics

    def print_evaluation_report(
        self,
        step: int,
        metrics: Dict[str, Any],
        detailed_metrics: Dict[str, Any],
        current_training_config: Optional[TrainingConfig] = None,
        current_clt_config: Optional[CLTConfig] = None,
    ):
        if not self.model.world_size > 1 or self.model.rank == 0:
            logger.info(
                "\n======================================================================="
                "\n--- Model Evaluation Report ---"
            )
            logger.info(f"Evaluation at Step: {step}")
            logger.info(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("--- Overall Performance ---")
            logger.info(f"  Total Reconstruction Loss: {metrics.get('reconstruction/total_loss', float('nan')):.4f}")
            logger.info(f"  Total Sparsity Loss: {metrics.get('sparsity/total_loss', float('nan')):.4f}")
            logger.info(
                f"  Explained Variance (Avg): {metrics.get('reconstruction/explained_variance', float('nan')):.4f}"
            )
            logger.info(f"  NMSE (Avg): {metrics.get('reconstruction/nmse', float('nan')):.4f}")
            logger.info(f"  L0 Norm (Avg per token): {metrics.get('sparsity/avg_l0', float('nan')):.2f}")
            logger.info(f"  Sparsity Fraction: {metrics.get('sparsity/sparsity_fraction', float('nan')):.4f}")

            # Layer-wise details
            if metrics.get("layerwise/reconstruction_loss"):
                logger.info("--- Layer-wise Reconstruction Loss ---")
                for layer, loss in metrics["layerwise/reconstruction_loss"].items():
                    logger.info(f"  {layer}: {loss:.4f}")

            if metrics.get("layerwise/explained_variance"):
                logger.info("--- Layer-wise Explained Variance ---")
                for layer, ev in metrics["layerwise/explained_variance"].items():
                    logger.info(f"  {layer}: {ev:.4f}")

            if metrics.get("layerwise/nmse"):
                logger.info("--- Layer-wise NMSE ---")
                for layer, nmse_val in metrics["layerwise/nmse"].items():
                    logger.info(f"  {layer}: {nmse_val:.4f}")

            if metrics.get("layerwise/l0"):
                logger.info("--- Layer-wise L0 Norm (Avg per token) ---")
                for layer, l0 in metrics["layerwise/l0"].items():
                    logger.info(f"  {layer}: {l0:.2f}")

            # Feature density details
            if detailed_metrics.get("feature_density_per_layer"):
                logger.info("Feature Density Per Layer:")
                for layer, density in detailed_metrics["feature_density_per_layer"].items():
                    logger.info(f"  Layer {layer}: {density:.4f}")

            # Dead features details
            if detailed_metrics.get("dead_features_per_layer_eval"):
                logger.info("Dead Features Per Layer (Evaluation Batch):")
                for layer, count in detailed_metrics["dead_features_per_layer_eval"].items():
                    logger.info(f"  Layer {layer}: {count}")

            # Active features details
            if detailed_metrics.get("active_features_per_layer_eval"):
                logger.info("Active Features Per Layer (Evaluation Batch):")
                for layer, count in detailed_metrics["active_features_per_layer_eval"].items():
                    logger.info(f"  Layer {layer}: {count}")

            # Overall dead/active features
            logger.info(f"Total Dead Features (Eval Batch): {detailed_metrics.get('dead_features/total_eval', 0)}")
            logger.info(f"Total Active Features (Eval Batch): {detailed_metrics.get('active_features/total_eval', 0)}")

            if current_training_config:
                logger.info("--- Training Configuration ---")
                logger.info(f"  Learning Rate: {current_training_config.learning_rate}")
                logger.info(f"  Sparsity Lambda: {current_training_config.sparsity_lambda}")
                # Add other relevant training config details

            if current_clt_config:
                logger.info("--- CLT Model Configuration ---")
                logger.info(f"  Activation Function: {current_clt_config.activation_fn}")
                logger.info(f"  Number of Features: {current_clt_config.num_features}")
                # Add other relevant CLT config details
            logger.info("=======================================================================\n")
