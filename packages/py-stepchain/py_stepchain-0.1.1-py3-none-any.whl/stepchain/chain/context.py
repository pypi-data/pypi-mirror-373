from __future__ import annotations
from typing import Any, Callable, Mapping, Tuple, NoReturn


def get_dotted(root: Any, path: str) -> Any:
    """
    Resolve a dotted path against a mapping/object.

    Examples:
      >>> get_dotted({"a": {"b": 1}}, "a.b")
      1
      >>> class X: pass
      >>> x = X(); x.v = 3
      >>> get_dotted({"x": x}, "x.v")
      3
    """

    cur = root
    for p in path.split("."):
        if cur is None:
            return None
        if isinstance(cur, Mapping):
            cur = cur.get(p, None)
        else:
            cur = getattr(cur, p, None)
    return cur


def _compile_dotted(parts: Tuple[str, ...], strict: bool) -> Callable[[Mapping[str, Any]], Any]:
    head, tail = parts[0], parts[1:]

    def resolver(ctx: Mapping[str, Any]) -> Any:
        cur = ctx.get(head, None)
        for p in tail:
            if cur is None:
                if strict:
                    raise LookupError(f"Unresolved reference: {'.'.join(parts)}")
                return None
            if isinstance(cur, Mapping):
                cur = cur.get(p, None)
            else:
                cur = getattr(cur, p, None)
        if strict and cur is None:
            raise LookupError(f"Unresolved reference: {'.'.join(parts)}")
        return cur

    return resolver


def _raise_lookup(key: str) -> NoReturn:
    raise LookupError(f"Unresolved reference: {key}")


def _const(value: Any) -> Callable[[Mapping[str, Any]], Any]:
    def resolver(_ctx: Mapping[str, Any]) -> Any:
        return value

    return resolver


def compile_ref(ref: Any, strict: bool = False) -> Callable[[Mapping[str, Any]], Any]:
    """
    Compile a reference spec into a resolver callable.

    - Literals return as-is.
    - `"key"` fetches from context.
    - `"key.inner.attr"` traverses mappings/attributes.
    - In `strict` mode, unresolved references raise `LookupError`.

    Returns:
      A function `(ctx) -> value` used at runtime to fetch the argument value.
    """

    if not isinstance(ref, str):
        return _const(ref)
    if "." in ref:
        return _compile_dotted(tuple(ref.split(".")), strict)
    key = ref
    if strict:

        def resolver(ctx: Mapping[str, Any]) -> Any:
            if key in ctx:
                return ctx[key]
            _raise_lookup(key)

        return resolver
    return lambda ctx: ctx.get(key, None)


def compile_kwargs(
    kwargs: Mapping[str, Any], strict: bool = False
) -> Mapping[str, Callable[[Mapping[str, Any]], Any]]:
    """Vectorized `compile_ref` for kwargs specs."""

    return {k: compile_ref(v, strict) for k, v in kwargs.items()}
