from py_binarsi import BLACK_KOMI, WHITE_KOMI, C_EMPTY, C_BLACK, C_WHITE, CLEAR_TARGETS_LEN, Colors, Move, MoveHelper, Board, SearchedClearTargets, SearchLegalMoves, SearchMateMoveIn1Play, SearchedGameover, PositionCommand
from views.board import BoardViews


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
(2) quit

please input number(1-2):""")


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
        print(BoardViews.stringify_board_hard(board))   # 盤面


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
