import os
from os import PathLike
import configparser
from glob import glob
from datetime import datetime, timezone
from typing import TypedDict
from nptdms import TdmsFile
import numpy as np
import numpy.typing as npt
from scipy.signal import butter, filtfilt
import h5py


def calculate_phase_2ch(
    ch1: npt.ArrayLike,
    ch2: npt.ArrayLike,
    parameters=None,
    parameters_type={"Variable": False, "Step": None},
):
    """Calculate phase from two signals of the interferometer."""

    S = ch1 + ch2
    C = ch1 - ch2

    if parameters is None and parameters_type["Variable"] is False:
        S = S - (np.amax(S) + np.amin(S)) / 2
        S = S / np.amax(S)
        C = C - (np.amax(C) + np.amin(C)) / 2
        C = C / np.amax(C)
    else:  # va fatto meglio il caso perché in realtà i vettori dei parametri non saranno None ma tutti 0 o tutti 1.
        S = S - parameters["offset"][0]
        S = S / parameters["max"][0]
        C = C - parameters["offset"][1]
        C = C / parameters["max"][1]
        # controllare che l'ordine con cui salvo in labview sia lo stesso (num e denom dell'arctan2)

    ph = np.arctan2(C, S)
    phase = np.unwrap(ph)
    return phase


def calculate_phase_3ch(
    ch1: npt.ArrayLike, ch2: npt.ArrayLike, ch3: npt.ArrayLike, parameters=None
):
    """Calculate phase from three signals of the interferometer."""
    if parameters is None:
        parameters["offset"] = [np.amin(ch1), np.amin(ch2), np.amin(ch3)]
        parameters["max"] = [np.amax(ch1), np.amax(ch2), np.amax(ch3)]

    ch1 = (ch1 - parameters["offset"][0]) / parameters["max"][0]
    ch2 = (ch2 - parameters["offset"][1]) / parameters["max"][1]
    ch3 = (ch3 - parameters["offset"][2]) / parameters["max"][2]

    I = ch2 - ch1 / 2 - ch3 / 2
    Q = np.sqrt(3) / 2 * (ch3 - ch1)

    ph = np.arctan2(I, Q)
    phase = np.unwrap(ph)
    return phase


def detrend(
    data: npt.ArrayLike, sampling_rate: float, highpass_cutoff_Hz: float = 50.0
) -> npt.ArrayLike:

    nyquist = 0.5 * sampling_rate
    normal_cutoff = highpass_cutoff_Hz / nyquist
    b, a = butter(N=4, Wn=normal_cutoff, btype="high", analog=False)
    filtered_data = filtfilt(b, a, data)

    return filtered_data


def read_config(filename: PathLike):
    config = configparser.ConfigParser()
    config.read(filename)

    parameters = {}
    for sec in config.sections():
        parameters[sec] = []
        for el in config[sec]:
            parameters[sec].append(float(config[sec][el]))
    return parameters


class Parameters(TypedDict):
    max: npt.ArrayLike
    offset: npt.ArrayLike
    normalization: npt.ArrayLike


class File:
    def __init__(self, filename: PathLike):
        tdms_file = TdmsFile(filename)

        first = True
        self.channels_name = []
        self.phasename = []

        self.filename = tdms_file.properties["name"]
        self.freq_sampling = round(tdms_file.properties["SampleFrequency"], 5)

        self.parameters: Parameters = Parameters(
            max=np.fromstring(tdms_file.properties["Max"].replace(",", "."), sep="\t"),
            offset=np.fromstring(
                tdms_file.properties["Offset"].replace(",", "."), sep="\t"
            ),
            normalization=np.fromstring(
                tdms_file.properties["Normalization"].replace(",", "."), sep="\t"
            ),
        )

        (dirname, tail) = os.path.split(os.path.abspath(filename))
        self.folder = dirname

        try:
            # File generato con sw originale da Laboratorio
            self.author = tdms_file.properties["Author"]
            self.note = tdms_file.properties["Note"]
        except KeyError:
            # File generato con programma FNM o derivati
            self.author = ""
            self.note = ""

        for group in tdms_file.groups():
            for ch in group.channels():
                if first:
                    self.start_time = ch.properties["wf_start_time"]
                    self.time = ch.time_track()
                    self.n_samples = ch.data.size
                    first = False

                if group.name == "Channels":
                    self.channels_name.append(ch.name.lower())
                elif group.name in ["Phases", "Phase", "phases", "phase"]:
                    self.phasename.append(ch.name.lower())
                setattr(self, ch.name.lower(), ch.data)

    def undersampling(self, factor=100, what="all"):
        validwhat = {"all", "channel", "phase"}
        if what == "all":
            whatchannels = self.channels_name + self.phasename
        elif what == "channel":
            whatchannels = self.channels_name
        elif what == "phase":
            whatchannels = self.phasename
        else:
            raise ValueError("results: what must be one of %r." % validwhat)

        for ch in whatchannels:
            data = getattr(self, ch)
            setattr(self, ch, data[0::factor])
        self.time = self.time[0::factor]
        self.freq_sampling = self.freq_sampling / factor
        self.n_samples = self.time.size

    def calc_phase(self, use_parameters=True, n_channels=3):
        validnchannels = {2, 3}
        if n_channels not in validnchannels:
            raise ValueError("results: n_channels must be one of %r." % validnchannels)

        # Elimino da phasename i nomi delle fasi calcolate.
        temp = []
        for el in self.phasename:
            if not el.startswith("phase_calc"):
                temp.append(el)
        self.phasename = temp

        # Potenzialmente in grado di gestire tdms con canali relativi a più interferometri e quindi più fasi.
        # Però i parametri vanno divisi anche loro
        n_sensors = int(len(self.channels_name) / n_channels)
        channelsmatrix = np.asarray(self.channels_name).reshape((n_sensors, n_channels))
        for sensor in range(n_sensors):
            if n_sensors == 1:
                phasename = "phase_calc"
            else:
                phasename = f"phase_calc_S{sensor+1}"

            self.phasename.append(phasename)
            if n_channels == 2:
                phase = calculate_phase_2ch(
                    getattr(self, channelsmatrix[sensor, 0]),
                    getattr(self, channelsmatrix[sensor, 1]),
                    parameters=self.parameters,
                )
            elif n_channels == 3:
                phase = calculate_phase_3ch(
                    getattr(self, channelsmatrix[sensor, 0]),
                    getattr(self, channelsmatrix[sensor, 1]),
                    getattr(self, channelsmatrix[sensor, 2]),
                    parameters=self.parameters,
                )
            setattr(self, phasename, np.asarray(phase))

    def convert_to_elongation(self, coefficient=9.239e6) -> npt.ArrayLike:
        """Restituisce un np array di delta allungamento (in metri), rispetto all'instate t0.
        Da Hocker 1979, il coefficiente tipico per la fibra ottica è 9.239 rad/um"""
        return (self.phase - self.phase[0]) / coefficient

    def convert_to_temperature(
        self, fiber_length_m: float, coefficient: float = 42.56
    ) -> npt.ArrayLike:
        """Restituisce un np array di delta temperatura (in °C), rispetto all'instate t0.
        Da Hocker 1979, il coefficiente tipico per la fibra ottica è 42.56 rad/(°C*m)'
        """
        return (self.phase - self.phase[0]) / (coefficient * fiber_length_m)

    def deletechannels(self):
        for ch in self.channels_name:
            delattr(self, ch)
        self.channels_name = []

    def deletephase(self):
        for ph in self.phasename:
            delattr(self, ph)
        self.phasename = []

    def export_to_h5(self, filename: PathLike):

        with h5py.File(filename, "w") as f:

            f.create_dataset("time", data=self.time)
            f.attrs["author"] = self.author
            f.attrs["note"] = self.note
            f.attrs["start_time"] = (
                datetime.fromtimestamp(
                    self.start_time.astype(np.int64) / 1e6, tz=timezone.utc
                )
                .astimezone()
                .isoformat(timespec="milliseconds")
            )
            f.attrs["freq_sampling"] = self.freq_sampling
            f.attrs["n_samples"] = self.n_samples
            f.attrs["files"] = self.filename
            f.attrs["folder"] = self.folder

            if self.phasename:
                if len(self.phasename) > 1:
                    ph_group = f.create_group(name="phases")
                    for ph in self.phasename:
                        ph_group.create_dataset(ph, data=getattr(self, ph))
                else:
                    f.create_dataset(
                        "phase", data=getattr(self, self.phasename[0]), dtype="f4"
                    )
            if self.channels_name:
                ch_group = f.create_group(name="channels")
                for ch in self.channels_name:
                    ch_group.create_dataset(ch, data=getattr(self, ch), dtype="f4")

    @property
    def absolute_time(self) -> list[datetime]:
        """Return the absolute time array"""
        return np.datetime64(self.start_time) + np.arange(
            self.n_samples
        ) * np.timedelta64(int(1 / self.freq_sampling * 1e6), "us")

        return [
            datetime.fromtimestamp(
                self.start_time.astype(np.int64) / 1e6 + i / self.freq_sampling,
                tz=timezone.utc,
            ).astimezone()
            for i in range(self.n_samples)
        ]

    def __repr__(self):
        message = (
            f"filename:\t{self.filename}\n"
            f"folder:\t{self.folder}\n"
            f"author:\t{self.author}\n"
            f"note:\t{self.note}\n"
            f"startime:\t{self.start_time}\n"
            f"freq_sampling:\t{self.freq_sampling}\n"
            f"parameters:\t{self.parameters.keys()}\n"
            f"n_samples:\t{self.n_samples}\n"
            f"channels_name:\t{self.channels_name}\n"
            f"phasename:\t{self.phasename}\n"
        )
        return message


class multipleFiles(File):
    def __init__(self, folder: PathLike, filename: str):
        pattern = folder + "/*" + filename + "*.tdms"

        firstCh = True
        firstFile = True
        self.channels_name = []
        self.phasename = []
        self.filename = []

        for currentFile in glob(pattern):
            tdms_file = TdmsFile(currentFile)
            self.filename.append(tdms_file.properties["name"])
            for group in tdms_file.groups():
                for ch in group.channels():
                    if firstFile:
                        self.folder = os.path.abspath(folder)
                        # self.time = ch.time_track()
                        try:
                            self.author = tdms_file.properties["Author"]
                            self.note = tdms_file.properties["Note"]
                        except KeyError:
                            self.author = ""
                            self.note = ""

                        self.parameters: Parameters = Parameters(
                            max=np.fromstring(
                                tdms_file.properties["Max"].replace(",", "."), sep="\t"
                            ),
                            offset=np.fromstring(
                                tdms_file.properties["Offset"].replace(",", "."),
                                sep="\t",
                            ),
                            normalization=np.fromstring(
                                tdms_file.properties["Normalization"].replace(",", "."),
                                sep="\t",
                            ),
                        )
                        if group.name == "Channels":
                            self.channels_name.append(ch.name.lower())
                        elif group.name in ["Phases", "Phase", "phases", "phase"]:
                            self.phasename.append(ch.name.lower())
                        setattr(self, ch.name.lower(), ch.data)

                    else:
                        setattr(
                            self,
                            ch.name.lower(),
                            np.append(getattr(self, ch.name.lower()), ch.data),
                        )

                    if firstCh:
                        self.freq_sampling = round(1 / ch.properties["wf_increment"], 5)
                        self.start_time = ch.properties["wf_start_time"]
                        firstCh = False
            del tdms_file
            firstFile = False
        try:
            self.n_samples = getattr(self, self.phasename[0].lower()).size
        except IndexError:
            self.n_samples = getattr(self, self.channels_name[0].lower()).size

        self.time = np.arange(0, self.n_samples) / self.freq_sampling
