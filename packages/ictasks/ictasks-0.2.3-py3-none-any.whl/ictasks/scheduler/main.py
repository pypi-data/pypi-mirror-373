import argparse

from scheduler import Scheduler

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("action", type=str)
    parser.add_argument("--input", type=str, default=None)

    args = parser.parse_args()

    s = Scheduler()
    if args.action == "init":
        s.initialize_db()
    elif args.action == "enqueue":
        s.enqueue(args.input)
    elif args.action == "cancel":
        s.cancel()
    elif args.action == "list":
        s.list_tasks()
