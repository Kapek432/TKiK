"""Główny transformer semantyczny - produkuje strukturę pomocniczą dla generatora."""

from __future__ import annotations

from typing import Any, Optional

from lark import Token, Transformer, v_args

from src.config import Config
from src.loaders import load_json_file
from src.semantic.shape_inference import (
    _get_arg_value,
    infer_conv2d,
    infer_dense,
    infer_flatten,
    infer_maxpool2d,
)
from src.semantic.symbol_table import SymbolTable
from src.semantic.validators import (
    ensure_identifier_defined,
    validate_config_block,
    validate_config_item,
    validate_dataset_source,
    validate_metric_against_output,
)


class NeuroLangCompiler(Transformer):
    """
    Główny transformer - waliduje semantykę i buduje strukturę dla generatora.
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Tworzy instancję kompilatora.

        Argumenty:
            config (Optional[Config]): Konfiguracja projektu.
        """
        super().__init__()
        self.config = config or Config.load()
        self.components = load_json_file(self.config.resource(self.config.paths.components_file))
        self.datasets = load_json_file(self.config.resource(self.config.paths.datasets_file))
        self.symbols = SymbolTable()
        self.parsed_networks: dict[str, dict[str, Any]] = {}
        self.parsed_config: dict[str, Any] = {
            "configs": {},
            "data_sources": {},
            "network_bindings": {},
        }

    @property
    def variables(self) -> dict[str, Any]:
        """
        Skrót do tablicy zmiennych w tabeli symboli.

        Zwraca:
            dict[str, Any]: Tablica zmiennych
        """
        return self.symbols.variables

    @property
    def defined_networks(self) -> set[str]:
        """
        Zbiór nazw zdefiniowanych sieci.

        Zwraca:
            set[str]: Zbiór nazw zdefiniowanych sieci
        """
        return self.symbols.defined_networks

    @property
    def defined_configs(self) -> set[str]:
        """
        Zbiór nazw zdefiniowanych konfiguracji.

        Zwraca:
            set[str]: Zbiór nazw zdefiniowanych konfiguracji
        """
        return self.symbols.defined_configs

    @property
    def defined_data(self) -> set[str]:
        """
        Zbiór aliasów zdefiniowanych źródeł danych.

        Zwraca:
            set[str]: Zbiór aliasów zdefiniowanych źródeł danych
        """
        return self.symbols.defined_data

    @property
    def parsed_network(self) -> dict[str, Any]:
        """
        Zwraca ostatnio przetworzoną sieć.

        Zwraca:
            dict[str, Any]: Ostatnio przetworzony rekord sieci
        """
        if not self.parsed_networks:
            return {"name": "", "layers": [], "last_output": None, "first_input": None}

        for instr in self.parsed_config.get("instructions", []):
            instr_net = instr.get("network")
            if isinstance(instr_net, str) and instr_net in self.parsed_networks:
                return self.parsed_networks[instr_net]

        return next(reversed(self.parsed_networks.values()))

    @v_args(inline=True)
    def NUMBER(self, token: Token) -> float | int:
        """
        Konwertuje token liczbowy na typ Pythona.

        Argumenty:
            token (Token): Token liczbowy

        Zwraca:
            float | int: Konwertowana wartość
        """
        text = str(token)
        return float(text) if "." in text else int(text)

    @v_args(inline=True)
    def CNAME(self, token: Token) -> str:
        """
        Konwertuje token identyfikatora na napis.

        Argumenty:
            token (Token): Token identyfikatora

        Zwraca:
            str: Konwertowana wartość
        """
        return str(token)

    @v_args(inline=True)
    def ESCAPED_STRING(self, token: Token) -> str:
        """
        Usuwa cudzysłowy z literalu napisu.

        Argumenty:
            token (Token): Token napisu

        Zwraca:
            str: Konwertowana wartość
        """
        return str(token)[1:-1]

    def true_val(self, args: Any) -> bool:
        """
        Mapuje słowo kluczowe true na logiczne True.

        Argumenty:
            args (Any): Argumenty

        Zwraca:
            bool: Mapowanie słowa kluczowego true na logiczne True
        """
        return True

    def false_val(self, args: Any) -> bool:
        """
        Mapuje słowo kluczowe false na logiczne False.

        Argumenty:
            args (Any): Argumenty

        Zwraca:
            bool: Mapowanie słowa kluczowego false na logiczne False
        """
        return False

    def start(self, args: list[Any]) -> None:
        """Zbiera instrukcje wyższego rzędu (``cmd_type``) do listy globalnej."""
        for instr in args:
            if instr is not None and isinstance(instr, dict) and "cmd_type" in instr:
                self.parsed_config.setdefault("instructions", []).append(instr)

    def instruction(self, args: list[Any]) -> Any:
        """
        Przekazuje wynik pojedynczej instrukcji w górę drzewa.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            Any: Wynik pojedynczej instrukcji
        """
        return args[0] if args else None

    @v_args(inline=True, meta=True)
    def var_decl(self, meta: Any, name_token: Token, value: Any) -> dict[str, Any]:
        """
        Rejestruje nową zmienną w tablicy symboli.

        Argumenty:
            meta (Any): Metadane
            name_token (Token): Token nazwy zmiennej
            value (Any): Wartość zmiennej
        """
        name = str(name_token)
        if name in self.symbols.variables:
            raise ValueError(
                f"SEMANTIC ERROR [L: {meta.line}, C: {meta.column}]: "
                f"Variable '{name}' is already declared."
            )
        self.symbols.variables[name] = value
        return {"cmd_type": "var_decl", "name": name, "value": value}

    @v_args(inline=True, meta=True)
    def var_assign(self, meta: Any, name_token: Token, value: Any) -> dict[str, Any]:
        """
        Aktualizuje wartość istniejącej zmiennej.

        Argumenty:
            meta (Any): Metadane
            name_token (Token): Token nazwy zmiennej
            value (Any): Wartość zmiennej
        """
        name = str(name_token)
        if name not in self.symbols.variables:
            raise ValueError(
                f"SEMANTIC ERROR [L: {meta.line}, C: {meta.column}]: "
                f"Attempt to assign to undefined variable '{name}'."
            )
        self.symbols.variables[name] = value
        return {"cmd_type": "var_assign", "name": name, "value": value}

    @v_args(inline=True, meta=True)
    def call(
        self,
        meta: Any,
        name_token: Token,
        provided_args: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        """
        Przetwarza wywołanie Nazwa(...) i zapamiętuje lokalizację w źródle.

        Argumenty:
            meta (Any): Metadane
            name_token (Token): Token nazwy wywołania
            provided_args (Optional[list[dict[str, Any]]]): Lista argumentów
        """
        return {
            "name": str(name_token),
            "args": provided_args if provided_args is not None else [],
            "line": meta.line,
            "col": meta.column,
        }

    def list_expr(self, args: list[Any]) -> list[Any]:
        """
        Konwertuje listę wyrażeń na listę Pythona.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            list[Any]: Konwertowana lista
        """
        return [arg for arg in args if arg is not None]

    def config_item(self, args: list[Any]) -> dict[str, Any]:
        """
        Konwertuje pozycję klucz: wartość na słownik jednoelementowy.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Konwertowany słownik
        """
        return {str(args[0]): args[1]}

    @v_args(inline=True)
    def layer_decl(self, call_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Waliduje warstwę - pełne wnioskowanie wymiarów dzieje się w network_block.

        Argumenty:
            call_dict (dict[str, Any]): Słownik wywołania warstwy

        Zwraca:
            dict[str, Any]: Walidowany słownik warstwy
        """
        layer_name = call_dict.get("name")
        line = call_dict.get("line", "?")
        col = call_dict.get("col", "?")

        if layer_name not in self.components:
            raise ValueError(
                f"SEMANTIC ERROR [L: {line}, C: {col}]: Unknown component '{layer_name}'."
            )

        provided_args = call_dict.get("args", [])

        if layer_name == "Dropout":
            p = _get_arg_value(provided_args, 0, "p", float(self.config.model.default_dropout_p))
            if not (0 <= p <= 1):
                raise ValueError(
                    f"SEMANTIC ERROR [L: {line}, C: {col}]: Parameter 'p' in Dropout "
                    f"layer must be in range [0, 1], got {p}."
                )

        return call_dict

    def _apply_shape_inference(self, ctx: Any, layer: dict[str, Any]) -> None:
        """
        Uruchamia wnioskowanie wymiarów dla pojedynczej warstwy.

        Argumenty:
            ctx (Any): Kontekst sieci
            layer (dict[str, Any]): Słownik warstwy
        """
        layer_name = layer.get("name")
        provided_args = layer.get("args", [])
        line = layer.get("line", "?")
        col = layer.get("col", "?")

        if layer_name == "Dense":
            infer_dense(ctx, provided_args, line, col)
        elif layer_name == "Conv2D":
            infer_conv2d(ctx, provided_args, line, col, self.config)
        elif layer_name == "MaxPool2D":
            infer_maxpool2d(ctx, provided_args, line, col)
        elif layer_name == "Flatten":
            infer_flatten(ctx)

    @v_args(inline=True, meta=True)
    def factor(self, meta: Any, *args: Any) -> Any:
        """
        Oblicza wartość factor - liczba, zmienna lub wyrażenie w nawiasach.

        Argumenty:
            meta (Any): Metadane
            args (Any): Lista argumentów

        Zwraca:
            Any: Obliczona wartość factor
        """
        if len(args) == 1:
            value = args[0]
            if isinstance(value, str):
                if value == "true":
                    return True
                if value == "false":
                    return False
                if value not in self.symbols.variables:
                    raise ValueError(
                        f"SEMANTIC ERROR [L: {meta.line}, C: {meta.column}]: "
                        f"Use of undefined variable '{value}'."
                    )
                return self.symbols.variables[value]
            return value
        return args[1]

    def term(self, args: list[Any]) -> float | int:
        """
        Oblicza wynik operatorów multiplikatywnych.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            float | int: Obliczona wartość
        """
        result = args[0]
        for i in range(1, len(args), 2):
            op, operand = str(args[i]), args[i + 1]
            if op == "*":
                result *= operand
            elif op == "/":
                if operand == 0:
                    raise ValueError("SEMANTIC ERROR: Division by zero!")
                result /= operand
            elif op == "//":
                if operand == 0:
                    raise ValueError("SEMANTIC ERROR: Division by zero!")
                result //= operand
        return result

    def math_expr(self, args: list[Any]) -> float | int:
        """
        Oblicza wynik operatorów addytywnych.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            float | int: Obliczona wartość
        """
        result = args[0]
        for i in range(1, len(args), 2):
            op, operand = str(args[i]), args[i + 1]
            if op == "+":
                result += operand
            elif op == "-":
                result -= operand
        return result

    def arg(self, args: list[Any]) -> dict[str, Any]:
        """
        Konwertuje argument na słownik pozycyjny lub kluczowy.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Konwertowany słownik
        """
        if len(args) == 1:
            return {"type": "positional", "value": args[0]}
        return {"type": "keyword", "name": str(args[0]), "value": args[1]}

    def arguments(self, args: list[Any]) -> list[Any]:
        """
        Zwraca listę argumentów wywołania.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            list[Any]: Lista argumentów
        """
        return args

    def config_value(self, args: list[Any]) -> Any:
        """
        Zwraca wartość pozycji konfiguracyjnej.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            Any: Wartość pozycji konfiguracyjnej
        """
        return args[0]

    def arg_value(self, args: list[Any]) -> Any:
        """
        Zwraca wartość argumentu wywołania.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            Any: Wartość argumentu wywołania
        """
        return args[0]

    def net_statement(self, args: list[Any]) -> Any:
        """
        Przekazuje pojedynczą instrukcję wewnątrz network.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            Any: Pojedyncza instrukcja wewnątrz network
        """
        return args[0]

    def repeat_block(self, args: list[Any]) -> list[dict[str, Any]]:
        """
        Rozwija pętlę repeat w płaski ciąg instrukcji.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            list[dict[str, Any]]: Płaski ciąg instrukcji
        """
        count_node = args[0]
        if isinstance(count_node, str):
            if count_node not in self.symbols.variables:
                raise ValueError(
                    f"SEMANTIC ERROR: Use of undefined variable '{count_node}' in 'repeat' block."
                )
            iters = int(self.symbols.variables[count_node])
        else:
            iters = int(count_node)
        if iters <= 0:
            raise ValueError(
                "SEMANTIC ERROR: Number of repetitions for 'repeat' loop must be positive."
            )
        statements = args[1:]
        result: list[dict[str, Any]] = []
        for _ in range(iters):
            for stmt in statements:
                if stmt is None:
                    continue
                if isinstance(stmt, list):
                    result.extend(stmt)
                else:
                    result.append(stmt)
        return result

    def network_block(self, args: list[Any]) -> None:
        """
        Finalizuje blok network - zbiera warstwy i uruchamia shape inference.

        Argumenty:
            args (list[Any]): Lista argumentów
        """
        name = args[0]
        idx = 1
        if idx < len(args) and isinstance(args[idx], list):
            idx += 1

        statements = args[idx:]
        layers: list[dict[str, Any]] = []
        for stmt in statements:
            if stmt is None:
                continue
            if isinstance(stmt, list):
                layers.extend(stmt)
            else:
                layers.append(stmt)

        ctx = self.symbols.context_for(name)
        self.symbols.enter_network(name)
        for layer in layers:
            self._apply_shape_inference(ctx, layer)
        self.symbols.leave_network()

        self.parsed_networks[name] = {
            "name": name,
            "layers": layers,
            "last_output": ctx.last_output_shape,
            "first_input": ctx.first_input_shape,
        }
        self.parsed_config.setdefault("networks", {})[name] = self.parsed_networks[name]
        self.symbols.defined_networks.add(name)

    def data_block(self, args: list[Any]) -> None:
        """
        Rozpoznaje źródło danych i rejestruje jego alias.

        Argumenty:
            args (list[Any]): Lista argumentów
        """
        source = args[0]
        remaining = args[1:]
        alias: str = source
        config_items: list[Any] = []
        for item in remaining:
            if isinstance(item, dict):
                config_items.append(item)
            elif isinstance(item, str):
                alias = item

        validate_dataset_source(source, set(self.datasets.keys()))

        params: dict[str, Any] = {}
        for item in config_items:
            params.update(item)

        self.parsed_config.setdefault("data_sources", {})[alias] = {
            "source": source,
            "alias": alias,
            "params": params,
        }
        self.parsed_config["data"] = self.parsed_config["data_sources"][alias]
        self.symbols.defined_data.add(alias)

    @v_args(inline=True, meta=True)
    def config_block(self, meta: Any, name: str, *items: dict[str, Any]) -> None:
        """
        Przetwarza blok train_config.

        Argumenty:
            meta (Any): Metadane
            name (str): Nazwa bloku
            items (dict[str, Any]): Lista słowników
        """
        cfg: dict[str, Any] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            key = next(iter(item.keys()))
            if key in cfg:
                raise ValueError(
                    f"SEMANTIC ERROR [L: {meta.line}, C: {meta.column}]: "
                    f"Parameter '{key}' is defined multiple times in block '{name}'."
                )
            validate_config_item(key, item[key], meta.line, meta.column)
            cfg.update(item)
        validate_config_block(cfg, name, meta.line, meta.column, config=self.config)
        self.parsed_config.setdefault("configs", {})[name] = {"name": name, "params": cfg}
        self.parsed_config["training"] = {"name": name, "params": cfg}
        self.symbols.defined_configs.add(name)

    @v_args(inline=True)
    def load_model_cmd(self, name: str, path: str) -> dict[str, Any]:
        """
        Przetwarza komendę load_model.

        Argumenty:
            name (str): Nazwa sieci
            path (str): Ścieżka do modelu

        Zwraca:
            dict[str, Any]: Słownik komendy load_model
        """
        return {"cmd_type": "load", "network": name, "filepath": path}

    @v_args(inline=True, meta=True)
    def train_cmd(
        self,
        meta: Any,
        net: str,
        cfg: str,
        data: str,
        device: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Waliduje komendę train i sprawdza zgodność metryk z wyjściem sieci.

        Argumenty:
            meta (Any): Metadane
            net (str): Nazwa sieci
            cfg (str): Nazwa konfiguracji
            data (str): Nazwa danych
            device (Optional[str]): Typ urządzenia

        Zwraca:
            dict[str, Any]: Walidowany słownik komendy train
        """
        ensure_identifier_defined("network", net, self.symbols, meta.line, meta.column)
        ensure_identifier_defined("config", cfg, self.symbols, meta.line, meta.column)
        ensure_identifier_defined("data", data, self.symbols, meta.line, meta.column)

        network_entry = self.parsed_networks.get(net, {})
        last_out = network_entry.get("last_output")
        configs = self.parsed_config.get("configs", {})
        training_params = configs.get(cfg, self.parsed_config.get("training", {})).get("params", {})
        task = training_params.get("task", "multiclass")
        metrics = training_params.get("metrics", [])
        for metric in metrics:
            validate_metric_against_output(
                metric,
                last_out,
                _get_arg_value,
                meta.line,
                meta.column,
                task=task,
                config=self.config,
            )

        self.parsed_config.setdefault("network_bindings", {})[net] = {
            "config": cfg,
            "data": data,
        }

        return {
            "cmd_type": "train",
            "network": net,
            "config": cfg,
            "data": data,
            "device": device,
        }

    @v_args(inline=True)
    def save_cmd(self, net: str, path: str) -> dict[str, str]:
        """
        Przetwarza komendę save.

        Argumenty:
            net (str): Nazwa sieci
            path (str): Ścieżka do modelu

        Zwraca:
            dict[str, Any]: Słownik komendy save
        """
        return {"cmd_type": "save", "network": net, "filepath": path}

    @v_args(inline=True, meta=True)
    def evaluate_cmd(self, meta: Any, net: str, data: str) -> dict[str, Any]:
        """
        Przetwarza komendę evaluate.

        Argumenty:
            meta (Any): Metadane
            net (str): Nazwa sieci
            data (str): Nazwa danych

        Zwraca:
            dict[str, Any]: Słownik komendy evaluate
        """
        ensure_identifier_defined("network", net, self.symbols, meta.line, meta.column)
        ensure_identifier_defined("data", data, self.symbols, meta.line, meta.column)
        bound_config = self.parsed_config.get("network_bindings", {}).get(net, {}).get("config")
        return {
            "cmd_type": "evaluate",
            "network": net,
            "data": data,
            "config": bound_config,
        }

    def print_cmd(self, args: list[Any]) -> dict[str, Any]:
        """
        Przekazuje wynik instrukcji print w górę.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Wynik instrukcji print
        """
        return args[0]

    def print_string(self, args: list[Any]) -> dict[str, str]:
        """
        Wariant print "tekst".

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy print
        """
        return {"cmd_type": "print", "subtype": "string", "value": args[0]}

    @v_args(inline=True, meta=True)
    def print_summary(self, meta: Any, name: str) -> dict[str, str]:
        """
        Wariant print summary Net.

        Argumenty:
            meta (Any): Metadane
            name (str): Nazwa sieci

        Zwraca:
            dict[str, Any]: Słownik komendy print
        """
        ensure_identifier_defined("network", name, self.symbols, meta.line, meta.column)
        return {"cmd_type": "print", "subtype": "summary", "network": name}

    def print_expr(self, args: list[Any]) -> dict[str, Any]:
        """
        Wariant print <expr>.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy print
        """
        return {"cmd_type": "print", "subtype": "expr", "value": args[0]}

    @v_args(inline=True, meta=True)
    def export_cmd(self, meta: Any, net: str, path: str) -> dict[str, str]:
        """
        Przetwarza komendę export.

        Argumenty:
            meta (Any): Metadane
            net (str): Nazwa sieci
            path (str): Ścieżka do modelu

        Zwraca:
            dict[str, Any]: Słownik komendy export
        """
        ensure_identifier_defined("network", net, self.symbols, meta.line, meta.column)
        return {"cmd_type": "export", "network": net, "filepath": path}

    @v_args(inline=True, meta=True)
    def predict_cmd(self, meta: Any, net: str, source: str) -> dict[str, Any]:
        """
        Przetwarza komendę predict.

        Argumenty:
            meta (Any): Metadane
            net (str): Nazwa sieci
            source (str): Źródło danych

        Zwraca:
            dict[str, Any]: Słownik komendy predict
        """
        ensure_identifier_defined("network", net, self.symbols, meta.line, meta.column)
        is_path = isinstance(source, str) and source.lower().endswith(".csv")
        if not is_path and source not in self.symbols.defined_data:
            raise ValueError(
                f"SEMANTIC ERROR [L: {meta.line}, C: {meta.column}]: "
                f"Attempt to predict on undefined data source '{source}'."
            )
        bound_config = self.parsed_config.get("network_bindings", {}).get(net, {}).get("config")
        return {
            "cmd_type": "predict",
            "network": net,
            "source": source,
            "is_path": is_path,
            "config": bound_config,
        }

    @v_args(inline=True, meta=True)
    def summary_cmd(self, meta: Any, net: str) -> dict[str, str]:
        """
        Przetwarza komendę summary.

        Argumenty:
            meta (Any): Metadane
            net (str): Nazwa sieci

        Zwraca:
            dict[str, Any]: Słownik komendy summary
        """
        ensure_identifier_defined("network", net, self.symbols, meta.line, meta.column)
        return {"cmd_type": "summary", "network": net}

    def if_block(self, args: list[Any]) -> dict[str, Any]:
        """
        Przetwarza blok warunkowy if.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy if_block
        """
        condition = args[0]
        body: list[Any] = []
        elif_clauses: list[Any] = []
        else_body: Optional[list[Any]] = None

        for child in args[1:]:
            if isinstance(child, dict) and child.get("_clause_type") == "elif":
                elif_clauses.append(child)
            elif isinstance(child, dict) and child.get("_clause_type") == "else":
                else_body = child.get("body", [])
            elif child is not None:
                body.append(child)

        return {
            "cmd_type": "if_block",
            "condition": condition,
            "body": body,
            "elif_clauses": elif_clauses,
            "else_body": else_body,
        }

    def elif_clause(self, args: list[Any]) -> dict[str, Any]:
        """
        Przetwarza klauzule else if.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy elif_clause
        """
        return {
            "_clause_type": "elif",
            "condition": args[0],
            "body": list(args[1:]),
        }

    def else_clause(self, args: list[Any]) -> dict[str, Any]:
        """
        Przetwarza klauzule else.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy else_clause
        """
        return {"_clause_type": "else", "body": list(args)}

    def condition(self, args: list[Any]) -> dict[str, Any]:
        """
        Przepuszcza wierzchołek 'condition' - cały warunek składany niżej.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy condition
        """
        return args[0]

    def atom_condition(self, args: list[Any]) -> dict[str, Any]:
        """
        Przekazuje atomowy warunek (jedyne dziecko) w górę drzewa.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy atom_condition
        """
        return args[0]

    def not_condition(self, args: list[Any]) -> dict[str, Any]:
        """
        Fallback gdy 'not_condition' zwija się do samego atomu.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy not_condition
        """
        return args[0]

    def cond_not(self, args: list[Any]) -> dict[str, Any]:
        """
        Tworzy warunek negacji: not <cond>.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy cond_not
        """
        return {"type": "not", "operand": args[0]}

    def cond_group(self, args: list[Any]) -> dict[str, Any]:
        """Przepuszcza warunek z nawiasami (grupowanie).

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy cond_group
        """
        return args[0]

    def and_condition(self, args: list[Any]) -> dict[str, Any]:
        """Łączy wiele warunków operatorem 'and'.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy and_condition
        """
        if len(args) == 1:
            return args[0]
        return {"type": "and", "operands": list(args)}

    def or_condition(self, args: list[Any]) -> dict[str, Any]:
        """Łączy wiele warunków operatorem 'or'.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy or_condition
        """
        if len(args) == 1:
            return args[0]
        return {"type": "or", "operands": list(args)}

    def cond_gpu(self, args: list[Any]) -> dict[str, str]:
        """Predykat 'gpu_available'."""
        return {"type": "gpu_available"}

    def cond_mps(self, args: list[Any]) -> dict[str, str]:
        """Predykat 'mps_available'."""
        return {"type": "mps_available"}

    def cond_has_data(self, args: list[Any]) -> dict[str, str]:
        """Predykat 'has_data'."""
        return {"type": "has_data"}

    @v_args(inline=True)
    def cond_bool(self, value: bool) -> dict[str, Any]:
        """
        Literał logiczny 'true' / 'false'.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy cond_bool
        """
        return {"type": "bool", "value": bool(value)}

    def cond_math(self, args: list[Any]) -> dict[str, Any]:
        """
        Warunek bez operatora porównania - wyrażenie traktowane jako truthy.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy cond_math
        """
        value = args[0]
        return {"type": "truthy", "value": value}

    def cond_compare(self, args: list[Any]) -> dict[str, Any]:
        """
        Warunek porównania dwóch wyrażeń arytmetycznych.

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            dict[str, Any]: Słownik komendy cond_compare
        """
        left, op_token, right = args
        op = str(op_token)
        if op not in {"==", "!=", "<", "<=", ">", ">="}:
            raise ValueError(
                f"SEMANTIC ERROR: Unsupported comparison operator '{op}'."
            )
        for side in (left, right):
            if not isinstance(side, (int, float, bool)):
                raise ValueError(
                    "SEMANTIC ERROR: Comparison operands must be numeric "
                    f"(got {type(side).__name__})."
                )
        return {
            "type": "compare",
            "op": op,
            "left": left,
            "right": right,
        }

    def device_type(self, args: list[Any]) -> str:
        """
        Zwraca wybrany typ urządzenia (cpu/cuda/mps).

        Argumenty:
            args (list[Any]): Lista argumentów

        Zwraca:
            str: Wybrany typ urządzenia
        """
        return str(args[0])
