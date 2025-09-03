import numpy as np
import matplotlib.pyplot as plt
from ..spikegadgets.trodesconf import readTrodesExtractedDataFile


def get_licks_rewards(time, Din_well, Dout_pump):
    """Returns the (relative) timing of the following events:
    - every lick at a reward well
    - the first lick of a train of licks (typically when the animal licks it licks many times)
    - pump turning on to deliver milk reward
    - the lick that was followed by reward

    Parameters
    ----------
    time : dict
        output of readTrodesExtractedDataFile for time
    Din_well : dict
        output of readTrodesExtractedDataFile for DIO
    Dout_pump : dict
        output of readTrodesExtractedDataFile for DIO

    Returns
    -------
    lick_times
    first_lick_times
    pump_on_times
    rewarded_lick_times:
        _description_
    """
    x = []
    for i in Din_well["data"]["time"]:
        x.append(time["data"]["systime"][np.nonzero(time["data"]["time"] == i)[0][0]])
    x = np.asarray(x)
    x = (x - time["data"]["systime"][0]) * 1e-9

    lick_times = [x[i] for i in range(len(x)) if Din_well["data"]["state"][i] == 1]
    lick_times = np.asarray(lick_times)

    # time between lick trains (unit: seconds)
    lick_train_interval_s = 13

    first_lick_times = lick_times[
        np.nonzero(np.diff(lick_times) > lick_train_interval_s)[0] + 1
    ]
    first_lick_times = np.insert(first_lick_times, 0, lick_times[0])

    pump_times = []
    for i in Dout_pump["data"]["time"]:
        pump_times.append(
            time["data"]["systime"][np.nonzero(time["data"]["time"] == i)[0][0]]
        )
    pump_times = np.asarray(pump_times)
    pump_times = (pump_times - time["data"]["systime"][0]) * 1e-9

    pump_on_times = [
        pump_times[i]
        for i in range(len(pump_times))
        if Dout_pump["data"]["state"][i] == 1
    ]

    # delay between detection of lick and delivery of reward (unit: seconds)
    rewarded_lick_times = [
        i for i in first_lick_times if np.min(np.abs(pump_on_times - i)) < 0.1
    ]

    return lick_times, first_lick_times, pump_on_times, rewarded_lick_times


def plot_performance(
    ax,
    first_lick_times_left,
    first_lick_times_center,
    first_lick_times_right,
    rewarded_lick_times_left,
    rewarded_lick_times_center,
    rewarded_lick_times_right,
    pump_on_times_left,
    pump_on_times_center,
    pump_on_times_right,
):
    ax.plot(
        first_lick_times_left,
        np.ones(len(first_lick_times_left)),
        "bo",
        markersize=10,
        markerfacecolor="none",
    )
    ax.plot(
        rewarded_lick_times_left,
        np.ones(len(rewarded_lick_times_left)),
        "bo",
        markersize=10,
    )

    ax.plot(
        first_lick_times_center,
        2 * np.ones(len(first_lick_times_center)),
        "ro",
        markersize=10,
        markerfacecolor="none",
    )
    ax.plot(
        rewarded_lick_times_center,
        2 * np.ones(len(rewarded_lick_times_center)),
        "ro",
        markersize=10,
    )

    ax.plot(
        first_lick_times_right,
        3 * np.ones(len(first_lick_times_right)),
        "go",
        markersize=10,
        markerfacecolor="none",
    )
    ax.plot(
        rewarded_lick_times_right,
        3 * np.ones(len(rewarded_lick_times_right)),
        "go",
        markersize=10,
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylim([0, 4])

    ticks = [1, 2, 3]  # Replace with your desired tick locations
    ax.set_yticks(ticks)

    # Define the new tick labels
    labels = ["Left", "Center", "Right"]  # Replace with your custom labels

    # Set the new tick labels
    ax.set_yticklabels(labels)
    performance = (
        len(pump_on_times_left) + len(pump_on_times_center) + len(pump_on_times_right)
    ) / (
        len(first_lick_times_left)
        + len(first_lick_times_center)
        + len(first_lick_times_right)
    )
    ax.set_title(f"Overall performance: {performance}")


def plot_performance_as_curve(
    first_lick_times_left,
    first_lick_times_center,
    first_lick_times_right,
    rewarded_lick_times_left,
    rewarded_lick_times_center,
    rewarded_lick_times_right,
    ax=None,
):
    """plots the behavior as a smoothed performance curve

    Parameters
    ----------
    first_lick_times_left : _type_
        _description_
    first_lick_times_center : _type_
        _description_
    first_lick_times_right : _type_
        _description_
    rewarded_lick_times_left : _type_
        _description_
    rewarded_lick_times_center : _type_
        _description_
    rewarded_lick_times_right : _type_
        _description_
    ax : _type_, optional
        _description_, by default None
    """

    def find_elements_within_threshold(array1, array2, threshold):
        result = []
        for element in array1:
            # Check if any element in array2 is within the threshold of the current element
            if np.any(np.abs(array2 - element) <= threshold):
                result.append(1)
            else:
                result.append(0)
        return np.asarray(result)

    binary_left = find_elements_within_threshold(
        array1=first_lick_times_left, array2=rewarded_lick_times_left, threshold=0.1
    )
    binary_center = find_elements_within_threshold(
        array1=first_lick_times_center, array2=rewarded_lick_times_center, threshold=0.1
    )
    binary_right = find_elements_within_threshold(
        array1=first_lick_times_right, array2=rewarded_lick_times_right, threshold=0.1
    )
    first_lick_times = np.concatenate(
        (first_lick_times_left, first_lick_times_center, first_lick_times_right)
    )
    rewarded = np.concatenate((binary_left, binary_center, binary_right))

    inds = np.argsort(first_lick_times)
    first_lick_times_sorted = first_lick_times[inds]
    rewarded_sorted = rewarded[inds]

    trial_type = ["inbound"]
    for i in range(len(rewarded_sorted) - 1):
        if rewarded_sorted[i] == 0:
            trial_type.append(trial_type[i])
        else:
            if trial_type[i] == "inbound":
                trial_type.append("outbound")
            else:
                trial_type.append("inbound")

    rewarded_inbound = rewarded_sorted[np.asarray(trial_type) == "inbound"]
    rewarded_outbound = rewarded_sorted[np.asarray(trial_type) == "outbound"]

    lick_times_inbound = first_lick_times_sorted[np.asarray(trial_type) == "inbound"]
    lick_times_outbound = first_lick_times_sorted[np.asarray(trial_type) == "outbound"]

    def moving_average_filter(input_array, window_size=3):
        """
        Applies a moving average filter to an input array.

        Parameters:
        - input_array: A numpy array to which the filter will be applied.
        - window_size: The size of the window over which to compute the average.

        Returns:
        - filtered_array: A numpy array after applying the moving average filter.
        """
        # Create a window of ones for the moving average
        window = np.ones(int(window_size)) / float(window_size)
        # Apply convolution to get the moving average
        filtered_array = np.convolve(input_array, window, "valid")
        return filtered_array

    smoothed_rewarded_inbound = moving_average_filter(rewarded_inbound, window_size=5)
    smoothed_rewarded_outbound = moving_average_filter(rewarded_outbound, window_size=5)

    if ax is None:
        fig, ax = plt.subplots()
    ax.plot(
        np.arange(len(smoothed_rewarded_inbound) + 1),
        np.concatenate(([0], smoothed_rewarded_inbound)),
    )
    ax.plot(
        np.arange(len(smoothed_rewarded_outbound) + 1),
        np.concatenate(([0], smoothed_rewarded_outbound)),
    )
    ax.set_ylim([0, 1])
    ax.set_xlabel("Trials")
    ax.set_ylabel("Performance")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    return rewarded_inbound, rewarded_outbound, lick_times_inbound, lick_times_outbound
