import numpy as np
import spikeinterface as si
import matplotlib.pyplot as plt


def plot_waveforms_multiprobe(
    waveform_extractor, unit_id, scale_x=150, scale_y=0.5, ax=None
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(3, 10))

    peak_channels = si.get_template_extremum_channel(waveform_extractor)
    peak_channel = peak_channels[unit_id]

    probe_idx = peak_channel // 128
    channels_to_plot = np.arange(probe_idx * 128, (probe_idx + 1) * 128)

    t = np.linspace(0, 1, waveform_extractor.nsamples)

    for i in channels_to_plot:
        x, y = waveform_extractor.get_channel_locations()[
            np.nonzero(waveform_extractor.channel_ids == i)[0][0]
        ]
        ax.plot(
            t + x / scale_x,
            waveform_extractor.get_template(unit_id=unit_id)[:, i] + y / scale_y,
            "k",
        )

    ref_loc = waveform_extractor.get_channel_locations()[
        np.nonzero(waveform_extractor.channel_ids == channels_to_plot[0])[0][0]
    ]
    ax.plot(
        [-1 + ref_loc[0] / scale_x, -1 + ref_loc[0] / scale_x],
        [ref_loc[1] / scale_y, 100 + ref_loc[1] / scale_y],
        "k-",
    )
    ax.text(-2 + ref_loc[0] / scale_x, 50 + ref_loc[1] / scale_y, "100 $\mu$V")

    ax.set_title(f"probe {probe_idx}, unit {unit_id}")

    ax.set_axis_off()

    return ax


def plot_waveforms_singleshank(
    waveform_extractor, unit_id, scale_x=150, scale_y=0.5, ax=None
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(3, 10))

    t = np.linspace(0, 1, waveform_extractor.nsamples)

    for i in range(len(waveform_extractor.channel_ids)):
        x, y = waveform_extractor.get_channel_locations()[i]
        ax.plot(
            t + x / scale_x,
            waveform_extractor.get_template(unit_id=unit_id, force_dense=True)[:, i]
            + y / scale_y,
            "k",
        )

    ref_loc = [
        np.min(waveform_extractor.get_channel_locations()[:, 0]),
        np.min(waveform_extractor.get_channel_locations()[:, 1]),
    ]

    ax.plot(
        [
            -3 / waveform_extractor.nsamples + ref_loc[0] / scale_x,
            -3 / waveform_extractor.nsamples + ref_loc[0] / scale_x,
        ],
        [ref_loc[1] / scale_y, 100 + ref_loc[1] / scale_y],
        "k-",
    )
    ax.text(
        -4 / waveform_extractor.nsamples + ref_loc[0] / scale_x,
        100 + ref_loc[1] / scale_y,
        "100 $\mu$V",
    )

    ax.set_title(f"unit {unit_id}")

    ax.set_axis_off()

    return ax


def plot_waveforms_singleshank_new(
    sorting_analyzer, unit_id, scale_x=150, scale_y=0.5, ax=None
):
    if ax is None:
        fig, ax = plt.subplots(figsize=(3, 10))

    waveforms = sorting_analyzer.get_extension("waveforms")
    templates = sorting_analyzer.get_extension("templates")

    nsamples = waveforms.nbefore + waveforms.nafter

    t = np.linspace(0, 1, nsamples)

    for i in range(len(sorting_analyzer.channel_ids)):
        x, y = sorting_analyzer.get_channel_locations()[i]
        ax.plot(
            t + x / scale_x,
            templates.get_unit_template(unit_id=unit_id)[:, i] + y / scale_y,
            "k",
        )

    ref_loc = [
        np.min(sorting_analyzer.get_channel_locations()[:, 0]),
        np.min(sorting_analyzer.get_channel_locations()[:, 1]),
    ]

    ax.plot(
        [
            -3 / nsamples + ref_loc[0] / scale_x,
            -3 / nsamples + ref_loc[0] / scale_x,
        ],
        [ref_loc[1] / scale_y, 100 + ref_loc[1] / scale_y],
        "k-",
    )
    ax.text(
        -4 / nsamples + ref_loc[0] / scale_x,
        100 + ref_loc[1] / scale_y,
        "100 $\mu$V",
    )

    ax.set_title(f"unit {unit_id}")

    ax.set_axis_off()

    return ax
