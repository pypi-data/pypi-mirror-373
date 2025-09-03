import os

try:
    from prefect.futures import wait

    prefect_3 = True
except Exception as e:
    prefect_3 = False

def read_file(path: str):
    with open(path, "rb") as f:
        return f.read()


def write_file(path: str, content: bytes):
    folder = "/".join(path.split("/")[:-1])
    os.makedirs(folder, exist_ok=True)

    with open(path, "wb") as f:
        f.write(content)


def build_prefect_logger():
    try:
        import prefect

        logger = prefect.context.logger
    except Exception as e:
        from prefect import get_run_logger

        logger = get_run_logger()
    return logger

def resolve_future_tasks(future_tasks):
    if prefect_3:
        wait(future_tasks)

        for task in future_tasks:
            task.result()