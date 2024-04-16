import os
import pathlib
import platform
import typing

_PLATFORM: typing.Final[str] = platform.system()


if _PLATFORM == "Windows":
    pass
else:
    raise OSError(f"Unsupported platform: {_PLATFORM}")


def _find_rimworld_install_path() -> pathlib.Path | None:
    """Attempts to find the directory RimWorld is installed in.

    Returns:
        pathlib.Path:
            The path to the root directory of the RimWorld installation.
    Raises:
        NotImplementedError:
            The method was called on an unsupported operating system. This
            method currently only supports Windows.
    """
    if _PLATFORM == "Windows":
        return _get_windows_rimworld_path()
    else:
        raise NotImplementedError(
            f"The default RimWorld installation path for {_PLATFORM} hasn't "
            f"been implemented yet."
        )


def _get_windows_rimworld_path() -> pathlib.Path | None:
    default_path = pathlib.Path(
        os.getenv("ProgramFiles(x86)"),
        "Steam",
        "steamapps",
        "common",
        "RimWorld",
    )

    if default_path.exists() and _is_valid_rimworld_path(default_path):
        return default_path

    for drive in os.listdrives():
        try:
            rimworld_path = _scan_for_path(pathlib.Path(drive), 2)
        except ValueError:
            continue
        except PermissionError:
            continue
        else:
            return rimworld_path

    return None


def _is_valid_directory(path: pathlib.Path) -> bool:
    if path.is_file():
        return False

    if path.is_symlink():
        return False

    if path.is_reserved():
        return False

    if path.name.startswith(_PLATFORM):
        return False

    if path.name.startswith("OEM"):
        return False

    if path.name.startswith("$"):
        return False

    return path.is_dir()


def _is_valid_rimworld_path(path: pathlib.Path) -> bool:
    for node in path.iterdir():
        if node.name.startswith("RimWorld") and node.is_file():
            return True

    return False


def _scan_for_path(
    root_directory: pathlib.Path, check_depth: int = 3
) -> pathlib.Path:
    for path in root_directory.iterdir():
        if not _is_valid_directory(path):
            continue

        maybe_rimworld_path = path.joinpath("common", "RimWorld")

        if path.name == "steamapps" and _is_valid_rimworld_path(
            maybe_rimworld_path
        ):
            return maybe_rimworld_path
        elif check_depth > 0:
            try:
                return _scan_for_path(path, check_depth - 1)
            except ValueError:
                continue
            except PermissionError:
                continue

    raise ValueError("Could not find Steam directory (./steamapps/)")
