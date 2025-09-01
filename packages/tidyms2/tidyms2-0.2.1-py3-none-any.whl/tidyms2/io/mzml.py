"""mzML reader implementation.

Rationale
---------

mzML files can have typical sizes that span from 50 MiB to more than 1000 MiB.
mzML files are basically xml files with the acquired data and metadata
associated with the acquisition conditions. The data is inside <spectrum> and
<chromatogram> elements.  From the expected file sizes, it is clear that
loading the entire file in memory is not desirable.
There are tools to parse xml files in an incremental way (such as iterparse
inside the xml module), but the problem with this approach is that accessing a
specific scan in the file turns out to be rather slow.
Indexed mzML files have an <indexedmzML> tag that allows to search in a fast
way the location of spectrum and chromatogram tags.
Taking advantage of this information, this module search spectrum and
chromatogram elements and only loads the part associated with the selected
spectrum or chromatogram.
The function build_offset_list creates the list of offsets associated with
chromatograms and spectra using the information in <indexedmzML>. In the
case of non-indexed files, the offset list is built from scratch.
The functions get_spectrum and get_chromatogram takes the offset information
and extracts the relevant data from each spectrum/chromatogram.

# mzML specification:
# https://www.psidev.info/mzML
# terms defined here:
# https://raw.githubusercontent.com/HUPO-PSI/psi-ms-CV/master/psi-ms.obo

build_offset_list : Finds offsets with the location of spectra and chromatograms
get_spectrum : Extracts data from a spectrum using offsets.
get_chromatogram : Extracts data from a chromatogram using offsets.

"""

import base64
import enum
import re
import zlib
from os import SEEK_END
from os.path import getsize
from pathlib import Path
from typing import Any, cast
from xml.etree.ElementTree import Element, fromstring

import numpy as np

from ..core.models import Chromatogram, MSSpectrum, Sample
from .msdata import reader_registry


@reader_registry.register("mzML", "mzml")
class MZMLReader:
    """mzML format reader."""

    def __init__(self, src: Path | Sample, rebuild_index: bool = False):
        self.path = src if isinstance(src, Path) else src.path
        sp_offset, chrom_offset, index_offset = _build_offset_list(self.path, rebuild_index)
        self.spectra_offset = sp_offset
        self.chromatogram_offset = chrom_offset
        self.index_offset = index_offset

        self.n_chromatograms = len(self.chromatogram_offset)
        self.n_spectra = len(self.spectra_offset)

    def get_spectrum(self, index: int) -> MSSpectrum:
        """Retrieve a spectrum from file."""
        return _get_spectrum(
            self.path,
            self.spectra_offset,
            self.chromatogram_offset,
            self.index_offset,
            index,
        )

    def get_n_spectra(self) -> int:
        """Return the number of spectra in the file."""
        return self.n_spectra

    def get_n_chromatograms(self) -> int:
        """Return the number of chromatogram in the file."""
        return self.n_chromatograms

    def get_chromatogram(self, index: int) -> Chromatogram:
        """Retrieve a chromatogram from file."""
        return _get_chromatogram(
            self.path,
            self.spectra_offset,
            self.chromatogram_offset,
            self.index_offset,
            index,
        )


UNSUPPORTED_COMPRESSION = frozenset(
    (
        "MS:1002312",
        "MS:1002313",
        "MS:1002314",
        "MS:1002746",
        "MS:1002747",
        "MS:1002748",
        "MS:1003088",
        "MS:1003089",
        "MS:1003090",
    )
)


class _CompressionType(str, enum.Enum):
    """The compression types defined in the mzML spec and their accession numbers."""

    ZLIB = "MS:1000574"


MS_LEVEL = "MS:1000511"


class _ArrayType(str, enum.Enum):
    """The array types defined in the mzML specification and their accession numbers."""

    MZ_ARRAY = "MS:1000514"
    """An array with m/z data"""

    INT_ARRAY = "MS:1000515"
    """An array with spectral intensity"""

    TIME_ARRAY = "MS:1000595"
    """An array with with time data"""

    TIME = "MS:1000016"  # time value in scans


class _Polarity(str, enum.Enum):
    """mzML polarity values."""

    NEGATIVE = "MS:1000129"
    POSITIVE = "MS:1000130"


class _TimeUnits(str, enum.Enum):
    """mzML time units."""

    SECONDS = "UO:0000010"
    MINUTES = "UO:0000031"


class _DataTypes(str, enum.Enum):
    FLOAT16 = "UNKNOWN"
    FLOAT32 = "MS:1000521"
    FLOAT64 = "MS:1000523"
    INT32 = "MS:1000519"
    INT64 = "MS:1000522"


_MZML_TYPE_TO_NUMPY_TYPE = {
    _DataTypes.FLOAT16.value: np.float16,
    _DataTypes.FLOAT32.value: np.float32,
    _DataTypes.FLOAT64.value: np.float64,
    _DataTypes.INT32.value: np.int32,
    _DataTypes.INT64.value: np.int64,
}


class MZMLError(ValueError):
    """Exception raised when an error happens while parsing an mzML file."""


def _build_offset_list(filename: Path, rebuild_index: bool) -> tuple[list[int], list[int], int]:
    """Find the offset values where Spectrum or Chromatogram elements start.

    :param filename: path to a mzML file
    :param rebuild_index: if set to ``True`` rebuilds the index even if the file is indexed

    :return: Offsets where spectrum element start, offsets where chromatogram elements start
        Offset where the index starts. If the file is not indexed, return the file size.

    """
    if not rebuild_index and is_indexed(filename):
        index_offset = _get_index_offset(filename)
        spectra_offset, chromatogram_offset = _build_offset_list_indexed(filename, index_offset)
    else:
        spectra_offset, chromatogram_offset = _build_offset_list_non_indexed(filename)
        index_offset = getsize(filename)
    return spectra_offset, chromatogram_offset, index_offset


def _get_spectrum(
    filename: Path, spectra_offset: list[int], chromatogram_offset: list[int], index_offset: int, n: int
) -> MSSpectrum:
    """Extract spectrum data from file.

    :param filename: path to mzML file.
    :param :spectra_offset : offset list obtained from `_build_offset_list`.
    :parm chromatogram_offset: Offset list obtained from `_build_offset_list`.
    :parma index_offset: offset obtained from `_build_offset_list`.
    :param n: scan number to select.
    :returns: dictionary with m/z, intensity, polarity , time, and ms level.

    """
    xml_str = _get_xml_data(filename, spectra_offset, chromatogram_offset, index_offset, n, "spectrum")
    elements = list(fromstring(xml_str))
    spectrum = dict()
    spectrum["index"] = n
    for el in elements:
        tag = el.tag
        if tag == "cvParam":
            accession = el.attrib.get("accession")
            if accession == MS_LEVEL:
                ms_level = el.attrib.get("value")
                spectrum["ms_level"] = 1 if ms_level is None else int(ms_level)
            elif accession == _Polarity.NEGATIVE:
                spectrum["polarity"] = -1
            elif accession == _Polarity.POSITIVE:
                spectrum["polarity"] = 1
        elif tag == "scanList":
            spectrum["time"] = _get_time(el)
        elif tag == "binaryDataArrayList":
            sp_data = _parse_binary_data_list(el)
            spectrum.update(sp_data)

    return MSSpectrum(**spectrum)


def _get_chromatogram(
    filename: Path, spectra_offset: list[int], chromatogram_offset: list[int], index_offset: int, n: int
) -> Chromatogram:
    """Extract time and intensity from xml chunk.

    :parm filename: path to mzML file
    :param spectra_offset: offset list obtained from _build_offset_list
    :param chromatogram_offset: offset list obtained from _build_offset_list
    :param index_offset: offset obtained from _build_offset_list
    :param n: chromatogram number
    :returns: dict

    """
    xml_str = _get_xml_data(filename, spectra_offset, chromatogram_offset, index_offset, n, "chromatogram")
    elements = fromstring(xml_str)
    name = elements.attrib.get("id")
    chromatogram: dict[str, Any] = dict(name=name)
    for el in list(elements):
        tag = el.tag
        if tag == "binaryDataArrayList":
            chrom_data = _parse_binary_data_list(el)
            chromatogram.update(chrom_data)
    return Chromatogram(**chromatogram)


class _ReverseReader:
    """Read file objects starting from the EOF.

    :param filename: Path to the file
    :param buffer_size: size of the chunk to get when using the `read_chunk` method
    :param kwargs: keyword arguments to pass to the open function

    """

    def __init__(self, filename: Path, buffer_size: int, **kwargs):
        self.file = open(filename, **kwargs)
        self.buffer_size = buffer_size
        self._size = self.file.seek(0, SEEK_END)
        self.offset = self._size
        self._is_complete = False

    @property
    def offset(self) -> int:
        """Retrieve the file offset."""
        return self._offset

    @offset.setter
    def offset(self, value: int):
        if value < 0:
            value = 0
            self._is_complete = True
        self._offset = value
        self.file.seek(value)

    def __enter__(self):
        return self

    def __exit__(self, t, value, traceback):
        self.file.close()

    def read_chunk(self) -> str | None:
        """Read a chunk of data from the file, starting from the end.

        If the beginning of the file has been reached, it returns None.
        """
        if self._is_complete:
            res = None
        else:
            self.offset = self.offset - self.buffer_size
            res = self.file.read(self.buffer_size)
        return res

    def reset(self):
        """Set the position of the reader to the EOF."""
        self.offset = self._size
        self._is_complete = False


def _read_binary_data_array(element: Element) -> tuple[np.ndarray, str]:
    """Extract the binary data and data kind from a binaryArray element.

    data : array
    # kind : can be one of {"mz", "spint", "time"}

    """
    has_zlib_compression = False
    data = None
    kind = "none"
    units = None
    dtype = None
    for e in element:
        tag = e.tag
        if tag == "binary":
            data = e.text if e.text is None else e.text.strip()
        elif tag == "cvParam":
            accession = e.attrib.get("accession")
            if accession in UNSUPPORTED_COMPRESSION:
                msg = "Currently only zlib compression is supported."
                raise MZMLError(msg)
            elif accession == _CompressionType.ZLIB:
                has_zlib_compression = True
            elif accession == _ArrayType.INT_ARRAY:
                kind = "int"
            elif accession == _ArrayType.MZ_ARRAY:
                kind = "mz"
            elif accession == _ArrayType.TIME_ARRAY:
                kind = "time"
                units = e.attrib.get("unitAccession")
            if accession in _MZML_TYPE_TO_NUMPY_TYPE:
                dtype = _MZML_TYPE_TO_NUMPY_TYPE[accession]
    if data:
        data = base64.b64decode(data)
        if has_zlib_compression:
            data = zlib.decompress(data)
        data = np.frombuffer(data, dtype=dtype).copy()
        if kind == "time":
            data = _time_to_seconds(data, units)
    else:
        data = np.array([])
    return data, kind


def _parse_binary_data_list(element: Element) -> dict:
    """Extract the data from a binaryDataArrayList.

    :param element: Element
    :returns: dictionary that maps data kind to its correspondent data array.

    """
    res = dict()
    for e in element:
        data, data_type = _read_binary_data_array(e)
        res[data_type] = data
    return res


def is_indexed(filename: Path) -> bool:
    """Check if a mzML file is indexed.

    :param filename: Path

    Notes
    -----
    This function assumes that the mzML file is validated. It looks up the last
    closing tag, that should be </indexedmzML> if the file is indexed.

    """
    with _ReverseReader(filename, 1024, mode="r") as fin:
        end_tag = "</indexedmzML>"
        chunk = cast(str, fin.read_chunk())
        res = chunk.find(end_tag) != -1
    return res


def _get_index_offset(filename: Path) -> int:
    """Search the byte offset where the indexListOffset element starts.

    :param filename: Path

    :returns: index offset

    """
    tag = "<indexListOffset>"
    # reads mzml backwards until the tag is found
    # we exploit the fact that according to the mzML schema the
    # indexListOffset should have neither attributes nor sub elements
    with _ReverseReader(filename, 1024, mode="r") as fin:
        xml = ""
        ind = -1
        while ind == -1:
            chunk = fin.read_chunk()
            if chunk is not None:
                xml = chunk + xml
                ind = chunk.find(tag)
        # starts at the beginning of the text tag
        start = ind + len(tag)
        xml = xml[start:]
        end = xml.find("<")
    index_offset = int(xml[:end])
    return index_offset


def _build_offset_list_non_indexed(filename: Path) -> tuple[list[int], list[int]]:
    """Build manually the indices for non-indexed mzML files."""
    # indices are build by finding the offset where spectrum or chromatogram
    # elements starts.
    spectrum_regex = re.compile("<spectrum .[^(><.)]+>")
    chromatogram_regex = re.compile("<chromatogram .[^(><.)]+>")
    ind = 0
    spectrum_offset_list = list()
    chromatogram_offset_list = list()
    with open(filename) as fin:
        while True:
            line = fin.readline()
            if line == "":
                break
            spectrum_offset = _find_spectrum_tag_offset(line, spectrum_regex)
            if spectrum_offset:
                spectrum_offset_list.append(ind + spectrum_offset)
            chromatogram_offset = _find_chromatogram_tag_offset(line, chromatogram_regex)
            if chromatogram_offset:
                chromatogram_offset_list.append(ind + chromatogram_offset)
            ind += len(line)
    return spectrum_offset_list, chromatogram_offset_list


def _find_spectrum_tag_offset(line: str, regex: re.Pattern) -> int | None:
    if line.lstrip().startswith("<spectrum"):
        match = regex.search(line)
        if match:
            start, end = match.span()
        else:
            start = None
        return start


def _find_chromatogram_tag_offset(line: str, regex: re.Pattern) -> int | None:
    if line.lstrip().startswith("<chromatogram"):
        match = regex.search(line)
        if match:
            start, end = match.span()
        else:
            start = None
        return start


def _build_offset_list_indexed(filename: Path, index_offset: int) -> tuple[list[int], list[int]]:
    """Build a list of offsets where spectra and chromatograms are stored.

    :param filename: Path
    :param index_offset : offset obtained from _get_index_offset
    :returns: offset where spectra are stored and offset where chromatograms are stored

    """
    end_tag = "</indexList>"
    with open(filename, "r") as fin:
        fin.seek(index_offset)
        index_xml = fin.read()
        end = index_xml.find(end_tag)
        index_xml = index_xml[: end + len(end_tag)]
    index_xml = fromstring(index_xml)

    spectra_offset = list()
    chromatogram_offset = list()
    for index in index_xml:
        for offset in index:
            if offset.text is None:
                raise MZMLError("Non integer offset found in indexed file.")
            value = int(offset.text)
            if index.attrib["name"] == "spectrum":
                spectra_offset.append(value)
            elif index.attrib["name"] == "chromatogram":
                chromatogram_offset.append(value)
    return spectra_offset, chromatogram_offset


def _get_xml_data(
    filename: Path, spectra_offset: list[int], chromatogram_offset: list[int], index_offset: int, n: int, kind: str
) -> str:
    """Get the xml string associated with a spectrum or chromatogram.

    :param filename: str
    :param spectra_offset: offsets obtained from _build_offset_list
    :param chromatogram_offset: offsets obtained from _build_offset_list
    :param index_offset: offset obtained from _get_index_offset
    :param n: number of spectrum/chromatogram to select
    :param kind: {"spectrum", "chromatogram"}

    Returns
    -------
    str

    """
    if kind == "spectrum":
        lst, other = spectra_offset, chromatogram_offset
        end_tag = "</spectrum>"
    elif kind == "chromatogram":
        lst, other = chromatogram_offset, spectra_offset
        end_tag = "</chromatogram>"
    else:
        raise MZMLError("Kind must be `spectrum` or `chromatogram`")

    start = lst[n]
    # Here we search the closest offset to start such that the complete data is contained in the text
    try:
        end = lst[n + 1]
    except IndexError:
        try:
            end = other[0]
        except IndexError:
            end = index_offset

    if end < start:
        end = index_offset

    with open(filename, "r") as fin:
        fin.seek(start)
        chunk = fin.read(end - start)
    end = chunk.find(end_tag)
    return chunk[: end + len(end_tag)]


def _get_time(element):
    for e in list(element):
        tag = e.tag
        if tag == "scan":
            for ee in list(e):
                accession = ee.attrib.get("accession")
                if accession == _ArrayType.TIME:
                    value = float(ee.attrib.get("value"))
                    units = ee.attrib.get("unitAccession")
                    value = _time_to_seconds(value, units)
                    return value


def _time_to_seconds(value, units):
    if units == _TimeUnits.MINUTES:
        value = value * 60
    return value
