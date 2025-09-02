import json
from abc import ABCMeta
from typing import Optional
from typing import Type

from sqlalchemy import select
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import Select
from vortex.Payload import Payload
from vortex.Tuple import Tuple

from peek_abstract_chunked_index.private.tuples.ACIEncodedChunkTupleABC import (
    ACIEncodedChunkTupleABC,
)
from peek_abstract_chunked_index.private.tuples.ACIUpdateDateTupleABC import (
    ACIUpdateDateTupleABC,
)
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.RunPyInPg import runPyInPgBlocking


class ACIChunkLoadRpcABC(metaclass=ABCMeta):
    def __init__(self, dbSessionCreator: DbSessionCreator):
        self._dbSessionCreator = dbSessionCreator

    # -------------
    def ckiChunkIndexDeltaBlocking(
        self,
        indexEncodedPayload: bytes,
        Declarative: Type[ACIEncodedChunkTupleABC],
        IndexTuple: Type[ACIUpdateDateTupleABC],
    ) -> bytes:
        """Chunked Key Index - Chunk Load Delta

        This method is used to tell the field/office services what
        chunks they need to get.

        """
        sql = select(
            Declarative.sqlCoreChunkKeyColumn().label("key"),
            Declarative.sqlCoreLastUpdateColumn().label("value"),
        ).order_by(Declarative.sqlCoreChunkKeyColumn())

        sqlStr = str(
            sql.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )

        sqlIndexTupleModStr = ".".join(
            [IndexTuple.__module__, IndexTuple.__name__]
        )

        return runPyInPgBlocking(
            self._dbSessionCreator,
            self._loadIndexDelta,
            sqlStr=sqlStr,
            indexEncodedPayload=indexEncodedPayload,
            sqlIndexTupleModStr=sqlIndexTupleModStr,
        )

    # -------------
    def ckiInitialLoadChunksPayloadBlocking(
        self,
        chunkKeys: list[str],
        Declarative: Type[ACIEncodedChunkTupleABC],
        sql: Optional[Select] = None,
    ) -> list[Tuple]:
        """Chunked Key Index - Initial Load Chunks Blocking

        This method is used to load the initial set of chunks from the server
        to the client.

        """
        chunkKeys = [str(ck) for ck in chunkKeys]
        if sql is None:
            table = Declarative.__table__
            sql = select(table).where(
                Declarative.sqlCoreChunkKeyColumn().in_(chunkKeys)
            )

        sqlStr = str(
            sql.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )

        sqlCoreLoadModStr = ".".join(
            [Declarative.__module__, Declarative.__name__]
        )

        return runPyInPgBlocking(
            self._dbSessionCreator,
            self._load,
            sqlCoreLoadModStr=sqlCoreLoadModStr,
            sqlStr=sqlStr,
            chunkKeys=chunkKeys,
        )

    @classmethod
    def _loadIndexDelta(
        cls,
        plpy,
        sqlStr: str,
        indexEncodedPayload: bytes,
        sqlIndexTupleModStr: str,
    ):
        # Import the tuple we'll reconstruct
        cls._loadTupleClass(sqlIndexTupleModStr)

        indexIn = Payload().fromEncodedPayload(indexEncodedPayload).tuples[0]
        indexInUpdateDateByChunkKey = indexIn.ckiUpdateDateByChunkKey

        results = {}

        cursor = plpy.cursor(sqlStr)
        while True:
            rows = cursor.fetch(500)
            if not rows:
                break
            for row in rows:
                # Our select query selects only the two columns we need
                results[row["key"]] = row["value"]

        deltas = {}

        # Tell the remote indexes to delete these
        deltas.update(
            [(k, None) for k in set(indexInUpdateDateByChunkKey) - set(results)]
        )

        # Tell the remote indexes to add the missing items
        deltas.update(
            [
                (k, results[k])
                for k in set(results) - set(indexInUpdateDateByChunkKey)
            ]
        )

        # For the items that match, tell the remote index if it needs an update
        for chunkKey in set(results) & set(indexInUpdateDateByChunkKey):
            if indexInUpdateDateByChunkKey[chunkKey] != results[chunkKey]:
                deltas[chunkKey] = results[chunkKey]

        indexIn.ckiSetUpdateDateByChunkKey(deltas)
        indexIn.ckiSetInitialLoadComplete(False)

        return Payload(tuples=[indexIn]).toEncodedPayload()

    @classmethod
    def _load(cls, plpy, sqlStr, sqlCoreLoadModStr, chunkKeys: list[str]):
        TupleClass = cls._loadTupleClass(sqlCoreLoadModStr)
        tupleLoaderMethod = TupleClass.sqlCoreLoad

        # ---------------
        # Turn a row["val"] into a row.val
        class Wrap:
            row = None

            def __getattr__(self, name):
                return self.row[name]

        wrap = Wrap()

        # ---------------
        # Iterate through and load the tuples
        results = []

        cursor = plpy.cursor(sqlStr)
        while True:
            rows = cursor.fetch(500)
            if not rows:
                break
            for row in rows:
                wrap.row = row
                results.append(tupleLoaderMethod(wrap))

        # ---------------
        # Process the results, create blanks where the chunk has been deleted

        deletedChunkKeys = set(chunkKeys) - set(
            [r.ckiChunkKey for r in results]
        )

        for chunkKey in deletedChunkKeys:
            results.append(TupleClass.ckiCreateDeleteEncodedChunk(chunkKey))

        return (
            json.dumps(Payload(tuples=results).toJsonDict())
            if results
            else None
        )

    @classmethod
    def _loadTupleClass(cls, sqlCoreLoadModStr):
        from importlib.util import find_spec

        modName, className = sqlCoreLoadModStr.rsplit(".", 1)
        import sys

        if modName in sys.modules:
            package_ = sys.modules[modName]

        else:
            modSpec = find_spec(modName)
            if not modSpec:
                raise Exception(
                    "Failed to find package %s,"
                    " is the python package installed?" % modName
                )

            package_ = modSpec.loader.load_module()
        TupleClass = getattr(package_, className)
        return TupleClass
