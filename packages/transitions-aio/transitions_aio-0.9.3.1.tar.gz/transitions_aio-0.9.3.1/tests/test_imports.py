def test_imports() -> None:
    from transitions_aio import Machine
    from transitions_aio.extensions import GraphMachine, HierarchicalGraphMachine, HierarchicalMachine, LockedMachine
    from transitions_aio.extensions import MachineFactory, LockedHierarchicalGraphMachine, LockedHierarchicalMachine
    from transitions_aio.extensions import LockedGraphMachine
    try:
        # only available for Python 3
        from transitions_aio.extensions import AsyncMachine, HierarchicalAsyncMachine
        from transitions_aio.extensions import AsyncGraphMachine, HierarchicalAsyncGraphMachine
    except (ImportError, SyntaxError):  # pragma: no cover
        pass
