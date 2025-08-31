from typing import List, Union

from folder_classifier.dto import Folder, File


def build_folder(paths: List[str]) -> Folder:
    """
    Create a Folder tree from a list of file paths;
    The file paths are delimited by "/" - leaf segments are assumed to be files
    """
    if not paths:
        raise ValueError("No paths provided")

    # Get all directory prefixes
    prefix_set = set()
    for p in paths:
        parts = p.split('/')
        for i in range(1, len(parts)):
            prefix_set.add('/'.join(parts[:i]))

    # Sort by depth so parents are created before children
    sorted_paths = sorted(paths, key=lambda x: x.count('/'))

    # Create root folder
    root_name = sorted_paths[0].split('/')[0]
    root = Folder(name=root_name, type="folder", items=[])

    # Build the tree
    for p in sorted_paths:
        parts = p.split('/')
        current = root
        for idx, part in enumerate(parts[1:], start=1):
            full_path = '/'.join(parts[:idx+1])
            is_last = idx == len(parts) - 1

            # existing item
            existing = next((item for item in current.items if item.name == part), None)
            if existing:
                if isinstance(existing, Folder):
                    current = existing
                continue

            # Determine type for new item
            if is_last and full_path not in prefix_set:
                new_item = File(name=part, type="file")
            else:
                new_item = Folder(name=part, type="folder", items=[])

            current.items.append(new_item)
            if isinstance(new_item, Folder):
                current = new_item

    return root


def render_tree(folder: Folder) -> str:
    """
    Render Folder tree using ASCII tree characters (├──, └──, │).
    """
    lines: List[str] = []

    def recurse(node: Union[Folder, File], prefix: str, is_last: bool):
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{node.name}")
        if isinstance(node, Folder):
            child_prefix = prefix + ("    " if is_last else "│   ")
            for idx, child in enumerate(node.items):
                recurse(child, child_prefix, idx == len(node.items) - 1)

    # root
    lines.append(folder.name)
    for idx, child in enumerate(folder.items):
        recurse(child, "", idx == len(folder.items) - 1)

    return "\n".join(lines)


def flatten_folder(folder: Folder, parent_path: str = "") -> List[str]:
    """
    Traverses a Folder and returns a list of file paths.
    Each path is constructed by joining folder and file names with '/'.
    """
    paths: List[str] = []
    # Build the path for the current folder
    current_path = f"{parent_path}/{folder.name}" if parent_path else folder.name

    for item in folder.items:
        if item.type == "file":
            paths.append(f"{current_path}/{item.name}")
        else:
            # Recursively flatten subfolders
            paths.extend(flatten_folder(item, current_path))
    return paths


