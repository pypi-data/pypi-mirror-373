"""Loki utils: query/tail logs from Loki"""
# TODO(asaiacai): eventually support querying
# centralized loki that lives outside the cluster

import asyncio
import json
import urllib.parse

import colorama
import kr8s
import websockets

from konduktor import logging

logger = logging.get_logger(__name__)

LOKI_REMOTE_PORT = 3100
WEBSOCKET_TIMEOUT = 10
INFINITY = 999999


async def _read_loki_logs(loki_url: str, timeout: int, job_name: str, worker_id: int):
    ws = await asyncio.wait_for(websockets.connect(loki_url), timeout=WEBSOCKET_TIMEOUT)
    logger.info(
        f'{colorama.Fore.YELLOW}Tailing logs from Loki. '
        f'Forwarding from remote port {LOKI_REMOTE_PORT}. Press Ctrl+C to stop. '
        f'{colorama.Style.RESET_ALL}'
    )
    try:
        while True:
            message = await asyncio.wait_for(ws.recv(), timeout=timeout)
            try:
                payload = json.loads(message)
                for stream in payload['streams']:
                    if stream['values'][0][1] is not None:
                        print(
                            f"{colorama.Fore.CYAN}{colorama.Style.BRIGHT} "
                            f"(job_name={job_name} worker_id={worker_id})"
                            f"{colorama.Style.RESET_ALL} {stream['values'][0][1]}",
                            flush=True,
                        )
            except json.JSONDecodeError:
                logger.warning(f'Failed to decode log skipping: {message}')
                logger.debug(f'Dropped log: {message}')
                continue
    except asyncio.exceptions.TimeoutError:
        logger.debug('Websocket timed-out, closing log stream!')
    except KeyboardInterrupt:
        logger.debug('Keyboard interrupt, closing log stream!')


def tail_loki_logs_ws(
    job_name: str, worker_id: int = 0, num_logs: int = 1000, follow: bool = True
):
    if num_logs > 5000:
        # TODO(asaiacai): we should not have a limit on the number of logs, but rather
        # let the user specify any number of lines, and we can print the last N lines.
        # this can be done in chunks. Potentially, we can query range
        # until we reach the end of the log and then invoke tail again.
        # Also include checks that the job is running/ever ran.
        raise ValueError('num_logs must be less than or equal to 5000')
    loki_svc = kr8s.objects.Service.get('loki', namespace='loki')
    with kr8s.portforward.PortForward(
        loki_svc, LOKI_REMOTE_PORT, local_port='auto'
    ) as port:
        loki_url = f'ws://localhost:{port}/loki/api/v1/tail'
        logger.debug(f'Loki URL: {loki_url}')
        params = {
            'query': urllib.parse.quote(
                r'{' + f'k8s_job_name="{job_name}-workers-0",'
                r' k8s_container_name="konduktor-container"} '
                f' | batch_kubernetes_io_job_completion_index = `{worker_id}`'
            ),
            'limit': num_logs,
            'delay': 5,
            # TODO(asaiacai): need to auto-generate the start and end times.
        }

        query_string = '&'.join(f'{key}={value}' for key, value in params.items())
        loki_url += f'?{query_string}'
        timeout = INFINITY if follow else WEBSOCKET_TIMEOUT
        asyncio.run(_read_loki_logs(loki_url, timeout, job_name, worker_id))


# TODO(asaiacai): write a query_range function to get all the
# logs for a job for not tailing option

# Run the WebSocket log tailing function
if __name__ == '__main__':
    tail_loki_logs_ws('tune-bc43', worker_id=0, follow=True)
