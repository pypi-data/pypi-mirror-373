import logging
import os

import psutil


class DataNotReady:
    def __init__(self):
        pass


class EndOfIteration:
    pass


def print_memory_summary(prefix="Memory Summary"):
    """Print a detailed memory summary using pympler"""
    from pympler import muppy, summary

    try:
        all_objects = muppy.get_objects()
        sum_obj = summary.summarize(all_objects)
        print(f"\n{prefix}:")
        summary.print_(sum_obj)
        print()  # Add blank line after summary
    except ImportError:
        print(f"{prefix}: pympler not available")
    except Exception as e:
        print(f"{prefix}: Error getting memory summary - {e}")


def print_process_memory_usage(prefix="sampler"):
    """Shared function to print memory usage for the current process"""
    pid = os.getpid()
    process = psutil.Process(pid)
    memory_maps = process.memory_maps(grouped=True)
    # Aggregate memory statistics
    total_rss = sum(mmap.rss for mmap in memory_maps) / 1024 / 1024  # MB
    total_pss = sum(mmap.pss for mmap in memory_maps) / 1024 / 1024  # MB
    total_uss = (
        sum(mmap.private_clean + mmap.private_dirty for mmap in memory_maps)
        / 1024
        / 1024
    )  # MB
    total_shared = (
        sum(mmap.shared_clean + mmap.shared_dirty for mmap in memory_maps) / 1024 / 1024
    )  # MB
    shared_files = len(
        [
            mmap
            for mmap in memory_maps
            if mmap.path and mmap.path != "[heap]" and mmap.path != "[stack]"
        ]
    )

    logging.info(
        f"{prefix}: PID {pid} - RSS: {total_rss:.2f} MB, PSS: {total_pss:.2f} MB, "
        f"USS: {total_uss:.2f} MB, Shared: {total_shared:.2f} MB, Files: {shared_files}"
    )
