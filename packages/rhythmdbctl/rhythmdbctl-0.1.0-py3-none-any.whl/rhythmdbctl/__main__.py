import argparse
import sys
from .database import RhythmDatabase
from .formatters import get_formatter


def parse_args():
    parser = argparse.ArgumentParser(
        prog="rhythmdbctl",
        description="CLI tool to access and control Rhythmbox database",
    )

    parser.add_argument(
        "--db-path",
        type=str,
        default="~/.local/share/rhythmbox/rhythmdb.xml",
        help="Path to rhythmdb.xml (default: ~/.local/share/rhythmbox/rhythmdb.xml)",
    )

    parser.add_argument(
        "--format",
        choices=["table", "json", "csv"],
        default="table",
        help="Output format (default: table)",
    )

    parser.add_argument(
        "--fields", type=str, help="Comma-separated list of fields to include in output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    list_parser = subparsers.add_parser("list", help="List entries from database")
    list_parser.add_argument(
        "--type",
        choices=["song", "iradio", "podcast", "all"],
        default="all",
        help="Entry type to list",
    )
    list_parser.add_argument("--limit", type=int, help="Limit number of results")
    list_parser.add_argument(
        "--sort-by",
        choices=[
            "title",
            "artist",
            "album",
            "genre",
            "rating",
            "play_count",
            "duration",
        ],
        help="Sort entries by field",
    )
    list_parser.add_argument(
        "--reverse", action="store_true", help="Sort in descending order"
    )
    list_parser.add_argument(
        "--min-rating", type=float, help="Minimum rating filter (0-5)"
    )
    list_parser.add_argument(
        "--max-rating", type=float, help="Maximum rating filter (0-5)"
    )
    list_parser.add_argument(
        "--min-play-count", type=int, help="Minimum play count filter"
    )
    list_parser.add_argument(
        "--max-play-count", type=int, help="Maximum play count filter"
    )

    subparsers.add_parser("stats", help="Show database statistics")

    search_parser = subparsers.add_parser("search", help="Search entries")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--field",
        choices=["title", "artist", "album", "genre", "all"],
        default="all",
        help="Field to search in",
    )

    return parser.parse_args()


def load_database(db_path):
    try:
        db = RhythmDatabase(db_path)
        db.load()
        return db
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error loading database: {e}", file=sys.stderr)
        sys.exit(1)


def list_entries(
    db,
    entry_type="all",
    limit=None,
    output_format="table",
    fields=None,
    sort_by=None,
    reverse=False,
    min_rating=None,
    max_rating=None,
    min_play_count=None,
    max_play_count=None,
):
    entries = db.filter_entries(
        entry_type=entry_type if entry_type != "all" else None,
        sort_by=sort_by,
        reverse=reverse,
        min_rating=min_rating,
        max_rating=max_rating,
        min_play_count=min_play_count,
        max_play_count=max_play_count,
    )

    if limit:
        entries = entries[:limit]

    field_list = None
    if fields:
        field_list = [f.strip() for f in fields.split(",")]

    formatter = get_formatter(output_format)
    output = formatter.format(entries, field_list)
    print(output)


def show_stats(db):
    stats = db.get_statistics()

    print(f"Total entries: {stats['total']}")
    print("\nBreakdown by type:")
    for entry_type, count in sorted(stats["by_type"].items()):
        print(f"  {entry_type}: {count}")

    if stats["total_duration"] > 0:
        hours = stats["total_duration"] // 3600
        minutes = (stats["total_duration"] % 3600) // 60
        print(f"\nTotal duration: {hours}h {minutes}m")

    if stats["total_size"] > 0:
        size_gb = stats["total_size"] / (1024**3)
        print(f"Total size: {size_gb:.2f} GB")

    if stats["avg_rating"] > 0:
        print(f"Average rating: {stats['avg_rating']:.1f}/5")

    if stats["total_play_count"] > 0:
        print(f"Total play count: {stats['total_play_count']}")

    # Show rating distribution
    distribution = db.get_rating_distribution()
    if any(count > 0 for count in distribution.values()):
        dist_parts = []
        for rating in range(6):  # 0 to 5
            count = distribution[rating]
            if count > 0:
                dist_parts.append(f"{rating}★:{count}")
        if dist_parts:
            print(f"Rating distribution: {', '.join(dist_parts)}")


def search_entries(db, query, field="all", output_format="table", fields=None):
    if field == "all":
        search_fields = None
    else:
        search_fields = [field]

    results = db.search(query, search_fields)

    if not results:
        print(f"No entries found matching '{query}'")
        return

    field_list = None
    if fields:
        field_list = [f.strip() for f in fields.split(",")]

    formatter = get_formatter(output_format)
    output = formatter.format(results, field_list)
    print(output)


def main():
    args = parse_args()

    if not args.command:
        print("Error: No command specified. Use -h for help.", file=sys.stderr)
        sys.exit(1)

    db = load_database(args.db_path)

    if args.command == "list":
        list_entries(
            db,
            args.type,
            args.limit,
            args.format,
            args.fields,
            args.sort_by,
            args.reverse,
            args.min_rating,
            args.max_rating,
            args.min_play_count,
            args.max_play_count,
        )
    elif args.command == "stats":
        show_stats(db)
    elif args.command == "search":
        search_entries(db, args.query, args.field, args.format, args.fields)


if __name__ == "__main__":
    main()
