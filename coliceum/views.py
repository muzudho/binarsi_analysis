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

(1) VS computer
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
