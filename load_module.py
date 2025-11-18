import os
import importlib.util
import importlib
from types import ModuleType

def get_task_module(task_path: str) -> tuple[list[str], list[ModuleType]]:
    """
    指定された task_path 内のタスクフォルダーから main.py をインポートし、
    毎回再読込を行ったうえでタスク名リストとモジュールリストを返す。

    Args:
        task_path (str): タスクフォルダー群が存在する親ディレクトリのパス

    Returns:
        tuple[list[str], list[ModuleType]]:
            - task_names: 各 main.py の get_name() が返す文字列のリスト
            - modules: 対応するモジュールオブジェクトのリスト
    """
    task_names: list[str] = []
    modules: list[ModuleType] = []

    for entry in os.listdir(task_path):
        folder_path = os.path.join(task_path, entry)

        # フォルダーでない場合はスキップ
        if not os.path.isdir(folder_path):
            continue

        main_file = os.path.join(folder_path, "main.py")

        # main.py が存在しない場合はスキップ
        if not os.path.isfile(main_file):
            continue

        try:
            # importlib を使って main.py をロード
            spec = importlib.util.spec_from_file_location(entry, main_file)
            if spec is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 毎回リロードして最新の内容を反映
            module = importlib.reload(module)

            # 必要な4つの関数が存在するか確認
            required_funcs = ["pre_proc", "post_proc", "main_proc", "get_name"]
            if not all(hasattr(module, func) for func in required_funcs):
                continue

            try:
                # get_name() を呼び出してタスク名を取得
                task_name = module.get_name()
                if not isinstance(task_name, str):
                    continue
            except Exception:
                continue

            # リストに追加
            task_names.append(task_name)
            modules.append(module)

        except Exception:
            # インポートエラーなどが発生した場合はスキップ
            continue

    return task_names, modules

