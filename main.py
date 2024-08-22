import datetime
import random
from py_binarsi import Board


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
            cmd = input().split(' ', 1)

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
            # example: ７六歩
            #       code: do 7g7f
            elif cmd[0] == 'do':
                self.do(cmd)

            # 一手戻す
            #       code: undo
            elif cmd[0] == 'undo':
                self.undo()

            # 盤表示
            #       code: board
            elif cmd[0] == 'board':
                self.print_board()

            # 合法手一覧表示
            #       code: legal_moves
            elif cmd[0] == 'legal_moves':
                self.print_legal_moves()

            # 自己対局
            #       code: selfmatch
            elif cmd[0] == 'selfmatch':
                self.self_match()

            # SFENを出力
            #       code: sfen
            elif cmd[0] == 'sfen':
                self.print_sfen()


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

        # 盤面編集履歴（対局棋譜のスーパーセット）再生
        for move_u in move_u_list:
            self._board.push_usi(move_u)


    def go(self):
        """思考開始～最善手返却"""

        if self._board.is_game_over():
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

                best_move = cshogi.move_to_code(matemove)
                print('info score mate 1 pv {}'.format(best_move), flush=True)
                print(f'bestmove {best_move}', flush=True)
                return

        # 投了のケースは対応済みなので、これ以降は指し手が１つ以上ある

        # １手指す
        best_move = cshogi.move_to_code(random.choice(list(self._board.legal_moves)))

        print(f"info depth 0 seldepth 0 time 1 nodes 0 score cp 0 string I'm random move")
        print(f'bestmove {best_move}', flush=True)


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
        cmd : str
            例： "do", "4n"
        """
        self._board.push_usi(cmd[1])

        # 盤表示
        self.print_board()
        self.print_sfen()
        print("") # 空行


    def undo(self):
        """一手戻す
            code: undo
        """
        self._board.pop()


    def print_board(self):
        """盤表示
            code: board
        """
        print(self._board.as_str())


    def print_legal_moves(self):
        """合法手一覧表示
            code: legal_moves
        """
        print("合法手一覧表示　ここから：")

        for i in range(0, len(self._board.legal_moves)):
            move = self._board.legal_moves[i]
            print(f"    ({i + 1:2}) move:{move.to_code()}")

        print("合法手一覧表示　ここまで：")


    def self_match(self):
        """自己対局
            code: selfmatch
        """
        print("自己対局　ここから：")

        # 盤表示
        self.print_board()
        self.print_sfen()
        print("") # 空行

        for i in range(1, 100):

            if len(self._board.legal_moves) < 1:
                print("合法手なし")
                break

            # １つ選ぶ
            best_move = random.sample(self._board.legal_moves, 1)[0]

            # １手指す
            self._board.push_usi(best_move.to_code())

            # 盤表示
            self.print_board()
            self.print_sfen()
            print("") # 空行

        print("自己対局　ここまで：")


    def print_sfen(self):
        """SFEN を出力"""
        print(f"sfen {self._board.as_sfen()}")
        print(f"stones_before_change {self._board.as_stones_before_change()}")


if __name__ == '__main__':
    """コマンドから実行時"""
    try:
        usi_engine = UsiEngine()
        usi_engine.usi_loop()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise

