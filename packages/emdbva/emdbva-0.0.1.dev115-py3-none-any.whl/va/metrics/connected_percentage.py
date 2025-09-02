import numpy as np
import mrcfile
from scipy.ndimage import label, find_objects


def estimate_diameter_bbox(coords_physical):
    return np.linalg.norm(coords_physical.max(axis=0) - coords_physical.min(axis=0))

def detect_small_blobs(volume, threshold, min_diameter, voxel_size=1.0, connectivity=2):
    binary = volume > threshold
    structure = np.ones((3, 3, 3)) if connectivity == 3 else None
    labeled, _ = label(binary, structure=structure)
    cleaned = np.zeros_like(binary, dtype=bool)
    total_removed_voxels = 0
    slices = find_objects(labeled)
    for label_id, sl in enumerate(slices, start=1):
        if sl is None:
            continue
        region = (labeled[sl] == label_id)
        coords = np.argwhere(region) + np.array([s.start for s in sl])
        diameter = estimate_diameter_bbox(coords * voxel_size) if len(coords) >= 2 else 0.0
        if diameter >= min_diameter:
            cleaned[tuple(coords.T)] = True
        else:
            total_removed_voxels += len(coords)
    return cleaned, total_removed_voxels

def compute_connected_metrics(mrc_path, threshold, min_diameter=5.0, voxel_size=None, connectivity=2):
    with mrcfile.open(mrc_path, permissive=True) as mrc:
        volume = mrc.data.copy()
        if voxel_size is None:
            voxel_size = float(mrc.voxel_size.x)

    total_voxels = np.sum(volume > threshold)
    if total_voxels == 0:
        return {
            "connected_percentage": 0.0,
            "connected_volume": 0.0,
            "disconnected_percentage": 0.0,
            "disconnected_volume": 0.0
        }

    cleaned_mask, removed_voxels = detect_small_blobs(volume, threshold, min_diameter, voxel_size, connectivity)
    kept_voxels = total_voxels - removed_voxels

    kept_volume = kept_voxels * (voxel_size ** 3)
    removed_volume = removed_voxels * (voxel_size ** 3)
    total_volume = kept_volume + removed_volume

    return {
        "connected_percentage": (kept_volume / total_volume) * 100 if total_volume > 0 else 0.0,
        "connected_volume": kept_volume,
        "disconnected_percentage": (removed_volume / total_volume) * 100 if total_volume > 0 else 0.0,
        "disconnected_volume": removed_volume
    }
