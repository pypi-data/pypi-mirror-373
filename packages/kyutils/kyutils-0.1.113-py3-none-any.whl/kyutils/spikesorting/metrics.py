import spikeinterface as si
import spikeinterface.qualitymetrics as sq

import json
import numpy as np


def compute_standard_metrics(waveform_extractor, path_to_json: str):
    """Computes ISI violation, SNR, nearest neighbor isolation, and nearest neighbor noise overlap metrics.

    Parameters
    ----------
    waveform_extractor : si.WaveformExtractor
    path_to_json : str
        path to save metrics dict as json file

    Returns
    -------
    metrics_dict : dict
        dict of metrics
    """
    snrs = sq.compute_snrs(
        waveform_extractor,
        random_chunk_kwargs_dict={
            "num_chunks_per_segment": 20,
            "chunk_size": 30000,
            "seed": 0,
        },
    )
    _, isi_violation_count = sq.compute_isi_violations(
        waveform_extractor, isi_threshold_ms=2.0, min_isi_ms=0
    )
    num_spikes = sq.compute_num_spikes(waveform_extractor)
    isi_violation_fraction = {
        i: j / k
        for i, j, k in zip(
            isi_violation_count.keys(),
            isi_violation_count.values(),
            num_spikes.values(),
        )
    }

    nn_isolation_params = {
        "max_spikes": 3000,
        "min_spikes": 10,
        "n_neighbors": 7,
        "n_components": 10,
        "radius_um": 200,
        "seed": 0,
    }

    nn_noise_params = {
        "max_spikes": 3000,
        "min_spikes": 10,
        "n_neighbors": 7,
        "n_components": 10,
        "radius_um": 200,
        "seed": 0,
    }

    nn_isolation = {}
    nn_noise = {}
    for i in waveform_extractor.sorting.get_unit_ids():
        nn_isolation[i], _ = sq.nearest_neighbors_isolation(
            waveform_extractor, this_unit_id=i, **nn_isolation_params
        )
        nn_noise[i] = sq.nearest_neighbors_noise_overlap(
            waveform_extractor, this_unit_id=i, **nn_noise_params
        )

    metrics_dict = {}

    metrics_dict["snr"] = snrs
    metrics_dict["num_spikes"] = num_spikes
    metrics_dict["isi_violation_fraction"] = isi_violation_fraction
    metrics_dict["nn_isolation"] = nn_isolation
    metrics_dict["nn_noise_overlap"] = nn_noise

    for metric_name, metric_data in metrics_dict.items():
        metrics_dict[metric_name] = {
            str(i): np.float64(j) for i, j in metric_data.items()
        }

    with open(path_to_json, "w") as f:
        # Serialize the dictionary and write it to the file
        json.dump(metrics_dict, f)

    return metrics_dict
