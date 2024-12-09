"""Module implementing formatter for maillog events."""

from collections import defaultdict
from dataclasses import dataclass

from .event import MaillogEvent


@dataclass
class EventFormatter:
    """Class for formatting log messages."""

    @staticmethod
    def pretty_print(events: list[MaillogEvent]) -> str:
        """
        Pretty-print log messages.

        1. Group messages by process name and process id.
        2. Order grouped messages by timestamp.
        3. Output messages for each group.
        """

        events_grouped = defaultdict(list)
        for event in events:
            events_grouped[(event.process_name, event.process_id)].append(event)

        groups_ordered = sorted(events_grouped.items(), key=lambda x: x[1][0].timestamp)

        result = ""
        for (pname, pid), event in groups_ordered:
            result += f"{pname} (pid={pid}):\n"
            for e in event:
                print(f"    {e.timestamp} {e.log_level}: {e.message}\n")
            result += "\n"
        return result
