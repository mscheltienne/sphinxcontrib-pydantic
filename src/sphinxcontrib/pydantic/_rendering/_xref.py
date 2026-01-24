"""Cross-reference utilities for RST generation."""

from __future__ import annotations


def create_role_reference(name: str, target: str, role: str = "py:obj") -> str:
    """Create RST role syntax for a cross-reference.

    Parameters
    ----------
    name : str
        The display name for the reference.
    target : str
        The reference target (fully qualified path).
    role : str
        The RST role to use (default: "py:obj").

    Returns
    -------
    str
        RST role syntax like ``:py:obj:`name <target>```.

    Examples
    --------
    >>> create_role_reference("my_field", "module.Class.my_field")
    ':py:obj:`my_field <module.Class.my_field>`'
    >>> create_role_reference("MyClass", "module.MyClass", role="py:class")
    ':py:class:`MyClass <module.MyClass>`'
    """
    return f":{role}:`{name} <{target}>`"
