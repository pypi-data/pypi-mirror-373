from cashd.app import start_cashd
import sys


def window():
    if len(sys.argv) == 1:
        start_cashd(with_webview=True)
        return

    if "window" in sys.argv:
        start_cashd(with_webview=True)
        return

    if "browser" in sys.argv:
        start_cashd(with_webview=False)
        return


if __name__ == "__main__":
    start_cashd(with_webview=True)
