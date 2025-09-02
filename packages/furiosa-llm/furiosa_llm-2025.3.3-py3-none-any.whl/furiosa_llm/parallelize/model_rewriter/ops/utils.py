from furiosa_llm.parallelize.model_rewriter.ops.types import MultiDeviceCommOp, SingleDeviceCommOp


def is_multi_dev_comm_op(node) -> bool:
    return node.op == "call_function" and isinstance(node.target, MultiDeviceCommOp)


def is_single_dev_comm_op(node) -> bool:
    return node.op == "call_function" and isinstance(node.target, SingleDeviceCommOp)
