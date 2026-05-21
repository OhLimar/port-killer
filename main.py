#!/usr/bin/env python3

import sys
import argparse
import platform

try:
    import psutil
except ImportError:
    print("psutil is required: pip install psutil")
    sys.exit(1)


SYSTEM = platform.system()


def find_process_by_port(port: int):
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr.port == port and conn.status == psutil.CONN_LISTEN:
            if conn.pid is None:
                continue
            try:
                return psutil.Process(conn.pid)
            except psutil.NoSuchProcess:
                continue
    return None


def format_process_info(proc: psutil.Process) -> str:
    try:
        cmdline = " ".join(proc.cmdline()) or "<no cmdline>"
        return (
            f"  pid      {proc.pid}\n"
            f"  name     {proc.name()}\n"
            f"  user     {proc.username()}\n"
            f"  cmd      {cmdline[:120]}"
        )
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return f"  pid      {proc.pid}\n  details  access denied"


def kill_process(proc: psutil.Process, force: bool = False):
    pid = proc.pid
    try:
        if SYSTEM == "Windows" or force:
            proc.kill()
        else:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                print(f"process {pid} did not exit after SIGTERM, sending SIGKILL")
                proc.kill()
        print(f"process {pid} killed")
    except psutil.AccessDenied:
        print("permission denied — try running with sudo")
        sys.exit(1)
    except psutil.NoSuchProcess:
        print(f"process {pid} already exited")


def main():
    parser = argparse.ArgumentParser(
        prog="port-killer",
        description="Kill the process listening on a given port.",
        epilog="example: port-killer 3000 --force"
    )
    parser.add_argument("port", type=int, help="TCP port number to free")
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="skip confirmation and use SIGKILL directly"
    )
    parser.add_argument(
        "--info", "-i",
        action="store_true",
        help="show process info without killing"
    )
    args = parser.parse_args()

    port = args.port

    if not (1 <= port <= 65535):
        print(f"invalid port: {port}")
        sys.exit(1)

    proc = find_process_by_port(port)

    if proc is None:
        print(f"no process found on port {port}")
        sys.exit(0)

    print(f"\nprocess on port {port}:\n")
    print(format_process_info(proc))

    if args.info:
        sys.exit(0)

    print()
    if not args.force:
        answer = input("kill this process? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("aborted")
            sys.exit(0)

    kill_process(proc, force=args.force)


if __name__ == "__main__":
    main()