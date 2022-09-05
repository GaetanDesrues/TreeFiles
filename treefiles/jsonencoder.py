import dataclasses
import logging

from treefiles.baseio_.baseio_ import IOEncoder
from treefiles.tree import Tree


class JsonEncoder(IOEncoder):
    """General purpose encode"""

    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, Tree):
            return obj.abs()
        return super().default(obj)


log = logging.getLogger(__name__)
