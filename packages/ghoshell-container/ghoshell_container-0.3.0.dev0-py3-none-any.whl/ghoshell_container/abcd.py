from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import Type, TypeVar, Callable, Optional, List, Generic, Any, Union, Iterable, Dict
from typing import get_args, get_origin
from typing_extensions import Self

__all__ = [
    "IoCContainer",
    "INSTANCE", 'BINDING', 'ABSTRACT',
    "FactoryFunc", "BootstrapFunc", "ShutdownFunc",
    "Provider",
    "Bootstrapper", "BootstrapProvider",
    'Contracts',
    'get_generic_contract_type',
]

INSTANCE = TypeVar('INSTANCE')
"""instance in the container"""

ABSTRACT = Type[INSTANCE]

FactoryFunc = Callable[..., INSTANCE]

BootstrapFunc = Callable[..., None]
"""type for bootstrap"""

ShutdownFunc = Callable[..., None]


class IoCContainer(metaclass=ABCMeta):
    """
    Basic Design of the Inverse of Control Container.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        name of the container
        """
        pass

    @property
    @abstractmethod
    def bloodline(self) -> List[str]:
        """
        bloodline of the container
        :return: the name of the containers from root to the current one.
        """
        pass

    @property
    @abstractmethod
    def parent(self) -> Self | None:
        """
        :return: the parent container of this one.
        """
        pass

    # --- basic get and set of container --- #

    @abstractmethod
    def set(self, contract: Type[INSTANCE], instance: INSTANCE) -> None:
        """
        向容器里设置一个单例. 
        set a singleton into the container
        """
        pass

    @abstractmethod
    def get(self, contract: Type[INSTANCE], *, recursively: bool = True) -> Optional[INSTANCE]:
        """
        从容器里获取一个实例. 
        get bound instance or initialize one from registered contract, or generate one by factory or provider.
        :return: None if no bound instance.
        """
        pass

    @abstractmethod
    def fetch(self, contract: Type[INSTANCE]) -> Optional[INSTANCE]:
        """
        从容器里获取一个实例, 同时校验类型是否一致. 
        :param contract: use type of the object (usually a contract class) to fetch the implementation.
        :exception: TypeError if the bound instance does not implement contract
        """
        pass

    def force_fetch(self, contract: Type[INSTANCE], strict: bool = False) -> INSTANCE:
        """
        强制从容器里获取一个实例, 如果没有绑定会抛出异常.
        if fetch contract failed, raise error.
        :exception: TypeError if the bound instance does not implement contract
        :exception: KeyError if contract is not bound
        """
        r = self.fetch(contract)
        if r is None:
            raise KeyError(f'no binding found for contract {contract}')
        return r

    @abstractmethod
    def bound(self, contract: Type[INSTANCE], *, recursively: bool = True) -> bool:
        """
        判断一个抽象是否已经被绑定了.
        return whether contract is bound.
        """
        pass

    @abstractmethod
    def alias(self, contract: Type[INSTANCE], *aliases: Type[INSTANCE]) -> None:
        """
        set aliases of contract
        """
        pass

    @abstractmethod
    def unbound(self, contract: Type[INSTANCE]) -> None:
        """
        unbound contract.
        """
        pass

    # ---- make and call from container ---- #

    @abstractmethod
    def new(self, contract: Type[INSTANCE], **kwargs) -> INSTANCE:
        """
        通过反射 class 的 __init__ 函数, 自动生成一个实例.
        new an instance and inject the dependencies to the __init__ automatically
        experimental feature.

        :param contract: the class of the instance
        :param kwargs: more arguments for the __init__
        :return: the instance of it.
        :exception KeyError: if the cls is not bound
        """
        pass

    @abstractmethod
    def make(self, contract: Type[INSTANCE], **kwargs) -> INSTANCE:
        """
        尝试从容器获取实例, 如果没有绑定, 通过反射 __init__ 函数, 自动生成一个实例,
        get an instance from container, if not exists, new it after

        :param contract: the class of the instance
        :param kwargs: more arguments for the __init__
        :return: the instance of it.
        :exception KeyError: if the cls is not bound
        """
        pass

    @abstractmethod
    def call(self, caller: Callable, *args, **kwargs) -> Any:
        """
        通过反射入参, 提供相关入参给函数.
        call a method or function, and inject the dependencies to the kwargs.
        :return: the caller result.
        """
        pass

    # ---- container lifecycle ---- #

    @abstractmethod
    def bootstrap(self) -> None:
        """
        执行 bootstrap, 将所有的 bootstrapper 执行一次.
        只执行一次. 可以操作依赖关系. 比如实例化后反向注册.

        bootstrap the container (once of the lifecycle)
        will be called when get any contract from the container
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """
        shutdown the container and all the registered shutdown functions.
        """
        pass

    @abstractmethod
    def add_bootstrapper(self, bootstrapper: Bootstrapper | BootstrapFunc) -> None:
        """
        注册启动函数.
        register a bootstrap container into the container
        """
        pass

    @abstractmethod
    def add_shutdown(self, shutdown: ShutdownFunc) -> None:
        """
        注册关闭函数.
        add a shutdown function to the container. when the container shutdown, the shutdown functions will be called.
        """
        pass

    def __enter__(self) -> Self:
        """
        example for container lifecycle:

        with container:
            xxxx

        or

        container.bootstrap()
        ...
        container.shutdown()
        """
        self.bootstrap()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        example for container lifecycle
        """
        self.shutdown()

    # --- register methods --- #

    @abstractmethod
    def bind(
            self,
            contract: Type[INSTANCE],
            binding: BINDING | None = None,
            *,
            singleton: bool = True,
            kwargs: Dict[str, Any] | None = None,
    ) -> None:
        """
        bind a factory method for the contract into the container
        :param contract: the abstract class of the instance
        :param singleton: whether to bind a singleton
        :param binding: the factory method. if given, method return None
        :param kwargs: additional arguments for the factory method
        :return: if factory method is None, return a decorator to wrap one
        """
        pass

    @abstractmethod
    def factory(
            self,
            contract: Type[INSTANCE],
            *,
            singleton: bool = True,
            kwargs: Dict[str, Any] | None = None,
    ) -> Callable[[FactoryFunc], FactoryFunc]:
        """
        factory decorator
        """
        pass

    @abstractmethod
    def get_bound(self, contract: Type[INSTANCE]) -> Union[INSTANCE, Provider, None]:
        """
        get bound of a contract
        useful to debug
        :return: instance or provider
        """
        pass

    @abstractmethod
    def register(self, *providers: Provider) -> None:
        """
        register factory of the contract by provider
        """
        pass

    @abstractmethod
    def get_provider(self, contract: Type[INSTANCE]) -> Optional[Provider[INSTANCE]]:
        """
        get provider of a contract
        """
        pass

    @abstractmethod
    def contracts(self, recursively: bool = True) -> Iterable[ABSTRACT]:
        """
        yield from bound contracts
        """
        pass

    @abstractmethod
    def providers(self, recursively: bool = True) -> Iterable[Provider]:
        """
        iterate all the providers
        """
        pass

    # --- dict interface --- #

    def __getitem__(self, item):
        return self.get(item, recursively=True)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __delitem__(self, key):
        self.unbound(key)

    def __len__(self) -> int:
        return len(list(self.contracts()))

    def __iter__(self):
        for contract in self.contracts():
            yield contract, self.get(contract)


class Provider(Generic[INSTANCE], metaclass=ABCMeta):
    """
    provider that define a factory
    """

    registered_at: str = ""
    """the code line where this provider is registered"""

    @abstractmethod
    def singleton(self) -> bool:
        """
        if singleton, return True.
        """
        pass

    def inheritable(self) -> bool:
        """
        if the provider is inheritable to sub container
        """
        return not self.singleton()

    def contract(self) -> Type[INSTANCE]:
        """
        :return: contract for this provider.
        override this method to define a contract without get from generic args
        """
        return get_generic_contract_type(self.__class__)

    def aliases(self) -> Iterable[Type[INSTANCE]]:
        """
        additional contracts that shall bind to this provider if the binding contract is not Bound.
        """
        return []

    @abstractmethod
    def factory(self, con: IoCContainer) -> INSTANCE:
        """
        factory method to generate an instance of the contract.
        """
        pass


BINDING = Union[ABSTRACT, FactoryFunc, Provider, INSTANCE]


class Bootstrapper(metaclass=ABCMeta):
    """
    contract method for container bootstrap
    """

    registered_at: str = ""

    @abstractmethod
    def bootstrap(self, container: IoCContainer) -> None:
        pass


class BootstrapProvider(Generic[INSTANCE], Provider[INSTANCE], Bootstrapper, metaclass=ABCMeta):
    """
    将 bootstrapper 和 Provider 可以融合在一起.
    """

    @abstractmethod
    def contract(self) -> Type[INSTANCE]:
        pass


class Contracts:
    """
    A contracts validator that both indicate the contract types and validate if they are bound to container
    """

    def __init__(self, contracts: Iterable[ABSTRACT]):
        self.contracts = contracts

    @classmethod
    def new(cls, *contracts: Type[INSTANCE]) -> Self:
        return cls(contracts)

    def validate(self, container: IoCContainer) -> None:
        for contract in self.contracts:
            if not container.bound(contract):
                raise NotImplementedError(f'Contract {contract} not bound to container {container.bloodline}')

    def join(self, target: Contracts) -> Contracts:
        """
        join contracts
        """
        contracts = set(self.contracts)
        for c in target.contracts:
            contracts.add(c)
        return Contracts(list(contracts))


def get_generic_contract_type(cls: Type) -> ABSTRACT:
    """
    get generic INSTANCE type from the instance of the provider.
    """
    if "__orig_bases__" in cls.__dict__:
        orig_bases = getattr(cls, "__orig_bases__")
        for parent in orig_bases:
            if get_origin(parent) is not Provider:
                continue
            args = get_args(parent)
            if not args:
                break
            return args[0]
    raise AttributeError("can not get contract type")
