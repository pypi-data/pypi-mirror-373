from abc import abstractmethod
from typing import Dict


class ACIUpdateDateTupleABC:
    """Chunked Index Object Update Date Tuple

    This tuple represents the state of the chunks in the cache.
    Each chunkKey has a lastUpdateDate as a string, this is used for offline caching
    all the chunks.
    """

    @property
    @abstractmethod
    def ckiUpdateDateByChunkKey(self) -> Dict[str, str]:
        """Chunk Key Index - Chunk Key

        This property should return a dict of chunkKey:updateDate

        :return: The value of updateDateByChunkKey.

        Example code:

                return self.updateDateByChunkKey

        """
        raise NotImplementedError()

    @abstractmethod
    def ckiSetUpdateDateByChunkKey(self, value: Dict[str, str]) -> None:
        """Set Chunk Key Index - Chunk Key

        Set the value of ckiUpdateDateByChunkKey

        Example code:

            self.updateDateByChunkKey = value

        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def ckiInitialLoadComplete(self) -> bool:
        """Initial Load Complete

        This property should a boolean of if the initial load has completed
        or not.

        :return: The value of updateDateByChunkKey.

        Example code:

                return self.initialLoadComplete

        """
        raise NotImplementedError()

    @abstractmethod
    def ckiSetInitialLoadComplete(self, value: bool) -> None:
        """Set Initial Load Complete

        Set the value of ckiInitialLoadComplete

        :return: The value of updateDateByChunkKey.

        Example code:

            self.initialLoadComplete = value

        """
        raise NotImplementedError()
