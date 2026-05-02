"""Wstępny skaner drzewa AST - wydobywa zmienne i wymiary sieci."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from lark import Token, Tree, Visitor

if TYPE_CHECKING:
    from src.semantic.transformer import NeuroLangCompiler


_BIN_OPS = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: None if b == 0 else a / b,
    "//": lambda a, b: None if b == 0 else a // b,
}


class NeuroLangVisitor(Visitor):
    """
    Pierwszy przebieg analizy - zbiera metadane potrzebne transformerowi.

    Dzięki niemu transformer (działający od dołu do góry) zna wartości zmiennych
    oraz wymiar wejściowy każdej sieci jeszcze przed zejściem do warstw.
    """

    def __init__(self, compiler: "NeuroLangCompiler") -> None:
        """
        Tworzy instancję kompilatora.

        Argumenty:
            compiler (NeuroLangCompiler): Instancja kompilatora, której stan jest
                aktualizowany w trakcie przebiegu.
        """
        self.compiler = compiler
        self.temp_vars: dict[str, Any] = {}

    def var_decl(self, tree: Tree) -> None:
        """
        Wstępnie zapisuje wartość deklaracji let, jeśli można ją policzyć.

        Argumenty:
            tree (Tree): Drzewo AST deklaracji let
        """
        name = str(tree.children[0])
        value = self._evaluate(tree.children[1])
        if value is not None:
            self.temp_vars[name] = value

    def network_block(self, tree: Tree) -> None:
        """
        Wyciąga wymiary wejściowe z nagłówka network Nazwa(...).

        Argumenty:
            tree (Tree): Drzewo AST bloku network
        """
        name = str(tree.children[0])
        args_node: Optional[Tree] = None
        for child in tree.children:
            if hasattr(child, "data") and child.data == "arguments":
                args_node = child
                break

        ctx = self.compiler.symbols.context_for(name)
        if args_node is None:
            return

        shape: list[Any] = []
        for arg_child in args_node.children:
            value = self._evaluate(arg_child)
            if value is not None:
                shape.append(value)

        if len(shape) == 1:
            ctx.first_input_shape = (1, int(shape[0]))
        elif len(shape) == 3:
            ctx.first_input_shape = (
                1,
                int(shape[0]),
                int(shape[1]),
                int(shape[2]),
            )
            ctx.last_output_shape = (
                int(shape[0]),
                int(shape[1]),
                int(shape[2]),
            )

    def _evaluate(self, node: Any) -> Any:
        """
        Rekurencyjnie liczy wartość węzła wyrażenia matematycznego.

        Argumenty:
            node (Any): Węzeł drzewa składniowego

        Zwraca:
            Any: Wynik ewaluacji węzła
        """
        if isinstance(node, Token):
            if node.type == "NUMBER":
                text = str(node)
                return float(text) if "." in text else int(text)
            if node.type == "CNAME":
                return self.temp_vars.get(str(node))
            return None

        if not isinstance(node, Tree):
            return None

        if node.data == "factor":
            return self._eval_factor(node)
        if node.data == "term":
            return self._eval_binary(node)
        if node.data == "math_expr":
            return self._eval_binary(node)
        if node.data == "arg":
            return self._evaluate(node.children[-1])
        if node.data == "arg_value":
            return self._evaluate(node.children[0])

        for child in node.children:
            result = self._evaluate(child)
            if result is not None:
                return result
        return None

    def _eval_factor(self, tree: Tree) -> Any:
        """
        Ocena węzła factor - liczba, zmienna lub wyrażenie w nawiasach.

        Argumenty:
            tree (Tree): Drzewo AST węzła factor

        Zwraca:
            Any: Obliczona wartość węzła factor
        """
        if len(tree.children) == 1:
            return self._evaluate(tree.children[0])
        return self._evaluate(tree.children[0])

    def _eval_binary(self, tree: Tree) -> Any:
        """
        Ocena węzła term lub math_expr z operatorami binarnymi.

        Argumenty:
            tree (Tree): Drzewo AST węzła term lub math_expr

        Zwraca:
            Any: Obliczona wartość węzła term lub math_expr
        """
        children = list(tree.children)
        if not children:
            return None
        result = self._evaluate(children[0])
        if result is None:
            return None
        idx = 1
        while idx + 1 < len(children):
            op_token = children[idx]
            operand = self._evaluate(children[idx + 1])
            if operand is None:
                return None
            op = str(op_token)
            if op not in _BIN_OPS:
                return None
            computed = _BIN_OPS[op](result, operand)
            if computed is None:
                return None
            result = computed
            idx += 2
        return result
