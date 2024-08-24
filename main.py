import datetime
import random
from py_binarsi import Move, MoveHelper, Board


class UsiEngine():
    """USIエンジン"""


    def __init__(self):
        """初期化"""

        # 盤
        self._board = Board()


    def usi_loop(self):
        """USIループ"""

        while True:

            # 入力
            input_str = input()
            cmd = input_str.split(' ', 1)

            # USI握手
            if cmd[0] == 'usi':
                self.usi()

            # 対局準備
            elif cmd[0] == 'isready':
                self.isready()

            # 新しい対局
            elif cmd[0] == 'usinewgame':
                self.usinewgame()

            # 局面データ解析
            elif cmd[0] == 'position':
                self.position(cmd)

            # 思考開始～最善手返却
            elif cmd[0] == 'go':
                self.go()

            # 中断
            elif cmd[0] == 'stop':
                self.stop()

            # 対局終了
            elif cmd[0] == 'gameover':
                self.gameover(cmd)

            # アプリケーション終了
            elif cmd[0] == 'quit':
                break

            # 以下、独自拡張

            # 一手指す
            #   code: do 4n
            elif cmd[0] == 'do':
                self.do(cmd)

            # 逆操作コードの表示
            #   code: inverse 4n
            elif cmd[0] == 'inverse':
                self.print_inverse_move(
                    move_u=cmd[1])

            # 一手戻す
            #   code: undo
            elif cmd[0] == 'undo':
                self.undo()

            # 盤表示
            #   code: board
            elif cmd[0] == 'board':
                self.print_board()

            # 合法手一覧表示
            #   code: legal_moves
            elif cmd[0] == 'legal_moves':
                self.print_legal_moves()

            # 編集用の手一覧表示（合法手除く）
            #   code: moves_for_edit
            elif cmd[0] == 'moves_for_edit':
                self.print_moves_for_edit()

            # 自己対局
            #   code: selfmatch
            #   code: selfmatch 100
            #
            #   FIXME position startpos まで打ってから selfmatch を打つことを想定。もっと簡単にできないか？
            elif cmd[0] == 'selfmatch':
                self.self_match(input_str)

            # SFENを出力
            #   code: sfen
            elif cmd[0] == 'sfen':
                self.print_sfen()

            # 操作履歴を出力
            #   code: history
            elif cmd[0] == 'history':
                self.print_history()


    def usi(self):
        """usi握手"""

        # エンジン名は別ファイルから読込。pythonファイルはよく差し替えるのでデータは外に出したい
        try:
            file_name = "engine_name.txt"
            with open(file_name, 'r', encoding="utf-8") as f:
                engine_name = f.read().strip()

        except FileNotFoundError as ex:
            print(f"[usi engine > usi] '{file_name}' file not found.  ex:{ex}")
            raise

        print(f'id name {engine_name}')
        print('usiok', flush=True)


    def isready(self):
        """対局準備"""
        print('readyok', flush=True)


    def usinewgame(self):
        """新しい対局"""
        # 盤をクリアー
        self._board.clear()
        print(f"[{datetime.datetime.now()}] usinewgame end", flush=True)


    def position(self, cmd):
        """局面データ解析"""
        pos = cmd[1].split('moves')
        sfen_text = pos[0].strip()
        # 区切りは半角空白１文字とします
        moves_text = (pos[1].split(' ') if len(pos) > 1 else [])
        self.position_detail(sfen_text, moves_text)


    def position_detail(self, sfen_u, move_u_list):
        """局面データ解析

        Parameters
        ----------
        sfen_u : str
            SFEN文字列
        move_u_list : list
            盤面編集履歴。実体は指し手コードの空白区切りリスト。対局棋譜のスーパーセット
        """

        # 平手初期局面に変更
        if sfen_u == 'startpos':
            self._board.reset()

        # 指定局面に変更
        elif sfen_u[:5] == 'sfen ':
            self._board.set_sfen(sfen_u[5:])
        
        else:
            raise ValueError(f"unsupported position  {sfen_u=}")


        # 初期局面を記憶（SFENで初期局面を出力したいときのためのもの）
        self._board.update_squares_at_init()


        # 盤面編集履歴（対局棋譜のスーパーセット）再生
        for move_u in move_u_list:
            self._board.push_usi(move_u)


    def go(self):
        """思考開始～最善手返却"""

        if self._board.is_gameover():
            """投了局面時"""

            # 投了
            print(f'bestmove resign', flush=True)
            return

        # ビナーシに入玉はありません

        # 一手詰めを詰める
        if not self._board.is_check():
            """自玉に王手がかかっていない時で"""

            if (matemove := self._board.mate_move_in_1ply()):
                """一手詰めの指し手があれば、それを取得"""

                best_move_u = matemove.to_code()
                print('info score mate 1 pv {}'.format(best_move_u), flush=True)
                print(f'bestmove {best_move_u}', flush=True)
                return

        # 投了のケースは対応済みなので、これ以降は指し手が１つ以上ある

        # １手指す
        best_move = random.choice(list(self._board.legal_moves))

        print(f"info depth 0 seldepth 0 time 1 nodes 0 score cp 0 string I'm random move")
        print(f'bestmove {best_move.to_code()}', flush=True)


    def stop(self):
        """中断"""
        print('bestmove resign', flush=True)


    def gameover(self, cmd):
        """対局終了"""

        if 2 <= len(cmd):
            # 負け
            if cmd[1] == 'lose':
                print("（＞＿＜）負けた")

            # 勝ち
            elif cmd[1] == 'win':
                print("（＾▽＾）勝ったぜ！")

            # 持将棋
            elif cmd[1] == 'draw':
                print("（ー＿ー）持将棋か～")

            # その他
            else:
                print(f"（・＿・）何だろな？：'{cmd[1]}'")


    def do(self, cmd):
        """一手指す

        Parameters
        ----------
        cmd : list
            例： ["do", "4n"]
        """
        self._board.push_usi(cmd[1])

        # 現在の盤表示
        self.print_board()
        self.print_sfen(from_present=True)
        print("") # 空行


    def print_inverse_move(self, move_u):
        """逆操作コードの表示

        Parameters
        ----------
        move_u : str
            指し手コード
            例： "4n"
            例： "dn$01"
        """

        move = Move.code_to_obj(move_u)
        inverse_move = MoveHelper.inverse_move(
            board=self._board,
            move=move)

        if inverse_move is None:
            print(f"[print_inverse_move] 未実装： {inverse_move=}")
            return

        # 表示
        print(f"{move_u} --inverse--> {inverse_move.to_code()}")


    def undo(self):
        """一手戻す
            code: undo
        """
        self._board.pop()

        # 現在の盤表示
        self.print_board()
        self.print_sfen(from_present=True)
        print("") # 空行


    def print_board(self):
        """盤表示
            code: board
        """
        print(self._board.as_str())


    def print_legal_moves(self):
        """合法手一覧表示
            code: legal_moves
        """
        print("""\
LEGAL MOVES
-----------""")

        # コードで降順にソートする
        move_list = sorted(self._board.legal_moves, key=lambda x:x.to_code())

        for i in range(0, len(move_list)):
            move = move_list[i]
            print(f"    ({i + 1:2}) do {move.to_code()}")

        print("""\
-----------
""")


    def print_moves_for_edit(self):
        """編集用の手一覧表示（合法手除く）
            code: moves_for_edit
        """
        print("編集用の手一覧表示（合法手除く）　ここから：")

        for i in range(0, len(self._board.moves_for_edit)):
            move = self._board.moves_for_edit[i]
            print(f"    ({i + 1:2}) move_for_edit:{move.to_code()}")

        print("編集用の手一覧表示（合法手除く）　ここまで：")


    def print_history(self):
        """履歴表示
            code: history
        """
        print("""\
HISTORY
-------
    番号： (対局棋譜番号|盤面編集番号）
    凡例： `&` - 対局棋譜ではなく盤面編集の操作を示す
    　　： `$` - 上書された石の並びを示す""")

        moves_num = 0

        for i in range(0, len(self._board.board_editing_history.items)):
            board_editing_item = self._board.board_editing_history.items[i]
            move = board_editing_item.move

            if not move.when_edit:
                moves_num += 1
                sequence_number_str = f'{moves_num:2}|{i + 1:2}'
            else:
                sequence_number_str = f'  |{i + 1:2}'

            stones_before_change = board_editing_item.stones_before_change

            if stones_before_change == '':
                stones_before_change = '-'

            print(f"    ({sequence_number_str}) move:{move.to_code()} ${stones_before_change}")

        print("""\
-------
""")


    def self_match_once(self, match_count):
        """自己対局"""

        print(f"{match_count + 1} 局目ここから：")

        # 100手も使わない
        for i in range(1, 100):

            if self._board.is_gameover():
                print("# gameover")
                break

            # １つ選ぶ
            best_move = random.sample(self._board.legal_moves, 1)[0]

            # １手指す
            self._board.push_usi(best_move.to_code())

            # 現在の盤表示
            self.print_board()
            self.print_sfen(from_present=True)
            print("") # 空行

        print(f"{match_count + 1} 局目ここまで")


    def self_match(self, input_str):
        """自己対局
            code: selfmatch
        
        Parameters
        ----------
        input_str : str
            コマンド文字列
        """
        print("自己対局　ここから：")

        # 現在の盤表示
        self.print_board()
        self.print_sfen(from_present=True)
        print("") # 空行

        # 連続対局回数
        tokens = input_str.split(' ')
        if len(tokens) < 2:
            max_match_count = 1
        else:
            max_match_count = int(tokens[1])
        
        black_win_count = 0
        white_win_count = 0
        no_game_count = 0

        # 連続対局
        for i in range(0, max_match_count):

            self.usinewgame()
            self.position(['position', 'startpos'])

            # 自己対局
            self.self_match_once(match_count=i)

            if self._board.gameover_reason == 'black win':
                black_win_count += 1

            elif self._board.gameover_reason == 'white win':
                white_win_count += 1
            
            else:
                no_game_count += 1

        total = black_win_count + white_win_count + no_game_count

        print(f"""\
自己対局　ここまで：
    黒勝ち： {black_win_count:6} 黒勝率： {black_win_count/total:3.3f}
    白勝ち： {white_win_count:6} 白勝率： {white_win_count/total:3.3f}
    無効　： {no_game_count:6} 無効率： {no_game_count/total:3.3f}
""")


    def print_sfen(self, from_present=False):
        """SFEN を出力

        Parameters
        ----------
        from_present : bool
            現局面からのSFENにしたいなら真。初期局面からのSFENにしたいなら偽
        """
        print(f"[from beginning] sfen {self._board.as_sfen()}")

        stone_before_change_str = self._board.as_stones_before_change()
        if stone_before_change_str != '':
            print(f"                 stones_before_change {stone_before_change_str}")

        print(f"[from present]   sfen {self._board.as_sfen(from_present=True)}")

        stone_before_change_str = self._board.as_stones_before_change(from_present=True)
        if stone_before_change_str != '':
            print(f"                 stones_before_change {stone_before_change_str}")


if __name__ == '__main__':
    """コマンドから実行時"""
    try:
        usi_engine = UsiEngine()
        usi_engine.usi_loop()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise

