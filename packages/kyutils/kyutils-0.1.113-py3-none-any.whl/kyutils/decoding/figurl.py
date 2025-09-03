import numpy as np

import sortingview.views as vv
import ripple_detection as rd

from scipy.ndimage import gaussian_filter1d

import os

os.environ["KACHERY_ZONE"] = "franklab.default"

actual = vv.TimeseriesGraph()
actual.add_line_series(
    name="Actual position (cm)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        position_df["linear_position"],
        dtype=np.float32,
    ),
    color="black",
    width=1.5,
)


decode_minus_actual = vv.TimeseriesGraph()
decode_minus_actual.add_line_series(
    name="Decoded CA1 - Actual (cm)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        # dx_hpc,
        ahead_behind_distance_hpc,
        dtype=np.float32,
    ),
    color="#1f77b4",
    width=1.5,
)
decode_minus_actual.add_line_series(
    name="Decoded V11 - Actual (cm)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        # dx_v1,
        ahead_behind_distance_v1,
        dtype=np.float32,
    ),
    color="#ff7f0e",
    width=1.5,
)

decode_minus_actual_zoom = vv.TimeseriesGraph(y_range=[-20, 20])
decode_minus_actual_zoom.add_line_series(
    name="Decoded CA1 - Actual Zoom (cm)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        # dx_hpc,
        ahead_behind_distance_hpc,
        dtype=np.float32,
    ),
    color="#1f77b4",
    width=1.5,
)
decode_minus_actual_zoom.add_line_series(
    name="Decoded V11 - Actual Zoom (cm)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        # dx_v1,
        ahead_behind_distance_v1,
        dtype=np.float32,
    ),
    color="#ff7f0e",
    width=1.5,
)

decode_minus_actual_zoom_lowpass = vv.TimeseriesGraph(y_range=[-20, 20])
decode_minus_actual_zoom_lowpass.add_line_series(
    name="Decoded CA1 - Actual Zoom (cm)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        butter_lowpass_filter(ahead_behind_distance_hpc, cutoff, fs, order=6),
        dtype=np.float32,
    ),
    color="#1f77b4",
    width=1.5,
)
decode_minus_actual_zoom_lowpass.add_line_series(
    name="Decoded V11 - Actual Zoom (cm)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        butter_lowpass_filter(ahead_behind_distance_v1, cutoff, fs, order=6),
        dtype=np.float32,
    ),
    color="#ff7f0e",
    width=1.5,
)

multiunit_firing_rate_view = vv.TimeseriesGraph()
multiunit_firing_rate_view.add_line_series(
    name="CA1 Multiunit Rate (spikes/s)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        rd.get_multiunit_population_firing_rate(
            spike_indicator_hpc, sampling_frequency=sampling_rate
        ),
        dtype=np.float32,
    ),
    color="#1f77b4",
    width=1.3,
)
multiunit_firing_rate_view.add_line_series(
    name="V1 Multiunit Rate (spikes/s)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(
        rd.get_multiunit_population_firing_rate(
            spike_indicator_v1, sampling_frequency=sampling_rate
        ),
        dtype=np.float32,
    ),
    color="#ff7f0e",
    width=1.3,
)

speed_view = vv.TimeseriesGraph()
speed_view.add_line_series(
    name="Speed (cm/s)",
    t=np.asarray(time, dtype=np.float32),
    y=np.asarray(speed_interp, dtype=np.float32),
    color="black",
    width=1.5,
)

gyro_view = vv.TimeseriesGraph()
gyro_view.add_line_series(
    name="Gyro X (deg/s)",
    t=np.asarray(time[:-100], dtype=np.float32),
    y=np.asarray(gyro_x_interp[:-100], dtype=np.float32),
    color="#1f77b4",
    width=1.3,
)
gyro_view.add_line_series(
    name="Gyro Y (deg/s)",
    t=np.asarray(time[:-100], dtype=np.float32),
    y=np.asarray(gyro_y_interp[:-100], dtype=np.float32),
    color="#ff7f0e",
    width=1.3,
)
gyro_view.add_line_series(
    name="Gyro Z (deg/s)",
    t=np.asarray(time[:-100], dtype=np.float32),
    y=np.asarray(gyro_z_interp[:-100], dtype=np.float32),
    color="#2ca02c",
    width=1.3,
)

view_height = 800

vertical_panel_content = [
    vv.LayoutItem(actual, stretch=1, title="Actual position"),
    vv.LayoutItem(decode_minus_actual, stretch=1, title="Decoded - Actual"),
    vv.LayoutItem(decode_minus_actual_zoom, stretch=1, title="Decoded - Actual Zoom"),
    vv.LayoutItem(
        decode_minus_actual_zoom_lowpass,
        stretch=1,
        title="Decoded - Actual Zoom Lowpass",
    ),
    vv.LayoutItem(multiunit_firing_rate_view, stretch=1, title="Multiunit"),
    vv.LayoutItem(speed_view, stretch=1, title="Speed"),
    vv.LayoutItem(gyro_view, stretch=1, title="Gyro"),
]

view = vv.Box(
    direction="vertical",
    show_titles=True,
    items=vertical_panel_content,
)

view_label = f"L10 20231006 run epochs {tag} decode analysis fit {epoch_to_fit} predict {epoch_to_predict}"
view_url = view.url(label=view_label)

with open(
    f"/nimbus/kyu/L10/20231006/run_epochs/view_url_{tag}_decode_analysis_fit_{epoch_to_fit}_predict_{epoch_to_predict}.txt",
    "w",
) as file:
    file.write(view_url)
