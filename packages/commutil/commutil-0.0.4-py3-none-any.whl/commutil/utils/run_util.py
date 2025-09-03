from typing import Callable, Dict, Optional, List, Any, Iterable
from collections.abc import Iterable
from functools import partial
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
# from multiprocessing import Pool
import subprocess
from .string_util import u_color, highlight_args


def run_cmd(cmd, verbose=False, shell=True):
    if verbose:
        # dbg(cmd, head="Run $")
        print(f"Run $ {cmd}")
    process = subprocess.Popen(cmd, shell=shell)
    process.wait()


def multi_runner(cmd_list, choice="thread", n=2, **kwargs):
    run_cmd_wrapper = partial(run_cmd, **kwargs)

    if choice in ["thread", "t", "th", "T", "threads"]:
        with ThreadPoolExecutor(max_workers=n) as executor:
            futures = [executor.submit(run_cmd_wrapper, cmd) for cmd in cmd_list]
            for future in futures:
                future.result()
    elif choice in ["process", "p", "pro", "P", "processes"]:
        with ProcessPoolExecutor(max_workers=n) as executor:
            futures = [executor.submit(run_cmd_wrapper, cmd) for cmd in cmd_list]
            for future in futures:
                future.result()
    # elif choice in ["pool", "po", "poo", "Pool"]:
    #     with Pool(processes=n) as pool:
    #         pool.map(run_cmd_wrapper, cmd_list)
    else:
        raise ValueError("Invalid choice")


def run_cmd_list(cmd_list: List[str], n: int = 1, choice="thread", confirm=None, **kwargs):
    if not cmd_list:
        print("Empty command list, nothing to execute")
        return
    if not confirm:
        print(f"\n{u_color('=== Command List Preview ===', 'bright_cyan')}")
        for i, cmd in enumerate(cmd_list):
            print(f"{str(i + 1) + '.'}", end=" ")
            print(highlight_args(cmd))

        print(f"\n{u_color('=== Statistics ===', 'cyan')}")
        print(f"{'Total commands:'} {str(len(cmd_list))}")

        mode_text = f"{'Batch (threads: ' + str(n) + ')' if n > 1 else 'Stream'}"
        print(f"{'Execution mode:'} {mode_text}")

        print(f"\n{'Execute these commands? (y/n):'} ", end="")
        confirmation = input().strip().lower()
        if confirmation not in ['y', 'yes', 'yep']:
            print("Execution canceled")
            return

    if n == 1:
        for cmd in cmd_list:
            print(f"Stream $ {cmd}")
            run_cmd(cmd, **kwargs)
    else:
        for cmd in cmd_list:
            print(f"Batch $ {cmd}")
        multi_runner(cmd_list=cmd_list, n=n, choice=choice, **kwargs)


def split_sequence(sequence, n=1):
    length = len(sequence)
    if n <= 0:
        return []
    if n == 1:
        return [sequence]
    if n >= length:
        return [[item] for item in sequence] + [[] for _ in range(n - length)]

    base_size = length // n
    remainder = length % n

    result = []
    start = 0
    for i in range(n):
        end = start + base_size + (1 if i < remainder else 0)
        result.append(sequence[start:end])
        start = end
    return result


def split_dict(dictionary, n=1):
    items = list(dictionary.items())
    length = len(items)

    if n <= 0:
        return []
    if n == 1:
        return [dictionary.copy()]
    if n >= length:
        result = [{k: v} for k, v in items]
        result.extend([{} for _ in range(n - length)])
        return result

    base_size = length // n
    remainder = length % n

    result = []
    start = 0
    for i in range(n):
        end = start + base_size + (1 if i < remainder else 0)
        part_dict = dict(items[start:end])
        result.append(part_dict)
        start = end
    return result


def make_args(arg_dict):
    args = []
    kwargs = {}
    pos_para = {}
    for key, value in arg_dict.items():
        if key.startswith("_") and key[1:].isdigit():
            index = int(key[1:])
            pos_para[index] = value
        else:
            kwargs[key] = value
    indices = sorted(pos_para.keys())
    for index in indices:
        args.append(pos_para[index])
    return args, kwargs


# outside executor
def _execute_function(serialized_func, args, kwargs):
    import cloudpickle
    func = cloudpickle.loads(serialized_func)
    result = func(*args, **kwargs)
    return result


def run_func(_func, choice="thread", n=1, paras=[], desc=">--RUN-FUNC--<"):
    from tqdm import tqdm
    tasks = [make_args(para) for para in paras]

    results = [None] * len(tasks)

    if choice in ["thread", "t", "th", "T", "threads"]:
        with ThreadPoolExecutor(max_workers=n) as executor:
            # futures = []
            # for args, kwargs in tasks:
            #     futures.append(executor.submit(_func, *args, **kwargs))
            # for future in futures:
            #     future.result()
            future2id = {executor.submit(_func, *args, **kwargs): i for i, (args, kwargs) in enumerate(tasks)}
            for future in tqdm(as_completed(future2id), total=len(tasks), desc=desc):
                task_id = future2id[future]
                results[task_id] = future.result()

    elif choice in ["process", "p", "pro", "P", "processes"]:
        import cloudpickle
        serialized_func = cloudpickle.dumps(_func)
        with ProcessPoolExecutor(max_workers=n) as executor:
            # futures = []
            # for args, kwargs in tasks:
            #     futures.append(executor.submit(_execute_function, serialized_func, args, kwargs))
            # for future in futures:
            #     future.result()

            future2id = {executor.submit(_execute_function, serialized_func, args, kwargs): i for i, (args, kwargs) in enumerate(tasks)}
            for future in tqdm(as_completed(future2id), total=len(tasks), desc=desc):
                task_id = future2id[future]
                results[task_id] = future.result()

    else:
        raise ValueError("Invalid choice")

    return results


# utils for CmdGen
def extract_value_split(cmd, key, mode):
    parts = cmd.split()
    key = mode + key
    if key in parts:
        return parts[parts.index(key) + 1]
    return ""


def ensure_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, (tuple, set)):
        return list(x)
    if isinstance(x, dict):
        return list(x.keys())
    if isinstance(x, str):
        return [x]
    if isinstance(x, Iterable):
        return list(x)
    return [x]


class CmdGen:
    def __init__(self, script="python run.py", mode="--", **kwargs):
        self.mode = mode
        self.script = script
        list_params = {k: ensure_list(v) for k, v in kwargs.items() if not isinstance(v, tuple)} # if not tuple, make it list (str-int-bool -> list)
        tuple_params = {k: list(v) for k, v in kwargs.items() if isinstance(v, tuple)}
        if tuple_params and not all(len(v) == len(next(iter(tuple_params.values()))) for v in tuple_params.values()):
            raise ValueError("All tuple parameters must have the same length")

        self._original_kwargs = {"list_params": list_params, "tuple_params": tuple_params}
        self._filter_conditions = {k: None for params_dict in self._original_kwargs.values() for k in params_dict}

        kwargs = {k: ensure_list(v) for k, v in kwargs.items()}
        self._kwargs_order = {k: {v: i for i, v in enumerate(kwargs[k])} for k in kwargs}

        self.config_list = self._gen_config_list(self._original_kwargs)

    def _handle_list_params(self, params) -> List[Dict]:
        if not params:
            return [{}]
        keys = list(params.keys())
        values = list(params.values())

        configs = []
        from itertools import product
        for values_combo in product(*values):
            configs.append({k: v for k, v in zip(keys, values_combo)})

        return configs

    def _handle_tuple_params(self, base_configs: List[Dict], tuple_params: Dict) -> List[Dict]:
        if not tuple_params:
            return base_configs
        tuple_len = len(next(iter(tuple_params.values())))

        # sorted_keys = sorted(zip_params.keys())
        keys = list(tuple_params.keys())
        return [{**base, **{k: tuple_params[k][i] for k in keys}}
                for base in base_configs
                for i in range(tuple_len)]

    def _gen_config_list(self, kwargs) -> List[Dict]:
        list_params = kwargs["list_params"]
        tuple_params = kwargs["tuple_params"]
        config_list = [{}]

        if list_params: config_list = self._handle_list_params(list_params)
        if tuple_params: config_list = self._handle_tuple_params(config_list, tuple_params)
        return config_list

    def filter(self, **kwargs) -> 'CmdGen':
        for key, value in kwargs.items():
            if key not in self._filter_conditions:
                raise KeyError(f"Filter key '{key}' not found")
            self._filter_conditions[key] = (value if callable(value) or value is None else ensure_list(value))
        return self

    def _apply_filters(self, config: Dict[str, Any]) -> bool:
        for key, condition in self._filter_conditions.items():
            if condition is None:
                continue
            value = config[key]
            if callable(condition):
                try:
                    if not condition(value):
                        return False
                except Exception as e:
                    raise ValueError(f"Filter function error for '{key}': {e}")
            elif value not in condition:
                return False
        return True

    def _format_cmd(self, config):
        cmd = self.script
        order = []
        for k, v in config.items():
            order.append(self._kwargs_order.get(k, {}).get(v, 1e9))
            if self.mode == "v":
                cmd += f" {v}"
            elif self.mode == "cli":
                k = k.replace("_", "-")
                cmd += f" {k} {v}"
            else:
                if isinstance(v, bool):
                    cmd += f" {self.mode}{k}" if v else ""
                else:
                    if isinstance(v, str):
                        cmd += f" {self.mode}{k} \"{v}\""
                    else:
                        cmd += f" {self.mode}{k} {v}"
        return cmd.strip(), order

    def add(self, **kwargs) -> 'CmdGen':
        for k, v in kwargs.items():
            if isinstance(v, tuple):
                self._original_kwargs["tuple_params"][k] = list(v)
            else:
                self._original_kwargs["list_params"][k] = ensure_list(v)
            self._filter_conditions.update({k: None for k in kwargs})
        self.config_list = self._gen_config_list(self._original_kwargs)
        return self

    def rm(self, *keys) -> 'CmdGen':
        for k in keys:
            if k in self._original_kwargs["list_params"]:
                self._original_kwargs["list_params"].pop(k, None)
            elif k in self._original_kwargs["tuple_params"]:
                self._original_kwargs["tuple_params"].pop(k, None)
            self._filter_conditions.pop(k, None)
        self.config_list = self._gen_config_list(self._original_kwargs)
        return self

    def reset(self) -> 'CmdGen':
        self._filter_conditions = {k: None for k in self._original_kwargs}
        return self

    def gen(self) -> List[str]:
        cmd_and_order = [self._format_cmd(config) for config in self.config_list if self._apply_filters(config)]
        cmd_and_order.sort(key=lambda x: x[1])
        return [cmd for cmd, _ in cmd_and_order]

    def cat(self, *genes: 'CmdGen', sep=" && ") -> List[str]:
        self_list, self_mode = self.gen(), self.mode
        if not genes: return self_list

        other_lists, other_modes = [gene.gen() for gene in genes], [gene.mode for gene in genes]
        return [sep.join(z_cmd) for z_cmd in zip(self_list, *other_lists)]

    @classmethod
    def concat(cls, *genes: 'CmdGen', sep=" && ") -> list[str]:
        cmd_lists = [gene.gen() for gene in genes]
        return [sep.join(z_cmd) for z_cmd in zip(*cmd_lists)]
