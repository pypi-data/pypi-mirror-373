import json
import csv
from abc import ABC, abstractmethod
from typing import List, Optional
from io import StringIO
from .models import Entry


class BaseFormatter(ABC):
    @abstractmethod
    def format(self, entries: List[Entry], fields: Optional[List[str]] = None) -> str:
        pass


class TableFormatter(BaseFormatter):
    def format(self, entries: List[Entry], fields: Optional[List[str]] = None) -> str:
        if not entries:
            return "No entries found."

        output = []
        for entry in entries:
            line = f"{entry.title or 'Unknown'} - {entry.artist or 'Unknown'}"
            if entry.album:
                line += f" ({entry.album})"
            output.append(line)

            details = []
            if entry.duration:
                details.append(f"Duration: {entry.format_duration()}")
            if entry.rating:
                details.append(f"Rating: {'★' * int(entry.rating)}")
            if entry.genre:
                details.append(f"Genre: {entry.genre}")
            if entry.play_count and entry.play_count > 0:
                details.append(f"Plays: {entry.play_count}")

            if details:
                output.append("  " + " | ".join(details))

        return "\n".join(output)


class JSONFormatter(BaseFormatter):
    def format(self, entries: List[Entry], fields: Optional[List[str]] = None) -> str:
        data = []
        for entry in entries:
            entry_dict = entry.to_dict()
            if fields:
                entry_dict = {k: v for k, v in entry_dict.items() if k in fields}
            data.append(entry_dict)

        return json.dumps(data, indent=2, ensure_ascii=False)


class CSVFormatter(BaseFormatter):
    def format(self, entries: List[Entry], fields: Optional[List[str]] = None) -> str:
        if not entries:
            return ""

        output = StringIO()

        if fields:
            fieldnames = fields
        else:
            fieldnames = [
                "title",
                "artist",
                "album",
                "genre",
                "duration",
                "rating",
                "play_count",
                "entry_type",
            ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for entry in entries:
            entry_dict = entry.to_dict()
            filtered_dict = {k: v for k, v in entry_dict.items() if k in fieldnames}
            writer.writerow(filtered_dict)

        return output.getvalue()


def get_formatter(format_type: str) -> BaseFormatter:
    formatters = {"table": TableFormatter, "json": JSONFormatter, "csv": CSVFormatter}

    formatter_class = formatters.get(format_type.lower())
    if not formatter_class:
        raise ValueError(
            f"Unknown format: {format_type}. Available formats: {', '.join(formatters.keys())}"
        )

    return formatter_class()
