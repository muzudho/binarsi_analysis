# 石（PieCe）番号
PC_EMPTY = 0
PC_BLACK = 1
PC_WHITE = 2

_pc_to_str = {
    0 : ' ',
    1 : '1',
    2 : '0',
}

# 盤面積
FILE_LEN = 7
RANK_LEN = 6
BOARD_AREA = FILE_LEN * RANK_LEN

_rank_to_num = {
    'a' : 0,
    'b' : 1,
    'c' : 2,
    'd' : 3,
    'e' : 4,
    'f' : 5,
}


class Square():
    """マス"""


    def __init__(self, sq):
        self._sq = sq


    @property
    def as_num(self):
        return self._sq


    @staticmethod
    def file_rank_to_sq(file, rank):
        return file * RANK_LEN + rank


    @staticmethod
    def code_to_sq_obj(code):
        """1a を Square(0) に変換するといった操作"""
        global _rank_to_num

        file_num = int(code[0:1]) - 1
        rank_num = _rank_to_num[code[1:2]]

        return Square(Square.file_rank_to_sq(file_num, rank_num))


class Move():
    """指し手

    例： "4n", "dn", "5o"

    軸（axis）、演算子（operator）

    軸： [1, 2, 3, 4, 5, 6, 7, a, b, c, d, e, f]
    演算子：
        s : Shift
        n : Not
        ze: ZEro
        no: NOr
        xo: XOr
        na: NAnd
        a : And
        xn: XNor
        o : Or
        on: ONe
    """

    def __init__(move_u):
        self._axis = move_u[0:1]
        
        if len(move_u) == 2:
            self._operator = move_u[1:2]
        else:
            self._operator = move_u[1:3]


class Board():
    """ビナーシ盤
    
        1 2 3 4 5 6 7
      +---------------+
    a | . . . . . . . |
    b | . . . . . . . |
    c | . . . . . . . |
    d | . . . . . . . |
    e | . . . . . . . |
    f | . . . . . . . |
      +---------------+

    マス番号：

         1  2  3  4  5  6  7
      +----------------------+
    a |  0  6 12 18 24 30 36 |
    b |  1  7 13 19 25 31 37 |
    c |  2  8 14 20 26 32 38 |
    d |  3  9 15 21 27 33 39 |
    e |  4 10 16 22 28 34 40 |
    f |  5 11 17 23 29 35 41 |
      +----------------------+
    """

    def __init__(self):
        # 各マス
        self._squares = [PC_EMPTY] * BOARD_AREA


    def reset(self):
        """TODO 平手初期局面に戻す"""
        self._squares = [PC_EMPTY] * BOARD_AREA

        sq = Square.code_to_sq_obj('3c').as_num
        self._squares[sq] = PC_WHITE


    def set_sfen(self, sfen_code):
        """TODO 指定局面に変更"""
        pass


    def push_usi(self, move_u):
        """TODO 一手指す"""
        pass


    def pop(self, move_u):
        """TODO 一手戻す"""
        pass


    def is_gameover(self):
        """TODO 終局しているか？"""
        pass


    def is_nyugyoku(self):
        """無視。ビナーシに入玉はありません"""
        pass

    def is_check(self):
        """TODO 一手詰めがあるか？"""
        pass

    def mate_move_in_1ply(self):
        """TODO 一手詰めの手を返す"""
        pass

    def legal_moves(self):
        """TODO 合法手の一覧を返す"""
        pass

    def as_str(self):
        """（拡張仕様）盤のテキスト形式"""
        global _pc_to_str

        # 数値を文字列に変更
        s = ["Q"] * BOARD_AREA
        for sq in range(0, BOARD_AREA):
            s[sq] = _pc_to_str[self._squares[sq]]

        return f"""\
    1 2 3 4 5 6 7
  +---------------+
a | {s[0]} {s[ 6]} {s[12]} {s[18]} {s[24]} {s[30]} {s[36]} |
b | {s[1]} {s[ 7]} {s[13]} {s[19]} {s[25]} {s[31]} {s[37]} |
c | {s[2]} {s[ 8]} {s[14]} {s[20]} {s[26]} {s[32]} {s[38]} |
d | {s[3]} {s[ 9]} {s[15]} {s[21]} {s[27]} {s[33]} {s[39]} |
e | {s[4]} {s[10]} {s[16]} {s[22]} {s[28]} {s[34]} {s[40]} |
f | {s[5]} {s[11]} {s[17]} {s[23]} {s[29]} {s[35]} {s[41]} |
  +---------------+
"""
