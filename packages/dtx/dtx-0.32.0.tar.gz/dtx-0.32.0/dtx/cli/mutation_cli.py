from __future__ import annotations

import sys
import textwrap
import unicodedata
from dataclasses import MISSING, fields, is_dataclass
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union, get_args, get_origin, get_type_hints
#                                                                                                   ^ add this

from rich.console import Console
from rich.table import Table

from dtx_attacks.attacks.mutation.ascii.handler import AsciiSmugglingConfig, AsciiSmugglingMutation
from dtx_attacks.attacks.mutation.rotr import Rot13Config, Rot13Mutation
from dtx_attacks.attacks.mutation.art.handler import ArtPromptMutation, ArtPromptMutationConfig
from dtx_attacks.attacks.mutation.binary import BinaryMutation, BinaryMutationConfig
from dtx_attacks.attacks.mutation.base64 import Base64Mutation, Base64MutationConfig


try:
    from types import UnionType
except Exception:
    UnionType = None  # type: ignore


class OptionSpec:
    def __init__(
        self,
        name: str,
        type: Type,
        required: bool = False,
        default: Any = None,
        help: str = "",
        choices: Optional[Sequence[Any]] = None,
    ):
        self.name = name
        self.type = type
        self.required = required
        self.default = default
        self.help = help
        self.choices = choices


class AbstractTechnique:
    def display_name(self) -> str: ...
    def help(self) -> str: ...
    def get_option_specs(self) -> Dict[str, OptionSpec]: ...
    def get(self, key: str) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...
    def unset(self, key: str) -> None: ...
    def validate(self) -> None: ...
    def transform(self, text: str, *, seed: Optional[int] = None) -> str: ...


class DataclassTechniqueAdapter(AbstractTechnique):
    def __init__(self, mutation_cls: Type, config_cls: Type):
        if not is_dataclass(config_cls):
            raise TypeError("config_cls must be a dataclass")
        self._mutation_cls = mutation_cls
        self._config_cls = config_cls
        self._specs: Dict[str, OptionSpec] = self._build_specs(config_cls)
        self._values: Dict[str, Any] = {k: s.default for k, s in self._specs.items()}

    def display_name(self) -> str:
        return getattr(self._mutation_cls, "name", self._mutation_cls.__name__)

    def help(self) -> str:
        return getattr(self._mutation_cls, "description", "")

    def get_option_specs(self) -> Dict[str, OptionSpec]:
        return self._specs

    def get(self, key: str) -> Any:
        return self._values.get(key, None)

    def set(self, key: str, value: Any) -> None:
        spec = self._specs.get(key)
        if not spec:
            raise KeyError(f"Unknown option '{key}'")
        casted = self._cast(value, spec.type)
        if spec.choices and casted not in spec.choices:
            raise ValueError(f"Option '{key}' must be one of {list(spec.choices)}")
        self._values[key] = casted

    def unset(self, key: str) -> None:
        spec = self._specs.get(key)
        if not spec:
            raise KeyError(f"Unknown option '{key}'")
        self._values[key] = spec.default

    def validate(self) -> None:
        missing = [k for k, s in self._specs.items() if s.required and self._values.get(k) is None]
        if missing:
            raise ValueError(f"Missing required options: {', '.join(missing)}")

    def transform(self, text: str, *, seed: Optional[int] = None) -> str:
        self.validate()
        cfg = self._config_cls(**self._values)
        mut = self._mutation_cls(config=cfg)
        out = mut.mutate(text)
        return text if out is None else out

    @staticmethod
    def _build_specs(cfg_cls: Type) -> Dict[str, OptionSpec]:
        specs: Dict[str, OptionSpec] = {}

        # Resolve annotation strings -> real types
        try:
            mod_globals = vars(sys.modules[cfg_cls.__module__])
        except Exception:
            mod_globals = None
        try:
            hints = get_type_hints(cfg_cls, globalns=mod_globals, localns=mod_globals, include_extras=True)
        except TypeError:
            hints = get_type_hints(cfg_cls, globalns=mod_globals, localns=mod_globals)

        for f in fields(cfg_cls):
            ann = hints.get(f.name, f.type)  # real typing object (e.g., bool, List[str])
            py_type, is_opt = _unwrap_optional(ann)

            default = (
                None
                if f.default is MISSING and f.default_factory is MISSING
                else (f.default if f.default is not MISSING else f.default_factory())  # type: ignore[misc]
            )
            required = (not is_opt) and (f.default is MISSING and f.default_factory is MISSING)
            meta = f.metadata or {}

            specs[f.name] = OptionSpec(
                name=f.name,
                type=py_type,            # <-- real type, not a string
                required=bool(meta.get("required", required)),
                default=default,
                help=meta.get("help", ""),
                choices=meta.get("choices", None),
            )
        return specs

    @staticmethod
    def _cast(v: Any, t: Type) -> Any:
        if v is None:
            return None
        origin = get_origin(t)
        args = get_args(t)

        if origin in (list, List):
            elem_t = args[0] if args else str
            if isinstance(v, list):
                return [DataclassTechniqueAdapter._cast(x, elem_t) for x in v]
            s = str(v).strip()
            return [] if not s else [DataclassTechniqueAdapter._cast(x.strip(), elem_t) for x in s.split(",")]

        if t is bool:
            if isinstance(v, bool):
                return v
            s = str(v).strip().lower()
            if s in ("1", "true", "t", "yes", "y", "on"): return True
            if s in ("0", "false", "f", "no", "n", "off"): return False
            raise ValueError(f"Cannot cast '{v}' to bool")

        if t is int:   return int(v)
        if t is float: return float(v)
        if t is str:   return str(v)
        return t(v)


def _unwrap_optional(t: Type) -> Tuple[Type, bool]:
    origin = get_origin(t)
    if origin is Union or (UnionType is not None and origin is UnionType):
        args = [a for a in get_args(t) if a is not type(None)]
        return (args[0] if args else Any), True
    return t, False


class LambdaTechnique(AbstractTechnique):
    def __init__(self, name: str, description: str, fn):
        self._name = name
        self._desc = description
        self._fn = fn
        self._specs: Dict[str, OptionSpec] = {}
    def display_name(self) -> str: return self._name
    def help(self) -> str: return self._desc
    def get_option_specs(self) -> Dict[str, OptionSpec]: return self._specs
    def get(self, key: str) -> Any: return None
    def set(self, key: str, value: Any) -> None: raise KeyError("No options for this technique")
    def unset(self, key: str) -> None: ...
    def validate(self) -> None: ...
    def transform(self, text: str, *, seed: Optional[int] = None) -> str:
        return self._fn(text)


# ---------------- REPL ----------------
class PromptsMutationRepl:
    """
    Commands:
      /q               quit
      /h               help
      /list            list techniques
      /s <text>        search techniques
      /back            reselect technique (menu)  [alias: /r]
      /seed <n>        set RNG seed
      /opts            show current technique options
      /set k=v         set option (lists: comma-separated)
      /unset k         reset option to default
      /preview mode    on|auto|off (controls invisible-char preview)
    """

    def __init__(self, default_tech: Optional[str] = None, seed: Optional[int] = None, no_color: bool = False):
        # UI to stderr
        self.console = Console(file=sys.stderr, no_color=no_color)
        self.seed = seed
        self.default_tech = default_tech
        self._configure_lib_logging()
        self.registry: Dict[str, AbstractTechnique] = self._build_registry()
        self.current_tech: Optional[str] = None
        self.preview_mode: str = "auto"  # on | auto | off

    def _configure_lib_logging(self):
        try:
            from loguru import logger as _lg
            _lg.remove()
            _lg.add(sys.stderr, level="ERROR")
        except Exception:
            pass

    def _build_registry(self) -> Dict[str, AbstractTechnique]:
        return {
            "art": DataclassTechniqueAdapter(ArtPromptMutation, ArtPromptMutationConfig),
            "rotr": DataclassTechniqueAdapter(Rot13Mutation, Rot13Config),
            "ascii": DataclassTechniqueAdapter(AsciiSmugglingMutation, AsciiSmugglingConfig),
            "binary": DataclassTechniqueAdapter(BinaryMutation, BinaryMutationConfig),
            "base64": DataclassTechniqueAdapter(Base64Mutation, Base64MutationConfig),
            "reverse": LambdaTechnique("reverse", "Reverse characters", lambda s: s[::-1]),
            "uppercase": LambdaTechnique("uppercase", "Upper-case the prompt", lambda s: s.upper()),
        }

    def run(self):
        self.console.print("[bold cyan]Prompt Mutation REPL[/bold cyan] (type /h for help)")
        if self.seed is not None:
            self.console.print(f"Using seed: [bold]{self.seed}[/bold]")

        if self.default_tech:
            self._select_tech(self.default_tech)
        if not self.current_tech:
            self._menu_select(default=None)
            # Do NOT read a prompt immediately; show "Enter Prompt>" on the loop.

        while True:
            try:
                # Dynamic shell prompt
                prompt_lbl = "[bold green]Enter Prompt>[/bold green]" if self.current_tech else "[bold green]mutation>[/bold green]"
                cmd = self.console.input(f"{prompt_lbl} ").strip()
                if not cmd:
                    continue

                # Commands
                if cmd == "/q":
                    return
                if cmd == "/h":
                    self._print_help();  continue
                if cmd == "/list":
                    self._list_techniques();  continue
                if cmd.startswith("/s "):
                    self._search(cmd[3:].strip());  continue
                if cmd in ("/r", "/back"):
                    # Reselect technique; then return to loop to show "Enter Prompt>"
                    self._menu_select(default=self.current_tech)
                    continue
                if cmd.startswith("/seed "):
                    self._set_seed(cmd);  continue
                if cmd == "/opts":
                    self._show_opts();  continue
                if cmd.startswith("/set "):
                    self._set_opt(cmd[5:].strip());  continue
                if cmd.startswith("/unset "):
                    self._unset_opt(cmd[7:].strip());  continue
                if cmd.startswith("/preview "):
                    self._set_preview(cmd[9:].strip());  continue

                # Optional "<tech>:" quick switch
                if cmd.endswith(":") and cmd[:-1] in self.registry:
                    self.current_tech = cmd[:-1]
                    self.console.print(f"Technique set to [bold]{self.current_tech}[/bold].")
                    # Do not read immediately; show "Enter Prompt>" next loop
                    continue

                # Normal input -> multiline read & transform
                if not self.current_tech:
                    # No technique yet: open menu, then show "Enter Prompt>" on next loop
                    self._menu_select(default=None)
                    continue

                # We have a technique: treat this line as the first line of the prompt
                text = self._read_multiline(initial_line=cmd)
                transformed = self._transform(text)
                self._print_output(transformed)
                # Stay on current technique; do not reopen the menu

            except EOFError:
                self.console.print()
                return
            except KeyboardInterrupt:
                self.console.print()
                return
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)

    # -------- core ops --------
    def _transform(self, text: str) -> str:
        tech = self.registry.get(self.current_tech)
        if not tech:
            raise ValueError(f"Technique '{self.current_tech}' not found.")
        return tech.transform(text, seed=self.seed)

    # -------- menus & options --------
    def _menu_select(self, default: Optional[str]):
        self._list_techniques()
        prompt = "Select technique by number or name"
        if default:
            prompt += f" [default: {default}]"
        choice = self.console.input(f"{prompt}: ").strip()

        if not choice and default and default in self.registry:
            self.current_tech = default
            self.console.print(f"Using technique: [bold]{self.current_tech}[/bold]")
            return

        if choice.isdigit():
            idx = int(choice) - 1
            names = sorted(self.registry.keys())
            if 0 <= idx < len(names):
                self.current_tech = names[idx]
            else:
                self.console.print("[red]Invalid number[/red]")
                return
        else:
            self._select_tech(choice)

        if self.current_tech:
            self.console.print(f"Using technique: [bold]{self.current_tech}[/bold]")

    def _select_tech(self, name: str):
        if name in self.registry:
            self.current_tech = name
        else:
            self.console.print(f"[red]Unknown technique:[/red] {name}")

    def _show_opts(self):
        tech = self.registry.get(self.current_tech or "")
        if not tech:
            self.console.print("[red]No technique selected[/red]")
            return
        specs = tech.get_option_specs()
        if not specs:
            self.console.print("(no options)")
            return
        table = Table(title=f"Options for '{tech.display_name()}'", show_lines=False)
        table.add_column("Name", style="bold")
        table.add_column("Type")
        table.add_column("Required")
        table.add_column("Default")
        table.add_column("Current")
        table.add_column("Help")
        for k, s in specs.items():
            cur = tech.get(k)
            table.add_row(k, _typename(s.type), "Y" if s.required else "N", repr(s.default), repr(cur), s.help or "")
        self.console.print(table)

    def _set_opt(self, expr: str):
        tech = self.registry.get(self.current_tech or "")
        if not tech:
            self.console.print("[red]No technique selected[/red]")
            return
        if "=" not in expr:
            self.console.print("[red]Usage:[/red] /set key=value")
            return
        k, v = expr.split("=", 1)
        k = k.strip()
        v = v.strip()
        tech.set(k, v)
        self.console.print(f"Set [bold]{k}[/bold] = {v}")

    def _unset_opt(self, key: str):
        tech = self.registry.get(self.current_tech or "")
        if not tech:
            self.console.print("[red]No technique selected[/red]")
            return
        tech.unset(key.strip())
        self.console.print(f"Unset [bold]{key.strip()}[/bold]")

    def _set_preview(self, mode_expr: str):
        mode = mode_expr.lower()
        if mode in {"on", "auto", "off"}:
            self.preview_mode = mode
            self.console.print(f"Preview mode set to [bold]{mode}[/bold]")
        else:
            self.console.print("[red]Usage:[/red] /preview on|auto|off")

    # -------- I/O --------
    def _list_techniques(self):
        table = Table(title="Available Techniques", show_lines=False)
        table.add_column("#", justify="right", width=4)
        table.add_column("Name", style="bold")
        table.add_column("Description")
        names = sorted(self.registry.keys())
        for i, n in enumerate(names, 1):
            desc = self.registry[n].help() or ""
            table.add_row(str(i), n, desc)
        self.console.print(table)

    def _search(self, query: str):
        names = [n for n in sorted(self.registry.keys()) if query.lower() in n.lower()]
        if not names:
            self.console.print(f"No techniques matching '{query}'.")
            return
        table = Table(title=f"Search: {query}", show_lines=False)
        table.add_column("#", justify="right", width=4)
        table.add_column("Name", style="bold")
        table.add_column("Description")
        for i, n in enumerate(names, 1):
            table.add_row(str(i), n, self.registry[n].help() or "")
        self.console.print(table)

    def _read_multiline(self, initial_line: Optional[str] = None) -> str:
        self.console.print("[dim]Continue prompt (or enter blank line to finish, Ctrl+D to send, /q to quit):[/dim]")
        lines: List[str] = []
        if initial_line is not None:
            if initial_line == "/q":
                raise EOFError()
            lines.append(initial_line)
        while True:
            line = sys.stdin.readline()
            if not line:
                break
            if line.strip() == "/q":
                raise EOFError()
            if line.strip() == "":
                break
            lines.append(line.rstrip("\n"))
        return "\n".join(lines)

    def _print_output(self, result: str):
        # stdout: transformed prompt only
        sys.stdout.write(result + "\n")
        sys.stdout.flush()

        # concise status to stderr
        print(f"[ok] {len(result)} chars (seed={self.seed})", file=sys.stderr)

        # preview logic
        hidden = _hidden_count(result)
        show = (
            (self.preview_mode == "on" and hidden > 0) or
            (self.preview_mode == "auto" and _looks_invisible(result))
        )
        if show:
            print(f"(contains {hidden} hidden chars; preview below)", file=sys.stderr)
            print(_to_codepoints(result), file=sys.stderr)

    # -------- help --------
    def _print_help(self):
        msg = """
        Commands:
          /q               Quit
          /h               Help
          /list            List techniques
          /s <text>        Search techniques by substring
          /back            Reselect technique via menu (alias: /r)
          /seed <n>        Set RNG seed
          /opts            Show current technique options
          /set k=v         Set an option (lists: comma-separated)
          /unset k         Reset an option to default
          /preview mode    on|auto|off (controls invisible-char preview)

        Usage:
          - Select a technique, then paste/type your prompt (multiline supported).
          - After each transform, the current technique remains active. Use /back to pick another.
          - Finish with a blank line or Ctrl+D.
          - You can prefix a line with '<tech>:' to switch technique for that turn.
        """
        self.console.print(textwrap.dedent(msg))


# ---------------- invisibility helpers ----------------
PUA_START = 0xE0000
PUA_END = 0xE0FFF
ZERO_WIDTH = {"\u200B", "\u200C", "\u200D", "\u2060", "\ufeff"}  # ZWSP, ZWNJ, ZWJ, WJ, BOM

def _looks_invisible(s: str) -> bool:
    if not s:
        return False
    total = len(s)
    invis = 0
    for ch in s:
        cp = ord(ch)
        cat = unicodedata.category(ch)
        if ch in ZERO_WIDTH or (PUA_START <= cp <= PUA_END) or cat == "Cf":
            invis += 1
    return invis >= max(3, int(0.6 * total))

def _hidden_count(s: str) -> int:
    c = 0
    for ch in s:
        cp = ord(ch)
        if ch in ZERO_WIDTH or (PUA_START <= cp <= PUA_END) or unicodedata.category(ch) == "Cf":
            c += 1
    return c

def _to_codepoints(s: str) -> str:
    cps = [f"U+{ord(ch):04X}" for ch in s]
    out_lines, line = [], []
    for i, token in enumerate(cps, 1):
        line.append(token)
        if i % 16 == 0:
            out_lines.append(" ".join(line)); line = []
    if line:
        out_lines.append(" ".join(line))
    return "\n".join(out_lines)

def _typename(t: Type) -> str:
    return getattr(t, "__name__", str(t))
