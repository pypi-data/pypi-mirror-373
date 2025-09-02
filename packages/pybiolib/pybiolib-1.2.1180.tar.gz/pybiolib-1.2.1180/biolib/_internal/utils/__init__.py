import time
import uuid


def open_browser_window_from_notebook(url_to_open: str) -> None:
    try:
        from IPython.display import (  # type:ignore # pylint: disable=import-error, import-outside-toplevel
            Javascript,
            display,
            update_display,
        )
    except ImportError as error:
        raise Exception('Unexpected environment. This function can only be called from a notebook.') from error

    display_id = str(uuid.uuid4())
    display(Javascript(f'window.open("{url_to_open}");'), display_id=display_id)
    time.sleep(1)
    update_display(Javascript(''), display_id=display_id)
