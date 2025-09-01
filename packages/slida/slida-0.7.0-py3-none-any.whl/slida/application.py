import argparse
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from slida import __version__
from slida.config import CombinedConfig, Config
from slida.qt.application_view import ApplicationView
from slida.transitions import TRANSITION_PAIRS


def main():
    parser = argparse.ArgumentParser()

    try:
        Config.set_current(CombinedConfig.read())
        Config.current().correct_invalid()
    except Exception as e:
        parser.error(str(e))

    parser.add_argument("path", default="", nargs="*")
    parser.add_argument("--list-transitions", action="store_true", help="List available transitions and exit")
    parser.add_argument("--print-config", action="store_true", help="Also print debug info about the current config")

    Config.current().extend_argument_parser(parser)
    args = parser.parse_args()
    custom_dirs = [d for d in [Path(p) for p in args.path] if d.is_dir()]

    if args.list_transitions:
        transition_names = sorted(p.name for p in TRANSITION_PAIRS)
        print("Available transitions:")
        for name in transition_names:
            print(f"  {name}")
        sys.exit()

    try:
        Config.set_current(CombinedConfig.read(args, custom_dirs))
        Config.current().check()
    except Exception as e:
        parser.error(str(e))

    if args.print_config:
        print(Config.current())
        sys.exit()

    if not args.path:
        print("You need to set a path.", file=sys.stderr)
        sys.exit(1)

    app = QApplication([])
    app.setWindowIcon(QIcon(str(Path(__file__).parent / "slida.png")))
    app.setApplicationName("Slida v" + __version__)
    app.setQuitOnLastWindowClosed(True)

    slida = ApplicationView(args.path)
    slida.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
