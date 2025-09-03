import numpy as np
from spikeinterface import BaseSorting
from numpy.typing import NDArray


def get_spike_indicator(
    sorting: BaseSorting,
    time: NDArray[np.float64],
    timestamps_ephys: NDArray[np.float64],
):
    """Count the number of spikes of all the units in a sorting in bins defined by `time`.

    Parameters
    ----------
    sorting : spikeinterface.BaseSorting
        sorting object
    time : NDArray[np.float64], (N, )
        time vector for decoding; usually separated by 2 ms
    timestamps_ephys : NDArray[np.float64], (N, )
        timestamps for ephys; used to convert the spike timings from index to seconds.

    Returns
    -------
    spike_indicator : NDArray[np.int], (N, K) where K=number of units in the sorting
        Number of spikes per bin.
    """
    spike_indicator = []
    for unit_id in sorting.get_unit_ids():
        spike_times = timestamps_ephys[sorting.get_unit_spike_train(unit_id)]
        spike_times = spike_times[(spike_times > time[0]) & (spike_times <= time[-1])]
        spike_indicator.append(
            np.bincount(np.digitize(spike_times, time[1:-1]), minlength=time.shape[0])
        )
    return np.asarray(spike_indicator).T


def plot_place_fields_ratemap_from_classifier(
    path_to_classifier_model, unit_id, ax=None, color="red", alpha=1
):
    classifier = rtc.SortedSpikesClassifier.load_model(
        filename=path_to_classifier_model
    )
    place_fields = classifier.place_fields_[("", direction)].values / 0.002
    linearized_position = classifier.place_fields_[("", direction)].position.values
    if ax is None:
        fig, ax = plt.subplots(figsize=(5, 3))
    ax.plot(linearized_position, place_fields[:, unit_id], color=color, alpha=alpha)
    # ax.set_xlabel("Linearized position (cm)")
    # ax.set_ylabel('P(spike|position)')


def smooth_position(position, t_position, position_sampling_rate):
    """Smooths position using a number of methods:
    - detects changes that are too rapid, replaces those with nan, and interpolates over them
    - applies a moving average


    Parameters
    ----------
    position : _type_
        _description_
    t_position : _type_
        _description_
    position_sampling_rate : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """
    import position_tools as pt

    max_plausible_speed = (100.0,)
    position_smoothing_duration = 0.125
    speed_smoothing_std_dev = 0.100

    speed = pt.get_speed(
        position,
        t_position,
        sigma=speed_smoothing_std_dev,
        sampling_frequency=position_sampling_rate,
    )

    is_too_fast = speed > max_plausible_speed
    position[is_too_fast] = np.nan

    position = pt.interpolate_nan(position)

    # moving_average_window = int(position_smoothing_duration * position_sampling_rate)
    # position = bottleneck.move_mean(
    #     position, window=moving_average_window, axis=0, min_count=1
    # )

    # def remove_tracking_errors(data, threshold=30):
    #     # Calculate the differences between consecutive points
    #     diffs = np.diff(data, axis=0)
    #     distances = np.linalg.norm(diffs, axis=1)

    #     # Identify points where the change exceeds the threshold
    #     error_indices = np.where(distances > threshold)[0] + 1

    #     # Handle edge case where the first or last point is an error
    #     if 0 in error_indices:
    #         data[0] = data[1]
    #     if len(data) - 1 in error_indices:
    #         data[-1] = data[-2]

    #     # Interpolate over errors
    #     for index in error_indices:
    #         if index < len(data) - 1:
    #             data[index] = (data[index - 1] + data[index + 1]) / 2

    #     return data

    # def moving_average(data, window_size=3):
    #     """Simple moving average"""
    #     return np.convolve(data, np.ones(window_size) / window_size, mode="same")

    # def detect_extended_jumps(data, smoothed_data, threshold):
    #     """Detects extended jumps in the data"""
    #     distances = np.linalg.norm(data - smoothed_data, axis=1)
    #     return distances > threshold

    # def segment_data(data, is_jump):
    #     """Segments the data into normal and jump segments"""
    #     segments = []
    #     start = 0

    #     for i in range(1, len(is_jump)):
    #         if is_jump[i] != is_jump[i - 1]:
    #             segments.append((start, i, is_jump[i - 1]))
    #             start = i
    #     segments.append((start, len(is_jump), is_jump[-1]))

    #     return segments

    # def interpolate_jumps(data, segments):
    #     """Interpolates over the segments identified as jumps"""
    #     for start, end, is_jump in segments:
    #         if is_jump:
    #             if start == 0:
    #                 data[start:end] = data[end]
    #             elif end == len(data):
    #                 data[start:end] = data[start - 1]
    #             else:
    #                 interp_values = np.linspace(data[start - 1], data[end], end - start)
    #                 data[start:end] = interp_values
    #     return data

    # def remove_extended_jumps(
    #     data, jump_threshold=30, outlier_threshold=50, window_size=5
    # ):
    #     # Initial jump removal
    #     data = remove_tracking_errors(data, threshold=jump_threshold)

    #     # Calculate smoothed trajectory
    #     smoothed_data = np.vstack(
    #         (
    #             moving_average(data[:, 0], window_size),
    #             moving_average(data[:, 1], window_size),
    #         )
    #     ).T

    #     # Detect extended jumps
    #     is_jump = detect_extended_jumps(data, smoothed_data, outlier_threshold)

    #     # Segment the data
    #     segments = segment_data(data, is_jump)

    #     # Interpolate over extended jumps
    #     return interpolate_jumps(data, segments)

    # # Process the data
    # position = remove_extended_jumps(position)

    return position


def get_ahead_behind(
    decode_acausal_posterior_1d,
    track_graph,
    classifier_1d,
    position_2d,
    track_segment_id,
    head_direction,
):
    import trajectory_analysis_tools as tat

    (
        actual_projected_position,
        actual_edges,
        actual_orientation,
        mental_position_2d,
        mental_position_edges,
    ) = tat.get_trajectory_data(
        posterior=decode_acausal_posterior_1d,
        track_graph=track_graph,
        decoder=classifier_1d,
        actual_projected_position=position_2d,
        track_segment_id=track_segment_id,
        actual_orientation=head_direction,
    )
    return tat.get_ahead_behind_distance(
        track_graph,
        actual_projected_position,
        actual_edges,
        actual_orientation,
        mental_position_2d,
        mental_position_edges,
    )


from scipy.signal import correlate


def plot_linearized_position(
    ax, start_time, end_time, first=False, last=False, filter_freq=30
):
    idx = (time > start_time) & (time < end_time)

    ax.plot(time[idx], position_df["linear_position"][idx], "k", linewidth=3, alpha=0.5)
    # ax.plot(time[idx], map_decode_hpc_filtered[idx], 'r--')
    # ax.plot(time[idx], map_decode_v1_filtered[idx], 'b--')

    ahead_behind_distance_hpc_filtered = lowpass_filter(
        ahead_behind_distance_hpc, filter_freq, 500
    )
    ahead_behind_distance_v1_filtered = lowpass_filter(
        ahead_behind_distance_v1, filter_freq, 500
    )

    ax.plot(
        time[idx],
        position_df["linear_position"][idx] + ahead_behind_distance_hpc_filtered[idx],
        "b",
        linewidth=1,
        alpha=1,
    )
    ax.plot(
        time[idx],
        position_df["linear_position"][idx] + ahead_behind_distance_v1_filtered[idx],
        "r",
        linewidth=1,
        alpha=1,
    )

    if first:
        ax.set_ylabel("Linearized position")

    if last:
        ax.text(
            time[idx][0] + 0.4,
            20,
            "Actual",
            ha="center",
            va="center",
            color="k",
            fontsize=12,
            alpha=0.5,
        )

        ax.plot([time[idx][0] + 0.1, time[idx][0] + 0.1], [50, 100], "k")
        ax.text(
            time[idx][0] + 0.4,
            75,
            "50 cm",
            ha="center",
            va="center",
            color="k",
            fontsize=9,
        )
    ax.set_xlim([start_time, end_time])
    ax.set_ylim([0, 360])
    ax.set_xticks([])
    ax.set_yticks([])


def plot_deviation(ax, start_time, end_time, first=False, last=False, filter_freq=6):
    idx = (time > start_time) & (time < end_time)

    ahead_behind_distance_hpc_filtered = lowpass_filter(
        ahead_behind_distance_hpc, filter_freq, 500
    )
    ahead_behind_distance_v1_filtered = lowpass_filter(
        ahead_behind_distance_v1, filter_freq, 500
    )

    ax.axhline(0, color="k", alpha=0.5)
    ax.plot(time[idx], ahead_behind_distance_hpc_filtered[idx], "b")
    ax.plot(time[idx], ahead_behind_distance_v1_filtered[idx], "r")
    ax.plot(
        [time[idx][-1] - 0.5 - 0.5, time[idx][-1] - 0.5],
        [-20, -20],
        "k",
    )
    if last:
        ax.text(
            time[idx][-1] - 0.5 - 0.25,
            -23,
            "500 ms",
            ha="center",
            va="center",
            color="k",
            fontsize=9,
        )
        ax.plot([time[idx][-1] - 0.5, time[idx][-1] - 0.5], [-20, -10], "k")
        ax.text(
            time[idx][-1] - 0.25,
            -15,
            "10 cm",
            ha="center",
            va="center",
            color="k",
            fontsize=9,
        )
        ax.text(
            time[idx][0] + 0.5,
            -20,
            "HPC",
            ha="right",
            va="center",
            color="b",
            fontsize=12,
        )
        ax.text(
            time[idx][0] + 0.8,
            -20,
            "V1",
            ha="right",
            va="center",
            color="r",
            fontsize=12,
        )
    if first:
        ax.set_ylabel("Deviation")
    # ax.set_ylabel("Decoded-actual (cm)")
    ax.set_ylim([-25, 25])
    ax.set_xlim([start_time, end_time])
    ax.set_xticks([])
    ax.set_yticks([])


# idx = (time > int(min*60+sec)) & (time < int(min*60+sec+dt))


# plot_linearized_position(ax[0,0], 702.65, 705)
# plot_deviation(ax[1,0], 702.65, 705)


def lowpass_filter(data, cutoff, fs, order=5):
    """
    Apply a Butterworth lowpass filter to a NumPy array.

    :param data: NumPy array containing the data to filter.
    :param cutoff: Cut-off frequency of the filter.
    :param fs: Sampling rate of the data.
    :param order: Order of the filter.
    :return: Filtered data.
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    y = filtfilt(b, a, data)
    return y
