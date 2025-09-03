import sys
import threading
import traceback


def list_threads_with_stacktraces():
    """
    Return a list of threads with their stack traces.
    """
    thread_info_list = []
    # get the current thread frames
    thread_frames = sys._current_frames()
    # get a list of all threads
    thread_list = threading.enumerate()

    for thread in thread_list:
        # get thread info
        ident = thread.ident
        trace = thread_frames.get(ident)
        stack = []

        if trace:
            # get thread stack trace
            for filename, lineno, name, line in traceback.extract_stack(trace):
                frame = {
                    "file": filename,
                    "line": lineno,
                    "function": name,
                    "code": str(line).strip() if line else ""
                }
                stack.append(frame)

        thread_info = {
            "name": thread.name,
            "id": ident,
            "daemon": thread.daemon,
            "alive": thread.is_alive(),
            "stack_trace": stack
        }

        thread_info_list.append(thread_info)

    return thread_info_list