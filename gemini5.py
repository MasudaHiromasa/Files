import os
import importlib.util
from types import ModuleType
from typing import List, Optional
from dataclasses import dataclass

# 必須関数名のリストを定義 (グローバルまたは定数として定義)
REQUIRED_FUNCTIONS = ["get_description", "pre_proc", "main_proc", "post_proc"]

@dataclass
class TaskModuleInfo:
    """タスクのメタデータ（情報）のみを保持するデータクラス"""
    name: str          # サブフォルダー名 (例: "task_A")
    description: str   # name.txt から取得した識別名
    main_py_path: str  # main.py への絶対パス
    module_id: str     # ロード時に使用する一意なモジュール識別名 (例: "task_A_main")


def load_task_module(task_info: TaskModuleInfo) -> Optional[ModuleType]:
    """
    TaskModuleInfo オブジェクトの情報に基づいて、モジュール本体を動的に読み込む単体関数。
    """
    try:
        # spec_from_file_location を使用して簡潔に記述
        spec = importlib.util.spec_from_file_location(task_info.module_id, task_info.main_py_path)
        if not spec or not spec.loader:
            print(f"エラー: '{task_info.name}' のスペック作成に失敗しました。")
            return None

        module = importlib.util.module_from_spec(spec)
        # sys.modulesには登録しない
        spec.loader.exec_module(module)
        
        # 必須関数の最終チェック
        for func_name in REQUIRED_FUNCTIONS:
            if not hasattr(module, func_name) or not callable(getattr(module, func_name)):
                print(f"エラー: ロード時に関数 '{func_name}' が見つかりませんでした。")
                return None
                    
        return module

    except Exception as e:
        print(f"エラー: '{task_info.name}' のモジュール読み込み中に例外が発生しました: {e}")
        return None


def get_task_info_list(task_folder: str) -> List[TaskModuleInfo]:
    """
    指定されたフォルダー内のタスクのメタデータ (TaskModuleInfo) のリストを返します。
    name.txt から識別名を取得し、main.pyの実行は行いません。
    """
    task_infos: List[TaskModuleInfo] = []

    if not os.path.isdir(task_folder):
        print(f"エラー: 指定されたパス '{task_folder}' が見つかりません。")
        return task_infos

    for subdir_name in os.listdir(task_folder):
        subdir_path = os.path.join(task_folder, subdir_name)
        main_py_path = os.path.join(subdir_path, "main.py")
        name_txt_path = os.path.join(subdir_path, "name.txt")
        
        # main.py と name.txt の両方が存在することをチェック
        if not os.path.exists(main_py_path) or not os.path.exists(name_txt_path):
            continue
            
        try:
            # name.txt から識別名を読み込む
            with open(name_txt_path, 'r', encoding='utf-8') as f:
                description = f.read().strip()
            
            if not description:
                print(f"警告: '{subdir_name}' の name.txt が空です。スキップします。")
                continue

            # モジュール実行なしで情報を格納
            info = TaskModuleInfo(
                name=subdir_name,
                description=description,
                main_py_path=main_py_path,
                module_id=f"{subdir_name}_main" # 一意なID
            )
            task_infos.append(info)
            print(f"'{subdir_name}' のメタデータを name.txt から取得しました: '{description}'")
            
        except Exception as e:
            print(f"エラー: '{subdir_name}' の name.txt 読み込み中に例外が発生しました: {e}")

    return task_infos

# --- 使用例 ---

if __name__ == '__main__':
    # ... (テストディレクトリのセットアップコードは省略) ...
    test_dir = "test_tasks_txt"
    # ※ このコードを実行するには、上記のテストディレクトリ作成が必要です。

    print(f"--- タスク情報のリストアップフェーズ ---")
    # 情報リストを取得 (この時点ではmain.pyは実行されていない)
    task_list = get_task_info_list(test_dir)

    print("\n--- ユーザー提示フェーズ ---")
    for i, task_info in enumerate(task_list):
        print(f"ID: {i}, 名前: {task_info.name}, 識別名: {task_info.description}")

    # ユーザーが特定のタスクを選んだと仮定 (例: 最初のタスク)
    if task_list:
        print("\n--- 遅延読み込みフェーズ (ID 0を選択) ---")
        selected_task_info = task_list[0] # リストの最初の要素を選択
        print(f"'{selected_task_info.name}' を実行するためにモジュールをロードします...")
        
        # load_task_module 関数を使ってモジュールをロード
        loaded_module = load_task_module(selected_task_info)
        
        if loaded_module:
            print(f"モジュール '{loaded_module.__name__}' をロードしました。")
            loaded_module.main_proc()
        else:
            print("モジュールのロードに失敗したため、実行できませんでした。")
