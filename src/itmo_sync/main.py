import asyncio
import sys
from pathlib import Path

from itmo_sync.generate import generate_calendars


async def main() -> None:
    project_root = Path(__file__).resolve().parent.parent.parent
    base_output_dir = project_root / "public"

    print("🚀 Starting ITMO schedule synchronization...")

    try:
        await generate_calendars(base_output_dir)
        print("✨ Generation completed successfully!")
    except Exception as e:
        print(f"❌ An error occurred during schedule generation: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
