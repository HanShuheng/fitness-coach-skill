#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def extract_user_id_arg(argv: list[str]) -> list[str]:
    cleaned: list[str] = []
    skip_next = False
    for index, arg in enumerate(argv):
        if skip_next:
            skip_next = False
            continue
        if arg in {"--user-id", "--profile-id"}:
            if index + 1 < len(argv):
                import os

                os.environ["FITNESS_COACH_USER_ID"] = argv[index + 1]
                skip_next = True
            continue
        if arg.startswith("--user-id="):
            import os

            os.environ["FITNESS_COACH_USER_ID"] = arg.split("=", 1)[1]
            continue
        if arg.startswith("--profile-id="):
            import os

            os.environ["FITNESS_COACH_USER_ID"] = arg.split("=", 1)[1]
            continue
        cleaned.append(arg)
    return cleaned


sys.argv = extract_user_id_arg(sys.argv)

from fitness_coach_lib.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
