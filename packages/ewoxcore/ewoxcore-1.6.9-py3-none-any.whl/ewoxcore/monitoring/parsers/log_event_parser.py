from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable, TypeVar
from datetime import date, datetime, timedelta
from ewoxcore.monitoring.models.log_event import LogEvent
from ewoxcore.utils.json_util import JsonUtil


class LogEventParser():
    @staticmethod
    def parse(response:Any) -> Tuple[int, List[LogEvent]]:
        m_json:Any = JsonUtil.serialize(response)
        m_dec:Any = JsonUtil.deserialize_object(m_json)

        total:int = m_dec.hits.total.value

        items:List[LogEvent] = []
        for qe in m_dec.hits.hits:
            qe_data:LogEvent = qe._source
            event = LogEvent(
                correlation_id=qe_data.correlationId,
                user_id=qe_data.userId,
                company_id=qe_data.companyId,
                log_level=qe_data.logLevel,
                message=qe_data.message,
                event_name=qe_data.eventName,
                event_type=qe_data.eventType,
                data_class=qe_data.dataClass,
                data=qe_data.data,
                is_encoded=qe_data.isEncoded,
                created_at=qe_data.createdAt
            )
            items.append(event)

        return (total, items)
    

    @staticmethod
    def parse_aggregate(response:Any) -> Tuple[int, List[str]]:
        m_json:Any = JsonUtil.serialize(response)
        m_dec:Any = JsonUtil.deserialize_object(m_json)

        total:int = m_dec.hits.total.value

        items:List[str] = []
        for qe in m_dec.aggregations.aggsTerm.buckets:
            items.append(qe.key)

        return (total, items)