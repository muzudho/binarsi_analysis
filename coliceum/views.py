import math
import time
from py_binarsi import BLACK_KOMI, WHITE_KOMI, C_EMPTY, C_BLACK, C_WHITE, BOARD_AREA, CLEAR_TARGETS_LEN, Colors, Move, MoveHelper, Board, SearchedClearTargets, SearchLegalMoves, SearchMateMoveIn1Play, SearchedGameover, PositionCommand, SfenHelper


class MoveCodeHelp():
    """指し手コードの解説

    NOTE 画面レイアウトの都合から、４文字以内のコードしか利用できない。 "board" は５文字あるので入らない
    """


    def __init__(self, code, description):
        """初期化
        
        Parameters
        ----------
        code : str
            指し手コード
        description : str
            人が読める形式の指し手表示
        """
        self._code = code
        self._description = description


    @property
    def code(self):
        """指し手コード"""
        return self._code


    @property
    def description(self):
        """人が読める形式の指し手表示"""
        return self._description


class Views():
    """コロシアム用画面"""


    @staticmethod
    def print_0():
        print("""\
     ________
    /   __   |
    |  /  |  |
    |  |  |  |
    |  |  |  |
    |  |_/   |
    |_______/""", flush=True)


    @staticmethod
    def print_1():
        print("""\
       ___
      /   |
     /    |
    |__   |
      |   |
      |   |
      |___|""", flush=True)


    @staticmethod
    def print_black():
        print("""\
     ________    ___     ________     ________   __    __ 
    /   __   |  |_  |   /_____   |   /   ____|  |  |  |  |
    |  |__|  |   |  |    _____|  |   |  /       |  |_/  / 
    |   __  /_   |  |   /   __   |   |  |       |      /_
    |  |  |  |   |  |   |  |  |  |   |  |       |   /|_ |_
    |  |_/   |   |  |_  |  |_/   |_  |  |____   |  |  |_ |_
    |_______/    |___|  |__________| |_______|  |__|   |__|""", flush=True)


    @staticmethod
    def print_white():
        print("""\
     __     ___     ___   ___         ___      __        ________
    |  |   /   |   /  /  /  |        /  |   __|  |____  |   __   |
    |  |  /    |  /  /   |  |____    |_/   |__    ___/  |  |__|  |
    |  | /     | /  /    |   __  |_   __      |  |      |   _____/
    |  |/  /|  |/  /     |  |  |  |  |  |     |  |      |  |   ___
    |     / |     /      |  |  |  |  |  |     |  |      |  |__/  /
    |____/  |____/       |__|  |__/  |__|     |__|      |_______/""", flush=True)


    @staticmethod
    def print_comp():
        print("""\
     ________   ________    ______  ______   ________
    /   ____|  /   __   |  |   __ |/ __   |  |   __  |
    |  /       |  |  |  |  |  |  |  |  |  |  |  |  |  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  |__/  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  _____/
    |  |____   |  |_/   |  |  |  |  |  |  |  |  |
    |_______|  |_______/   |__|  |__|  |__|  |__|""", flush=True)


    @staticmethod
    def print_you():
        print("""\
     __     ___   ________    __    __ 
    |  |   /  /  /   __   |  |  |  |  |
    |  |__/  /   |  |  |  |  |  |  |  |
    |__    _/    |  |  |  |  |  |  |  |
       |  |      |  |  |  |  |  |  |  |
       |  |      |  |_/   |  |  |_/   |
       |__|      |_______/   |_______/""", flush=True)


    @staticmethod
    def print_win():
        print("""\
     __     ___     ___   ___   ____      __ 
    |  |   /   |   /  /  /  |  |    |    |  |
    |  |  /    |  /  /   |_/   |     |   |  |
    |  | /     | /  /     __   |  |   |  |  |
    |  |/  /|  |/  /     |  |  |  ||   | |  |
    |     / |     /      |  |  |  | |   ||  |
    |____/  |____/       |__|  |__|  |______|""", flush=True)


    @staticmethod
    def print_lose():
        print("""\
     __          ________    _______    ________
    |  |        /   __   |  /   ____|  |   __   |
    |  |        |  |  |  |  |  /____   |  |__|  |
    |  |        |  |  |  |  |____   |  |   _____/
    |  |_____   |  |  |  |       |  |  |  |   ___
    |        |  |  |_/   |   ___/   /  |  |__/  /
    |________|  |_______/   |______/   |_______/""", flush=True)


    @staticmethod
    def print_settled(board, searched_clear_targets, searched_gameover, your_turn, is_human_vs_human):
        """決着の表示、コロシアム用
        
        - 三本勝負で決着したのなら、特に説明は要らない
        - 点数計算で決着したのなら、点数も表示
        """

#         # TODO デバッグ消す
#         print(f"""\
# DEBUG コロシアム用の決着表示
#     {searched_gameover.is_black_win=}
#     {searched_gameover.is_white_win=}
#     {your_turn=}
# """)
        
        # どちらも勝っていないなら、この関数を呼び出さないでください
        if not searched_gameover.is_black_win and not searched_gameover.is_white_win:
            raise ValueError(f"undefined gameover. {searched_gameover.reason=}")

        # 人間 VS 人間
        if is_human_vs_human:
            # 黒番の勝ち
            if searched_gameover.is_black_win:
                Views.print_black()
                Views.print_win()
            
            # 白番の勝ち
            else:
                Views.print_white()
                Views.print_win()                

        else:
            # あなたの勝ち
            if (your_turn == C_BLACK and searched_gameover.is_black_win) or (your_turn == C_WHITE and searched_gameover.is_white_win):
                Views.print_you()
                Views.print_win()
            
            # あなたの負け
            else:
                Views.print_you()
                Views.print_lose()

        # 点数計算で決着したなら、点数も表示
        if searched_gameover.is_point_calculation:
            print(f"""\
Black {searched_gameover._black_count_with_komi:2.1f}
White {searched_gameover._white_count_with_komi:2.1f}""")


    @staticmethod
    def print_clear_targets(searched_clear_targets):
        """クリアーターゲットの一覧表示
        
        Parameters
        ----------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
        """

        # Top と Bottom
        disp1 = ['             '] * CLEAR_TARGETS_LEN
        disp2 = ['    WANTED   '] * CLEAR_TARGETS_LEN

        for i in range(0, CLEAR_TARGETS_LEN):
            if searched_clear_targets.clear_targets_list[i] != -1:
                disp1[i] = f' CLEAR in {searched_clear_targets.clear_targets_list[i]:2} '
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


    @staticmethod
    def is_one_settled(board, searched_clear_targets):
        """今１つでもクリアーしたものがあるか？"""
        for clear_target in searched_clear_targets.clear_targets_list:
            if clear_target == board.moves_number:
                return True

        return False


    @staticmethod
    def print_title():
        """タイトル表示"""

        #          2         3         4         5         6         7
        #          0         0         0         0         0         0
        print("""\
 ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
<   ______                                                          >
 >  |  __  |   __   _______     ______    _______    ______   __   <
<   | |__| |  |__| |   __  |_  |  ___ |_ |   ____| /   ____/ |__|   >
 >  |  __ /_   __  |  |  |  |  |  _____| |  |      |_____  |  __   <
<   | |__|  | |  | |  |  |  |  | |_____  |  |       ____/ /  |  |   >
 >  |______/  |__| |__|  |__|  |_______| |__|      |_____/   |__|  <
<                                                                   >
 v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

(1) human VS computer
(2) human VS human
(3) computer VS computer
(4) quit

please input number(1-4):""")


    @staticmethod
    def print_history(board):
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

        for i in range(0, len(board.board_editing_history.items)):
            board_editing_item = board.board_editing_history.items[i]
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


    @staticmethod
    def print_moves_for_edit(board):
        """編集用の手一覧表示（合法手除く）
            code: moves_for_edit
        """
        print("編集用の手一覧表示（合法手除く）　ここから：")

        legal_moves = SearchLegalMoves.generate_legal_moves(board)

        for i in range(0, len(legal_moves.items_for_edit)):
            move = legal_moves.items_for_edit[i]
            print(f"    ({i + 1:2}) move_for_edit:{move.to_code()}")

        print("編集用の手一覧表示（合法手除く）　ここまで：")


    @staticmethod
    def print_mate1(board, searched_clear_targets):
        """１手詰めがあれば、その手をどれか１つ表示"""

        legal_moves = SearchLegalMoves.generate_legal_moves(board)

        # 一手詰めの手を返す。無ければナンを返す
        mate_move_in_1ply = SearchMateMoveIn1Play.find_mate_move_in_1ply(
            board=board,
            move_list=legal_moves.distinct_items,
            searched_clear_targets=searched_clear_targets)

        if mate_move_in_1ply is None:
            print(f"there is no checkmate")
            return

        print(mate_move.to_code())


    @staticmethod
    def print_test_board(board):
        """デバッグ用の盤表示
            code: board
            TODO あとで消す
        """
        print(Views.stringify_board_hard(board))   # 盤面


    @staticmethod
    def print_inverse_move(board, input_str):
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
            board=board,
            move=move,
            stones_before_change=stones_before_change)

        if inverse_move is None:
            print(f"[print_inverse_move] 未実装： {inverse_move=}")
            return

        # 表示
        print(f"{move_u} --inverse--> {inverse_move.to_code()}")


    @staticmethod
    def print_result_summary(
            i,
            black_bingo_win_count,
            black_point_win_count_when_simultaneous_clearing,
            black_point_win_count_when_stalemate,
            white_bingo_win_count,
            white_point_win_count_when_simultaneous_clearing,
            white_point_win_count_when_stalemate):
        """対局結果の集計の表示、またはファイルへの上書き"""

        global BLACK_KOMI, WHITE_KOMI

        bingo_total = black_bingo_win_count + white_bingo_win_count
        point_total_when_simultaneous_clearing = black_point_win_count_when_simultaneous_clearing + white_point_win_count_when_simultaneous_clearing
        point_total_when_stalemate = black_point_win_count_when_stalemate + white_point_win_count_when_stalemate
        total = bingo_total + point_total_when_simultaneous_clearing + point_total_when_stalemate
        black_total = black_bingo_win_count + black_point_win_count_when_simultaneous_clearing + black_point_win_count_when_stalemate
        white_total = white_bingo_win_count + white_point_win_count_when_simultaneous_clearing + white_point_win_count_when_stalemate

        with open('result_summary.log', 'w', encoding='utf8') as f:
            text = f"""\
{i+1} 対局集計

    黒コミ：{BLACK_KOMI:2.1f}
    白コミ：{WHITE_KOMI:2.1f}

    三本勝負
    ーーーーーーーー
    黒　　　　勝ち数： {black_bingo_win_count:6}　　　率： {black_bingo_win_count/total:3.3f}
    白　　　　勝ち数： {white_bingo_win_count:6}　　　率： {white_bingo_win_count/total:3.3f}
    ーーーーーーーー

    点数計算（同着）
    ーーーーーーーー
    黒　　　　勝ち数： {black_point_win_count_when_simultaneous_clearing:6}　　　率： {black_point_win_count_when_simultaneous_clearing/total:3.3f}
    白　　　　勝ち数： {white_point_win_count_when_simultaneous_clearing:6}　　　率： {white_point_win_count_when_simultaneous_clearing/total:3.3f}
    ーーーーーーーー

    点数計算（満局）
    ーーーーーーーー
    黒　　　　勝ち数： {black_point_win_count_when_stalemate:6}　　　率： {black_point_win_count_when_stalemate/total:3.3f}
    白　　　　勝ち数： {white_point_win_count_when_stalemate:6}　　　率： {white_point_win_count_when_stalemate/total:3.3f}
    ーーーーーーーー

    決着方法比較
    ーーーーーーーー
    三本勝負　　　　： {bingo_total:6}　　　率： {bingo_total/total:3.3f}
    点数計算（同着）： {point_total_when_simultaneous_clearing:6}　　　率： {point_total_when_simultaneous_clearing/total:3.3f}
    点数計算（満局）： {point_total_when_stalemate:6}　　　率： {point_total_when_stalemate/total:3.3f}
    ーーーーーーーー

    先後比較
    ーーーーーーーー
    黒　　　　勝ち数： {black_total:6}　　　率： {black_total/total:3.3f}
    白　　　　勝ち数： {white_total:6}　　　率： {white_total/total:3.3f}
    ーーーーーーーー
"""

            f.write(text)
            print(text, flush=True)


    @staticmethod
    def stringify_board_header(board, searched_clear_targets=None):
        """盤面のヘッダー
                
        Parameters
        ----------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
            指し手生成中はナン
        """

        edits_num = len(board.board_editing_history.items)
        if board.moves_number != edits_num:
            edits_num_str = f"| {edits_num} edits "
        else:
            edits_num_str = ""

        if 0 < edits_num:
            latest_move = board.board_editing_history.items[-1].move
            if latest_move.when_edit:
                latest_move_str = f"edited {latest_move.to_code()}"
            else:
                latest_move_str = f"moved {latest_move.to_code()}"
        else:
            latest_move_str = 'init'


        # クリアーターゲット状況
        if searched_clear_targets is None:
            clear_targets_list_str = ''

        else:
            clear_targets_u_list = []
            if searched_clear_targets.clear_targets_list[0] != -1:
                clear_targets_u_list.append('b3')
            if searched_clear_targets.clear_targets_list[1] != -1:
                clear_targets_u_list.append('b4')
            if searched_clear_targets.clear_targets_list[2] != -1:
                clear_targets_u_list.append('b5')
            if searched_clear_targets.clear_targets_list[3] != -1:
                clear_targets_u_list.append('w3')
            if searched_clear_targets.clear_targets_list[4] != -1:
                clear_targets_u_list.append('w4')
            if searched_clear_targets.clear_targets_list[5] != -1:
                clear_targets_u_list.append('w5')

            if 0 < len(clear_targets_u_list):
                clear_targets_list_str = f" | {' '.join(clear_targets_u_list)}"
            else:
                clear_targets_list_str = ''


        # 次の手番
        # NOTE 終局理由を取得するには、一手指していないと分からない。盤を表示するだけなのに一手指すのは激重すぎる。したがって終局理由は盤表示には含めないことにする
        next_turn = board.get_next_turn()
        if next_turn == C_BLACK:
            next_turn_str = 'next black'
        elif next_turn == C_WHITE:
            next_turn_str = 'next white'
        else:
            raise ValueError(f"unsupported turn  {next_turn}")


        return f"[{board.moves_number:2} moves {edits_num_str}| {latest_move_str}{clear_targets_list_str} | {next_turn_str}]"


    @staticmethod
    def stringify_board_normal(board):
        """通常の盤面

        例：
                1 2 # 4 5 6 7
              +---------------+
            a | . . . . . . . |
            b | . . . . . . . |
            c | . . 1 . . . . |
            d | . . 0 . . . . |
            e | . . . . . . . |
            f | . . . . . . . |
              +---------------+
        """

        # 数値を表示用文字列(Str)に変更
        s = [' '] * BOARD_AREA
        for sq in range(0, BOARD_AREA):
            s[sq] = Colors.as_string_board(board.get_color(sq))

        # Way
        a = {
            '1' : board.get_current_way_str('1'),
            '2' : board.get_current_way_str('2'),
            '3' : board.get_current_way_str('3'),
            '4' : board.get_current_way_str('4'),
            '5' : board.get_current_way_str('5'),
            '6' : board.get_current_way_str('6'),
            '7' : board.get_current_way_str('7'),
            'a' : board.get_current_way_str('a'),
            'b' : board.get_current_way_str('b'),
            'c' : board.get_current_way_str('c'),
            'd' : board.get_current_way_str('d'),
            'e' : board.get_current_way_str('e'),
            'f' : board.get_current_way_str('f'),
        }

        return f"""\
    {a['1']} {a['2']} {a['3']} {a['4']} {a['5']} {a['6']} {a['7']}
  +---------------+
{a['a']} | {s[0]} {s[ 6]} {s[12]} {s[18]} {s[24]} {s[30]} {s[36]} |
{a['b']} | {s[1]} {s[ 7]} {s[13]} {s[19]} {s[25]} {s[31]} {s[37]} |
{a['c']} | {s[2]} {s[ 8]} {s[14]} {s[20]} {s[26]} {s[32]} {s[38]} |
{a['d']} | {s[3]} {s[ 9]} {s[15]} {s[21]} {s[27]} {s[33]} {s[39]} |
{a['e']} | {s[4]} {s[10]} {s[16]} {s[22]} {s[28]} {s[34]} {s[40]} |
{a['f']} | {s[5]} {s[11]} {s[17]} {s[23]} {s[29]} {s[35]} {s[41]} |
  +---------------+\
"""


    @staticmethod
    def stringify_board_hard(board):
        """TODO 罫線も引ける盤面

        例：
                1 2 # 4 5 6 7
              +------+-+------+
            a | . . .|.|. . . |
            b | . . .|.|. . . |
            c | . . 1|.|. . . |
            d | . . 0|.|. . . |
            e | . . .|.|. . . |
            f | . . .|.|. . . |
              +------+-+------+

        あまりにも複雑なので、画面全体を単なる１８×９の配列として実装する。
        例：
                0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17
              +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
            0 |   |   |   | 1 |   | 2 |   | # |   | 4 |   | 5 |   | 6 |   | 7 |   |   |
            1 |   |   | + | - | - | - | - | - | + | - | + | - | - | - | - | - | - | + |
            2 | a |   | | | . |   | . |   | . | | | . | | | . |   | . |   | . |   | | |
            3 | b |   | | | . |   | . |   | . | | | . | | | . |   | . |   | . |   | | |
            4 | c |   | | | . |   | . |   | 1 | | | . | | | . |   | . |   | . |   | | |
            5 | d |   | | | . |   | . |   | 0 | | | . | | | . |   | . |   | . |   | | |
            6 | e |   | | | . |   | . |   | . | | | . | | | . |   | . |   | . |   | | |
            7 | f |   | | | . |   | . |   | . | | | . | | | . |   | . |   | . |   | | |
            8 |   |   | + | - | - | - | - | - | + | - | + | - | - | - | - | - | - | + |
              +---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+
        """

        width = 18
        height = 9
        t = [' '] * (width * height)

        # 筋の符号
        # -------
        # TODO キャッシュ化したい。まだできてない
        way_squares = {
            '1' : Square.file_rank_to_sq(3, 0),
            '2' : Square.file_rank_to_sq(5, 0),
            '3' : Square.file_rank_to_sq(7, 0),
            '4' : Square.file_rank_to_sq(9, 0),
            '5' : Square.file_rank_to_sq(11, 0),
            '6' : Square.file_rank_to_sq(13, 0),
            '7' : Square.file_rank_to_sq(15, 0),
            'a' : Square.file_rank_to_sq(0, 2),
            'b' : Square.file_rank_to_sq(0, 3),
            'c' : Square.file_rank_to_sq(0, 4),
            'd' : Square.file_rank_to_sq(0, 5),
            'e' : Square.file_rank_to_sq(0, 6),
            'f' : Square.file_rank_to_sq(0, 7),
        }

        for way_code in Way.characters:
            t[way_squares[way_code]] = board.get_current_way_str(way_code)


        print("罫線も引ける盤面　ここから：")
        for j in range(0, height):
            for i in range(0, width):
                sq = j*width+i
                print(t[sq], end='')
            
            print() # 改行

        print("罫線も引ける盤面　ここまで：")


    @staticmethod
    def create_human_presentable_move_text(board, move):
        """人間が読めるような指し手の名前"""

        # 盤面編集フラグ
        if move.when_edit:
            edit_mark = '&'
        else:
            edit_mark = ''

        # 路ロック解除フラグ
        if move.is_way_unlock:
            way_unlock_str = '#'
        else:
            way_unlock_str = ''

        # 石の並び
        if move.option_stones == '':
            option_stones_str = ''
        else:
            option_stones_str = f'${move.option_stones}'

        # 路
        way = move.way
        way_str = move.way.to_human_presentable_text()

        # 演算子
        op = move.operator.code

        # 指し手
        # ------

        # NAND
        if op == 'na':
            # モディーする
            if board.exists_stone_on_way(move.way):
                p = way.low_way().to_human_presentable_text()
                q = way.high_way().to_human_presentable_text()

            # ニューする
            else:
                (p_way, q_way, error_reason) = board.get_input_ways_by_binary_operation(move.way)
                p = p_way.to_human_presentable_text()
                q = q_way.to_human_presentable_text()

            move_str = f"{way_str} <- {p} NAND {q}"

        # NOT High
        elif op == 'nH':
            # モディーする
            p = way.high_way().to_human_presentable_text()
            move_str = f"{way_str} <-        NOT  {p}"

        # NOT Low
        elif op == 'nL':
            # モディーする
            p = way.low_way().to_human_presentable_text()
            move_str = f"{way_str} <-        NOT  {p}"

        # NOR
        elif op == 'no':
            # モディーする
            if board.exists_stone_on_way(move.way):
                p = way.low_way().to_human_presentable_text()
                q = way.high_way().to_human_presentable_text()

            # ニューする
            else:
                (p_way, q_way, error_reason) = board.get_input_ways_by_binary_operation(move.way)
                p = p_way.to_human_presentable_text()
                q = q_way.to_human_presentable_text()

            move_str = f"{way_str} <- {p} NOR  {q}"

        # One
        elif op == 'on':
            move_str = f"{way_str} <- '1'"

        # Shift
        elif op.startswith('s'):
            bits = op[1:2]

            if move.way.is_file:
                sub_message = f"{bits}-bit to bottom"
            
            elif move.way.is_rank:
                sub_message = f"{bits}-bit to right"
            
            elif move.way.is_empty:
                sub_message = f"is illegal move"
            
            else:
                raise ValueError(f"undefined axis {move.way.axis_id=}")

            move_str = f'{way_str} <- SHIFT  {sub_message}'

        # XNOR
        elif op == 'xn':
            # モディーする
            if board.exists_stone_on_way(move.way):
                p = way.low_way().to_human_presentable_text()
                q = way.high_way().to_human_presentable_text()

            # ニューする
            else:
                (p_way, q_way, error_reason) = board.get_input_ways_by_binary_operation(move.way)
                p = p_way.to_human_presentable_text()
                q = q_way.to_human_presentable_text()

            move_str = f"{way_str} <- {p} XNOR {q}"

        # XOR
        elif op == 'xo':
            ## 対象の路に石が置いてある
            if board.exists_stone_on_way(move.way):
                p = way.low_way().to_human_presentable_text()
                q = way.high_way().to_human_presentable_text()

            else:
                (p_way, q_way, error_reason) = board.get_input_ways_by_binary_operation(move.way)
                p = p_way.to_human_presentable_text()
                q = q_way.to_human_presentable_text()

            move_str = f"{way_str} <- {p} XOR  {q}"

        # Zero
        elif op == 'ze':
            move_str = f"{way_str} <- '0'"
        
        # AND
        elif op == 'a':
            ## 対象の路に石が置いてある
            if board.exists_stone_on_way(move.way):
                p = way.low_way().to_human_presentable_text()
                q = way.high_way().to_human_presentable_text()

            else:
                (p_way, q_way, error_reason) = board.get_input_ways_by_binary_operation(move.way)
                p = p_way.to_human_presentable_text()
                q = q_way.to_human_presentable_text()

            move_str = f"{way_str} <- {p} AND  {q}"

        # Cut
        elif op == 'c':
            move_str = f"{way_str} <- Cut the edge"

        # Edit
        elif op == 'e':
            move_str = f"{way_str} <- Edit"
        
        # NOT
        elif op == 'n':
            ## 対象の路に石が置いてある
            if board.exists_stone_on_way(move.way):
                # n演算では、石の置いている対象路を指定してはいけません。nL, nH を参考にしてください
                move_str = f"(undefined 1)  {move.to_human_presentable_text()=}"

            else:
                # ニューする
                p = board.get_src_way_by_unary_operation(move.way).to_human_presentable_text()
                move_str = f"{way_str} <-        NOT  {p}"

        # OR
        elif op == 'o':
            ## 対象の路に石が置いてある
            if board.exists_stone_on_way(move.way):
                p = way.low_way().to_human_presentable_text()
                q = way.high_way().to_human_presentable_text()

            else:
                (p_way, q_way, error_reason) = board.get_input_ways_by_binary_operation(move.way)
                p = p_way.to_human_presentable_text()
                q = q_way.to_human_presentable_text()

            move_str = f"{way_str} <- {p} OR   {q}"

        else:
            raise ValueError(f"undefined operator {op=}")


        # 空白
        if way_unlock_str != '' and option_stones_str != '':
            space = ' '
        else:
            space = ''

        return f"{edit_mark}{move_str}{space}{way_unlock_str}{option_stones_str}"


    @staticmethod
    def print_distinct_legal_move_list(board):
        """（同じ指し手を除いた）合法手一覧表示
            code: legal_moves
        """
        print("""\
DISTINCT LEGAL MOVES
--------------------

+--------+---+
|Distinct|All| Command
+--------+---+""")

        legal_moves = SearchLegalMoves.generate_legal_moves(board)

        # 指した結果が同じになるような指し手も表示する
        # コードをキーにして降順にソートする
        legal_move_list = sorted(legal_moves.items, key=lambda x:x.to_code())

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


    @staticmethod
    def create_legal_move_code_help_list(board):
        """合法手メニュー一覧の作成"""

        menu_items = []

        # 指した結果が同じになるような指し手も表示する

        legal_move_list = SearchLegalMoves.generate_legal_moves(board).items

        # 合法手は１００個も無いだろう。連番は２桁で十分
        # 指し手コードの表示名は今のところ ３４文字が最長。 &, #, $ は付かないとき
        # "NOT on 2-file and put it in 3-file"
        for i in range(0, len(legal_move_list)):
            move = legal_move_list[i]

            # 指し手を、コードではなく、人間が読める名前で表示したい
            menu_items.append(MoveCodeHelp(
                code=move.to_code(),
                description=Views.create_human_presentable_move_text(board, move)))

        # description が降順になるようにソートする
        menu_items = sorted(menu_items, key=lambda x:x.description)

        return menu_items


    @staticmethod
    def print_legal_moves_menu(legal_move_code_help_list):
        """合法手メニューの表示

        縦方向に並べたい

        1 5  9
        2 6 10
        3 7 11
        4 8

        例えば 11 件で 3 列なら、行は roundup(11/3) で 4行と求まるから、
        2 列目の先頭は 1 + 4、 3 列目の先頭は 1 + 2*4 という連番になる
        """

        item_len = len(legal_move_code_help_list)
        column_num = 3
        row_num = math.ceil(item_len / 3)

        def print_separator():
            for i in range(0, column_num):
                print("+--+----+------------------------------------", end='')

            print("+")


        print("""\
LEGAL MOVES
-----------

+--+----+------------------------------------+
|No|Code|Description                         |""")

        print_separator()

        for j in range(0, row_num):
            for i in range(0, column_num):
                seq = i * row_num + j

                if seq < item_len:
                    # 指し手を、コードではなく、人間が読める名前で表示したい
                    help = legal_move_code_help_list[seq]
                    print(f"|{seq+1:2}|{help.code:4}| {help.description:<35}", end='')

                else:
                    print(f"|  |    |                                    ", end='') # 空欄

            print("|") # 改行

        print_separator()
