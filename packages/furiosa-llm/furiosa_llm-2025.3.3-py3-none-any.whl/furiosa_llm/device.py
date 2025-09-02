import re
from typing import List, Optional, Sequence, Set

from furiosa_llm.parallelize.mppp.config import POSSIBLE_FUSION_GRANULARITY, Device, UnitDevice


def parse_devices_str(s: str) -> List[Device]:
    """
    Parse a string representation indicating specific devices (e.g., cpu:0,cpu:1,gpu:0)
    :param s: a string representing of devices
    :return: a list of `Device` objects
    """
    devices = []
    for device_str in s.split(","):
        device_str = device_str.strip()
        devices.append(Device(device_str))
    return devices


PE_RANGE_IDX_RE = re.compile(r"(\d)-(\d)")
NUM_PES_PER_NPU = 8


def normalize_devices_into_single_pes(devices: Sequence[Device]) -> List[Device]:
    """
    Normalize devices into single PEs. This function is only for npu devices.
    Allowed device formats are "npu:0:3", "npu:0:4-7", "npu:0:*", and "npu:0".
    :param devices: a list of Device objects
    :return: a list of `Device` objects which are all single PEs, sorted by npu index and pe index.
    """
    ret = []

    for device in devices:
        if device.kind != "npu":
            raise ValueError("Only npu devices can be normalized.")

        ret.extend(device.split_into_single_pes())

    # This sorts single pes by its npu index and pe index.
    ret.sort()

    return ret


def fusion_pes(devices: Sequence[Device]) -> Device:
    """Given a list of single pe devices, fuse them into a single fused pe device."""
    assert all(dev.is_single_pe for dev in devices)

    num_pes = len(devices)
    if num_pes not in POSSIBLE_FUSION_GRANULARITY:
        raise ValueError("Only 1, 2, 4, 8 PEs can be fused.")

    if num_pes == 1:
        return devices[0]
    devices = sorted(devices)

    # All devices must be single pe (in the form of "npu:\d:\d")
    dev_idx = devices[0].idx

    start_pe_idx = int(UnitDevice(devices[0]).pe_idx)

    if start_pe_idx % num_pes != 0:
        raise ValueError(f"Invalid start pe index for fusion: {start_pe_idx}")

    for device, expected_pe_idx in zip(devices, range(start_pe_idx, start_pe_idx + num_pes)):
        if int(UnitDevice(device).pe_idx) != expected_pe_idx:
            raise ValueError(
                f"Unexpected pe index. Expected: {expected_pe_idx}, actual: {device.idx}"
            )

    return Device(f"npu:{dev_idx}:{start_pe_idx}-{start_pe_idx + num_pes - 1}")


def get_device_mesh(
    devices: Sequence[Device],
    tensor_parallel_size: int,
    pipeline_parallel_size: int,
    data_parallel_size: Optional[int] = None,
) -> List[List[List[Device]]]:
    """Get parallel 3d mesh for given devices and parallelism degrees, whose dimensions corresponds to dp, pp, and tp respectively."""

    # Create tensor parallelism_groups
    is_npu = devices[0].kind == "npu"

    if is_npu and (
        tensor_parallel_size
        not in (
            1,
            2,
            4,
        )
        and tensor_parallel_size % 8 != 0
    ):
        raise ValueError("Tensor parallelism degree must be 1, 2, 4, or multiples of 8.")

    minimal_pus: List[Device]

    if is_npu:
        # In case of npu, parallelism strategy is defined in pe granularity.
        minimal_pus = normalize_devices_into_single_pes(devices)
    else:
        minimal_pus = list(devices)
    data_parallel_size = data_parallel_size or len(minimal_pus) // (
        pipeline_parallel_size * tensor_parallel_size
    )

    if (
        data_parallel_size <= 0
        or len(minimal_pus) < data_parallel_size * pipeline_parallel_size * tensor_parallel_size
    ):
        # If data_parallel_size is 0, make it 1 to print appropriate error message.
        data_parallel_size = 1 if data_parallel_size <= 0 else data_parallel_size
        raise ValueError(
            f"Not enough devices to run the model. {data_parallel_size * tensor_parallel_size * pipeline_parallel_size} PEs are required. \
Given devices: {','.join([d for d in devices])} ({len(minimal_pus)} PEs)"
        )

    if len(minimal_pus) > data_parallel_size * pipeline_parallel_size * tensor_parallel_size:
        minimal_pus = minimal_pus[
            : data_parallel_size * pipeline_parallel_size * tensor_parallel_size
        ]
        print(
            f"INFO: subsetting devices to {data_parallel_size * pipeline_parallel_size * tensor_parallel_size} PEs."
        )

    if is_npu:
        # Fusion PEs according to the tensor_parallel_size if the device is npu.
        fusion_granularity = min(8, tensor_parallel_size)

        fusioned_pes = [
            fusion_pes(minimal_pus[start : start + fusion_granularity])
            for start in range(0, len(minimal_pus), fusion_granularity)
        ]

        across_fusioned_pe_tp_degree = tensor_parallel_size // fusion_granularity
        assert len(fusioned_pes) % across_fusioned_pe_tp_degree == 0

        # 2d-matrix (list of tp groups)
        tp_groups = [
            fusioned_pes[start : start + across_fusioned_pe_tp_degree]
            for start in range(0, len(fusioned_pes), across_fusioned_pe_tp_degree)
        ]
    else:
        # Otherwise, there's no fusion.
        if tensor_parallel_size != 1:
            raise NotImplementedError("Tensor parallelism across chips is not supported yet.")
        fusioned_pes = minimal_pus

        # 2d-matrix (list of tp groups)
        tp_groups = [
            fusioned_pes[start : start + tensor_parallel_size]
            for start in range(0, len(fusioned_pes), tensor_parallel_size)
        ]

    used: Set[int] = set()
    dp_pp_tp_groups = []

    # create pp groups, each of which consists of multiple tp groups. List of pp groups naturally become dp group.
    for _ in range(data_parallel_size):
        cur_pp_group: List[List[Device]] = []
        while len(cur_pp_group) < pipeline_parallel_size:
            # Add not used tp_group to pp group
            cur_last_device_npu_idx = cur_pp_group[-1][-1].idx if len(cur_pp_group) > 0 else -1
            assert isinstance(cur_last_device_npu_idx, int)
            for i, tp_group in enumerate(tp_groups):
                assert isinstance(tp_group[-1].idx, int)
                if i in used or cur_last_device_npu_idx >= tp_group[-1].idx:
                    continue
                cur_pp_group.append(tp_group)
                used.add(i)
                break
            else:
                raise ValueError(
                    "Cannot form a proper pp group with current option. Pipeline parallelism across pes on same device has no benefit."
                )
        # Merge devices in one tp group into one `Device`.
        cur_pp_group = [[Device(",".join(tp_group))] for tp_group in cur_pp_group]
        dp_pp_tp_groups.append(cur_pp_group)

    return dp_pp_tp_groups
