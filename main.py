import datetime
import random
import time
from py_binarsi import C_EMPTY, C_BLACK, C_WHITE, CLEAR_TARGETS_LEN, Colors, Move, MoveHelper, Board, Search


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
                self.position(input_str)

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
                self.print_inverse_move(input_str)

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

            # クリアーターゲットを出力
            #   code: clear_targets
            elif cmd[0] == 'clear_targets':
                self.print_clear_targets()

            # プレイ
            #   code: play 4n
            elif cmd[0] == 'play':
                self.play(input_str)

            # デバッグ情報表示
            #   code: dump
            elif cmd[0] == 'dump':
                self.dump()

            # １手詰めがあれば、その手をどれか１つ表示
            #   code: mate1
            elif cmd[0] == 'mate1':
                self.print_mate1()

            # 動作テスト
            #   code: test
            elif cmd[0] == 'test':
                self.test()


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


    def position(self, input_str):
        """局面データ解析"""

        cmd = input_str.split(' ', 1)

        # 余計な半角空白は入っていない前提
        pos_list = cmd[1].split(' moves ')
        sfen_text = pos_list[0]

        #print(f"[position] {pos_list=}")

        # 区切りは半角空白１文字とします
        move_u_list = (pos_list[1].split(' ') if len(pos_list) > 1 else [])

        #print(f"[position] {move_u_list=}")

        self.position_detail(sfen_text, move_u_list)


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


    def sub_go(self, search):
        """思考開始～最善手返却
        
        Parameters
        ----------
        search : Search
            探索部

        Returns
        -------
        best_move : Move
            最善手。投了なら None
        reason : str
            説明
        """

        if self._board.is_gameover(search):
            """投了局面時"""

            # 投了
            return None, 'resign'

        # ビナーシに入玉はありません

        # ビナーシに王手はありません

        # 一手詰めを詰める
        if (matemove := search.mate_move_in_1ply(self._board)):
            """一手詰めの指し手があれば、それを取得"""
            return matemove, 'mate 1 move'

        # 投了のケースは対応済みなので、これ以降は指し手が１つ以上ある
        
        move_list = search.legal_moves.distinct_items

        # ランダムムーブ
        is_random_move = False

        if is_random_move:
            # １手指す
            def go_random_move(move_list):
                """ランダム・ムーブ"""
                best_move = random.choice(move_list)
                return best_move, 'best move'


            return go_random_move(move_list)


        else:
            # ［利］が正の数の指し手のリスト
            positive_move_list = []

            # ［利］が零の指し手のリスト
            come_out_even_move_list = []

            # ［利］が負の数の指し手のリスト
            negative_move_list = []

            for move in move_list:

                # DO 対象となる路の石（または空欄）の長さを測る
                way_segment = self._board.get_stone_segment_on_way(move.way)

                # DO （１手指す前の）対象となる路の石（または空欄）の並びを取得
                current_colors = self._board.get_colors_on_way(move.way, way_segment)

                # DO （１手指す前の）対象路の色を数える
                current_color_count = {
                    C_EMPTY : 0,
                    C_BLACK : 0,
                    C_WHITE : 0,
                }

                for color in current_colors:
                    current_color_count[color] += 1

                # DEBUG
                #print(f"[sub_go]  {move.to_code()=}  {current_colors=}  {current_color_count=}")

                # DO １手指す
                self._board.push_usi(move.to_code())

                # DO （１手指した後の）対象となる路の石（または空欄）の並びを取得
                next_colors = self._board.get_colors_on_way(move.way, way_segment)

                # DO （１手指した後の）対象路の色を数える
                next_color_count = {
                    C_EMPTY : 0,
                    C_BLACK : 0,
                    C_WHITE : 0,
                }

                for color in next_colors:
                    next_color_count[color] += 1

                # DEBUG
                #print(f"[sub_go]  {move.to_code()=}  {next_colors=}  {next_color_count=}")

                # DO １手戻す
                self._board.pop()

                # DO 手番の石の差分から、相手番の石の差分を引く。これを［利］と呼ぶとする

                # DO １手指した後の石の数から、１手指す前の石の数を引く。これを差分とする
                difference_color_count = {
                    C_EMPTY : next_color_count[C_EMPTY] - current_color_count[C_EMPTY],
                    C_BLACK : next_color_count[C_BLACK] - current_color_count[C_BLACK],
                    C_WHITE : next_color_count[C_WHITE] - current_color_count[C_WHITE],
                }

                # DEBUG
                #print(f"[sub_go]  {move.to_code()=}  {difference_color_count=}")

                # DO ［利］が正のもの、零のもの、負のものに分けて、それぞれのリストに追加する
                # 石の［利］を調べる
                profit = 0

                # DEBUG
                #print(f"[sub_go]  {move.to_code()=}  {self._board.get_next_turn()=}")

                if self._board.get_next_turn() == C_BLACK:
                    profit = difference_color_count[C_BLACK] - difference_color_count[C_WHITE]

                else:
                    profit = difference_color_count[C_WHITE] - difference_color_count[C_BLACK]

                # DEBUG
                #print(f"[sub_go]  {move.to_code()=}  {profit=}")

                # ［利］が正の数の指し手のリスト
                if 0 < profit:
                    positive_move_list.append(move)

                # ［利］が零の指し手のリスト
                elif profit == 0:
                    come_out_even_move_list.append(move)

                # ［利］が負の数の指し手のリスト
                else:
                    negative_move_list.append(move)


            # DO 利が正の指し手のリストが空でなければ、そこから１つ選んで返す。ここで関数終了
            if 0 < len(positive_move_list):
                best_move = random.choice(positive_move_list)
                return best_move, 'best move'

            # DO 利が零の指し手のリストが空でなければ、そこから１つ選んで返す。ここで関数終了
            if 0 < len(come_out_even_move_list):
                best_move = random.choice(come_out_even_move_list)
                return best_move, 'best move'

            # DO 利が負の指し手のリストが空でなければ、そこから１つ選んで返す。ここで関数終了
            best_move = random.choice(negative_move_list)
            return best_move, 'best move'


    def go(self):
        """思考開始～最善手返却"""

        search = Search(self._board)

        # 次の１手取得
        (best_move, reason) = self.sub_go(search)

        if reason == 'resign':
            # 投了
            print(f'bestmove resign', flush=True)
            return

        # ビナーシに入玉はありません

        # 一手詰めを詰める
        if reason == 'mate 1 move':
            best_move_u = best_move.to_code()
            print('info score mate 1 pv {}'.format(best_move_u), flush=True)
            print(f'bestmove {best_move_u}', flush=True)
            return

        # １手指す
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


    def sub_do(self, move_u):
        """一手指す

        Parameters
        ----------
        move_u : str
            例： "4n"
        """
        self._board.push_usi(move_u)


    def do(self, cmd):
        """一手指す　～　盤表示

        Parameters
        ----------
        cmd : list
            例： ["do", "4n"]
        """

        move_u = cmd[1]

        if not Move.validate_code(move_u, no_panic=True):
            print("illegal move")
            return

        self.sub_do(move_u)

        # 現在の盤表示
        self.print_board()
        self.print_sfen(from_present=True)
        print("") # 空行


    def print_inverse_move(self, input_str):
        """逆操作コードの表示

        Parameters
        ----------
        input_str : str
            指し手コード
            例： "inverse 4n"
            例： "inverse 3e#0 0"
        """

        tokens = input_str.split(' ')

        move_u = tokens[1]

        if 2 < len(tokens):
            stones_before_change = tokens[2]
        else:
            stones_before_change = ''

        Move.validate_code(move_u)
        move = Move.code_to_obj(move_u)

        inverse_move = MoveHelper.inverse_move(
            board=self._board,
            move=move,
            stones_before_change=stones_before_change)

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
+--------+---+
|Distinct|All|
+--------+---+""")

        search = Search(self._board)

        # 指した結果が同じになるような指し手も表示する
        # コードをキーにして降順にソートする
        legal_move_list = sorted(search.legal_moves.items, key=lambda x:x.to_code())

        # 冗長な指し手を省いた通し番号
        j = 0

        for i in range(0, len(legal_move_list)):
            move = legal_move_list[i]

            #print(f"    <{i+1:2}>  {move.to_code()}  {move.same_move_u=}")

            if move.same_move_u != '':
                same_move_str = f' | same {move.same_move_u}'
                num_str = f'        |{i+1:3}'

            else:
                same_move_str = ''
                num_str = f'{j+1:8}|{i+1:3}'
                j += 1

            print(f"|{num_str}| do {move.to_code():<3}{same_move_str}")

        print("""\
+--------+---+
""")


    def print_moves_for_edit(self):
        """編集用の手一覧表示（合法手除く）
            code: moves_for_edit
        """
        print("編集用の手一覧表示（合法手除く）　ここから：")

        search = Search(self._board)

        for i in range(0, len(search.legal_moves.items_for_edit)):
            move = search.legal_moves.items_for_edit[i]
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


    def print_clear_targets(self):
        """クリアーターゲットの一覧表示"""

        # Top と Bottom
        disp1 = ['             '] * CLEAR_TARGETS_LEN
        disp2 = ['    WANTED   '] * CLEAR_TARGETS_LEN

        for i in range(0, CLEAR_TARGETS_LEN):
            if self._board._clear_targets_list[i] != -1:
                disp1[i] = f' CLEAR in {self._board._clear_targets_list[i]:2} '
                disp2[i] = '             '

        print(f"""\
CLEAR TARGETS
----------------------------------------------------------------------------------------

     [b3]           [b4]           [b5]           [w3]           [w4]           [w5]
+-----------+  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+
| . . . . . |  | 1 . . . . |  | . . 1 . . |  | . . . . . |  | 0 . . . . |  | . . . . . |
| . . . . . |  | . 1 . . . |  | . . 1 . . |  | . . 0 . . |  | . 0 . . . |  | . . . . . |
| . 1 1 1 . |  | . . 1 . . |  | . . 1 . . |  | . . 0 . . |  | . . 0 . . |  | 0 0 0 0 0 |
| . . . . . |  | . . . 1 . |  | . . 1 . . |  | . . 0 . . |  | . . . 0 . |  | . . . . . |
| . . . . . |  | . . . . . |  | . . 1 . . |  | . . . . . |  | . . . . . |  | . . . . . |
+-----------+  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+
{disp1[0]:13}  {disp1[1]:13}  {disp1[2]:13}  {disp1[3]:13}  {disp1[4]:13}  {disp1[5]:13}
{disp2[0]:13}  {disp2[1]:13}  {disp2[2]:13}  {disp2[3]:13}  {disp2[4]:13}  {disp2[5]:13}

----------------------------------------------------------------------------------------
""")


    def self_match_once(self, match_count):
        """自己対局"""

        print(f"{match_count + 1} 局目ここから：")

        # 100手も使わない
        for i in range(1, 100):

            search = Search(self._board)

            if self._board.is_gameover(search):
                print("# gameover")
                break

            # １つ選ぶ
            (best_move, reason) = self.sub_go(search)

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
            self.position('position startpos')

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
        print(f"[from beginning] sfen {self._board.as_sfen().to_code()}")

        stone_before_change_str = self._board.as_stones_before_change()
        if stone_before_change_str != '':
            print(f"                 stones_before_change {stone_before_change_str}")

        print(f"[from present]   sfen {self._board.as_sfen(from_present=True).to_code()}")

        stone_before_change_str = self._board.as_stones_before_change(from_present=True)
        if stone_before_change_str != '':
            print(f"                 stones_before_change {stone_before_change_str}")


    def print_0(self):
        print("""\
     ________
    /   __   |
    |  /  |  |
    |  |  |  |
    |  |  |  |
    |  |_/   |
    |_______/""", flush=True)


    def print_1(self):
        print("""\
       ___
      /   |
     /    |
    |__   |
      |   |
      |   |
      |___|""", flush=True)


    def print_comp(self):
        print("""\
     ________   ________    ______  ______   ________
    /   ____|  /   __   |  |   __ |/ __   |  |   __  |
    |  /       |  |  |  |  |  |  |  |  |  |  |  |  |  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  |__/  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  _____/
    |  |____   |  |_/   |  |  |  |  |  |  |  |  |
    |_______|  |_______/   |__|  |__|  |__|  |__|""", flush=True)


    def print_you(self):
        print("""\
     __     ___   ________    __    __ 
    |  |   /  /  /   __   |  |  |  |  |
    |  |__/  /   |  |  |  |  |  |  |  |
    |__    _/    |  |  |  |  |  |  |  |
       |  |      |  |  |  |  |  |  |  |
       |  |      |  |_/   |  |  |_/   |
       |__|      |_______/   |_______/""", flush=True)


    def print_win(self):
        print("""\
     __     ___     ___   ___   ____      __ 
    |  |   /   |   /  /  /  |  |    |    |  |
    |  |  /    |  /  /   |_/   |     |   |  |
    |  | /     | /  /     __   |  |   |  |  |
    |  |/  /|  |/  /     |  |  |  ||   | |  |
    |     / |     /      |  |  |  | |   ||  |
    |____/  |____/       |__|  |__|  |______|""", flush=True)


    def print_lose(self):
        print("""\
     __          ________    _______    ________
    |  |        /   __   |  /   ____|  |   __   |
    |  |        |  |  |  |  |  /____   |  |__|  |
    |  |        |  |  |  |  |____   |  |   _____/
    |  |_____   |  |  |  |       |  |  |  |   ___
    |        |  |  |_/   |   ___/   /  |  |__/  /
    |________|  |_______/   |______/   |_______/""", flush=True)



    def play(self, input_str):
        """一手入力すると、相手番をコンピュータが指してくれる"""

        # 待ち時間（秒）を置く。ターミナルの行が詰まって見づらいので、イラストでも挟む
        if self._board.get_next_turn() == C_BLACK:
            self.print_1()
        else:
            self.print_0()

        time.sleep(0.7)

        # DO 一手指す
        move_u = input_str.split(' ')[1]

        if not Move.validate_code(move_u, no_panic=True):
            print("illegal move")
            return

        self.sub_do(move_u)

        # 現在の盤表示
        self.print_board()
        self.print_sfen(from_present=True)
        print("") # 空行


        def print_clear_target_if_it_now():
            """今クリアーしたものがあれば、クリアー目標表示"""
            one_cleared = False
            for clear_target in self._board.clear_targets_list:
                if clear_target == self._board.moves_number:
                    one_cleared = True
                    break
            
            if one_cleared:
                self.print_clear_targets()
                time.sleep(0.7)

        # 今クリアーしたものがあれば、クリアー目標表示
        print_clear_target_if_it_now()

        def print_if_end_of_game():
            current_turn = Colors.Opponent(self._board.get_next_turn())
            
            if self._board.gameover_reason == 'black win':
                if current_turn == C_BLACK:
                    self.print_you()
                    self.print_win()
                
                elif current_turn == C_WHITE:
                    self.print_you()
                    self.print_lose()

            elif self._board.gameover_reason == 'white win':
                if current_turn == C_BLACK:
                    self.print_you()
                    self.print_lose()
                
                elif current_turn == C_WHITE:
                    self.print_you()
                    self.print_win()

            elif self._board.gameover_reason == 'draw (illegal move)':
                self.print_lose()

            elif self._board.gameover_reason == 'stalemate':
                self.print_lose()
            
            else:
                raise ValueError(f"undefined gameover. {self._board.gameover_reason=}")


        search = Search(self._board)

        if self._board.is_gameover(search):
            print_if_end_of_game()
            return

        # 待ち時間（秒）を置く。コンピュータの思考時間を演出。ターミナルの行が詰まって見づらいので、イラストでも挟む
        time.sleep(0.7)
        self.print_comp()
        time.sleep(0.7)

        # DO コンピュータが次の一手を算出する
        (best_move, reason) = self.sub_go(search)

        if best_move is None:
            # ターミナルが見づらいので、空行を挟む
            self.print_win()
            return
        
        # ターミナルが見づらいので、イラストを挟む
        if self._board.get_next_turn() == C_BLACK:
            self.print_1()
        else:
            self.print_0()

        time.sleep(0.7)

        # DO コンピュータが一手指す
        self.sub_do(best_move.to_code())

        search = Search(self._board)

        # 現在の盤表示
        self.print_board()
        self.print_sfen(from_present=True)
        print("") # 空行

        # 今クリアーしたものがあれば、クリアー目標表示
        print_clear_target_if_it_now()

        if self._board.is_gameover(search):
            print_if_end_of_game()
            return

        # ターミナルが見づらいので、イラストを挟む
        time.sleep(0.7)
        self.print_you()


    def dump(self):
        """デバッグ情報表示"""
        print(f"[dump] {self._board._next_turn_at_init=}")


    def print_mate1(self):
        """TODO １手詰めがあれば、その手をどれか１つ表示"""

        search = Search(self._board)

        mate_move = search.legal_moves.get_mate_move_in_1ply(self._board)

        if mate_move is None:
            print(f"there is no checkmate")
            return

        print(mate_move.to_code())


    def test(self):
        """TODO 動作テスト"""

        print("TODO 動作テスト")

        self.usi()
        self.isready()
        self.usinewgame()
        self.position('position sfen 7/7/2o4/7/7/7 w - - 1 moves 4n')
        self.print_board()

        search = Search(self._board)

        # 指し手のリストから冗長な指し手を省き、さらにコードをキーにして降順にソートする
        actual_move_list = sorted(search.legal_moves.distinct_items, key=lambda x:x.to_code())

        # FIXME 間違ってる
        expected_move_u_list = [
            '2a',
            '2n',
            # '2na'
            # '2no'
            # '2o',
            # '2xn',
            # '2xo',
            '3nH',
            # '4nL',
            # '5a',
            '5n',
            # '5na',
            # '5no',
            '5o',
            # '5xn', 
            # '5xo',
            'bn',
            'cs1',
            'dn',
        ]


        if len(actual_move_list) != len(expected_move_u_list):
            print(f"error  {len(actual_move_list)=}  {len(expected_move_u_list)=}")


        for i in range(0, len(actual_move_list)):
            actual_move = actual_move_list[i]
            expected_move_u = expected_move_u_list[i]

            if actual_move.to_code() == expected_move_u:
                print(f"ok  {actual_move.to_code()}")

            else:
                print(f"error  {actual_move.to_code()=}  {expected_move_u=}")


if __name__ == '__main__':
    """コマンドから実行時"""
    try:
        usi_engine = UsiEngine()
        usi_engine.usi_loop()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise

