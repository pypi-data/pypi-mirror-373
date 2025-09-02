import json
from typing import Any, List, Mapping, Optional, Sequence, Set

from kelvin.sdk.lib.models.generic import KPath
from kelvin.sdk.lib.models.types import WorkloadFileType
from kelvin.sdk.lib.models.workloads.ksdk_workload_deployment import WorkloadTemplateData
from kelvin.sdk.lib.utils.general_utils import flatten, guess_delimiter, inflate

try:
    from typing import Literal
except ImportError:  # pragma: no cover
    from typing_extensions import Literal  # type: ignore # noqa: F401


def load_workload_data(
    file: KPath, file_type: WorkloadFileType, field_map: Optional[Mapping[str, Any]] = None
) -> Sequence[Mapping[str, Any]]:
    data: Sequence = []
    if file_type == WorkloadFileType.CSV:
        data = _load_csv_workload_data(file, field_map=field_map)
    elif file_type in {WorkloadFileType.YAML, WorkloadFileType.JSON}:
        try:
            data = _load_yaml_workload_data(file)
        except Exception as e:
            raise ValueError(f"Unable to read workload data - {e}")

    if not data:
        raise ValueError("No workloads found.")

    return data


def _load_csv_workload_data(file: KPath, field_map: Optional[Mapping[str, Any]] = None) -> Sequence[Mapping[str, Any]]:
    """Load workload data from CSV.

    Parameters
    ----------
    file : KPath
        CSV data file.
    field_map : Optional[Mapping[str, Any]]
        Optional mapping of field names.

    Returns
    -------
    Sequence[Mapping[str, Any]]:
        a sequence of mapping entries corresponding to individual deployments.

    """
    import csv

    if field_map is None:
        field_map = {}

    with file.open("rt") as f:
        header = f.readline().rstrip("\n")
        delimiter = guess_delimiter(header)
        fieldnames = [field_map.get(x, x) for x in header.split(delimiter)]

        reader = csv.DictReader(f, fieldnames=fieldnames, delimiter=delimiter)

        return [inflate(x) for x in reader]


def _load_yaml_workload_data(file: KPath) -> Sequence[Mapping[str, Any]]:
    """Load workload data from YAML/JSON.

    Parameters
    ----------
    file : KPath
        YAML/JSON data file.

    Returns
    -------
    Sequence[Mapping[str, Any]]:
        a sequence of mapping entries corresponding to individual deployments.

    """
    import yaml

    with file.open("rt") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, List):
        raise ValueError("Workload data must be a list")

    bad = [(i, x) for i, x in enumerate(data) if not isinstance(x, Mapping)]
    if bad:
        bad_entries = "\n".join(f"  - {i + 1}: {type(x).__name__}" for i, x in bad)  # noqa: E221
        raise ValueError(f"All entries in workload data must be mappings:\n{bad_entries}")

    return data


def save_workload_data(
    file: KPath, filename: str, file_type: WorkloadFileType, output_filename: Optional[str], results: Sequence[Mapping]
) -> bool:
    if output_filename is None:
        head, tail = filename.rsplit(".", 1)
        output_filename = f"{head}_result.{tail}"

    output_file = KPath(output_filename).complete_path()
    if file_type == WorkloadFileType.CSV:
        with file.open("rt") as f:
            delimiter = guess_delimiter(f.readline().rstrip("\n"))
        return _save_csv_workload_data(output_file, results, delimiter=delimiter)
    elif file_type in {WorkloadFileType.YAML, WorkloadFileType.JSON}:
        return _save_yaml_workload_data(output_file, results)
    return False


def _save_csv_workload_data(file: KPath, data: Sequence[Mapping[str, Any]], delimiter: str = ",") -> bool:
    """Save workload data to CSV.

    Parameters
    ----------
    file: KPath
        CSV data file.
    data: Sequence[Mapping[str, Any]]
        Workload data.
    delimiter: str
        Optional delimiter.

    Returns
    -------
    bool:
        a boolean indicating the csv data was successfully saved.

    """
    import csv

    if not data:
        return False

    flattened_data: List[Mapping[str, Any]] = []
    fields: Set[str] = {*()}

    for x in data:
        v = dict(flatten(x))
        flattened_data += [v]
        fields |= {*v}

    fieldnames = [*WorkloadTemplateData.__fields__]  # type: ignore
    fieldnames += sorted(fields - {*fieldnames})

    with file.open("wt") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(flattened_data)

    return True


def _save_yaml_workload_data(file: KPath, data: Sequence[Mapping[str, Any]]) -> bool:
    """Save workload data to YAML/JSON.

    Parameters
    ----------
    file: KPath
        YAML/JSON data file.
    data: Sequence[Mapping[str, Any]]
        Workload data.

    Returns
    -------
    bool:
        a boolean indicating the yaml data was successfully saved.

    """
    import yaml

    if not data:
        return False

    with file.open("wt") as f:
        if file.suffix == ".json":
            json.dump(data, f)
        else:
            yaml.dump(data, f)

    return True
