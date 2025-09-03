"""
Selection preview functions for Sharp Frames TUI.
Optimized for speed to enable real-time preview updates.
"""

from typing import List, Dict, Any
import time
import statistics


def get_selection_count(frames_with_scores: List[Dict[str, Any]], method: str, **params) -> int:
    """
    Calculate how many frames would be selected without actually selecting them.
    Optimized for speed to enable real-time preview updates (<100ms target).
    
    Args:
        frames_with_scores: List of frame dictionaries with sharpness scores
        method: Selection method ('best-n', 'batched', 'outlier-removal')
        **params: Method-specific parameters
        
    Returns:
        Number of frames that would be selected
        
    Raises:
        ValueError: For unsupported selection methods
    """
    if not frames_with_scores:
        return 0
    
    total_frames = len(frames_with_scores)
    
    if method == 'best-n':
        n = params.get('n', 300)
        min_buffer = params.get('min_buffer', 3)
        
        # With min_buffer constraint, we might not be able to select all n frames
        if min_buffer > 0:
            required_positions = n + (n - 1) * min_buffer
            if required_positions > total_frames:
                # Calculate maximum possible frames with this buffer
                max_possible = (total_frames + min_buffer) // (min_buffer + 1)
                return min(n, max_possible)
        
        return min(max(0, n), total_frames)
    
    elif method == 'batched':
        batch_size = params.get('batch_size', 5)
        batch_buffer = params.get('batch_buffer', 2)
        
        # Calculate how many batches can be created
        step_size = batch_size + batch_buffer
        if step_size <= 0:
            return 0
        return (total_frames + step_size - 1) // step_size if step_size > 0 else 0
    
    elif method == 'outlier-removal':
        outlier_sensitivity = params.get('outlier_sensitivity', 50)
        return _preview_outlier_removal_count_fast(frames_with_scores, outlier_sensitivity)
    
    else:
        raise ValueError(f"Unsupported selection method: {method}")


def get_selection_preview(frames_with_scores: List[Dict[str, Any]], method: str, **params) -> Dict[str, Any]:
    """
    Return detailed preview information including count, distribution, and statistics.
    
    Args:
        frames_with_scores: List of frame dictionaries with sharpness scores
        method: Selection method ('best-n', 'batched', 'outlier-removal')
        **params: Method-specific parameters
        
    Returns:
        Dictionary containing:
        - count: number of frames that would be selected
        - distribution: histogram of selected frames across timeline
        - statistics: min/max/avg sharpness of selection
    """
    if not frames_with_scores:
        return {
            'count': 0,
            'distribution': [],
            'statistics': {'min_sharpness': 0, 'max_sharpness': 0, 'avg_sharpness': 0}
        }
    
    # Get basic count
    count = get_selection_count(frames_with_scores, method, **params)
    
    # Calculate detailed preview based on method
    if method == 'best-n':
        return _preview_best_n_detailed(frames_with_scores, count, **params)
    elif method == 'batched':
        return _preview_batched_detailed(frames_with_scores, count, **params)
    elif method == 'outlier-removal':
        return _preview_outlier_removal_detailed(frames_with_scores, **params)
    else:
        return {
            'count': count,
            'distribution': [],
            'statistics': {'min_sharpness': 0, 'max_sharpness': 0, 'avg_sharpness': 0}
        }


# === Fast Preview Implementations ===

def _preview_outlier_removal_count_fast(frames_with_scores: List[Dict[str, Any]], outlier_sensitivity: int) -> int:
    """Fast heuristic-based preview for outlier removal using legacy sensitivity parameter."""
    total_frames = len(frames_with_scores)
    
    # Use more granular heuristic for responsive preview
    # Estimate based on sensitivity: higher sensitivity = more aggressive removal
    if outlier_sensitivity >= 90:
        removal_rate = 0.40  # Remove ~40% of frames
    elif outlier_sensitivity >= 80:
        removal_rate = 0.30  # Remove ~30% of frames
    elif outlier_sensitivity >= 70:
        removal_rate = 0.25  # Remove ~25% of frames
    elif outlier_sensitivity >= 60:
        removal_rate = 0.20  # Remove ~20% of frames
    elif outlier_sensitivity >= 50:
        removal_rate = 0.15  # Remove ~15% of frames
    elif outlier_sensitivity >= 40:
        removal_rate = 0.10  # Remove ~10% of frames
    elif outlier_sensitivity >= 30:
        removal_rate = 0.07  # Remove ~7% of frames
    elif outlier_sensitivity >= 20:
        removal_rate = 0.05  # Remove ~5% of frames
    elif outlier_sensitivity >= 10:
        removal_rate = 0.03  # Remove ~3% of frames
    else:
        removal_rate = 0.01  # Remove ~1% of frames
    
    estimated_selected = int(total_frames * (1.0 - removal_rate))
    return max(1, min(estimated_selected, total_frames))


def _preview_best_n_detailed(frames_with_scores: List[Dict[str, Any]], count: int, **params) -> Dict[str, Any]:
    """Detailed preview for best-n selection."""
    if count == 0:
        return {
            'count': 0,
            'distribution': [],
            'statistics': {'min_sharpness': 0, 'max_sharpness': 0, 'avg_sharpness': 0}
        }
    
    # Sort by sharpness score to simulate selection
    sorted_frames = sorted(frames_with_scores, key=lambda x: x.get('sharpnessScore', 0), reverse=True)
    selected_frames = sorted_frames[:count]
    
    # Calculate statistics
    selected_scores = [frame.get('sharpnessScore', 0) for frame in selected_frames]
    statistics_data = {
        'min_sharpness': min(selected_scores) if selected_scores else 0,
        'max_sharpness': max(selected_scores) if selected_scores else 0,
        'avg_sharpness': sum(selected_scores) / len(selected_scores) if selected_scores else 0
    }
    
    # Calculate distribution (histogram across timeline)
    distribution = _calculate_timeline_distribution(frames_with_scores, selected_frames)
    
    return {
        'count': count,
        'distribution': distribution,
        'statistics': statistics_data
    }


def _preview_batched_detailed(frames_with_scores: List[Dict[str, Any]], count: int, **params) -> Dict[str, Any]:
    """Detailed preview for batched selection using legacy parameters."""
    if count == 0:
        return {
            'count': 0,
            'distribution': [],
            'statistics': {'min_sharpness': 0, 'max_sharpness': 0, 'avg_sharpness': 0}
        }
    
    total_frames = len(frames_with_scores)
    batch_size = params.get('batch_size', 5)
    batch_buffer = params.get('batch_buffer', 2)
    
    # Simulate legacy batched selection
    step_size = batch_size + batch_buffer
    selected_frames = []
    
    i = 0
    while i < total_frames:
        # Take a batch of consecutive frames
        batch = frames_with_scores[i:i + batch_size]
        if not batch:
            break
        
        # Select best frame from this batch
        best_frame = max(batch, key=lambda x: x.get('sharpnessScore', 0))
        selected_frames.append(best_frame)
        
        # Move to next batch position (skip batch_buffer frames)
        i += step_size
    
    # Calculate statistics
    selected_scores = [frame.get('sharpnessScore', 0) for frame in selected_frames]
    statistics_data = {
        'min_sharpness': min(selected_scores) if selected_scores else 0,
        'max_sharpness': max(selected_scores) if selected_scores else 0,
        'avg_sharpness': sum(selected_scores) / len(selected_scores) if selected_scores else 0
    }
    
    # For batched selection, distribution is predictable (one per batch)
    distribution = [1] * len(selected_frames)
    
    return {
        'count': len(selected_frames),
        'distribution': distribution,
        'statistics': statistics_data
    }


def _preview_outlier_removal_detailed(frames_with_scores: List[Dict[str, Any]], **params) -> Dict[str, Any]:
    """Detailed preview for outlier removal selection using legacy parameters."""
    outlier_sensitivity = params.get('outlier_sensitivity', 50)
    outlier_window_size = params.get('outlier_window_size', 15)
    
    # For detailed preview, we need to do actual outlier calculation
    # But optimize for common cases
    total_frames = len(frames_with_scores)
    
    if total_frames <= 10:
        # For small datasets, just return all frames
        count = total_frames
        selected_frames = frames_with_scores
    else:
        # Use fast outlier detection for preview
        count = _preview_outlier_removal_count_fast(frames_with_scores, outlier_sensitivity)
        
        # For statistics, estimate based on removing lowest scores
        all_scores = [frame.get('sharpnessScore', 0) for frame in frames_with_scores]
        sorted_scores = sorted(all_scores, reverse=True)
        estimated_selected_scores = sorted_scores[:count]
        
        # Create mock selected frames for statistics
        selected_frames = [
            {'sharpnessScore': score} for score in estimated_selected_scores
        ]
    
    # Calculate statistics
    selected_scores = [frame.get('sharpnessScore', 0) for frame in selected_frames]
    statistics_data = {
        'min_sharpness': min(selected_scores) if selected_scores else 0,
        'max_sharpness': max(selected_scores) if selected_scores else 0,
        'avg_sharpness': sum(selected_scores) / len(selected_scores) if selected_scores else 0
    }
    
    # Distribution for outlier removal is less predictable, use uniform approximation
    distribution = _create_uniform_distribution(count, 10)  # 10 bins
    
    return {
        'count': count,
        'distribution': distribution,
        'statistics': statistics_data
    }


# === Helper Functions ===

def _calculate_timeline_distribution(all_frames: List[Dict[str, Any]], 
                                   selected_frames: List[Dict[str, Any]], 
                                   num_bins: int = 10) -> List[int]:
    """Calculate distribution of selected frames across timeline."""
    if not selected_frames or not all_frames:
        return [0] * num_bins
    
    total_frames = len(all_frames)
    bin_size = total_frames / num_bins
    distribution = [0] * num_bins
    
    # Create mapping of frame to index
    frame_to_index = {}
    for i, frame in enumerate(all_frames):
        frame_id = frame.get('id', '') or frame.get('path', '') or str(i)
        frame_to_index[frame_id] = i
    
    # Count selected frames in each bin
    for frame in selected_frames:
        frame_id = frame.get('id', '') or frame.get('path', '')
        if frame_id in frame_to_index:
            frame_index = frame_to_index[frame_id]
            bin_index = min(int(frame_index / bin_size), num_bins - 1)
            distribution[bin_index] += 1
    
    return distribution


def _create_uniform_distribution(count: int, num_bins: int) -> List[int]:
    """Create approximately uniform distribution across bins."""
    if count == 0 or num_bins == 0:
        return [0] * max(1, num_bins)
    
    base_count = count // num_bins
    remainder = count % num_bins
    
    distribution = [base_count] * num_bins
    
    # Distribute remainder across first bins
    for i in range(remainder):
        distribution[i] += 1
    
    return distribution


# === Performance Monitoring ===

def _measure_performance(func, *args, **kwargs):
    """Measure function execution time for performance monitoring."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Log performance warning if preview takes too long
    if elapsed > 0.1:  # 100ms threshold
        print(f"Warning: Selection preview took {elapsed:.3f}s, target is <0.1s")
    
    return result


# === Caching Support ===

_preview_cache = {}
_cache_max_size = 100


def _calculate_cache_key(frames_with_scores: List[Dict[str, Any]], method: str, **params) -> str:
    """Calculate cache key for preview results."""
    # Use frame count and method as key components for fast caching
    frame_count = len(frames_with_scores)
    
    # Include first and last frame sharpness for basic content identification
    if frames_with_scores:
        first_score = frames_with_scores[0].get('sharpnessScore', 0)
        last_score = frames_with_scores[-1].get('sharpnessScore', 0) if len(frames_with_scores) > 1 else first_score
    else:
        first_score = last_score = 0
    
    # Create key from method and key parameters
    param_str = ""
    if method == 'best-n':
        param_str = f"n={params.get('n', 300)}"
    elif method == 'batched':
        param_str = f"batch_size={params.get('batch_size', 5)}_batch_buffer={params.get('batch_buffer', 2)}"
    elif method == 'outlier-removal':
        param_str = f"outlier_sensitivity={params.get('outlier_sensitivity', 50)}_outlier_window_size={params.get('outlier_window_size', 15)}"
    
    return f"{method}_{frame_count}_{first_score:.2f}_{last_score:.2f}_{param_str}"


def _get_cached_preview(cache_key: str) -> Dict[str, Any]:
    """Get cached preview result if available."""
    return _preview_cache.get(cache_key)


def _cache_preview_result(cache_key: str, result: Dict[str, Any]):
    """Cache preview result with size limit."""
    global _preview_cache
    
    # Simple cache size management
    if len(_preview_cache) >= _cache_max_size:
        # Remove oldest entries (simple FIFO)
        keys_to_remove = list(_preview_cache.keys())[:_cache_max_size // 2]
        for key in keys_to_remove:
            del _preview_cache[key]
    
    _preview_cache[cache_key] = result


def _calculate_cached_preview(frames_with_scores: List[Dict[str, Any]], method: str, **params) -> Dict[str, Any]:
    """Calculate preview with caching support."""
    cache_key = _calculate_cache_key(frames_with_scores, method, **params)
    
    # Check cache first
    cached_result = _get_cached_preview(cache_key)
    if cached_result:
        return cached_result
    
    # Calculate new result
    result = get_selection_preview(frames_with_scores, method, **params)
    
    # Cache result
    _cache_preview_result(cache_key, result)
    
    return result