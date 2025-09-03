from ghoshell_container.abcd import (
    IoCContainer,
    INSTANCE, BINDING, ABSTRACT,
    FactoryFunc, BootstrapFunc, ShutdownFunc,
    Bootstrapper,
    Provider, BootstrapProvider,
)
from ghoshell_container.containers import Container, DeclaredContainer, Inject
from ghoshell_container.utils import (
    provide, get_caller_info, get_container, set_container, depends,
)

set_container(Container(name='ghoshell_container.root'))
