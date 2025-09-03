import pandas as pd
import numpy as np
import pickle
import spikeinterface as si


def get_spikes_position(trial_name: str, unit_id, waveform_extractor):
    path_to_position = f"/nimbus/kyu/L10/20231005/dlc/L10-20231005-phil-2023-10-25/videos/{trial_name}DLC_resnet50_L10-20231005Oct25shuffle1_500000_filtered.h5"
    df = pd.read_hdf(path_to_position)

    x = df[("DLC_resnet50_L10-20231005Oct25shuffle1_500000", "led", "x")].to_numpy()
    y = df[("DLC_resnet50_L10-20231005Oct25shuffle1_500000", "led", "y")].to_numpy()
    position = np.column_stack((x, y))

    with open("timestamps_position.pkl", "rb") as f:
        timestamps_position = pickle.load(f)

    with open("timestamps_ephys.pkl", "rb") as f:
        timestamps_ephys = pickle.load(f)

    with open("timestamps_ephys_all.pkl", "rb") as f:
        timestamps_ephys_all = pickle.load(f)

    ref_time_offset = timestamps_ephys[trial_name][0]

    timestamps_ephys_all = timestamps_ephys_all - ref_time_offset

    position_offset = 10
    pixels_to_cm = 5.3
    t_position = timestamps_position[trial_name][position_offset:] - ref_time_offset
    position = position[position_offset:] / pixels_to_cm

    spike_times = waveform_extractor.sorting.get_unit_spike_train(unit_id)
    spike_times = timestamps_ephys_all[spike_times]
    spike_times = spike_times[
        (spike_times > t_position[0]) & (spike_times <= t_position[-1])
    ]

    return spike_times, position, t_position
