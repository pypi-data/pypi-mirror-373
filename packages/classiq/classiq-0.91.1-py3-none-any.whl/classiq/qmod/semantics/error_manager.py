from collections.abc import Iterator
from contextlib import contextmanager
from typing import Optional

from classiq.interface.ast_node import ASTNode
from classiq.interface.exceptions import CLASSIQ_SLACK_COMMUNITY_LINK
from classiq.interface.source_reference import SourceReference, SourceReferencedError


class ErrorManager:
    def __new__(cls) -> "ErrorManager":
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_instantiated"):
            return
        self._instantiated = True
        self._errors: list[SourceReferencedError] = []
        self._warnings: list[SourceReferencedError] = []
        self._current_nodes_stack: list[ASTNode] = []
        self._call_stack: list[str] = []
        self._ignore_errors: bool = False

    @property
    def _current_source_ref(self) -> Optional[SourceReference]:
        if self._current_nodes_stack:
            return self._current_nodes_stack[-1].source_ref
        return None

    @contextmanager
    def ignore_errors_context(self) -> Iterator[None]:
        previous = self._ignore_errors
        self._ignore_errors = True
        try:
            yield
        finally:
            self._ignore_errors = previous

    @property
    def annotated_errors(self) -> list[str]:
        return [str(error) for error in self._errors]

    @property
    def annotated_warnings(self) -> list[str]:
        return [str(error) for error in self._warnings]

    def add_error(
        self,
        error: str,
        *,
        source_ref: Optional[SourceReference] = None,
        function: Optional[str] = None,
        warning: bool = False,
    ) -> None:
        if self._ignore_errors:
            return

        source_ref_error = SourceReferencedError(
            error=error.replace(CLASSIQ_SLACK_COMMUNITY_LINK, ""),
            source_ref=(
                source_ref if source_ref is not None else self._current_source_ref
            ),
            function=(function if function is not None else self.current_function),
        )
        if warning:
            self._warnings.append(source_ref_error)
        else:
            self._errors.append(source_ref_error)

    def get_errors(self) -> list[SourceReferencedError]:
        return self._errors

    def get_warnings(self) -> list[SourceReferencedError]:
        return self._warnings

    def clear(self) -> None:
        self.clear_errors()
        self.clear_warnings()

    def clear_errors(self) -> None:
        self._current_nodes_stack = []
        self._errors = []

    def clear_warnings(self) -> None:
        self._warnings = []

    def has_errors(self) -> bool:
        return len(self._errors) > 0

    def has_warnings(self) -> bool:
        return len(self._warnings) > 0

    def report_errors(
        self, error_type: type[Exception], mask: Optional[list[int]] = None
    ) -> None:
        if self.has_errors():
            errors = (
                self.annotated_errors
                if mask is None
                else [self.annotated_errors[idx] for idx in mask]
            )
            self.clear_errors()
            raise error_type("\n\t" + "\n\t".join(errors))

    @property
    def current_function(self) -> Optional[str]:
        return self._call_stack[-1] if self._call_stack else None

    @contextmanager
    def node_context(self, node: ASTNode) -> Iterator[None]:
        self._current_nodes_stack.append(node)
        yield
        self._current_nodes_stack.pop()

    @contextmanager
    def call(self, func_name: str) -> Iterator[None]:
        self._call_stack.append(func_name)
        yield
        self._call_stack.pop()
