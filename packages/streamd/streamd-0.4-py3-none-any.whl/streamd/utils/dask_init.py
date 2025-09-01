import logging
import math

from dask.distributed import Client, SSHCluster
from rdkit import Chem
import time


def init_dask_cluster(n_tasks_per_node, ncpu, use_multi_servers=True, hostfile=None):
    """Initialize a Dask cluster on local or remote hosts.

    :param n_tasks_per_node: Number of tasks on a single server.
    :param ncpu: Number of CPU cores on a server.
    :param use_multi_servers: Whether to span the cluster across multiple hosts.
    :param hostfile: Optional file listing hostnames for SSH cluster.
    :return: Tuple of (dask_client, cluster).
    """
    if hostfile and use_multi_servers:
        with open(hostfile) as f:
            hosts = [line.strip() for line in f if line.strip()]
            n_servers = len(hosts)
    else:
        hosts = []
        n_servers = 1

    n_workers = n_tasks_per_node
    n_threads = math.ceil(ncpu / n_tasks_per_node)
    if hosts:
        logging.warning(f'Dask init, {ncpu}, {n_threads}, {n_workers}, {hosts},{n_servers}')
        cluster = SSHCluster(
            hosts=[hosts[0]] + hosts,
            connect_options={"known_hosts": None},
            worker_options={"nthreads": n_threads, 'n_workers': n_workers},
            scheduler_options={"port": 0, "dashboard_address": ":8786"},
        )
        dask_client = Client(cluster)
        time.sleep(10)
        logging.warning(cluster)

    else:
        cluster = None
        dask_client = Client(n_workers=n_workers, threads_per_worker=n_threads)  # to run dask on a single server

    dask_client.forward_logging(level=logging.INFO)
    dask_client.run(lambda: logging.getLogger().setLevel(logging.INFO))
    dask_client.run(lambda: logging.getLogger('distributed').setLevel(logging.ERROR))
    dask_client.run(lambda: logging.getLogger('MDAnalysis').setLevel(logging.CRITICAL))

    return dask_client, cluster


def calc_dask(func, main_arg, dask_client, dask_report_fname=None, **kwargs):
    """Execute a function over an iterable using a Dask client.

    Tasks are submitted to the provided client and results are yielded as
    soon as they finish. When ``dask_report_fname`` is provided a performance
    report is written for later inspection.

    :param func: Callable executed for each item in ``main_arg``.
    :param main_arg: Iterable supplying positional arguments to ``func``.
    :param dask_client: Active :class:`dask.distributed.Client` instance.
    :param dask_report_fname: Optional path for a Dask performance report.
    :param kwargs: Extra keyword arguments passed to ``func``.
    :return: Generator yielding results from ``func``.
    """
    main_arg = iter(main_arg)
    Chem.SetDefaultPickleProperties(Chem.PropertyPickleOptions.AllProps)
    task_times = {}  # Dictionary to store start times for each task

    try:
        if dask_client is not None:
            from dask.distributed import as_completed, performance_report
            # https://stackoverflow.com/a/12168252/895544 - optional context manager
            from contextlib import contextmanager
            none_context = contextmanager(lambda: iter([None]))()
            with (performance_report(filename=dask_report_fname) if dask_report_fname is not None else none_context):
                nworkers = len(dask_client.scheduler_info()['workers'])
                futures = []
                for i, arg in enumerate(main_arg, 1):
                    future = dask_client.submit(func, arg, **kwargs)
                    futures.append(future)
                    task_times[future.key] = {'start': time.time()}
                    if i == nworkers:
                        break
                seq = as_completed(futures, with_results=True)
                for i, (future, results) in enumerate(seq, 1):
                    logging.info(f'Finished task N: {i}. Argument: {results}. '
                                    f'Function: {future.key.split("-")[0]}. '
                                    f'Time: {round(time.time()-task_times[future.key]["start"], 3)} s.'
                                    )
                    yield results
                    del future
                    try:
                        arg = next(main_arg)
                        new_future = dask_client.submit(func, arg, **kwargs)
                        seq.add(new_future)
                        task_times[new_future.key] = {'start': time.time()}
                    except StopIteration:
                        continue
    finally:
        dask_client.cancel(futures)
