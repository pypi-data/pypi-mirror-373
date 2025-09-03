from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil import tz
import spikeinterface.full as si
import probeinterface as pi

from pynwb import NWBHDF5IO, NWBFile
from pynwb.ecephys import ElectricalSeries
from pynwb.file import Subject

from pathlib import Path
from ..probe.generate_probe import (
    get_Livermore_20um,
    get_Livermore_15um,
    get_Rice_EBL_128ch_1s,
)
from .utils import (
    TimestampsExtractor,
    TimestampsDataChunkIterator,
    SpikeInterfaceRecordingDataChunkIterator,
)

import matplotlib.pyplot as plt

from ..spikegadgets.trodesconf import readTrodesExtractedDataFile


def convert_to_nwb(
    dat_in_path: str, time_in_path: str, nwb_out_path: str, session_id: str = "1"
):
    """Minimal NWB conversion code for a four-probe (512 ch) implanted animal (e.g. L10) sampled at 20kHz.
    Assumes data has been exported to binary by trodesexport.
    Only converts ephys data and electrode information to NWB.

    Parameters
    ----------
    dat_in_path : str
        path to dat file containing recording
    time_in_path : str
        path to dat file containing time information
    nwb_out_path : str
        path to save the converted NWB file
    """
    # Create NWB file
    nwbfile = NWBFile(
        session_description="Homebox",
        identifier=str(uuid4()),
        session_start_time=datetime(
            2023, 9, 23, 19, 38, 35, tzinfo=tz.gettz("US/Pacific")
        ),
        experimenter=["Lee, Kyu Hyun", "Adenekan, Philip"],
        lab="Loren Frank",
        institution="University of California, San Francisco",
        experiment_description="L10 continuous recording in homebox",
        session_id=session_id,
    )

    # Add subject info
    nwbfile.subject = Subject(
        subject_id="L10",
        description="Wildtype male Long Evans rat implanted with Livermore probes in the hippocampus CA1 and primary visual cortex on Aug 25, 2023.",
        species="Rattus norvegicus",
        sex="M",
        genotype="wt",
        weight="0.485 kg",
        date_of_birth=datetime(2023, 4, 24, tzinfo=tz.gettz("US/Pacific")),
        strain="Long Evans",
    )

    # Define probes
    device_left_v1 = nwbfile.create_device(
        name="Livermore left V1", description="128c-4s4mm-20um-sl", manufacturer="LLNL"
    )
    device_left_ca1 = nwbfile.create_device(
        name="Livermore left CA1", description="128c-4s6mm-15um-sl", manufacturer="LLNL"
    )
    device_right_ca1 = nwbfile.create_device(
        name="Livermore right CA1",
        description="128c-4s4mm-20um-sl",
        manufacturer="LLNL",
    )
    device_right_v1 = nwbfile.create_device(
        name="Livermore right V1", description="128c-4s6mm-15um-sl", manufacturer="LLNL"
    )

    devices = [device_left_v1, device_left_ca1, device_right_ca1, device_right_v1]

    probe_left_v1 = get_Livermore_20um(order=0)
    probe_left_ca1 = get_Livermore_15um(order=1, shift=[2000, 4000])
    probe_right_ca1 = get_Livermore_20um(order=2, shift=[6000, 4000])
    probe_right_v1 = get_Livermore_15um(order=3, shift=[8000, 0])

    probegroup = pi.ProbeGroup()
    probegroup.add_probe(probe_left_v1)
    probegroup.add_probe(probe_left_ca1)
    probegroup.add_probe(probe_right_ca1)
    probegroup.add_probe(probe_right_v1)

    # Set location
    locations = [
        "Cornu ammonis 1 (CA1)",
        "Primary visual area (V1)",
        "Primary visual area (V1)",
        "Cornu ammonis 1 (CA1)",
    ]

    # Add column to electrode table
    nwbfile.add_electrode_column(name="label", description="label of electrode")

    # Add electrodes
    for probe_idx, probe in enumerate(probegroup.probes):
        for shank_id in np.unique(probe.shank_ids):
            # create an electrode group for this shank
            electrode_group = nwbfile.create_electrode_group(
                name=f"probe {probe_idx} shank {shank_id}",
                description=f"electrode group for probe {probe_idx} shank {shank_id}",
                device=devices[probe_idx],
                location=locations[probe_idx],
            )
            for hwchan_id in probe.device_channel_indices[probe.shank_ids == shank_id]:
                nwbfile.add_electrode(
                    id=hwchan_id,
                    group=electrode_group,
                    label=f"probe {probe_idx} shank {shank_id} hwchan {hwchan_id}",
                    location=locations[probe_idx],
                    rel_x=probe.contact_positions[
                        probe.device_channel_indices == hwchan_id
                    ][0][0],
                    rel_y=probe.contact_positions[
                        probe.device_channel_indices == hwchan_id
                    ][0][1],
                    reference="skull screw",
                )

    # Define table region
    all_table_region = nwbfile.create_electrode_table_region(
        region=list(range(len(nwbfile.electrodes.id[:]))),
        description="all electrodes",
    )

    sampling_frequency = 20000.0

    # Load recording
    recording = si.BinaryRecordingExtractor(
        file_paths=dat_in_path,
        sampling_frequency=sampling_frequency,
        num_channels=512,
        dtype="int16",
        gain_to_uV=0.19500000000000001,
        offset_to_uV=0,
        is_filtered=False,
    )

    # Match channel order to electrode table
    recording = recording.channel_slice(channel_ids=nwbfile.electrodes.id[:])

    data_iterator = SpikeInterfaceRecordingDataChunkIterator(
        recording=recording, return_scaled=False, buffer_gb=10
    )

    # Load timestamps
    # timestamps_extractor = TimestampsExtractor(time_in_path, sampling_frequency=20e3)

    # timestamps_iterator = TimestampsDataChunkIterator(
    #     recording=timestamps_extractor, buffer_gb=3
    # )
    time = readTrodesExtractedDataFile(time_in_path)
    starting_time = (
        time["data"]["systime"][
            time["data"]["time"] == np.int(time["first_timestamp"])
        ][0]
        * 1e-9
    )

    raw_electrical_series = ElectricalSeries(
        name="ElectricalSeries",
        data=data_iterator,
        electrodes=all_table_region,
        starting_time=starting_time,  # timestamp of the first sample in seconds relative to the session start time
        rate=sampling_frequency,
        # timestamps=timestamps_iterator,
        conversion=0.19500000000000001e-6,
        offset=0.0,
    )

    nwbfile.add_acquisition(raw_electrical_series)

    with NWBHDF5IO(nwb_out_path, "w") as io:
        io.write(nwbfile)


def compare_binary_to_nwb(
    nwb_path,
    data_path,
    epoch_list,
    probe_types,
    stereotaxic_coordinates,
    target_channel_id=3,
    start_frame=3000,
    end_frame=30000,
):
    """Compare voltage traces of a recording in binary vs. NWB format.

    Parameters
    ----------
    dat_path : str
        path to extracted binary file (with reconfig making the hw channel order numerical)
    nwb_path : str
        path to converted NWB file
    target_channel_id : int, optional
        channel to compare, by default 0
    frames_to_compare : int, optional
        number of first N frames to load and compare, by default 3000
    """
    recording_dat = get_binary_recording(
        data_path, epoch_list, probe_types, stereotaxic_coordinates
    )
    recording_nwb = si.read_nwb_recording(nwb_path)

    if type(target_channel_id) is int:
        target_channel_id = [target_channel_id]
    print(
        f"Using channel {target_channel_id} from binary recording to compare with NWB recording."
    )

    target_channel_loc = recording_dat.get_channel_locations()[
        recording_dat.get_channel_ids() == target_channel_id
    ]
    print(
        f"Location of channel {target_channel_id} from binary recording: {target_channel_loc}"
    )

    target_channel_idx_nwb = np.where(
        np.all(recording_nwb.get_channel_locations() == target_channel_loc, axis=1)
    )[0]
    target_channel_id_nwb = recording_nwb.get_channel_ids()[target_channel_idx_nwb]
    target_channel_loc_nwb = recording_nwb.get_channel_locations()[
        target_channel_idx_nwb
    ]

    print(
        f"Channel {target_channel_id} in binary recording is channel {target_channel_id_nwb} in NWB recording."
    )
    print(
        f"Location of channel {target_channel_id_nwb} in NWB recording: {target_channel_loc_nwb}"
    )

    traces_dat = recording_dat.get_traces(
        start_frame=start_frame,
        end_frame=end_frame,
        channel_ids=target_channel_id,
        return_scaled=True,
    )
    traces_nwb = recording_nwb.get_traces(
        start_frame=start_frame,
        end_frame=end_frame,
        channel_ids=target_channel_id_nwb,
        return_scaled=True,
    )

    t = np.arange(start_frame, end_frame)

    fig, ax = plt.subplots()
    ax.plot(t, traces_dat, label="binary")
    ax.plot(t, traces_nwb, label="nwb")
    ax.legend()
    ax.set_ylabel("Voltage ($\mu$V)")
    ax.set_xlabel("Time (samples)")

    print(
        f"Do the values agree to within 1 microV? {np.allclose(traces_dat, traces_nwb, atol=1)}"
    )
    return np.allclose(traces_dat, traces_nwb, atol=1)


def get_binary_recording(
    data_path,
    epoch_list,
    probe_types,
    stereotaxic_coordinates,
    sampling_rate=30e3,
    gain_to_uV=0.19500000000000001,
):
    """Returns a spikeinterface BinaryRecordingExtractor for a given day of recording taken with 128 ch probes.
    - Concatenates the recordings of all epochs in `epoch_list` (in order)
    - Creates a probeinterface.probegroup using stereotaxic coordinates to infer distance
    - Assumes that the rec file has been converted to int16 binary with trodesexport
    - Assumes the data_path is structured as follows:
        data_path
        |
        ---20240611_L14_01_r1
        |  |
        |  ---20240611_L14_01_r1.rec
        |  ---20240611_L14_01_r1.kilosort
        |     |
        |     ---20240611_L14_01_r1.group0.dat
        ----20240611_L14_02_s1
            |
            ----20240611_L14_02_s1.rec
        ...

    Parameters
    ----------
    data_path : str
        path to data; has to end with /animal_name/date/
        example: /path/to/data/L14/20240611/
    epoch_list : list
        name of the epochs, should be in order
        example: epoch_list = ['01_s1', '02_r1', '03_s2', '04_r2', '05_s3', '06_r3', '07_s4']
    probe_types : list
        list of probes used; must be in order of left to right
        possible probe types: 'livermore20', 'livermore15', 'rice-ebl'
        example: probe_types = ['livermore20', 'livermore15', 'livermore20', 'livermore15']
    stereotaxic_coordinates : List[List], (n, 3)
        AP, ML, DV coordinates in microns
        example: stereotaxic_coordinates = [[8000.0, -3000.0, 2000.0],
                                            [4000.0, -2000.0, 2800.0],
                                            [4000.0, 2000.0, 2800.0],
                                            [8000.0, 3000.0, 2000.0]]
    sampling_rate : float, default: 30e3
    gain_to_uV : float, default: 0.19500000000000001

    Returns
    -------
    recording : si.Recording
        binary recordings that have been concatenated and with probegroup attached
    """

    accepted_probe_types = ["livermore20", "livermore15", "rice-ebl"]
    assert all(probe_type in accepted_probe_types for probe_type in probe_types), print(
        "`probe_types` has at least one unknown probe type."
    )

    if isinstance(data_path, str):
        data_path = Path(data_path)

    parts = data_path.parts
    date = parts[-1]
    animal_name = parts[-2]

    recording_list = []
    for epoch in epoch_list:
        recording_path = (
            data_path / epoch / (epoch + ".kilosort") / (epoch + ".group0.dat")
        )
        if not recording_path.exists():
            prefix = f"{date}_{animal_name}_0{epoch_list.index(epoch)+1}_{epoch}"
            recording_path = (
                data_path / epoch / f"{prefix}.kilosort" / f"{prefix}.group0.dat"
            )
        if not recording_path.exists():
            recording_path = (
                data_path
                / f"{date}_{animal_name}_{epoch}"
                / f"{date}_{animal_name}_{epoch}.kilosort"
                / f"{date}_{animal_name}_{epoch}.group0.dat"
            )

        recording_list.append(
            si.BinaryRecordingExtractor(
                recording_path,
                sampling_frequency=sampling_rate,
                dtype=np.int16,
                num_channels=int(len(probe_types) * 128),
                gain_to_uV=gain_to_uV,
                offset_to_uV=0,
                is_filtered=False,
            )
        )

    recording = si.concatenate_recordings(recording_list)

    shift = [[0, 0]]
    if len(probe_types) > 1:
        print(f"Recording has {len(probe_types)} probes")
        for i in range(len(probe_types) - 1):
            shift.append(
                [
                    np.sqrt(
                        (
                            stereotaxic_coordinates[i][0]
                            - stereotaxic_coordinates[i + 1][0]
                        )
                        ** 2
                        + (
                            stereotaxic_coordinates[i][1]
                            - stereotaxic_coordinates[i + 1][1]
                        )
                        ** 2
                    ),
                    stereotaxic_coordinates[i][2] - stereotaxic_coordinates[i + 1][2],
                ]
            )

        # Make probeinterface probegroup
        probegroup = pi.ProbeGroup()
        for probe_idx, probe_type in enumerate(probe_types):
            if probe_type == "livermore20":
                probegroup.add_probe(
                    get_Livermore_20um(
                        order=probe_idx, shift=np.sum(shift[: probe_idx + 1], axis=0)
                    )
                )
            elif probe_type == "livermore15":
                probegroup.add_probe(
                    get_Livermore_15um(
                        order=probe_idx, shift=np.sum(shift[: probe_idx + 1], axis=0)
                    )
                )
            elif probe_type == "rice-ebl":
                probegroup.add_probe(
                    get_Rice_EBL_128ch_1s(
                        order=probe_idx, shift=np.sum(shift[: probe_idx + 1], axis=0)
                    )
                )

        recording = recording.set_probegroup(probegroup)
    else:
        print(f"Recording has one probe")
        probe_type = probe_types[0]
        if probe_type == "livermore20":
            probe = get_Livermore_20um(order=0, shift=[0, 0])
        elif probe_type == "livermore15":
            probe = get_Livermore_15um(order=0, shift=[0, 0])
        elif probe_type == "rice-ebl":
            probe = get_Rice_EBL_128ch_1s(order=0, shift=[0, 0])
        recording = recording.set_probe(probe)

    return recording
