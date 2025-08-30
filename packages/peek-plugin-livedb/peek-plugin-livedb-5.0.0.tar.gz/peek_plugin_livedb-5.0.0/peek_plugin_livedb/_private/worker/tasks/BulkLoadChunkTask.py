import logging
from typing import List

from sqlalchemy import select

from peek_plugin_base.worker.task_db_conn import TaskDbConn
from peek_plugin_livedb._private.storage.LiveDbItem import LiveDbItem
from peek_plugin_base.worker.task import addPeekWorkerTask
from peek_plugin_livedb.tuples.LiveDbDisplayValueTuple import (
    LiveDbDisplayValueTuple,
)

logger = logging.getLogger(__name__)


@addPeekWorkerTask()
def qryChunkInWorker(offset, limit) -> List[LiveDbDisplayValueTuple]:
    """Query Chunk

    This returns a chunk of LiveDB items from the database


    :param offset: The offset of the chunk
    :param limit: An encoded payload containing the updates
    :returns: List[LiveDbDisplayValueTuple] serialised in a payload json
    """

    table = LiveDbItem.__table__

    session = TaskDbConn.getDbSession()
    try:
        result = session.execute(
            select(
                table.c.key,
                table.c.dataType,
                table.c.rawValue,
                table.c.displayValue,
            )
            .order_by(table.c.id)
            .offset(offset)
            .limit(limit)
        )

        return [
            LiveDbDisplayValueTuple(
                key=o.key,
                dataType=o.dataType,
                rawValue=o.rawValue,
                displayValue=o.displayValue,
            )
            for o in result.fetchall()
        ]

    finally:
        session.close()
