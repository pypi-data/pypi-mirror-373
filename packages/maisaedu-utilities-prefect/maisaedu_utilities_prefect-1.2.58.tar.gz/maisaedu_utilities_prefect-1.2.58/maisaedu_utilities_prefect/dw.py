import os
import json
import psycopg2
import urllib.parse

from prefect import task, Task

from typing import Optional

from .constants.env import CUSTOMER_PROD_RO, PROD, HLG_QA, DEV, DEV_QA, LOCAL


def get_dsn(credentials_file_path: str = "data/dw-credentials.txt") -> Optional[str]:
    with open(credentials_file_path) as f:
        return f.read()

def get_red_credentials(env=PROD):
    if env == PROD:
        path = "data/dw-redshift-prod-credentials.json"
    elif env == CUSTOMER_PROD_RO:
        path = "data/dw-redshift-customer-prod-ro-credentials.json"
    elif env == DEV:
        path = "data/dw-redshift-dev-credentials.json"
    elif env == DEV_QA:
        path = "data/dw-redshift-dev-qa-credentials.json"
    elif env == HLG_QA:
        path = "data/dw-redshift-hlg-qa-credentials.json"
    elif env == LOCAL:
        path = "data/dw-redshift-dev-credentials.json"

    with open(path) as f:
        r = f.read()
        return json.loads(r)


def get_dsn_as_url(fallback: str = "data/dw-credentials.txt") -> Optional[str]:
    dsn = get_dsn(fallback)
    if dsn is not None:
        param_list = [part.split("=") for part in dsn.split()]
        params = {key: value for key, value in param_list}
        quoted_user = urllib.parse.quote(params["user"].encode("utf-8"))
        quoted_pass = urllib.parse.quote(params["password"].encode("utf-8"))
        return (
            f"postgresql+psycopg2://{quoted_user}:{quoted_pass}"
            f"@{params['host']}:{params.get('port') or 5432}/{params['dbname']}"
        )


def query_file(
    filename: str,
    params=None,
    slug=None,
    tags=None,
    max_retries=None,
    retry_delay=None,
    timeout=None,
    trigger=None,
    skip_on_upstream_skip=True,
    cache_for=None,
    cache_validator=None,
    cache_key=None,
    checkpoint=None,
    state_handlers=None,
    on_failure=None,
    log_stdout=False,
    result=None,
    target=None,
    task_run_name=None,
    nout=None,
    **kwargs,
) -> Task:
    with open(filename) as f:
        query_text = f.read()

    @task(
        name=filename,
        slug=slug,
        tags=tags,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
        trigger=trigger,
        skip_on_upstream_skip=skip_on_upstream_skip,
        cache_for=cache_for,
        cache_validator=cache_validator,
        cache_key=cache_key,
        checkpoint=checkpoint,
        state_handlers=state_handlers,
        on_failure=on_failure,
        log_stdout=log_stdout,
        result=result,
        target=target,
        task_run_name=task_run_name,
        nout=nout,
    )
    def query(params):
        with psycopg2.connect(get_dsn()) as connection, connection.cursor() as cursor:
            cursor.execute(query_text, params or [])
            try:
                return cursor.fetchall()
            except psycopg2.ProgrammingError:
                # expect "no results to fetch"
                return []
            finally:
                connection.commit()

    return query(params, **kwargs)


def query_str(
    query_str: str,
    params=None,
    slug=None,
    tags=None,
    max_retries=None,
    retry_delay=None,
    timeout=None,
    trigger=None,
    skip_on_upstream_skip=True,
    cache_for=None,
    cache_validator=None,
    cache_key=None,
    checkpoint=None,
    state_handlers=None,
    on_failure=None,
    log_stdout=False,
    result=None,
    target=None,
    task_run_name=None,
    nout=None,
    **kwargs,
) -> Task:
    split = query_str.split()

    @task(
        name=f"{split[0]} ..." if len(split) > 0 else "query",
        slug=slug,
        tags=tags,
        max_retries=max_retries,
        retry_delay=retry_delay,
        timeout=timeout,
        trigger=trigger,
        skip_on_upstream_skip=skip_on_upstream_skip,
        cache_for=cache_for,
        cache_validator=cache_validator,
        cache_key=cache_key,
        checkpoint=checkpoint,
        state_handlers=state_handlers,
        on_failure=on_failure,
        log_stdout=log_stdout,
        result=result,
        target=target,
        task_run_name=task_run_name,
        nout=nout,
    )
    def query(params):
        with psycopg2.connect(get_dsn()) as connection, connection.cursor() as cursor:
            cursor.execute(query_str, params or [])
            try:
                return cursor.fetchall()
            except psycopg2.ProgrammingError:
                # expect "no results to fetch"
                return []
            finally:
                connection.commit()

    return query(params, **kwargs)
