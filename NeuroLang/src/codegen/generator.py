"""Orkiestrator generatora kodu PyTorch."""

from typing import Any, Optional

from src.codegen.conditions import condition_code
from src.codegen.control_flow import (
    generate_export,
    generate_load_weights,
    generate_print_commands,
    generate_save_weights,
    generate_summary,
    generate_variable,
)
from src.codegen.data import generate_data_loader
from src.codegen.device import generate_device_config, resolve_train_device
from src.codegen.evaluation import generate_evaluate_loop, generate_predict
from src.codegen.imports import generate_imports
from src.codegen.indent import CodeBuffer
from src.codegen.model import generate_model_class, generate_model_instantiations
from src.codegen.training import generate_training_loop
from src.config import Config


class PyTorchGenerator:
    """
    Komponuje fragmenty kodu PyTorch na podstawie słowników analizy semantycznej.
    """

    def __init__(
        self,
        parsed_network: dict[str, Any],
        parsed_config: dict[str, Any],
        components: dict[str, Any],
        visualize: bool = False,
        config: Optional[Config] = None,
    ) -> None:
        """
        Tworzy instancję generatora kodu PyTorch.

        Argumenty:
            parsed_network (dict[str, Any]): Opis sieci
            parsed_config (dict[str, Any]): Słownik konfiguracji (data/training/instructions)
            components (dict[str, Any]): Mapowanie komponentów NeuroLang -> PyTorch
            visualize (bool): Czy dołączyć kod wizualizacji
            config (Optional[Config]): Konfiguracja projektu
        """
        self.network = parsed_network or {}
        self.config_dict = parsed_config or {}
        self.components = components or {}
        self.visualize = visualize
        self.config = config or Config.load()
        self.buffer = CodeBuffer()
        self.data_alias: Optional[str] = None
        self.networks: dict[str, dict[str, Any]] = self.config_dict.get("networks", {})
        self._loaded_data_aliases: set[str] = set()

    @property
    def code(self) -> list[str]:
        """
        Widok linii kodu.

        Zwraca:
            list[str]: Lista linii kodu
        """
        return self.buffer.lines

    def add_line(self, line: str, indent: int = 0) -> None:
        """
        Dodaje linię do buforu.
        
        Argumenty:
            line (str): Linia kodu
            indent (int): Poziom wcięcia
        """
        self.buffer.add(line, indent)

    def generate(self) -> str:
        """
        Buduje kompletny skrypt PyTorch i zwraca go jako tekst.

        Zwraca:
            str: Kompletny skrypt PyTorch
        """
        data_cfg = self.config_dict.get("data")
        self.data_alias = data_cfg["alias"] if data_cfg else None

        defined_aliases: list[str] = list(self.config_dict.get("data_sources", {}).keys())
        if not defined_aliases and self.data_alias:
            defined_aliases = [self.data_alias]
        if defined_aliases:
            self.data_alias = defined_aliases[0]

        device = resolve_train_device(self.config_dict)

        generate_imports(self.buffer, self.visualize)
        generate_device_config(self.buffer, device)
        generate_data_loader(
            self.buffer,
            None,
            {},
            self.config,
            defined_aliases,
            initialize_aliases=True,
        )
        if self.networks:
            for network in self.networks.values():
                generate_model_class(self.buffer, network, self.components)
            generate_model_instantiations(self.buffer, self.networks)
        else:
            generate_model_class(self.buffer, self.network, self.components)
            fallback_name = self.network.get("name", "model")
            generate_model_instantiations(self.buffer, {fallback_name: self.network})

        for instr in self.config_dict.get("instructions", []):
            self._generate_instruction(instr, indent=0)

        if self.visualize:
            self._generate_visualization_code()

        return self.buffer.render()

    def _generate_instruction(self, instr: dict[str, Any], indent: int = 0) -> None:
        """
        Kieruje słownik instrukcji do właściwej funkcji generującej.
        
        Argumenty:
            instr (dict[str, Any]): Słownik instrukcji
            indent (int): Poziom wcięcia
        """
        cmd_type = instr.get("cmd_type")

        training_cfg = self._resolve_training_cfg(instr)
        training_params = training_cfg.get("params", {}) if training_cfg else {}
        model_var = self._resolve_model_var(instr)

        if cmd_type in ("train", "evaluate"):
            self._ensure_data_loaded(instr.get("data"), training_params, indent)
        elif cmd_type == "predict" and not instr.get("is_path", False):
            self._ensure_data_loaded(instr.get("source"), training_params, indent)

        if cmd_type == "train":
            generate_training_loop(
                self.buffer,
                instr,
                training_cfg,
                self.components,
                self.config,
                model_var,
                indent,
            )
        elif cmd_type == "evaluate":
            generate_evaluate_loop(
                self.buffer,
                instr,
                training_cfg,
                self.components,
                self.config,
                model_var,
                indent,
            )
        elif cmd_type == "predict":
            generate_predict(
                self.buffer,
                instr,
                training_cfg,
                self.config,
                model_var,
                indent,
            )
        elif cmd_type == "save":
            generate_save_weights(self.buffer, instr, model_var, indent)
        elif cmd_type == "load":
            generate_load_weights(self.buffer, instr, model_var, indent)
        elif cmd_type == "export":
            network = self._resolve_network(instr)
            first_input = network.get("first_input") or (1, 1, 28, 28)
            generate_export(self.buffer, instr, first_input, model_var, indent)
        elif cmd_type == "print":
            generate_print_commands(self.buffer, instr, model_var, indent)
        elif cmd_type == "summary":
            generate_summary(self.buffer, instr, model_var, indent)
        elif cmd_type == "if_block":
            self._generate_if_blocks(instr, indent)
        elif cmd_type in ("var_decl", "var_assign"):
            generate_variable(self.buffer, instr, indent)

    def _resolve_training_cfg(self, instr: dict[str, Any]) -> dict[str, Any]:
        """
        Zwraca konfigurację treningu właściwą dla instrukcji.

        Argumenty:
            instr (dict[str, Any]): Słownik instrukcji

        Zwraca:
            dict[str, Any]: Konfiguracja treningu
        """
        cfg_name = instr.get("config")
        configs = self.config_dict.get("configs", {})
        if isinstance(cfg_name, str) and cfg_name in configs:
            return configs[cfg_name]

        return self.config_dict.get("training", {})

    def _resolve_network(self, instr: dict[str, Any]) -> dict[str, Any]:
        """
        Zwraca opis sieci przypisany do instrukcji.

        Argumenty:
            instr (dict[str, Any]): Słownik instrukcji

        Zwraca:
            dict[str, Any]: Opis sieci
        """
        net_name = instr.get("network")
        if isinstance(net_name, str):
            if net_name in self.networks:
                return self.networks[net_name]
            if self.network.get("name") == net_name:
                return self.network
        return self.network

    def _resolve_model_var(self, instr: dict[str, Any]) -> str:
        """
        Zwraca nazwę zmiennej modelu dla instrukcji.

        Argumenty:
            instr (dict[str, Any]): Słownik instrukcji

        Zwraca:
            str: Nazwa zmiennej modelu
        """
        net_name = instr.get("network")
        if not isinstance(net_name, str):
            return "model"
        if len(self.networks) <= 1:
            return "model"
        return f"model_{net_name}"

    def _ensure_data_loaded(
        self, alias: Any, training_params: dict[str, Any], indent: int = 0
    ) -> None:
        """
        Gwarantuje wygenerowanie kodu ładowania danych dla wskazanego aliasu.

        Argumenty:
            alias (Any): Alias źródła danych
            training_params (dict[str, Any]): Parametry treningu dla inferencji typu targetu
            indent (int): Poziom wcięcia dla generowanego kodu (potrzebne gdy
                instrukcja train/evaluate/predict leży w środku bloku if)
        """
        if not isinstance(alias, str):
            return
        if alias in self._loaded_data_aliases:
            self.data_alias = alias
            return

        data_sources = self.config_dict.get("data_sources", {})
        data_cfg = data_sources.get(alias)
        if not data_cfg:
            return

        generate_data_loader(
            self.buffer,
            data_cfg,
            training_params,
            self.config,
            [],
            initialize_aliases=False,
            indent=indent,
        )
        self._loaded_data_aliases.add(alias)
        self.data_alias = alias

    def _generate_if_blocks(self, instr: dict[str, Any], indent: int = 0) -> None:
        """
        Rozwija blok warunkowy w kod if/elif/else Pythona.
        
        Argumenty:
            instr (dict[str, Any]): Słownik instrukcji
            indent (int): Poziom wcięcia
        """
        cond = condition_code(instr["condition"], self.data_alias)
        self.buffer.add(f"if {cond}:", indent)
        body = instr.get("body") or []
        if not body:
            self.buffer.add("pass", indent + 1)
        else:
            for sub in body:
                self._generate_instruction(sub, indent + 1)

        for elif_clause in instr.get("elif_clauses", []):
            elif_cond = condition_code(elif_clause["condition"], self.data_alias)
            self.buffer.add(f"elif {elif_cond}:", indent)
            elif_body = elif_clause.get("body") or []
            if not elif_body:
                self.buffer.add("pass", indent + 1)
            else:
                for sub in elif_body:
                    self._generate_instruction(sub, indent + 1)

        else_body = instr.get("else_body")
        if else_body is not None:
            self.buffer.add("else:", indent)
            if not else_body:
                self.buffer.add("pass", indent + 1)
            else:
                for sub in else_body:
                    self._generate_instruction(sub, indent + 1)

    def _generate_visualization_code(self) -> None:
        """
        Dodaje kod generujący graf architektury przez torchview.
        
        Argumenty:
            self (PyTorchGenerator): Instancja generatora
        """
        if not self.network:
            return
        first_input = self.network.get("first_input") or (1, 1, 28, 28)
        basename = str(self.config.paths.model_graph_basename)
        filename = str(self.config.paths.model_graph_file)
        if self.networks:
            first_network_name = next(iter(self.networks))
            model_var = f"model_{first_network_name}" if len(self.networks) > 1 else f"model_{first_network_name}"
        else:
            model_var = "model"
        self.buffer.add("try:")
        self.buffer.add(
            f"model_graph = draw_graph({model_var}, input_size={first_input}, "
            f"device=device, save_graph=True, filename={basename!r})",
            1,
        )
        self.buffer.add(f"print('Architecture visualization generated: ' + {filename!r})", 1)
        self.buffer.add("except Exception as e:")
        self.buffer.add("print(f'Error generating visualization: {e}')", 1)
        self.buffer.add("")
