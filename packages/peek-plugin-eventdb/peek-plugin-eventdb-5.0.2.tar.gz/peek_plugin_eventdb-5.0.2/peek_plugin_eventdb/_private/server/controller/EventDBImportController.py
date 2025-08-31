import logging
import os
from datetime import datetime
from typing import List
from typing import Optional

import pytz
from twisted.internet.defer import Deferred, inlineCallbacks
from twisted.internet.task import LoopingCall
from vortex.TupleSelector import TupleSelector
from vortex.handler.TupleDataObservableHandler import TupleDataObservableHandler

from peek_plugin_base.LoopingCallUtil import peekCatchErrbackWithLogger
from peek_plugin_base.storage.DbConnection import DbSessionCreator
from peek_plugin_base.storage.RunPyInPg import runPyInPg
from peek_plugin_base.util.PeekPsUtil import PeekPsUtil
from peek_plugin_eventdb._private.server.EventDBReadApi import EventDBReadApi
from peek_plugin_eventdb._private.server.controller.AdminStatusController import (
    AdminStatusController,
)
from peek_plugin_eventdb._private.server.controller.EventDBImportEventsInPgTask import (
    EventDBImportEventsInPgTask,
)
from peek_plugin_eventdb._private.server.controller.EventDBImportPropertiesInPgTask import (
    EventDBImportPropertiesInPgTask,
)
from peek_plugin_eventdb._private.server.tuple_selector_mappers.NewEventTSUpdateMapper import (
    NewEventsTupleSelector,
)
from peek_plugin_eventdb._private.storage.EventDBPropertyTable import (
    EventDBPropertyTable,
)
from peek_plugin_eventdb.tuples.EventDBPropertyTuple import EventDBPropertyTuple

logger = logging.getLogger(__name__)


class EventDBImportController:
    """EventDB Import Controller"""

    MAX_CPU_PERCENTAGE = 50.0
    NOTIFY_TIME_SECONDS = 5.0

    def __init__(
        self,
        dbSessionCreator: DbSessionCreator,
        statusController: AdminStatusController,
        tupleObservable: TupleDataObservableHandler,
    ):
        self._dbSessionCreator = dbSessionCreator
        self._statusController = statusController
        self._tupleObservable = tupleObservable

        self._updateSelectorQueue: list[NewEventsTupleSelector] = []
        self._updateNotifyLoopingCall: Optional[LoopingCall] = None

        self._process = None

    def start(self):
        assert not self._updateNotifyLoopingCall, "We've been started already"
        self._updateNotifyLoopingCall = LoopingCall(self._batchNotifyUpdates)
        self._updateNotifyLoopingCall.start(self.NOTIFY_TIME_SECONDS)

    def setReadApi(self, readApi: EventDBReadApi):
        self._readApi = readApi

    def shutdown(self):
        if (
            self._updateNotifyLoopingCall
            and self._updateNotifyLoopingCall.running
        ):
            self._updateNotifyLoopingCall.stop()
            self._updateNotifyLoopingCall = None

        self._process = None
        self._readApi = None
        self._tupleObservable = None

    @peekCatchErrbackWithLogger(logger)
    def _batchNotifyUpdates(self):
        """Batch Notify Updates

        PROBLEM: We don't know if any tuple selectors are already running.
        :return: None
        """
        if not self._updateSelectorQueue:
            return

        num = PeekPsUtil().cpuPercent
        if self.MAX_CPU_PERCENTAGE < num:
            logger.debug("Skipping this loop, CPU is too high: %s", num)
            return

        minDate = min([ts.minDate for ts in self._updateSelectorQueue])
        maxDate = max([ts.maxDate for ts in self._updateSelectorQueue])
        self._updateSelectorQueue = []

        self._tupleObservable.notifyOfTupleUpdate(
            NewEventsTupleSelector(minDate, maxDate)
        )

    @inlineCallbacks
    def importEvents(
        self, modelSetKey: str, eventsEncodedPayload: str
    ) -> Deferred:
        count, maxDate, minDate = yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportEventsInPgTask.importEvents,
            None,
            modelSetKey,
            eventsEncodedPayload,
        )

        # Notify anyone watching the events that new ones have arrived.
        if count:
            self._updateSelectorQueue.append(
                NewEventsTupleSelector(minDate, maxDate)
            )

        self._statusController.status.addedEvents += count
        self._statusController.status.lastActivity = datetime.now(pytz.utc)
        self._statusController.notify()

    @inlineCallbacks
    def deleteEvents(self, modelSetKey: str, eventKeys: List[str]) -> Deferred:
        count = yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportEventsInPgTask.deleteEvents,
            None,
            modelSetKey,
            eventKeys,
        )

        self._statusController.status.removedEvents += count
        self._statusController.status.lastActivity = datetime.now(pytz.utc)
        self._statusController.notify()

    @inlineCallbacks
    def updateAlarmFlags(
        self, modelSetKey: str, eventKeys: List[str], alarmFlag: bool
    ) -> Deferred:
        count = yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportEventsInPgTask.updateAlarmFlags,
            None,
            modelSetKey,
            eventKeys,
            alarmFlag,
        )

        self._statusController.status.updatedAlarmFlags += count
        self._statusController.status.lastActivity = datetime.now(pytz.utc)
        self._statusController.notify()

    @inlineCallbacks
    def replaceProperties(
        self, modelSetKey: str, propertiesEncodedPayload: str
    ) -> Deferred:
        yield runPyInPg(
            logger,
            self._dbSessionCreator,
            EventDBImportPropertiesInPgTask.replaceProperties,
            None,
            modelSetKey,
            propertiesEncodedPayload,
        )

        tupleSelector = TupleSelector(EventDBPropertyTable.tupleName(), {})
        self._tupleObservable.notifyOfTupleUpdate(tupleSelector)

        tupleSelector = TupleSelector(EventDBPropertyTuple.tupleName(), {})
        self._tupleObservable.notifyOfTupleUpdate(tupleSelector)
