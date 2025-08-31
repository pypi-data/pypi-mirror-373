from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Entry:
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    duration: Optional[int] = None
    file_size: Optional[int] = None
    location: Optional[str] = None
    mountpoint: Optional[str] = None
    rating: Optional[float] = None
    play_count: Optional[int] = None
    track_number: Optional[int] = None
    disc_number: Optional[int] = None
    year: Optional[int] = None
    date: Optional[int] = None
    bitrate: Optional[int] = None
    entry_type: Optional[str] = None

    @classmethod
    def from_xml_element(cls, element):
        entry = cls()

        entry.entry_type = element.get("type", "")
        if entry.entry_type.startswith("http://www.rhythmbox.org/rhythmdb/"):
            entry.entry_type = entry.entry_type.split("/")[-1]

        for child in element:
            tag = child.tag
            text = child.text

            if text is None:
                continue

            if tag == "title":
                entry.title = text
            elif tag == "artist":
                entry.artist = text
            elif tag == "album":
                entry.album = text
            elif tag == "genre":
                entry.genre = text
            elif tag == "duration":
                entry.duration = int(text)
            elif tag == "file-size":
                entry.file_size = int(text)
            elif tag == "location":
                entry.location = text
            elif tag == "mountpoint":
                entry.mountpoint = text
            elif tag == "rating":
                entry.rating = float(text)
            elif tag == "play-count":
                entry.play_count = int(text)
            elif tag == "track-number":
                entry.track_number = int(text)
            elif tag == "disc-number":
                entry.disc_number = int(text)
            elif tag == "year":
                entry.year = int(text)
            elif tag == "date":
                entry.date = int(text)
            elif tag == "bitrate":
                entry.bitrate = int(text)

        return entry

    def format_duration(self) -> str:
        if self.duration is None:
            return "Unknown"

        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}
