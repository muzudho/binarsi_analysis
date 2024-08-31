from py_binarsi import SearchLegalMoves


class Views():
    """ビュー"""


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
    def print_legal_moves_menu(board):
        """合法手メニューの表示"""

        # 指した結果が同じになるような指し手も表示する
        legal_move_list = SearchLegalMoves.generate_legal_moves(board).items

        # 合法手は１００個も無いだろう。連番は２桁で十分
        # （盤面編集を覗いた）対局棋譜に出てくる指し手コードは 1xo のような３桁のものが最長だろう。 &, #, $ は付かない

        print("""\
LEGAL MOVES
""")

        for i in range(0, len(legal_move_list)):
            move = legal_move_list[i]

            if i % 8 == 0:
                print("""\
+----------+----------+----------+----------+----------+----------+----------+----------+""")

            print(f"| ({i+1:2}) {move.to_code():<3} ", end='')

            if i % 8 == 7:
                print("|") # 改行

        if len(legal_move_list) % 8 != 0:
            for i in range(0, 8 - len(legal_move_list) % 8):
                print(f"|          ", end='') # 空欄

            print("|") # 改行

        print(f"""\
+----------+----------+----------+----------+----------+----------+----------+----------+""")
