from pathlib import Path

from python_minifier import minify


def minifyFile(filePath: Path) -> None:
    """Minifies a file from a certain path

    Args:
        filePath (Path): Path to the file to minify

    Raises:
        RuntimeError: In the event the file cannot be found or an error has occurred
    """
    try:
        with filePath.open("r+", encoding="utf-8") as fileRW:
            minifiedCode = minify(
                fileRW.read(),
                hoist_literals=False,
                remove_literal_statements=True,
                remove_debug=True,
            )

            fileRW.seek(0)
            fileRW.write(minifiedCode)
            fileRW.truncate()

    except Exception as e:
        raise RuntimeError(f"Failed to minify {filePath}: {e}")


def minifyToString(filePath: Path) -> str:
    """Minifies string of a python file

    Args:
        filePath (Path): Path to file to minify

    Returns:
        str: Minified string
    """
    with filePath.open("r") as fileR:
        minifiedCode: str = str(
            minify(
                fileR.read(),
                hoist_literals=False,
                remove_literal_statements=True,
                remove_debug=True,
            )
        )

    return minifiedCode
