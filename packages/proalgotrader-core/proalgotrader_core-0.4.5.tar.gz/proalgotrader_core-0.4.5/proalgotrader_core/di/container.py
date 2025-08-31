from dependency_injector import containers, providers

from proalgotrader_core.api import Api
from proalgotrader_core.args_manager import ArgsManager


class Container(containers.DeclarativeContainer):
    """
    Container for basic dependencies that can be used independently.
    Note: Algorithm and Application are now created using the factory pattern
    in start_with_factory() function.
    """

    config = providers.Configuration()

    args_manager = providers.Singleton(ArgsManager)

    api = providers.Singleton(Api, args_manager=args_manager)
