from pathlib import Path
from typing import Optional, Union
from collections import deque

def find_dir(
    start: Path = Path.cwd(),
    target: Union[str, None] = None,
    max_depth_up: Union[int, None] = None,
    max_depth_down: int = 3,
    subdir_limit: int = 100,
) -> Optional[Path]:
    """
    1) If `start` path contains `target` in its parts, walk upward until you find the actual `target` folder.
    2) Otherwise, search downward (up to `max_depth_down` levels) and limit each directory to checking `subdir_limit` entries.
    """

    if target is None:
        raise ValueError("target is required")

    # Check if we're already in target directory
    if target in start.parts:
        # We'll walk UP to find the target ancestor
        target_dir = start

        # If user doesn't provide a max_depth_up, default to the path's length
        if max_depth_up is None:
            max_depth_up = len(start.parts)

        depth = 0
        while target_dir.name != target:
            # If we've gone too far or reached the root
            if depth >= max_depth_up or target_dir == target_dir.parent:
                return None
            target_dir = target_dir.parent
            depth += 1

        # If we found it:
        if target_dir.is_dir():
            return target_dir
        return None

    def bfs(path: Path) -> Optional[Path]:
        visited = set()
        queue = deque([(path, 0)])  # (current_path, depth)

        while queue:
            current_path, depth = queue.popleft()

            if depth > max_depth_down:
                continue

            if current_path in visited:
                continue
            visited.add(current_path)

            # Does this directory contain target?
            target_candidate = current_path / target
            if target_candidate.is_dir():
                return target_candidate

            # List subdirs (limit to the first subdir_limit)
            try:
                entries = list(current_path.iterdir())
            except (PermissionError, OSError):
                continue

            count = 0
            for entry in entries:
                if count >= subdir_limit:
                    break
                if entry.is_dir():
                    # Skip hidden directories except target itself
                    if entry.name == target or not entry.name.startswith("."):
                        queue.append((entry, depth + 1))
                        count += 1

        return None

    return bfs(start)