import math
import time
from py_binarsi import C_BLACK, C_WHITE, CLEAR_TARGETS_LEN, Colors, SearchLegalMoves


class MoveCodeHelp():
    """指し手コードの解説

    NOTE 画面レイアウトの都合から、４文字以内のコードしか利用できない。 "board" は５文字あるので入らない
    NOTE coliceum.__init__.py の方に置きたいが、それだと循環参照してしまうので views.__init__.py の方に置いてある
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
    """ビュー"""


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
    def print_settled_for_play_command(board, searched_clear_targets, searched_gameover):
        """決着の表示、play コマンド用"""
        current_turn = Colors.opponent(board.get_next_turn())
        
        if searched_gameover.is_black_win:
            if current_turn == C_BLACK:
                Views.print_you()
                Views.print_win()
            
            elif current_turn == C_WHITE:
                Views.print_you()
                Views.print_lose()

        elif searched_gameover.is_white_win:
            if current_turn == C_BLACK:
                Views.print_you()
                Views.print_lose()
            
            elif current_turn == C_WHITE:
                Views.print_you()
                Views.print_win()
        
        else:
            raise ValueError(f"undefined gameover. {searched_gameover.reason=}")


    @staticmethod
    def print_settled_for_coliceum(board, searched_clear_targets, searched_gameover):
        """決着の表示、コロシアム用
        
        - 三本勝負で決着したのなら、特に説明は要らない
        - 点数計算で決着したのなら、点数も表示
        """

        # TODO デバッグ消す
        #print(f"DEBUG コロシアム用の決着表示")

        current_turn = Colors.opponent(board.get_next_turn())
        
        if searched_gameover.is_black_win:
            if current_turn == C_BLACK:
                Views.print_you()
                Views.print_win()
            
            elif current_turn == C_WHITE:
                Views.print_you()
                Views.print_lose()

        elif searched_gameover.is_white_win:
            if current_turn == C_BLACK:
                Views.print_you()
                Views.print_lose()
            
            elif current_turn == C_WHITE:
                Views.print_you()
                Views.print_win()
        
        else:
            raise ValueError(f"undefined gameover. {searched_gameover.reason=}")

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
    def print_sorted_legal_move_list(board):
        """合法手一覧表示
            code: legal_moves
        """
        print("""\
LEGAL MOVES
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

            print(f"|{num_str}| play {move.to_code():<3}{same_move_str}")

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
