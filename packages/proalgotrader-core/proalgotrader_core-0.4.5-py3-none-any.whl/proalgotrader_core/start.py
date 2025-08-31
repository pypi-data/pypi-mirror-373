import asyncio
from typing import Type

from logzero import logger
from dotenv import load_dotenv

from proalgotrader_core.application import Application
from proalgotrader_core.di.algorithm_factory import AlgorithmFactory
from proalgotrader_core.protocols.algorithm import AlgorithmProtocol


# Setup the loop at module level
try:
    event_loop = asyncio.get_running_loop()
except RuntimeError:
    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)


async def start_with_factory(strategy_class: Type[AlgorithmProtocol]) -> None:
    """
    Start function that uses the factory pattern to create
    Algorithm with pre-initialized AlgoSession
    """
    load_dotenv(verbose=True, override=True)

    algorithm_factory = AlgorithmFactory(
        event_loop=event_loop,
        strategy_class=strategy_class,
    )

    # Use factory to create algorithm with session
    algorithm = await algorithm_factory.create_algorithm_with_session()

    # Create application with the pre-initialized algorithm
    application = Application(algorithm=algorithm)

    try:
        await application.start()
    except Exception as e:
        logger.exception(e)


def run_strategy(strategy_class: Type[AlgorithmProtocol]) -> None:
    """
    Start function that uses the factory pattern for better initialization
    """
    try:
        event_loop.run_until_complete(start_with_factory(strategy_class=strategy_class))
    except Exception as e:
        logger.exception(e)
    finally:
        event_loop.close()
