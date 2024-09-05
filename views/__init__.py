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
