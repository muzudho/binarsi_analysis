import pexpect.popen_spawn as psp
import re
import time
from py_binarsi import BLACK_KOMI, WHITE_KOMI, C_EMPTY, C_BLACK, C_WHITE, CLEAR_TARGETS_LEN, Colors, Move, MoveHelper, Board, SearchedClearTargets, SearchLegalMoves, SearchMateMoveIn1Play, SearchedGameover, PositionCommand, SfenHelper
from coliceum.views import Views as ColiceumViews


class Coliceum():
    """対局コロシアム"""


    def __init__(self, child_process):
        """初期化

        Parameters
        ----------
        child_process : object
            このプロセスからオープンした新しいプロセス。このプロセスの子プロセスとしてぶら下げたもの。
            このプロセス自体をクローズさせる方法が分からない
        """

        self._proc = child_process
        self._board = Board()

        # 終局判定を新規作成
        self._searched_clear_targets = SearchedClearTargets.make_new_obj()


    @property
    def board(self):
        return self._board


    def sendline(self, message):
        """子プロセスの標準入力へ文字列を送ります"""

        #print(f"Coliceum said> {message}")
        self._proc.sendline(message)


    @property
    def messages_until_match(self):
        """expect() でマッチするまでの間に無視した文字列を返す"""
        return self._proc.before.decode('utf-8', errors="ignore")


    @property
    def matched_message(self):
        """expect() にマッチした文字列を返す"""

        # after は bytes オブジェクト
        return self._proc.after.decode('utf-8', errors="ignore")


    @property
    def match_obj(self):
        """expect() にマッチしたときの match オブジェクトを返す"""
        return self._proc.match


    def group(self, index):
        """expect() にマッチしたときの match オブジェクトを返す"""

        # group() の返却値はバイト文字列で、 b'word' のように b が付いてくるので、 decode() する必要がある
        return self._proc.match.group(index).decode('utf-8')


    def expect_line(self, format, timeout, end='\r\n'):
        """子プロセスが出力すると想定した文字列
        
        Windows を想定して、改行コードの '\r\n' を末尾に付ける
        
        Parameters
        ----------
        message : str
            文字列。正規表現で書く
        """

        #print(f"The engine would say> {format}")
        self._proc.expect(f"{format}{end}", timeout=timeout)


    def update_board(self):
        """盤面を最新にする。
        初期局面と棋譜付きの positionコマンドも返す
        
        Returns
        -------
        初期局面と棋譜付きの positionコマンド
        """

        # Coliceum sayd:
        self.sendline(f"sfen")

        # Engine said
        # NOTE `.*` では最右マッチしてしまうので、 `.*?` にして最左マッチにする
        self.expect_line("\\[from beginning\\](.*?)", timeout=None)
        position_command_str = f"position{self.group(1)}"
        #print(f"(debug 98) {position_command_str=}")
        position_command = PositionCommand.parse_and_update_board(self._board, position_command_str)

        return position_command


    def go_computer(self):
        """コンピューターに１手指させる～盤表示まで"""

        ColiceumViews.print_comp()
        print() # 改行

        self.sendline("go")

        # Engine said
        self.expect_line(r"bestmove ([\w\s]+)", timeout=None)
#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}""")
        # [2024-08-31 01:45:38.237119] usinewgame end
        # info depth 0 seldepth 0 time 1 nodes 0 score cp 0 string I'm random move

        # print(f"{self.matched_message=}")   # "bestmove 4n\r\n"
        # print(f"{self.group(1)=}")    # 4n
        bestmove_str = self.group(1)

        #if self._board.is_gameover(searched_gameover_for_computer):
        if bestmove_str == 'resign':
            # TODO 通常、コンピューターが投了する前に、決着は判定し終わっています。ここの書き方をあとで考える
            print("# computer resign")
            return


        self.sendline(f"do {bestmove_str}")
        # do コマンドすると、 `do ok` が出て終わる
        self.expect_line("do ok", timeout=None)

        # # Engine said
        # # NOTE `.*` では最右マッチしてしまうので、 `.*?` にして最左マッチにする
        # self.expect_line("\\[from beginning\\](.*?)", timeout=None)
        # position_command_str = f"position{self.group(1)}"
        # #print(f"(debug 98) {position_command_str=}")
        # position_command = PositionCommand.parse_and_update_board(self._board, position_command_str)
#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}
#
# Matched message
# ---------------
# [from beginning]{position_args}""")
        # もう１行 stones_before_change が続く可能性もある

        # Engine said
        #self.expect_line("\\[from present\\](.*?)", timeout=None)
        #position_args = self.group(1)

#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}
#
# Matched message
# ---------------
# [from present]{position_args}""")
        # もう１行 stones_before_change が続く可能性もある


    def go_human(self, who):
        """あなたに１手指させる～盤表示まで
        
        Parameters
        ----------
        who : str
            'you', 'black', 'white' の３つ
        """

        if who == 'you':
            ColiceumViews.print_you()

        elif who == 'black':
            ColiceumViews.print_black()

        elif who == 'white':
            ColiceumViews.print_white()

        else:
            raise ValueError("error go human")


        # 合法手メニューの表示
        legal_move_code_help_list = ColiceumViews.create_legal_move_code_help_list(self._board)
        print() # 改行
        ColiceumViews.print_legal_moves_menu(legal_move_code_help_list)

        # コマンド入力ループ
        while True:
            print(f"""Please input No(1-{len(legal_move_code_help_list)}) or Code or "help":""")
            input_str = input()

            # その他のコマンド表示
            if input_str == 'help':
                print(f"""\
`quit` - Exit the application.
`board` - Display the board.
`sfen` - Display the sfen.
`clear_targets` - Display the clear targets.
`legal_moves` - Display the legal moves.
`mate1` - Display the 1 move in mate 1 ply.
`distinct_legal_moves` - Display the distinct legal moves.
`history` - Display the input command list.
`moves_for_edit` - Display the operation for edit.
`test_board` - Test to display the new board (under development).
`inverse 4n` - Displays the inverse operation. The argument must be a move code.""")

            # アプリケーション終了
            elif input_str == 'quit':
                return 'quit'

            # 盤表示
            elif input_str == 'board':
                # コロシアムからエンジンへ SFEN コマンドを投げて、その結果から　クリアーターゲットを取得する必要がある

                # 盤を更新する
                position_command = self.update_board()

                print() # 改行
                print(ColiceumViews.stringify_board_header(self._board, position_command.searched_clear_targets))  # １行目表示
                print(ColiceumViews.stringify_board_normal(self._board))   # 盤面
                print() # 改行

            # SFEN 表示
            elif input_str == 'sfen':

                # 盤を更新する
                position_command = self.update_board()
                print() # 改行
                print(SfenHelper.stringify_sfen(self._board, position_command.searched_clear_targets))

            # TODO デバッグ用の盤表示。まだできてない
            elif input_str == 'test_board':
                ColiceumViews.print_test_board(self._board)

            # クリアーターゲット表示
            elif input_str == 'clear_targets':
                position_command = self.update_board()
                print() # 改行
                ColiceumViews.print_clear_targets(position_command.searched_clear_targets)

            # 合法手メニュー表示
            elif input_str == 'legal_moves':
                print() # 改行
                legal_move_code_help_list = ColiceumViews.create_legal_move_code_help_list(self._board)
                ColiceumViews.print_legal_moves_menu(legal_move_code_help_list)

            # 重複を覗いた合法手メニュー表示
            elif input_str == 'distinct_legal_moves':
                print() # 改行
                ColiceumViews.print_distinct_legal_move_list(self._board)

            # １手詰めがあれば、その手をどれか１つ表示
            elif input_str == 'mate1':
                position_command = self.update_board()
                print(f"""\

{ColiceumViews.stringify_mate1(self._board, position_command.searched_clear_targets)}
""")

            # 編集用の操作一覧
            elif input_str == 'moves_for_edit':
                ColiceumViews.print_moves_for_edit(self._board)

            # 操作履歴表示
            elif input_str == 'history':
                ColiceumViews.print_history(self._board)

            else:

                cmd = input_str.split(' ')

                if 1 < len(cmd):
                    # 逆操作コードの表示
                    #   code: inverse 4n
                    if cmd[0] == 'inverse':
                        ColiceumViews.print_inverse_move(self._board, input_str)
                
                else:
                    # 番号入力
                    result = re.match(r"^[0-9]+$", input_str)
                    if result:
                        input_num = int(input_str)

                        move_code_help = legal_move_code_help_list[input_num - 1]

                        move_u = move_code_help.code

                    else:
                        # 指し手コードとして受付
                        move_u = input_str


                    # 指し手コード書式チェック
                    if not Move.validate_code(move_u):
                        print(f"illegal move: `{move_u}`")

                        # メッセージ表示後、間隔を空ける
                        time.sleep(0.7)

                        # コマンドループをやり直し
                        continue

                    # FIXME 指し手コードの書式は合っているが、ルールに無い操作をすると応答がなく、Expect が例外を投げてしまう


                    # Coliceum said
                    self.sendline(f"do {move_u}")
                    # do コマンドすると、 `do ok` が出て終わる
                    self.expect_line("do ok", timeout=None)

                    # コマンド入力ループから抜ける（次のターンへ）
                    break


        # Engine said
        # NOTE `.*` では最右マッチしてしまうので、 `.*?` にして最左マッチにする
        #self.expect_line("\\[from beginning\\](.*?)", timeout=None)

#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}

# Matched message (Debug 1)
# ---------------
# {self.matched_message}""")

        #position_command_str = f"position{self.group(1)}"
        #print(f"(Debug 163) {position_command_str=}")
        #position_command = PositionCommand.parse_and_update_board(self._board, position_command_str)

        # Engine said
        # NOTE `.*` では最右マッチしてしまうので、 `.*?` にして最左マッチにする
        #self.expect_line("\\[from present\\](.*?)", timeout=None)
        #position_args = self.group(1)
#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}""")


    def self_match_once(self, match_count):
        """自己対局"""

        print(f"{match_count + 1} 局目ここから：")

        # 終局判定を新規作成
        searched_clear_targets = SearchedClearTargets.make_new_obj()
        
        position_command = None

        # 手数ループ。100手も使わない
        for i in range(1, 100):

            # 盤面を最新にする
            position_command = self.update_board()

            # 盤表示
            print() # 改行
            print(ColiceumViews.stringify_board_header(self._board, position_command.searched_clear_targets))  # １行目表示
            print(ColiceumViews.stringify_board_normal(self._board))   # 盤面
            print() # 改行

            # １手探す
            self.sendline("go")

            # Engine said
            self.expect_line(r"bestmove (\w+)", timeout=None)
            move_u = self.group(1)

            if move_u == 'resign':
                # 手数ループから抜ける
                break

            else:
                # １手指す
                self.sendline(f"do {move_u}")
                self.expect_line(r"do ok", timeout=None)


        print(f"{match_count + 1} 局目ここまで")

        return position_command.searched_clear_targets


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

            self.sendline("usinewgame")
            self.sendline('position startpos')

            # 自己対局
            # クリアーターゲット更新
            searched_clear_targets = self.self_match_once(match_count=i)

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

            if i < max_match_count - 10 and i % 10 == 9:
                # 対局結果の集計の表示、またはファイルへの上書き
                ColiceumViews.print_result_summary(
                    i,
                    black_bingo_win_count,
                    black_point_win_count_when_simultaneous_clearing,
                    black_point_win_count_when_stalemate,
                    white_bingo_win_count,
                    white_point_win_count_when_simultaneous_clearing,
                    white_point_win_count_when_stalemate)


        # 対局結果の集計の表示、またはファイルへの上書き
        ColiceumViews.print_result_summary(
            max_match_count - 1,
            black_bingo_win_count,
            black_point_win_count_when_simultaneous_clearing,
            black_point_win_count_when_stalemate,
            white_bingo_win_count,
            white_point_win_count_when_simultaneous_clearing,
            white_point_win_count_when_stalemate)

        print("自己対局　ここまで")


    @staticmethod
    def start():
        """TODO 開始

        # NOTE Python の subprocess はパイプのことだ。アプリケーションが終了して結果をリターンすることを前提としている
        # NOTE Python の multiprocessing は、外部プロセスを起動するものではない。プロセスを生成することを前提としている
        # NOTE Python の pexpect ライブラリーは、メッセージループで入力を待機するアプリケーションに向いているが、UNIX 系に限られる。公式で Windows には対応していないアナウンスがある
        # NOTE Socket 通信は、サーバー・クライアント型を想定している。標準入出力で通信を行う想定の外部プロセスに対応したものではない
        # NOTE Windows で pexpect ライブラリーを使ってみたという記事がある
        # 📖 [Windowsでpexpectを利用する](https://qiita.com/shita_fontaine/items/c2ceb1e66450d7e09490)
        """

        # binarsi_analisis リポジトリー直下の main.py を起動しています
        # engine は対局エンジンプロセス
        #print("Coliceum> python main.py")
        coliceum = Coliceum(
            child_process=psp.PopenSpawn('python main.py'))

        # 以下、基本的に expect_line、 print、 sendline、 を対話１回分として繰り返します

        # Coliceum said
        coliceum.sendline("usi")

        # Engine said
        coliceum.expect_line(r"id name (\w+)", timeout=None)
        #print(f"{coliceum.messages_until_match=}")  # ""
        #print(f"{coliceum.matched_message=}")       # "id name KifuwarabeBinarsi\r\n"
        #print(f"{coliceum.group(0)=}")    # "id name KifuwarabeBinarsi\r\n"
        #print(f"{coliceum.group(1)=}")    # "KifuwarabeBinarsi"

        # Engine said
        coliceum.expect_line("id author Muzudho", timeout=None)

        # Engine said
        coliceum.expect_line("usiok", timeout=None)
        coliceum.sendline("isready")

        # Engine said
        coliceum.expect_line("readyok", timeout=None)


        # タイトル～対局終了までのループ
        while True:
            coliceum.sendline("usinewgame")



            # タイトル表示
            ColiceumViews.print_title()
            input_str = input()

            your_turn = None
            is_human_vs_human = False

            # 人間 VS コンピューター
            if input_str == '1':
                # DO どちらの先手かは決められるようにした
                print(f"""\

CHOOSE
---------
(1) sente
(2) gote
---------
Do you play sente or gote(1-2)?> """)
                input_str = input()

                if input_str == '1':
                    your_turn = C_BLACK

                else:
                    your_turn = C_WHITE

            # 人間 VS 人間
            elif input_str == '2':
                is_human_vs_human = True

            # コンピューター VS コンピューター（セルフマッチ）
            elif input_str == '3':
                print("how many games(1-)?")

                rounds = input()

                coliceum.self_match(f"selfmatch {rounds}")

                print("please push any key:")
                input()

                continue

            # コロシアム終了
            elif input_str == '4':
                # 思考エンジンを終了させる
                coliceum.sendline("quit")

                # タイトル～対局終了までのループから抜ける
                break




            coliceum.sendline("position startpos")


            # DO 手番交互ループ
            while True:

                #print(f"[Coliceum > start] 手番交互ループ始まり")

                # 盤面を最新にする
                position_command = coliceum.update_board()

                # 盤表示
                print() # 改行
                print(ColiceumViews.stringify_board_header(coliceum.board, position_command.searched_clear_targets))  # １行目表示
                print(ColiceumViews.stringify_board_normal(coliceum.board))   # 盤面
                print() # 改行

                # 盤表示後、間隔を空ける
                time.sleep(0.7)

                # 今１つでもクリアーしたものがあれば、クリアー目標一覧表示
                if ColiceumViews.is_one_settled(coliceum.board, position_command.searched_clear_targets):
                    ColiceumViews.print_clear_targets(position_command.searched_clear_targets)
                    
                    # クリアーターゲット表示後、間隔を空ける
                    time.sleep(0.7)


                # 現局面の合法手一覧取得
                #
                #   ステールメートしているかどうかの判定に使う
                #
                legal_moves = SearchLegalMoves.generate_legal_moves(coliceum.board)

                # 終局判定
                searched_gameover = SearchedGameover.search(coliceum.board, legal_moves, position_command.searched_clear_targets.clear_targets_list)
                #print(f"[Coliceum > go_human (debug 231)] {searched_gameover.dump()}")

                # 決着が付いていれば、結果表示
                if coliceum.board.is_gameover(searched_gameover):
                    ColiceumViews.print_settled(coliceum.board, position_command.searched_clear_targets, searched_gameover, your_turn, is_human_vs_human)

                    # 結果表示後、間隔を空ける
                    time.sleep(0.7)

                    # ２行空行を入れる
                    print(f"""\

""")

                    # 手番交互ループから抜ける
                    break


                # 現在の手番を取得
                next_turn = coliceum.board.get_next_turn()

                # 人間のターン
                if next_turn == your_turn or is_human_vs_human:
                    if your_turn is not None:
                        who = 'you'
                    elif next_turn == C_BLACK:
                        who = 'black'
                    elif next_turn == C_WHITE:
                        who = 'white'
                    else:
                        raise ValueError("error on human turn")
                    
                    message = coliceum.go_human(who)

                    if message == 'quit':
                        # アプリケーションを終了する
                        return

                    #print(f"[Coliceum > start] 人間のターン終わり")

                # コンピューターのターン
                else:
                    coliceum.go_computer()

