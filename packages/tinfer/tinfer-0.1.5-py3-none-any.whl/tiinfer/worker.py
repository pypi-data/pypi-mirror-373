from typing import Dict, List, Type, Union

from mosec import Worker

__workers = []


def append_worker(
    worker: Type[Worker],
    num: int = 1,
    max_batch_size: int = 1,
    start_method: str = "spawn",
    env: Union[None, List[Dict[str, str]]] = None,
):
    __workers.append(locals())


def get_mosec_workers() -> List[Dict]:
    return __workers
