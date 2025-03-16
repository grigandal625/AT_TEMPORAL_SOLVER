import argparse
import asyncio
import logging
import os

from at_queue.core.session import ConnectionParameters

from at_temporal_solver.core.component import ATTemporalSolver

parser = argparse.ArgumentParser(
    prog="at-temporal-solver", description="General working memory for AT-TECHNOLOGY components"
)

parser.add_argument("-u", "--url", help="RabbitMQ URL to connect", required=False, default=None)
parser.add_argument("-H", "--host", help="RabbitMQ host to connect", required=False, default="localhost")
parser.add_argument("-p", "--port", help="RabbitMQ port to connect", required=False, default=5672)
parser.add_argument(
    "-L",
    "--login",
    "-U",
    "--user",
    "--user-name",
    "--username",
    "--user_name",
    dest="login",
    help="RabbitMQ login to connect",
    required=False,
    default="guest",
)
parser.add_argument("-P", "--password", help="RabbitMQ password to connect", required=False, default="guest")
parser.add_argument(
    "-v",
    "--virtualhost",
    "--virtual-host",
    "--virtual_host",
    dest="virtualhost",
    help="RabbitMQ virtual host to connect",
    required=False,
    default="/",
)


async def main(**connection_kwargs):
    connection_parameters = ConnectionParameters(**connection_kwargs)
    solver = ATTemporalSolver(connection_parameters=connection_parameters)
    await solver.initialize()
    await solver.register()

    try:
        if not os.path.exists("/var/run/at_temporal_solver/"):
            os.makedirs("/var/run/at_temporal_solver/")

        with open("/var/run/at_temporal_solver/pidfile.pid", "w") as f:
            f.write(str(os.getpid()))
    except PermissionError:
        pass

    await solver.start()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    args_dict = vars(args)

    asyncio.run(main(**args_dict))
