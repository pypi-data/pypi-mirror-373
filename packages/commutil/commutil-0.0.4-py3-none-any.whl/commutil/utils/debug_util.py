def _format_print(arg_names, args, *, head="DEBUG", ncols=0, replace_space=False, show_name=True, show_value=True, show_type=True, show_length=False, show_id=False):
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    if head:
        debug_info = []
        for i, arg in enumerate(args):
            try:
                if show_type:
                    type_name = arg.__class__.__name__
                else:
                    type_name = ""
                # t == "title"
                debug_info.append(f"{GREEN}{arg_names[i].strip()}⇥{RED}{arg}{BLUE}⇤{type_name}")
                # »«↦↤⇒⇐⇔⇕⇖⇗⇘⇙⇚⇛⇜⇝⇞⇟⇠⇡⇢⇣⇤⇥⇦⇧⇨⇩⇪⇫⇬⇭⇮⇯⇰⇱⇲⇳⇴⇵⇶⇷⇸⇹⇺⇻⇼⇽⇾⇿⋀⋁⋂⋃⋄⋅⋆⋇⋈⋉⋊⋋⋌⋍⋎⋏⋐⋑⋒⋓⋔⋕⋖⋗⋘⋙⋚⋛⋜⋝⋞⋟⋠⋡⋢⋣⋤⋥⋦⋧⋨⋩⋪⋫⋬⋭⋮⋯⋰⋱⋲⋳⋴⋵⋶⋷⋸⋹⋺⋻⋼⋽⋾⋿⌀⌁⌂⌃⌄⌅⌆⌇⌈⌉⌊⌋⌌⌍⌎⌏⌐⌑⌒⌓⌔⌕⌖⌗⌘⌙⌚⌛⌜⌝⌞⌟⌠⌡⌢⌣⌤⌥⌦⌧⌨〈〉⌫⌬⌭⌮⌯⌰⌱⌲⌳⌴⌵⌶⌷⌸⌹⌺
            except:
                debug_info.append(f"{GREEN}{arg_names[i].strip()}")
        print(f"{YELLOW}[{head}]" + "-" * ncols, ", ".join(debug_info), f"{RESET}")
        return

    default_columns = {
        "name": {"width": None, "color": "\033[32m", "formatter": str.strip},
        "value": {"width": None, "color": "\033[31m", "formatter": lambda x: str(x).replace(" ", "·")},
        "type": {"width": None, "color": "\033[34m", "formatter": lambda x: x.__class__.__name__},
        "length": {"width": None, "color": "\033[34m", "formatter": lambda x: str(len(x)) if hasattr(x, "__len__") else "N/A"},
        "id": {"width": None, "color": "\033[34m", "formatter": lambda x: str(id(x))},
    }

    show_columns = {"name": show_name, "value": show_value, "type": show_type, "length": show_length, "id": show_id}

    active_columns = {k: default_columns[k] for k, show in show_columns.items() if show}

    for col_name, col in active_columns.items():
        if col["width"] is None:
            if col_name == "name":
                col["width"] = max(len(n.strip()) for n in arg_names)
            else:
                col["width"] = max(len(col["formatter"](arg)) for arg in args)
        col["width"] = max(col["width"], len(col_name))

    borders = {
        "top": "╔" + "╦".join("═" * w["width"] for w in active_columns.values()) + "╗",
        "middle": "╠" + "╬".join("═" * w["width"] for w in active_columns.values()) + "╣",
        "bottom": "╚" + "╩".join("═" * w["width"] for w in active_columns.values()) + "╝",
        "row": "║" + "║".join("{}" for _ in active_columns) + "║",
    }

    print(f"{YELLOW}{borders['top']}{RESET}")
    headers = [f"{YELLOW}║{col['color']}{col_name:<{col['width']}}" for col_name, col in active_columns.items()]
    print("".join(headers) + f"{YELLOW}║{RESET}")

    for i, (arg_name, arg) in enumerate(zip(arg_names, args)):
        # if i > 0:
        if 1:
            print(f"{YELLOW}{borders['middle']}{RESET}")

        row_data = []
        for col_name, col in active_columns.items():
            if col_name == "name":
                formatted = col["formatter"](arg_name)
            else:
                formatted = col["formatter"](arg)
            row_data.append(f"{YELLOW}║{col['color']}{formatted:<{col['width']}}")

        print("".join(row_data) + f"{YELLOW}║{RESET}")

    print(f"{YELLOW}{borders['bottom']}{RESET}")


def dbg_cc(*args, **kwargs):
    # if ENVIRONMENT != "local":
    #     print(*args, **kwargs)
    #     return
    import inspect

    frame = inspect.currentframe().f_back
    code_context = inspect.getframeinfo(frame).code_context[0].strip()
    arg_names = code_context[code_context.find("(") + 1: code_context.rfind(")")].split(", ")  # TODO 可能 dbg("1, 2, 3, 4") 这样存在问题
    _format_print(arg_names, args, **kwargs)


def dbg_ast(*args, t=0, **kwargs):
    # if ENVIRONMENT != "local":
    #     print(*args, **kwargs)
    #     return
    # t -> title
    if t:
        YELLOW = "\033[33m"
        RESET = "\033[0m"
        message = args[0]
        width = max(t, len(message) + 10)
        top_bottom = "═" * (width - 2)
        print(YELLOW)
        print(f"╔{top_bottom}╗")
        print(f"║{f'>>> {message} <<<':^{width - 2}}║")
        print(f"╚{top_bottom}╝")
        print(RESET)
        return

    import inspect
    import ast
    frame = inspect.currentframe().f_back
    call_line = inspect.getframeinfo(frame).code_context[0].strip()
    tree = ast.parse(call_line)
    arg_names = [ast.get_source_segment(call_line, arg) for arg in tree.body[0].value.args]
    _format_print(arg_names, args, **kwargs)


def dbg_base(*args, head="DEBUG", ncols=0, **kwargs):
    # if ENVIRONMENT != "local":
    #     print(*args, **kwargs)
    #     return
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"
    import inspect

    frame = inspect.currentframe().f_back
    local_vars = frame.f_locals
    print(local_vars)
    debug_info = []
    for var_name in args:
        if var_name in local_vars:
            debug_info.append(f"{GREEN}{var_name}: {RED}{local_vars[var_name]}")
        else:
            debug_info.append(f"{GREEN}{var_name}")
    print(f"{YELLOW}[{head}]" + "-" * ncols, ", ".join(debug_info), f"{RESET}")


def dbg_str(*args: str, enabled=True, head: str = "DEBUG", ncols: int = 0, **kwargs) -> str:
    # if ENVIRONMENT != "local":
    #     print(*args, **kwargs)
    #     return
    if not enabled: return
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    RESET = "\033[0m"

    def parse_path(path: str) -> list:
        parts = []
        current = ""
        in_brackets = False
        for char in path:
            if char == "[":
                if current:
                    parts.append(current)
                    current = ""
                in_brackets = True
            elif char == "]":
                if current:
                    parts.append(current.strip("'\""))
                    current = ""
                in_brackets = False
            elif char == "." and not in_brackets:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char
        if current:
            parts.append(current)
        return parts

    def get_nested_value(obj, part):
        try:
            if part.isdigit():
                return obj[int(part)]
            return obj[part] if isinstance(obj, dict) else getattr(obj, part)
        except:
            raise

    import inspect

    frame = inspect.currentframe().f_back
    local_vars = frame.f_locals
    debug_info = []
    for var_path in args:
        try:
            parts = parse_path(var_path)
            value = local_vars[parts[0]]
            for part in parts[1:]:
                value = get_nested_value(value, part)
            debug_info.append(f"{GREEN}{var_path}: {RED}{value}")
        except Exception:
            debug_info.append(f"{GREEN}{var_path}")
    print(f"{YELLOW}[{head}]" + "-" * ncols + " " + ", ".join(debug_info) + RESET)


dbg = dbg_ast
