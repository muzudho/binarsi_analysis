from py_binarsi import SearchLegalMoves


class MoveCodeHelp():
    """指し手コードの解説"""


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
        way_str = move.way.to_human_presentable_text()

        # 演算子
        op = move.operator.code

        # 指し手
        # ------

        # NAND
        if op == 'na':
            move_str = f"NAND and put it in {way_str}"

        # NOT High
        elif op == 'nH':
            high_way_str = move.way.high_way().to_human_presentable_text()
            move_str = f"NOT on {high_way_str} and put it in {way_str}"

        # NOT Low
        elif op == 'nL':
            low_way_str = move.way.low_way().to_human_presentable_text()
            move_str = f"NOT on {low_way_str} and put it in {way_str}"

        # NOR
        elif op == 'no':
            move_str = f"NOR and put it in {way_str}"

        # One
        elif op == 'on':
            move_str = f"Fill 1 in {way_str}"

        # Shift
        elif op.startswith('s'):
            bits = op[1:2]

            if move.way.is_file:
                # 例： Shift 1-file 1-bit to forward
                # 半角 29 文字
                move_str = f'Shift {way_str} {bits}-bit to forward'
            
            elif move.way.is_rank:
                # 例： Shift c-rank 1-bit to right
                move_str = f'Shift {way_str} {bits}-bit to right'
            
            elif move.way.is_empty:
                move_str = f'Shift {way_str} is illegal move'
            
            else:
                raise ValueError(f"undefined axis {move.way.axis_id=}")

        # XNOR
        elif op == 'xn':
            move_str = f"XNOR and put it in {way_str}"

        # XOR
        elif op == 'xo':
            move_str = f"XOR and put it in {way_str}"

        # Zero
        elif op == 'ze':
            move_str = f"fill 0 in {way_str}"
        
        # AND
        elif op == 'a':
            move_str = f"AND and put it in {way_str}"

        # Cut
        elif op == 'c':
            move_str = f"Cut the edge {way_str}"

        # Edit
        elif op == 'e':
            move_str = f"Edit {way_str}"
        
        # NOT
        elif op == 'n':
            ## 対象の路に石が置いてある
            if board.exists_stone_on_way(move.way):
                # n演算では、石の置いている対象路を指定してはいけません。nL, nH を参考にしてください
                move_str = f"(undefined 1)  {move.to_code()=}"

            else:
                # ニューする
                src_way_str = board.get_src_way_by_unary_operation(move.way).to_human_presentable_text()
                move_str = f"NOT on {src_way_str} and put it in {way_str}"

        # OR
        elif op == 'o':
            move_str = f"OR and put it in {way_str}"

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


        return menu_items


    @staticmethod
    def print_legal_moves_menu(legal_move_code_help_list):
        """合法手メニューの表示"""

        column_num = 3

        def print_separator():
            for i in range(0, column_num):
                print("+-----------------------------------------", end='')

            print("+")


        print("""\
LEGAL MOVES""")

        for i in range(0, len(legal_move_code_help_list)):
            description = legal_move_code_help_list[i].description

            if i % column_num == 0:
                print_separator()

            # 指し手を、コードではなく、人間が読める名前で表示したい
            print(f"| ({i+1:2}) {description:<34} ", end='')

            if (i + 1) % column_num == 0:
                print("|") # 改行

        if len(legal_move_code_help_list) % column_num != 0:
            for i in range(0, column_num - len(legal_move_code_help_list) % column_num):
                print(f"|                                         ", end='') # 空欄

            print("|") # 改行

        print_separator()
