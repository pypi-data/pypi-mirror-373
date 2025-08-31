import argparse
import os
import sys

DEFAULT_EXCLUDES = {".git", "node_modules", "__pycache__"}


def print_tree(
    path: str,
    prefix: str = "",
    depth: int = 0,
    max_depth: int | None = None,
    only_dirs: bool = False,
    exclude: set[str] = set(),
    out=sys.stdout,
):
    try:
        entries = sorted(os.listdir(path))
    except PermissionError:
        print(prefix + "[access denied]", file=out)
        return

    entries = [e for e in entries if e not in exclude]

    total = len(entries)
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        is_dir = os.path.isdir(full_path)
        connector = "└── " if i == total - 1 else "├── "
        print(prefix + connector + entry + ("/" if is_dir else ""), file=out)

        if is_dir and (max_depth is None or depth < max_depth):
            extension = "    " if i == total - 1 else "│   "
            print_tree(
                full_path,
                prefix + extension,
                depth + 1,
                max_depth,
                only_dirs,
                exclude,
                out=out,
            )


def main():
    parser = argparse.ArgumentParser(
        prog="gtree", description="Print a project directory tree"
    )
    parser.add_argument(
        "path", nargs="?", default=".", help="Path to list (default: current directory)"
    )
    parser.add_argument("--max-depth", type=int, help="Limit depth of tree")
    parser.add_argument(
        "--only-dirs", action="store_true", help="Show only directories"
    )
    parser.add_argument(
        "--exclude",
        nargs="*",
        default=[],
        help="Extra names to exclude (space separated)",
    )
    parser.add_argument(
        "--output", "-o", help="Save output to file instead of printing"
    )

    args = parser.parse_args()

    root = os.path.abspath(args.path)
    exclude = DEFAULT_EXCLUDES.union(args.exclude)

    out = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout

    print(root, file=out)
    print_tree(
        root,
        max_depth=args.max_depth,
        only_dirs=args.only_dirs,
        exclude=exclude,
        out=out,
    )

    if args.output:
        out.close()
