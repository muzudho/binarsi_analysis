from py_binarsi import BLACK_KOMI, WHITE_KOMI, C_EMPTY, C_BLACK, C_WHITE, BOARD_AREA, CLEAR_TARGETS_LEN, Colors, Move, MoveHelper, Board, SearchedClearTargets, SearchLegalMoves, SearchMateMoveIn1Play, SearchedGameover, PositionCommand, SfenHelper


class Views():
    """コロシアム用画面"""


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
