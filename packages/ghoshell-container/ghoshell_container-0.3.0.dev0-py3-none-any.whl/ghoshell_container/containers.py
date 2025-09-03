from __future__ import annotations
from ghoshell_container.abcd import (
    IoCContainer, Provider, FactoryFunc, Bootstrapper, INSTANCE, BINDING, BootstrapFunc, ShutdownFunc,
)
from ghoshell_container.utils import get_caller_info, provide, is_builtin_type

import inspect
from typing import Type, Dict, Callable, Set, Optional, List, Any, Union, Iterable, get_type_hints
from typing import ClassVar
from typing_extensions import Self, is_protocol
import warnings

__all__ = [
    'Container',
    'DeclaredContainer',
    'Inject',
]


class Container(IoCContainer):
    """
    一个简单的 IoC 容器实现.
    IOC Container: 用来解耦各种 interface 和实现.
    """

    __instance_count__: ClassVar[int] = 0
    """the process level container instance count. for memory leak debug"""

    __cls_instance_count__: ClassVar[int] = 0
    """the class level container instance count. for memory leak debug"""

    def __init__(self, parent: Optional[IoCContainer] = None, *, name: str = "", inherit: bool = True):
        """
        :param parent: parent container
        :param name: name of the container
        :param inherit: inherit the registrar from the parent container if given.
        """
        self._bloodline = []
        # container extended by children container
        self._parent: Optional[IoCContainer] = None
        self._name = name
        self._bloodline = [name]
        # global singletons.
        self._instances: Dict[Any, Any] = {}
        self._factory: Dict[Any, FactoryFunc] = {}
        # providers bounds
        self._providers: Dict[Any, Provider] = {}
        self._bound: Set = set()
        self._bootstrapper_list: List[Union[Bootstrapper, BootstrapFunc]] = []
        self._bootstrapped: bool = False

        self._aliases: Dict[Any, Any] = {}
        """ the alias mapping from alias type to bound type"""

        self._depth: int = 0
        self._max_depth: int = 10
        self._making_stack: set = set()

        self._is_shutdown: bool = False
        self._is_shutting: bool = False
        self._shutdown_funcs: List[Callable[[], None]] = []
        # set parent now.
        if parent is not None:
            self.set_parent(parent, inherit)

        # count
        Container.__instance_count__ += 1
        self.__class__.__cls_instance_count__ += 1

    @property
    def name(self) -> str:
        return self._name

    @property
    def parent(self) -> Self | None:
        return self._parent

    @property
    def bloodline(self) -> List[str]:
        return self._bloodline

    def set_parent(self, parent: IoCContainer, shutdown: bool = True, inherit: bool = True) -> None:
        if not isinstance(parent, Container):
            raise AttributeError("container can only initialized with parent Container")
        if parent is self:
            raise AttributeError("container's parent must not be itself")
        self._parent = parent
        bloodline = self._parent._bloodline.copy()
        bloodline.append(self.name)
        self._bloodline = bloodline

        if shutdown:
            # when parent shutdown, shutdown self
            parent.add_shutdown(self.shutdown)
        if inherit and self._parent is not None:
            self._inherit(self._parent)

    def _inherit(self, parent: Container):
        """
        inherit none singleton provider from parent
        """
        for provider in parent.providers(recursively=True):
            if provider.inheritable() and not isinstance(provider, Bootstrapper):
                self._register(provider)

    def bind(
            self,
            contract: Type[INSTANCE],
            binding: BINDING | None = None,
            *,
            singleton: bool = True,
            kwargs: Dict[str, Any] | None = None,
    ) -> None:
        lineinfo = get_caller_info(2)
        if isinstance(binding, Provider):
            binding.registered_at = lineinfo
            self.register(binding)
            return None
        decorator = provide(contract, singleton=singleton, lineinfo=lineinfo, kwargs=kwargs)

        if isinstance(binding, contract):
            self.set(contract, binding)
            return None

        elif binding is not None:
            provider = decorator(binding)
            self.register(provider)
            return None
        else:
            # set contract itself to be make
            provider = decorator(contract)
            self.register(provider)
            return None

    def factory(
            self,
            contract: Type[INSTANCE],
            *,
            singleton: bool = True,
            kwargs: Dict | None = None,
    ) -> Callable[[FactoryFunc], FactoryFunc]:
        lineinfo = get_caller_info(2)
        decorator = provide(contract, singleton=singleton, lineinfo=lineinfo, kwargs=kwargs)

        def wrapper(factory: FactoryFunc) -> FactoryFunc:
            provider = decorator(factory)
            self.register(provider)
            return factory

        return wrapper

    def bootstrap(self) -> None:
        """
        执行 bootstrap, 只执行一次. 可以操作依赖关系. 比如实例化后反向注册.
        """
        self._check_destroyed()
        if self._bootstrapped:
            return
        # 必须在这里初始化, 否则会循环调用.
        self._bootstrapped = True
        if self._bootstrapper_list:
            for b in self._bootstrapper_list:
                if isinstance(b, Bootstrapper):
                    b.bootstrap(self)
                else:
                    self.call(b)

    def add_shutdown(self, shutdown: ShutdownFunc):
        self._shutdown_funcs.append(shutdown)

    def set(self, contract: Any, instance: INSTANCE) -> None:
        """
        设置一个实例, 不会污染父容器.
        """
        self._check_destroyed()
        if contract in self._providers:
            # 删除已经注册过的 providers.
            del self._providers[contract]
        # 设置单例.
        self._set_singleton(contract, instance)

    def _add_bound_contract(self, contract: Type[INSTANCE]) -> None:
        """
        添加好绑定关系, 方便快速查找.
        """
        self._bound.add(contract)

    def bound(self, contract: Type[INSTANCE], *, recursively: bool = True) -> bool:
        """
        return whether contract is bound.
        """
        self._check_destroyed()
        return contract in self._bound or (recursively and self._parent is not None and self._parent.bound(contract))

    def alias(self, contract: Type[INSTANCE], *aliases: Type[INSTANCE]) -> None:
        for alias in aliases:
            self._bind_alias(alias, contract)

    def unbound(self, contract: Type[INSTANCE]) -> None:
        if contract in self._instances:
            del self._instances[contract]
        if contract in self._providers:
            del self._providers[contract]
        if contract in self._bound:
            self._bound.remove(contract)
        if contract in self._aliases:
            del self._aliases[contract]

    def get(self, contract: Union[Type[INSTANCE], Any], *, recursively: bool = True) -> Optional[INSTANCE]:
        """
        get bound instance or initialize one from registered factory or provider.
        """
        self._check_destroyed()
        if contract is IoCContainer or contract is self.__class__:
            return self

        # 进行初始化.
        if not self._bootstrapped:
            if len(self._bootstrapper_list) > 0:
                caller_info = get_caller_info(2)
                warnings.warn(
                    "container have not bootstrapped before using: %s" % (
                        caller_info
                    ),
                    UserWarning,
                )
            # self.bootstrap()

        # get bound instance
        if contract in self._instances:
            return self._instances[contract]

        # use provider as factory to initialize instance of the contract
        if contract in self._providers:
            provider = self._providers[contract]
            made = provider.factory(self)
            if made is not None and provider.singleton():
                self._set_singleton(contract, made)
            return made

        # search aliases if the real contract exists
        if contract in self._aliases:
            contract = self._aliases[contract]
            return self.get(contract)

        # at last
        if recursively and self._parent is not None:
            return self._parent.get(contract)
        return None

    def get_bound(self, contract: Type[INSTANCE]) -> Union[INSTANCE, Provider, None]:
        """
        get bound of a contract
        :return: instance or provider
        """
        self._check_destroyed()
        if contract in self._instances:
            return self._instances[contract]
        elif contract in self._providers:
            return self._providers[contract]
        elif contract in self._aliases:
            alias = self._aliases[contract]
            return self.get_bound(alias)
        elif self._parent is not None:
            return self._parent.get_bound(contract)
        return None

    def register(self, *providers: Provider) -> None:
        """
        register factory of the contract by provider
        """
        self._check_destroyed()
        lineinfo = get_caller_info(2)
        for provider in providers:
            if not provider.registered_at:
                # easy to find where
                provider.registered_at = lineinfo
            self._register(provider)

    def _register(self, provider: Provider) -> None:
        contract = provider.contract()
        self._add_bound_contract(contract)
        self._register_provider(contract, provider)

        # additional bindings
        for alias in provider.aliases():
            if alias not in self._bound:
                self._bind_alias(alias, contract)
        if isinstance(provider, Bootstrapper):
            # add bootstrapper.
            self.add_bootstrapper(provider)

    def _bind_alias(self, alias: Any, contract: Any) -> None:
        if alias in self._bound:
            # do not rebind
            return
        self._aliases[alias] = contract
        self._bound.add(alias)

    def _register_provider(self, contract: Type[INSTANCE], provider: Provider) -> None:
        # remove singleton instance that already bound
        if contract in self._instances:
            del self._instances[contract]
        # override the existing one
        self._providers[contract] = provider

    def add_bootstrapper(self, bootstrapper: Bootstrapper | BootstrapFunc) -> None:
        """
        注册 Container 的 bootstrapper. 在正式运行时会先 bootstrap, 而且只执行一次.
        :param bootstrapper: 可以定义一些方法, 比如往容器里的某个类里注册一些工具.
        :return:
        """
        self._check_destroyed()
        self._bootstrapper_list.append(bootstrapper)
        if self._bootstrapped:
            # add bootstrapper and run it immediately
            if isinstance(bootstrapper, Bootstrapper):
                bootstrapper.bootstrap(self)
            else:
                self.call(bootstrapper)

    def fetch(self, contract: Type[INSTANCE]) -> Optional[INSTANCE]:
        """
        get contract with type check
        :exception: TypeError if instance do not implement contract
        """
        self._check_destroyed()
        instance = self.get(contract)
        if instance is not None:
            if not isinstance(instance, contract):
                raise TypeError(f"bound implements is not type of {contract}")
            return instance
        return None

    def get_provider(self, contract: Type[INSTANCE]) -> Optional[Provider]:
        if contract in self._providers:
            return self._providers[contract]
        if self._parent is not None:
            return self._parent.get_provider(contract)
        return None

    def _set_singleton(self, contract: Any, instance: Any) -> None:
        """
        设定常量.
        """
        self._add_bound_contract(contract)
        self._instances[contract] = instance

    def contracts(self, recursively: bool = True) -> Iterable[Type[INSTANCE]]:
        self._check_destroyed()
        done = set()
        for contract in self._bound:
            done.add(contract)
            yield contract
        if recursively and self._parent is not None:
            for contract in self._parent.contracts():
                if contract not in done:
                    done.add(contract)
                    yield contract

    def providers(self, recursively: bool = True) -> Iterable[Provider]:
        self._check_destroyed()
        done = set()
        for provider in self._providers.values():
            done.add(provider.contract())
            yield provider
        if recursively and self._parent is not None:
            for provider in self._parent.providers():
                if provider.contract() not in done:
                    done.add(provider.contract())
                    yield provider

    def _check_destroyed(self) -> None:
        if self._is_shutdown:
            raise RuntimeError(f"container {self._bloodline} is called after destroyed")

    def call(self, caller: Callable, *args, **kwargs) -> Any:
        named_kwargs = {name: value for name, value in kwargs.items()}
        named_kwargs = self._reflect_callable_args(caller, args, named_kwargs)
        return caller(*args, **named_kwargs)

    def make(self, contract: Type[INSTANCE], **kwargs) -> INSTANCE:
        try:
            if contract in self._instances:
                return self._instances[contract]
            return self._make(contract, **kwargs)
        except Exception as e:
            raise RuntimeError(f"failed to make instance {contract} cause `{e}` "
                               f"at container {self._bloodline}")

    def new(self, contract: Type[INSTANCE], **kwargs) -> INSTANCE:
        if not isinstance(contract, type):
            raise TypeError(f"Argument typehint: {type(contract)} should be class")
        elif is_builtin_type(contract):
            return contract(**kwargs)

        init_fn = getattr(contract, '__init__', None)
        if init_fn is not None:
            named_kwargs = self._reflect_callable_args(init_fn, (), kwargs)
            obj = contract(**named_kwargs)
        else:
            obj = contract(**kwargs)

        rebind = {}
        for name, typehint in get_type_hints(contract).items():
            if name.startswith('_'):
                continue

            member = contract.__dict__.get(name, None)
            if isinstance(member, Inject):
                if not self.bound(typehint) and member.binding is not None:
                    self.bind(typehint, member.binding)
                rebind[name] = self.get(typehint) or member.default

        if len(rebind) > 0:
            for name, value in rebind.items():
                setattr(obj, name, value)
        return obj

    def _make(self, contract: Type[INSTANCE], **kwargs) -> INSTANCE | None:
        try:
            self._depth += 1
            if self._depth > self._max_depth:
                raise RuntimeError(f'making depth {self._depth} exceeds max_depth {self._max_depth}')

            if contract in self._making_stack:
                raise RuntimeError(f'Infinite recursion while making instance {contract}')

            self._making_stack.add(contract)

            instance = self.get(contract)
            if instance is not None:
                return instance

            return self.new(contract, **kwargs)

        finally:
            self._depth -= 1
            self._making_stack.remove(contract)

    def _reflect_callable_args(
            self,
            caller: Callable,
            args: tuple,
            named_kwargs: Dict,
    ) -> Dict:
        target_module = inspect.getmodule(caller)
        if target_module is None:
            local_values = {}
        else:
            local_values = target_module.__dict__
        empty = inspect.Parameter.empty
        skip = len(args)
        i = 0
        for name, param in inspect.signature(caller).parameters.items():
            # ignore which already in kwargs
            i += 1
            if name in named_kwargs or i - 1 < skip:
                continue
            elif name == "self":
                continue
            injection = param.default
            annotation = param.annotation
            if annotation and annotation is not empty:
                typehint = annotation
                if is_builtin_type(typehint):
                    continue
                elif isinstance(typehint, str) and typehint in local_values:
                    typehint = local_values[typehint]
                elif isinstance(typehint, str):
                    continue
                elif is_protocol(typehint):
                    continue

                got = self._make(typehint)
                if got is not None:
                    injection = got
            if injection is not empty:
                named_kwargs[name] = injection
        return named_kwargs

    def shutdown(self) -> None:
        """
        Manually delete the container to prevent memory leaks.
        """
        if self._is_shutting:
            return
        self._is_shutting = True
        errors = []
        if self._shutdown_funcs:
            for shutdown in self._shutdown_funcs:
                try:
                    self.call(shutdown)
                except Exception as e:
                    errors.append(e)
        self._is_shutdown = True
        if errors:
            info = " | ".join(str(e) for e in errors)
            raise RuntimeError(f"container {self._bloodline} shutdown errors: {info}")

    def __del__(self):
        self.shutdown()
        del self._shutdown_funcs
        del self._instances
        del self._parent
        del self._providers
        del self._bound
        del self._bootstrapper_list
        del self._aliases
        Container.__instance_count__ -= 1
        self.__class__.__instance_count__ -= 1


class Inject:

    def __init__(self, default: INSTANCE | None = None, *, binding: BINDING | None = None):
        self.default = default
        self.binding = binding

    def __get__(self, instance, owner) -> INSTANCE | None:
        return self.default

    def __set__(self, instance, value):
        self.default = value

    def __delete__(self, instance):
        self.default = None


class DeclaredContainer(Container):

    def bootstrap(self) -> None:
        if self._bootstrapped:
            return
        super().bootstrap()
        rebind = {}
        for name, typehint in get_type_hints(self.__class__).items():
            if name.startswith('_') or is_builtin_type(typehint) or is_protocol(typehint):
                continue
            member = self.__class__.__dict__.get(name, None)
            if member is not None and isinstance(member, Inject):
                if member.binding is not None:
                    self.bind(typehint, member.binding)
                elif member.default is not None:
                    self.set(typehint, member.default)
                rebind[name] = self.force_fetch(typehint)
            else:
                rebind[name] = self.make(typehint)

        for name, value in rebind.items():
            setattr(self, name, value)
