import datetime
import random
import time
from py_binarsi import BLACK_KOMI, WHITE_KOMI, C_EMPTY, C_BLACK, C_WHITE, CLEAR_TARGETS_LEN, Colors, Move, MoveHelper, Board, SearchedClearTargets, SearchLegalMoves, SearchMateMoveIn1Play, SearchedGameover, PositionCommand
from views import Views
from views.board import BoardViews


# 思考エンジンの名前が書かれたテキストファイル
_engine_name_file_path = "usi_engine/engine_name.txt"


class UsiEngine():
    """USIエンジン"""


    def __init__(self):
        """初期化"""

        # 盤
        self._board = Board()


    def usi_loop(self):
        """USIループ"""

        # 終局判定を新規作成
        searched_clear_targets = SearchedClearTargets.make_new_obj()

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
                searched_clear_targets = self.position(input_str)
                if searched_clear_targets is None:
                    raise ValueError("searched_clear_targets is None")

            # 思考開始～最善手返却
            elif cmd[0] == 'go':
                self.go(searched_clear_targets)

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
                searched_clear_targets = self.do(cmd, searched_clear_targets)
                if searched_clear_targets is None:
                    raise ValueError("searched_clear_targets is None")

            # 一手戻す
            #   code: undo
            elif cmd[0] == 'undo':
                searched_clear_targets = self.undo(searched_clear_targets)
                if searched_clear_targets is None:
                    raise ValueError("searched_clear_targets is None")

            # 盤表示
            #   code: board
            elif cmd[0] == 'board':
                BoardViews.print_board(self._board, searched_clear_targets)

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
                BoardViews.print_sfen(self._board, searched_clear_targets)

            # プレイ
            #   code: play 4n
            elif cmd[0] == 'play':
                searched_clear_targets = self.play(input_str, searched_clear_targets)
                if searched_clear_targets is None:
                    raise ValueError("searched_clear_targets is None")

            # デバッグ情報表示
            #   code: dump
            elif cmd[0] == 'dump':
                self.dump()

            # 動作テスト
            #   code: test
            elif cmd[0] == 'test':
                self.test()


    def usi(self):
        """usi握手"""

        # エンジン名は別ファイルから読込。pythonファイルはよく差し替えるのでデータは外に出したい
        try:
            with open(_engine_name_file_path, 'r', encoding="utf-8") as f:
                engine_name = f.read().strip()

        except FileNotFoundError as ex:
            print(f"[usi engine > usi] '{_engine_name_file_path}' file not found.  ex:{ex}")
            raise

        print(f'id name {engine_name}')
        print(f'id author Muzudho')
        print('usiok', flush=True)


    def isready(self):
        """対局準備"""
        print('readyok', flush=True)


    def usinewgame(self):
        """対局中モードに遷移する
        
        対局終了するまで、 setoption などの対局外のコマンドを無視する
        """

        # （しなくていいが？）盤をクリアー
        self._board.clear()

        print(f"[{datetime.datetime.now()}] usinewgame end", flush=True)


    def position(self, input_str):
        """局面データ解析"""

        # position 行を解析します
        position_command = PositionCommand.parse_and_update_board(self._board, input_str)

        return position_command.searched_clear_targets


    @staticmethod
    def sub_go(board, legal_moves, mate_move_in_1ply, searched_clear_targets, searched_gameover):
        """思考開始～最善手返却
        
        Parameters
        ----------
        legal_moves : LegalMoves
            合法手一覧
        mate_move_in_1ply : Move
            一手詰めの指し手。無ければナン
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
        searched_gameover : SearchedGameover
            終局判定

        Returns
        -------
        best_move : Move
            最善手。投了なら None
        reason : str
            説明
        """

        if board.is_gameover(searched_gameover):
            """投了局面時"""

            # 投了
            return None, 'resign'

        # ビナーシに入玉はありません

        # ビナーシに王手はありません

        # 一手詰めを詰める
        if (matemove := mate_move_in_1ply):
            """一手詰めの指し手があれば、それを取得"""
            return matemove, 'mate 1 move'

        # 投了のケースは対応済みなので、これ以降は指し手が１つ以上ある
        
        move_list = legal_moves.distinct_items

        if len(move_list) < 1:
            raise ValueError(f"ステールメートで弾けなかった？")

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
                way_segment = board.get_stone_segment_on_way(move.way)

                # DO （１手指す前の）対象となる路の石（または空欄）の並びを取得
                current_colors = board.get_colors_on_way(move.way, way_segment)

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
                board.push_usi(move.to_code())

                # 指し手生成中に合法手生成したら処理速度が激減するので、やってはいけない
                # 指し手生成中にクリアーターゲット判定をしたら処理速度が激減するので、やってはいけない

                # DO （１手指した後の）対象となる路の石（または空欄）の並びを取得
                next_colors = board.get_colors_on_way(move.way, way_segment)

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
                board.pop()

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

                if board.get_next_turn() == C_BLACK:
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
            if 0 < len(negative_move_list):
                best_move = random.choice(negative_move_list)
                return best_move, 'best move'

            # NOTE is_gameover のチェックが漏れていたら、どのリストも空になるケースがありました
            raise ValueError(f"どのリストも空だ  {len(positive_move_list)=}  {len(come_out_even_move_list)=}  {len(negative_move_list)=}")


    def go(self, searched_clear_targets):
        """思考開始～最善手返却"""

        legal_moves = SearchLegalMoves.generate_legal_moves(self._board)
        
        # 一手詰めの手を返す。無ければナンを返す
        mate_move_in_1ply = SearchMateMoveIn1Play.find_mate_move_in_1ply(
            board=self._board,
            move_list=legal_moves.distinct_items,
            searched_clear_targets=searched_clear_targets)

        # クリアーターゲット新規作成
        searched_clear_targets = SearchedClearTargets.create_new_clear_targets(
            board=self._board,
            # 引き継ぎ
            clear_targets_list=searched_clear_targets.clear_targets_list)

        # 終局判定
        searched_gameover = SearchedGameover.search(self._board, legal_moves, searched_clear_targets.clear_targets_list)

        # 次の１手取得
        (best_move, reason) = UsiEngine.sub_go(self._board, legal_moves, mate_move_in_1ply, searched_clear_targets, searched_gameover)

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


    def do(self, cmd, searched_clear_targets):
        """一手指す　～　盤表示

        Parameters
        ----------
        cmd : list
            例： ["do", "4n"]
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
        
        Returns
        -------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
        """

        move_u = cmd[1]

        if not Move.validate_code(move_u, no_panic=True):
            print("illegal move")
            return searched_clear_targets

        # 一手指す
        self._board.push_usi(move_u)

        # 新規クリアーターゲット作成（そして関数の戻り値として返却）
        searched_clear_targets = SearchedClearTargets.create_new_clear_targets(
            board=self._board,
            # 引き継ぎ
            clear_targets_list=searched_clear_targets.clear_targets_list)

        # 終了の符牒
        print("do ok")

        return searched_clear_targets


    def undo(self, searched_clear_targets):
        """一手戻す
            code: undo
        """
        self._board.pop()

        legal_moves = SearchLegalMoves.generate_legal_moves(self._board)

        # クリアーターゲット新規作成
        searched_clear_targets = SearchedClearTargets.create_new_clear_targets(
            board=self._board,
            # 引き継ぎ
            clear_targets_list=searched_clear_targets.clear_targets_list)

        # 終局判定
        searched_gameover = SearchedGameover.search(self._board, legal_moves, searched_clear_targets.clear_targets_list)

        # 現在の盤表示
        BoardViews.print_board(self._board, searched_clear_targets)
        BoardViews.print_sfen(self._board, searched_clear_targets, from_present=True)
        print("") # 空行

        return searched_clear_targets


    @staticmethod
    def self_match_once(board, match_count):
        """自己対局"""

        print(f"{match_count + 1} 局目ここから：")

        # 終局判定を新規作成
        searched_clear_targets = SearchedClearTargets.make_new_obj()

        # 100手も使わない
        for i in range(1, 100):

            legal_moves = SearchLegalMoves.generate_legal_moves(board)

            # 一手詰めの手を返す。無ければナンを返す
            mate_move_in_1ply = SearchMateMoveIn1Play.find_mate_move_in_1ply(
                board=board,
                move_list=legal_moves.distinct_items,
                searched_clear_targets=searched_clear_targets)

            # クリアーターゲット新規作成
            searched_clear_targets = SearchedClearTargets.create_new_clear_targets(
                board=board,
                # 引き継ぎ
                clear_targets_list=searched_clear_targets.clear_targets_list)

            # 終局判定
            searched_gameover = SearchedGameover.search(board, legal_moves, searched_clear_targets.clear_targets_list)

            # 現在の盤表示
            BoardViews.print_board(board, searched_clear_targets)
            BoardViews.print_sfen(board, searched_clear_targets, from_present=True)
            print("") # 空行

            if board.is_gameover(searched_gameover):
                print(f"# gameover  {searched_gameover.reason=}  {searched_clear_targets.clear_targets_list=}")
                break

            # １つ選ぶ
            (best_move, reason) = UsiEngine.sub_go(board, legal_moves, mate_move_in_1ply, searched_clear_targets, searched_gameover)

            # １手指す
            board.push_usi(best_move.to_code())


        print(f"{match_count + 1} 局目ここまで")

        return searched_clear_targets


    def self_match(self, input_str):
        """自己対局
            code: selfmatch
        
        Parameters
        ----------
        input_str : str
            コマンド文字列
        """
        print("自己対局　ここから：")

        # 連続対局回数
        tokens = input_str.split(' ')
        if len(tokens) < 2:
            max_match_count = 1
        else:
            max_match_count = int(tokens[1])
        
        black_bingo_win_count = 0
        black_point_win_count_when_simultaneous_clearing = 0
        black_point_win_count_when_stalemate = 0
        white_bingo_win_count = 0
        white_point_win_count_when_simultaneous_clearing = 0
        white_point_win_count_when_stalemate = 0

        # 連続対局
        for i in range(0, max_match_count):

            self.usinewgame()
            self.position('position startpos')

            # 自己対局
            # クリアーターゲット更新
            searched_clear_targets = UsiEngine.self_match_once(self._board, match_count=i)

            # 終局判定のために、しかたなく終局後に合法手生成
            legal_moves = SearchLegalMoves.generate_legal_moves(self._board)

            # 終局判定
            searched_gameover = SearchedGameover.search(self._board, legal_moves, searched_clear_targets.clear_targets_list)

            if searched_gameover.is_black_win:
                if searched_gameover.black_count_with_komi == -1:
                    black_bingo_win_count += 1
                elif searched_gameover.is_simultaneous_clearing:
                    black_point_win_count_when_simultaneous_clearing += 1
                else:
                    black_point_win_count_when_stalemate += 1

            elif searched_gameover.is_white_win:
                if searched_gameover.white_count_with_komi == -1:
                    white_bingo_win_count += 1
                elif searched_gameover.is_simultaneous_clearing:
                    white_point_win_count_when_simultaneous_clearing += 1
                else:
                    white_point_win_count_when_stalemate += 1
            
            else:
                raise ValueError(f"{searched_gameover.is_black_win=}  {searched_gameover.is_white_win=}")

            if i % 10 == 9:
                # 対局結果の集計の表示、またはファイルへの上書き
                BoardViews.print_result_summary(
                    i,
                    black_bingo_win_count,
                    black_point_win_count_when_simultaneous_clearing,
                    black_point_win_count_when_stalemate,
                    white_bingo_win_count,
                    white_point_win_count_when_simultaneous_clearing,
                    white_point_win_count_when_stalemate)


        # 対局結果の集計の表示、またはファイルへの上書き
        BoardViews.print_result_summary(
            max_match_count - 1,
            black_bingo_win_count,
            black_point_win_count_when_simultaneous_clearing,
            black_point_win_count_when_stalemate,
            white_bingo_win_count,
            white_point_win_count_when_simultaneous_clearing,
            white_point_win_count_when_stalemate)

        print("自己対局　ここまで")


    def play(self, input_str, searched_clear_targets):
        """一手入力すると、相手番をコンピュータが指してくれる
        
        Returns
        -------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
        """

        # 待ち時間（秒）を置く。ターミナルの行が詰まって見づらいので、イラストでも挟む
        if self._board.get_next_turn() == C_BLACK:
            Views.print_1()
        else:
            Views.print_0()

        time.sleep(0.7)

        # DO あなたが一手指す
        move_u = input_str.split(' ')[1]

        if not Move.validate_code(move_u, no_panic=True):
            print("illegal move")
            return searched_clear_targets

        self._board.push_usi(move_u)

        # コンピューター側の合法手一覧
        legal_moves_for_computer = SearchLegalMoves.generate_legal_moves(self._board)

        # 一手詰めの手を返す。無ければナンを返す
        mate_move_in_1ply = SearchMateMoveIn1Play.find_mate_move_in_1ply(
            board=self._board,
            move_list=legal_moves_for_computer.distinct_items,
            searched_clear_targets=searched_clear_targets)

        # コンピューター側のためのクリアーターゲット新規作成
        searched_clear_targets_for_computer = SearchedClearTargets.create_new_clear_targets(
            board=self._board,
            # 引き継ぎ
            clear_targets_list=searched_clear_targets.clear_targets_list)

        # コンピューター側のための終局判定
        searched_gameover_for_computer = SearchedGameover.search(self._board, legal_moves_for_computer, searched_clear_targets_for_computer.clear_targets_list)

        # 現在の盤表示
        BoardViews.print_board(self._board, searched_clear_targets_for_computer)
        BoardViews.print_sfen(self._board, searched_clear_targets_for_computer, from_present=True)
        print("") # 空行

        # 今１つでもクリアーしたものがあれば、クリアー目標表示
        if Views.is_one_settled(self._board, searched_clear_targets_for_computer):
            Views.print_clear_targets(searched_clear_targets_for_computer)
            time.sleep(0.7)

        if self._board.is_gameover(searched_gameover_for_computer):
            Views.print_settled_for_play_command(self._board, searched_clear_targets_for_computer, searched_gameover_for_computer)
            return searched_clear_targets_for_computer

        # 待ち時間（秒）を置く。コンピュータの思考時間を演出。ターミナルの行が詰まって見づらいので、イラストでも挟む
        time.sleep(0.7)
        Views.print_comp()
        time.sleep(0.7)

        # DO コンピュータが次の一手を算出する
        (best_move, reason) = UsiEngine.sub_go(self._board, legal_moves_for_computer, mate_move_in_1ply, searched_clear_targets_for_computer, searched_gameover_for_computer)

        if best_move is None:
            # ターミナルが見づらいので、空行を挟む
            Views.print_win()
            return searched_clear_targets_for_computer
        
        # ターミナルが見づらいので、イラストを挟む
        if self._board.get_next_turn() == C_BLACK:
            Views.print_1()
        else:
            Views.print_0()

        time.sleep(0.7)

        # DO コンピュータが一手指す
        self._board.push_usi(best_move.to_code())

        # あなた側の合法手一覧
        legal_moves_for_you = SearchLegalMoves.generate_legal_moves(self._board)

        # あなた側のためのクリアーターゲット新規作成
        searched_clear_targets_for_you = SearchedClearTargets.create_new_clear_targets(
            board=self._board,
            # 引き継ぎ
            clear_targets_list=searched_clear_targets_for_computer.clear_targets_list)

        # あなた側のための終局判定
        searched_gameover_for_you = SearchedGameover.search(self._board, legal_moves_for_you, searched_clear_targets_for_you.clear_targets_list)

        # 現在の盤表示
        BoardViews.print_board(self._board, searched_clear_targets_for_you)
        BoardViews.print_sfen(self._board, searched_clear_targets_for_you, from_present=True)
        print("") # 空行

        # 今１つでもクリアーしたものがあれば、クリアー目標表示
        if Views.is_one_settled(self._board, searched_clear_targets_for_you):
            Views.print_clear_targets(searched_clear_targets_for_you)
            time.sleep(0.7)

        if self._board.is_gameover(searched_gameover_for_you):
            Views.print_settled_for_play_command(self._board, searched_clear_targets_for_you, searched_gameover_for_you)
            return searched_clear_targets_for_you

        # ターミナルが見づらいので、イラストを挟む
        time.sleep(0.7)
        Views.print_you()

        return searched_clear_targets_for_you


    def dump(self):
        """デバッグ情報表示"""
        print(f"[dump] {self._board._next_turn_at_init=}")


    def test(self):
        """動作テスト。デバッグ用"""

        print("動作テスト")

        self.usi()
        self.isready()
        self.usinewgame()
        searched_clear_targets = self.position('position sfen 7/7/2o4/7/7/7 w - - 1 moves 4n')
        BoardViews.print_board(self._board, searched_clear_targets)

        legal_moves = SearchLegalMoves.generate_legal_moves(self._board)

        # 指し手のリストから冗長な指し手を省き、さらにコードをキーにして降順にソートする
        actual_move_list = sorted(legal_moves.distinct_items, key=lambda x:x.to_code())

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
