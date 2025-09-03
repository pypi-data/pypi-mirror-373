from typing import List, Dict


def create_curation_json(curation_json: str, labels: dict, merge_groups: list):
    """Writes labels and merge_groups to a new curation.json file.

    Parameters
    ----------
    curation_json : str
        path where a new curation.json would be written
        example: "gh://LorenFrankLab/sorting-curations/main/khl02007/L5/20230411_r3_20230511_r1/curation.json"
    initial_curation_json : str
        _description_
    labels : dict
        _description_
    merge_groups : list
        _description_
    """
    return curation_json


def create_figurl_spikesorting(
    recording, sorting, label: str, metrics: List[dict] = None, curation_uri: str = None
):
    """Creates a figurl to view the sorting results.

    Parameters
    ----------
    recording : si.Recording
        Recording; have to be either Binary or NWB recording
    sorting : si.Sorting
        Sorting; have to be NpzSortingExtractor
    label : str
        label for this figurl
    metrics : List[dict], optional
        See example below for the format of metrics, by default None
    curation_uri : str, optional
        path to json file containing curation information in the GitHub repository, by default None
        Example: "gh://LorenFrankLab/sorting-curations/main/khl02007/L5/20230411_r3_20230511_r1/curation.json"

    Example
    -------
    metrics = [
        {
            "name": 'isi_viol',
            "label": 'fraction of ISI violations',
            "tooltip": "fraction of ISI violations",
            "data": {'1': 0.1, '2': 0.2, '3': 0.3},
        },
        {
            "name": 'snrs',
            "label": 'signal-to-noise ratio in z-score',
            "tooltip": "signal-to-noise ratio",
            "data": {'1': 0.1, '2': 0.1, '3': 1.3},
        },
        ]

    Returns
    -------
    url : str
        figurl
    """
    try:
        import kachery_cloud as kcl
        import sortingview as sv
        import sortingview.views as vv
        from sortingview.SpikeSortingView import SpikeSortingView
    except ImportError as e:
        print(
            f"Error: {e}. Please install `kachery-cloud` and `sortingview` to proceed."
        )
        return  # exit the function or handle this as needed

    X = SpikeSortingView.create(
        recording=recording,
        sorting=sorting,
        segment_duration_sec=60 * 20,
        snippet_len=(20, 20),
        max_num_snippets_per_segment=300,
        channel_neighborhood_size=12,
    )

    # Assemble the views in a layout
    # You can replace this with other layouts
    raster_plot_subsample_max_firing_rate = 50
    spike_amplitudes_subsample_max_firing_rate = 50
    view = vv.MountainLayout(
        items=[
            vv.MountainLayoutItem(label="Summary", view=X.sorting_summary_view()),
            vv.MountainLayoutItem(
                label="Units table",
                view=X.units_table_view(unit_ids=X.unit_ids, unit_metrics=metrics),
            ),
            vv.MountainLayoutItem(
                label="Raster plot",
                view=X.raster_plot_view(
                    unit_ids=X.unit_ids,
                    _subsample_max_firing_rate=raster_plot_subsample_max_firing_rate,
                ),
            ),
            vv.MountainLayoutItem(
                label="Spike amplitudes",
                view=X.spike_amplitudes_view(
                    unit_ids=X.unit_ids,
                    _subsample_max_firing_rate=spike_amplitudes_subsample_max_firing_rate,
                ),
            ),
            vv.MountainLayoutItem(
                label="Autocorrelograms",
                view=X.autocorrelograms_view(unit_ids=X.unit_ids),
            ),
            vv.MountainLayoutItem(
                label="Cross correlograms",
                view=X.cross_correlograms_view(unit_ids=X.unit_ids),
            ),
            vv.MountainLayoutItem(
                label="Avg waveforms",
                view=X.average_waveforms_view(unit_ids=X.unit_ids),
            ),
            vv.MountainLayoutItem(
                label="Electrode geometry", view=X.electrode_geometry_view()
            ),
            vv.MountainLayoutItem(
                label="Curation", view=vv.SortingCuration2(), is_control=True
            ),
        ]
    )
    if curation_uri:
        url_state = {"sortingCuration": curation_uri}
    else:
        url_state = None
    url = view.url(label=label, state=url_state)
    return url


def reformat_metrics(metrics: Dict[str, Dict[str, float]]) -> List[Dict]:
    """Converts metrics dict to a format acceptable to figurl

    Parameters
    ----------
    metrics : Dict[str, Dict[str, float]]

    Example:
        {
            'isi_viol': {'1': 0.1, '2': 0.2, '3': 0.3},
            'snrs': {'1': 0.1, '2': 0.1, '3': 1.3},
        }

    Returns
    -------
    new_external_metrics : List[Dict]

    Example:
        [
            {
                "name": 'isi_viol',
                "label": 'fraction of ISI violations',
                "tooltip": "fraction of ISI violations",
                "data" : {'1': 0.1, '2': 0.2, '3': 0.3},
            },
            {
                "name": 'snrs',
                "label": 'signal-to-noise ratio in z-score',
                "tooltip": "signal-to-noise ratio",
                "data" : {'1': 0.1, '2': 0.1, '3': 1.3},
            }
        ]
    """
    for metric_name in metrics:
        metrics[metric_name] = {
            str(unit_id): metric_value
            for unit_id, metric_value in metrics[metric_name].items()
        }
    new_external_metrics = [
        {
            "name": metric_name,
            "label": metric_name,
            "tooltip": metric_name,
            "data": metric,
        }
        for metric_name, metric in metrics.items()
    ]
    return new_external_metrics
