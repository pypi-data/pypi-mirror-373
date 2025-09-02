import typing

import almanet

from . import _state

__all__ = [
    "transition_model",
    "make_transition",
    "transition",
    "make_observer",
    "observe",
]


class _transition_procedure[I, O](typing.Protocol):
    __name__: str

    async def __call__(
        self,
        payload: I,
        *,
        session: almanet.Almanet,
        transition: "transition_model",
    ) -> O | None: ...


@almanet.shared.dataclass
class transition_model[I, O: _state.observable_state]:
    label: str
    source: type[I]
    target: type[O]
    procedure: _transition_procedure[I, O]
    description: str | None = None
    is_observer: bool = False

    def __post_init__(self):
        self.__name__ = self.label
        self.__doc__ = self.description

    async def _remote_execution(
        self,
        payload: I,
        *args,
        session: almanet.Almanet,
        **kwargs,
    ) -> O:
        kwargs["transition"] = self
        result = await self.procedure(payload, *args, **kwargs, session=session)
        if result is None:
            result = typing.cast(O, payload)
        await session.delay_call(self.target._uri_, result, result._next_delay_seconds_)
        return result

    async def _local_execution(
        self,
        payload: I,
        *args,
        **kwargs,
    ) -> O:
        kwargs["session"] = almanet.get_active_session()
        return await self._remote_execution(payload, *args, **kwargs)

    async def __call__(
        self,
        payload: I,
        *args,
        **kwargs,
    ) -> O:
        return await self._local_execution(payload, *args, **kwargs)


def make_transition[I, O: _state.observable_state](
    source: type[I],
    target: type[O],
    procedure: _transition_procedure,
    label: str | None = None,
    description: str | None = None,
    **extra,
) -> transition_model[I, O]:
    if not callable(procedure):
        raise ValueError("decorated function must be callable")

    if label is None:
        label = procedure.__name__

    if description is None:
        description = procedure.__doc__

    if not issubclass(target, _state.observable_state):
        raise ValueError(f"{label}: `target` must be subclass of `observable_state`")

    return transition_model(
        label=label,
        description=description,
        source=source,
        target=target,
        procedure=procedure,
        **extra,
    )


def transition[I, O: _state.observable_state](
    source: type[I],
    target: type[O],
    **extra,
) -> typing.Callable[[_transition_procedure[I, O]], transition_model[I, O]]:
    def wrap(function):
        return make_transition(source, target, procedure=function, **extra)

    return wrap


def make_observer[I: _state.observable_state, O: _state.observable_state](
    service: almanet.remote_service,
    source: type[I],
    target: type[O],
    **extra,
) -> transition_model[I, O]:
    instance = make_transition(
        source,
        target,
        **extra,
    )

    if not issubclass(source, _state.observable_state):
        raise ValueError(f"{instance.label}: `source` must be subclass of `observable_state`")

    service.add_procedure(
        instance._remote_execution,
        uri=source._uri_,
        payload_model=source,
        return_model=target,
        include_to_api=False,
    )
    return instance


def observe[I: _state.observable_state, O: _state.observable_state](
    service: almanet.remote_service,
    source: type[I],
    target: type[O],
    **extra,
) -> typing.Callable[[_transition_procedure[I, O]], transition_model[I, O]]:
    def wrap(function):
        return make_observer(
            service,
            source=source,
            target=target,
            procedure=function,
            is_observer=True,
            **extra,
        )

    return wrap
