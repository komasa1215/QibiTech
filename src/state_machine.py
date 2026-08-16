from __future__ import annotations
import json

class State:
    """
    @brief 「状態」を表すクラス
    """
    def __init__(self, name: str, parent: str) -> None:
        """
        @brief コンストラクタ
        @param name 状態の名称
        @param parent  状態の親状態の名称
        @return None
        """
        self._name: str = name
        self._parent: str = parent
        self._children: list[str] = []
        self._default_child_idx: int = -1
        self._transitions: list[Transition] = []
        self._entry_activity: str = "print(f'[{self.get_name()}] on entry()')"
        self._while_activity: str = "print(f'[{self.get_name()}] on while()')"
        self._exit_activity: str  = "print(f'[{self.get_name()}] on exit()')"

    def get_name(self) -> str:
        """
        @brief  状態の名称取得
        @param  なし
        @return  状態の名称
        """
        return self._name

    def get_parent_name(self) -> str:
        """
        @brief  親状態の名称取得
        @param  なし
        @return  親状態の名称
        """
        return self._parent

    def get_default_child_name(self) -> str:
        """
        @brief デフォルトの子状態の名称取得
        @param なし
        @return デフォルトの子状態の名称
        @warning  取得できない場合は None を返す
        """
        idx = self._default_child_idx
        if idx >= 0:
            return self._children[idx]
        return None

    def add_child(self, child: str, default: bool = False) -> None:
        """
        @brief 子状態の追加
        @param child 子状態の名称
        @param default デフォルトにするか/しないか
        @return なし
        """
        self._children.append(child)
        if default:
            self._default_child_idx = len(self._children) - 1

    def add_transition(self, transition: TransitionInfo) -> None:
        """
        @brief 状態遷移情報の追加
        @param transition 状態遷移情報
        @return なし
        """
        self._transitions.append(transition)

    def define_entry_activity(self, activity: list[str] ) -> None:
        """
        @brief エントリーアクティビティの定義
        @param activity エントリーアクティビティ
        @return なし
        """
        if len(activity) <= 0:
            return
        self._entry_activity = ""
        for tmp in activity:
            if len(self._entry_activity) > 0:
                self._entry_activity += '\n'
            self._entry_activity += tmp

    def define_while_activity(self, activity: list[str] ) -> None:
        """
        @brief ホワイルアクティビティの定義
        @param activity ホワイルアクティビティ
        @return なし
        """
        if len(activity) <= 0:
            return
        self._while_activity = ""
        for tmp in activity:
            if len(self._while_activity) > 0:
                self._while_activity += '\n'
            self._while_activity += tmp

    def define_exit_activity(self, activity: list[str] ) -> None:
        """
        @brief イグジットアクティビティの定義
        @param activity イグジットアクティビティ
        @return なし
        """
        if len(activity) <= 0:
            return
        self._exit_activity = ""
        for tmp in activity:
            if len(self._exit_activity) > 0:
                self._exit_activity += '\n'
            self._exit_activity += tmp

    def show(self) -> None:
        """
        @brief 内部情報表示
        @param なし
        @return なし
        @note  デバッグ用途
        """
        print(f"State: {self._name}")
        print(f"Parent: {self._parent}")
        print(f"Children: {[child_name for child_name in self._children]}")
        print(f"Default Child Index: {self._default_child_idx}")
        print(f"Transitions: {[(transition._target, transition._trigger) for transition in self._transitions]}")

    def on_entry_activity(self) -> None:
        """
        @brief エントリーアクティビティの実行
        @param なし
        @return なし
        """
       #print(f'[DEBUG] ENTRY {self.get_name()} {self._entry_activity}')
        exec(self._entry_activity)

    def on_while_activity(self) -> list[str]:
        """
        @brief ホワイルアクティビティの実行
        @param なし
        @return なし
        """
       #print(f'[DEBUG] WHILE {self.get_name()} {self._while_activity}')
        exec(self._while_activity)

    def on_exit_activity(self) -> None:
        """
        @brief イグジットアクティビティの実行
        @param なし
        @return なし
        """
       #print(f'[DEBUG] EXIT {self.get_name()} {self._exit_activity}')
        exec(self._exit_activity)

class TransitionInfo:
    """
    @brief 状態遷移情報クラス
    """
    def __init__(self, target: str, trigger: str) -> None:
        """
        @brief コンストラクタ
        @param target 遷移先の状態名
        @param trigger 状態遷移のトリガー(イベント)名
        @return なし
        """
        self._target = target
        self._trigger = trigger

    def condition(self) -> bool:
        """
        @brief 状態遷移のガード条件
        @param なし
        @return 遷移の許可判定(True:許可　False:不許可)
        """
        return True

class StateMachine:
    """
    @brief 状態遷移エンジンのクラス
    """
    def __init__(self) -> None:
        """
        @brief コンストラクタ
        @param なし
        @return なし
        """
        self._state_list: list[State] = []
        self._current_active_state_idx_list: list[int] = []
        self._next_active_state_idx_list: list[int] = []
        self._event_queue: list[str] = []

    def load_application(self, file_path: str) -> bool:
        """
        @brief アプリケーションファイルのロード
        @param file_path アプリケーションファイルのファイル名
        @return ロードの成功/失敗の結果
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

            # setup state transition
            self._state_list = self._create_state_list(data.get("states", []))
            self._next_active_state_idx_list = self._get_next_active_state_list("ROOT")
            if len(self._next_active_state_idx_list) == 0:
                return False
            return True

    def push_event(self, event: str) -> None:
        """
        @brief イベントのプッシュ(挿入)
        @param event イベント(ID)
        @return なし
        """
        self._event_queue.append(event)

    def pop_event(self) -> str:
        """
        @brief イベントのポップ(取り出し)
        @param なし
        @return イベント(ID)
        @warning イベントキューが空の場合は 'None' を返す。
        """
        if len(self._event_queue) > 0:
            return self._event_queue.pop(0)
        return None

    def start(self) -> None:
        """
        @brief 状態遷移エンジンの開始
        @param なし
        @return なし
        """
        self._execute_on_entry()
        self._current_active_state_idx_list = self._next_active_state_idx_list
        self._next_active_state_idx_list = []
        self._execute_on_while()

    def update(self) -> None:
        """
        @brief 状態遷移エンジンの更新
        @param なし
        @return なし
        """
        event = self.pop_event()
        if event != None:
            pivot_state_idx = self._check_transition(event)
            if pivot_state_idx != -1:
                pivot_state = self._state_list[pivot_state_idx]
                self._next_active_state_idx_list = self._get_next_active_state_list(pivot_state.get_name())

                self._execute_on_exit()
                self._execute_on_entry()

                self._current_active_state_idx_list = self._next_active_state_idx_list
                self._next_active_state_idx_list = []

        self._execute_on_while()

    def _create_state_list(self, data:dict) -> list[State]:
        """
        @brief オブジェクト生成
        @param data 生成オブジェクトのデータ
        @return 生成オブジェクトリスト
        """
        result: list[State] = []
        for state_data in data:
            # create State
            tmp = State(state_data["name"], state_data["parent"])
            # add state hierarchy
            default_child_idx = state_data["default_child"]
            for idx, child_name in enumerate(state_data["children"]):
                if idx == state_data["default_child"]:
                    tmp.add_child(child_name, True)
                else:
                    tmp.add_child(child_name)
            # add transition info
            for trans_data in state_data["transitions"]:
                trans = TransitionInfo(trans_data["target"], trans_data["trigger"])
                tmp.add_transition(trans)

            # define activity
            tmp.define_entry_activity(state_data["do_entry"])
            tmp.define_while_activity(state_data["do_while"])
            tmp.define_exit_activity(state_data["do_exit"])

            result.append(tmp)
        return result

    def _check_transition(self, event: str) -> int:
        """
        @brief イベントに対する状態遷移の判定
        @param event イベント
        @return 状態遷移の有無判定結果  負: 状態遷移なし その他: 状態遷移あり(遷移先状態の状態一覧のインデックス)
        """
        for idx in self._current_active_state_idx_list:
            state = self._state_list[idx]
            for transition in state._transitions:
                if transition._trigger == event and transition.condition():
                    idx = self._search_state_idx(transition._target)
                    if idx >= 0:
                        return idx
        return -1

    def _get_next_active_state_list(self, pivot_state: str) -> list[int]:
        """
        @brief アクティブな状態の一覧取得
        @param pivot_state  起点となる状態の名称
        @return アクティブな状態の一覧
        """
        tmp_list = []
        # add pivot state
        pivot_idx = self._search_state_idx(pivot_state)
        if pivot_idx < 0:
            return []
        tmp_list.append(pivot_idx)

        # add default children state
        state = self._state_list[pivot_idx]
        default_child_name = state.get_default_child_name()
        while default_child_name != None:
            idx = self._search_state_idx(default_child_name)
            tmp_list.append(idx)
            state = self._state_list[idx]
            default_child_name = state.get_default_child_name()

        # add parent state
        state = self._state_list[pivot_idx]
        parent_name = state.get_parent_name()
        while (parent_name != None) and (parent_name != ""):
            idx = self._search_state_idx(parent_name)
            tmp_list.insert(0, idx)
            state = self._state_list[idx]
            parent_name = state.get_parent_name()

        return tmp_list

    def _execute_on_entry(self) -> None:
        """
        @brief エントリーアクティビティの実行
        @param なし
        @return なし
        """
        # self._next_active_state_idx_listにしかない要素を抽出
        on_entry_list = [x for x in self._next_active_state_idx_list if x not in self._current_active_state_idx_list]
        for idx in on_entry_list:
            state = self._state_list[idx]
            state.on_entry_activity()

    def _execute_on_while(self) -> None:
        """
        @brief ホワイルアクティビティの実行
        @param なし
        @return なし
        """
        for idx in self._current_active_state_idx_list:
            state = self._state_list[idx]
            state.on_while_activity()

    def _execute_on_exit(self) -> None:
        """
        @brief イグジットアクティビティの実行
        @param なし
        @return なし
        """
        # self._current_active_state_idx_listにしかない要素を抽出
        on_exit_list = [x for x in self._current_active_state_idx_list if x not in self._next_active_state_idx_list]
        for idx in on_exit_list:
            state = self._state_list[idx]
            state.on_exit_activity()

    def _search_state_idx(self, state_name: str) -> int:
        """
        @brief 状態名称による状態一覧の探索
        @param state_name 状態の名称
        @return 状態一覧のインデックス
        """
        for idx, state in enumerate(self._state_list):
            if state.get_name() == state_name:
                return idx
        return -1

    def show(self) -> None:
        """
        @brief デバッグ用情報の表示
        @param なし
        @return なし
        """
        print(f'State List:')
        for state in self._state_list:
            print(f'\t{state.get_name()}')
        print(f'Current Active State List:')
        for idx in self._current_active_state_idx_list:
            print(f'\t{self._state_list[idx].get_name()}')
        print(f'Next Active State List:')
        for idx in self._next_active_state_idx_list:
            print(f'\t{self._state_list[idx].get_name()}')

if __name__ == "__main__":
    import time

    sm = StateMachine()
    result = sm.load_application('application.json')
    print(f'load_application : {result}')
    sm.show()

    event_list = ["SW_ON", "BTN_PUSH", "BTN_PUSH", "SW_OFF"]
    sm.start()
    for ev in event_list:
        print(f'\nEVENT: {ev}')
        sm.push_event(ev)
        sm.update()
        time.sleep(1)
