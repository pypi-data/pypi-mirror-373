from __future__ import annotations

import pytest

from arbolab.exceptions import MissingOptionalDependency


def test_linescale_lazy_import() -> None:
    from arbolab.plugins import linescale as ls

    with pytest.raises(MissingOptionalDependency) as exc:
        getattr(ls, "SomeClass")  # noqa: B009 - force lazy import
    assert "pip install arbolab[linescale]" in str(exc.value)


def test_treemotion_lazy_import() -> None:
    from arbolab.plugins import treemotion as tm

    with pytest.raises(MissingOptionalDependency) as exc:
        getattr(tm, "SomeClass")  # noqa: B009 - force lazy import
    assert "pip install arbolab[treemotion]" in str(exc.value)


def test_treeqinetic_lazy_import() -> None:
    from arbolab.plugins import treeqinetic as ptq

    with pytest.raises(MissingOptionalDependency) as exc:
        getattr(ptq, "SomeClass")  # noqa: B009 - force lazy import
    assert "pip install arbolab[treeqinetic]" in str(exc.value)


def test_treecablecalc_lazy_import() -> None:
    from arbolab.plugins import treecablecalc as tcc

    with pytest.raises(MissingOptionalDependency) as exc:
        getattr(tcc, "SomeClass")  # noqa: B009 - force lazy import
    assert "pip install arbolab[treecablecalc]" in str(exc.value)
