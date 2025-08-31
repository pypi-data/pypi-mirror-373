import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Dict
from .models import Entry


class RhythmDatabase:
    def __init__(self, db_path: str = "~/.local/share/rhythmbox/rhythmdb.xml"):
        self.db_path = Path(db_path).expanduser()
        self.tree = None
        self.entries: List[Entry] = []

    def load(self):
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        self.tree = ET.parse(self.db_path)
        root = self.tree.getroot()

        self.entries = []
        for element in root.findall(".//entry"):
            entry = Entry.from_xml_element(element)
            self.entries.append(entry)

    def filter_entries(
        self,
        entry_type: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        genre: Optional[str] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        min_play_count: Optional[int] = None,
        max_play_count: Optional[int] = None,
        date_added_after: Optional[str] = None,
        date_added_before: Optional[str] = None,
        sort_by: Optional[str] = None,
        reverse: bool = False,
    ) -> List[Entry]:

        filtered = self.entries

        if entry_type and entry_type != "all":
            filtered = [e for e in filtered if e.entry_type == entry_type]

        if artist:
            artist_lower = artist.lower()
            filtered = [
                e for e in filtered if e.artist and artist_lower in e.artist.lower()
            ]

        if album:
            album_lower = album.lower()
            filtered = [
                e for e in filtered if e.album and album_lower in e.album.lower()
            ]

        if genre:
            genre_lower = genre.lower()
            filtered = [
                e for e in filtered if e.genre and genre_lower in e.genre.lower()
            ]

        if min_rating is not None:
            filtered = [e for e in filtered if e.rating and e.rating >= min_rating]

        if max_rating is not None:
            filtered = [e for e in filtered if e.rating and e.rating <= max_rating]

        if min_play_count is not None:
            filtered = [
                e for e in filtered if e.play_count and e.play_count >= min_play_count
            ]

        if max_play_count is not None:
            filtered = [
                e for e in filtered if e.play_count and e.play_count <= max_play_count
            ]

        if date_added_after:
            # TODO: Implement date filtering when date_added field is available
            pass

        if date_added_before:
            # TODO: Implement date filtering when date_added field is available
            pass

        # Apply sorting if requested
        if sort_by:
            valid_sort_fields = [
                "title",
                "artist",
                "album",
                "genre",
                "rating",
                "play_count",
                "duration",
            ]
            if sort_by in valid_sort_fields:

                def sort_key(entry):
                    value = getattr(entry, sort_by, None)
                    if value is None:
                        return (
                            "" if isinstance(getattr(Entry(), sort_by, ""), str) else 0
                        )
                    return value

                filtered = sorted(filtered, key=sort_key, reverse=reverse)

        return filtered

    def search(self, query: str, fields: List[str] = None) -> List[Entry]:
        if fields is None:
            fields = ["title", "artist", "album", "genre"]

        query_lower = query.lower()
        results = []

        for entry in self.entries:
            for field in fields:
                value = getattr(entry, field, None)
                if value and query_lower in str(value).lower():
                    results.append(entry)
                    break

        return results

    def get_statistics(self) -> Dict:
        stats = {
            "total": len(self.entries),
            "by_type": {},
            "total_duration": 0,
            "total_size": 0,
            "avg_rating": 0,
            "total_play_count": 0,
        }

        rating_sum = 0
        rating_count = 0

        for entry in self.entries:
            entry_type = entry.entry_type or "unknown"
            stats["by_type"][entry_type] = stats["by_type"].get(entry_type, 0) + 1

            if entry.duration:
                stats["total_duration"] += entry.duration

            if entry.file_size:
                stats["total_size"] += entry.file_size

            if entry.rating is not None:
                rating_sum += entry.rating
                rating_count += 1

            if entry.play_count:
                stats["total_play_count"] += entry.play_count

        if rating_count > 0:
            stats["avg_rating"] = rating_sum / rating_count

        return stats

    def get_rating_distribution(self) -> Dict[int, int]:
        """Get the distribution of ratings across all entries.

        Returns:
            Dictionary mapping rating values (0-5) to entry counts
        """
        distribution = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        for entry in self.entries:
            if entry.rating is not None:
                # Ensure rating is within expected range
                rating = int(entry.rating)
                if 0 <= rating <= 5:
                    distribution[rating] += 1

        return distribution
