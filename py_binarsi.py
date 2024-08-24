import re

# 石（PieCe）番号
#   コンピュータ将棋プログラミングの Piece という変数名を踏襲
PC_EMPTY = 0
PC_BLACK = 1
PC_WHITE = 2

_pc_to_str = {
    0 : ' ',
    1 : '1',
    2 : '0',
}

_pc_to_binary = {
    1: 1,
    2: 0,
}

_bool_to_pc = {
    True: PC_BLACK,
    False: PC_WHITE,
}

# 軸
FILE_ID = 1
RANK_ID = 2

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

_num_to_rank = {
    0 : 'a',
    1 : 'b',
    2 : 'c',
    3 : 'd',
    4 : 'e',
    5 : 'f',
}

_axis_characters = ['1', '2', '3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'f']


class Square():
    """マス"""


    def __init__(self, sq):
        self._sq = sq


    @property
    def as_num(self):
        return self._sq


    @staticmethod
    def file_rank_to_sq(file, rank, swap=False):
        """筋と段をマス番号に変換

        Parameters
        ----------
        file : int
            筋番号
        rank : int
            マス番号
        swap : bool
            file と rank をひっくり返して利用
        """

        if swap:
            temp = file
            file = rank
            rank = temp

        if file < 0 or FILE_LEN <= file or rank < 0 or RANK_LEN <= rank:
            raise ValueError(f"{file=}  {rank=}")

        return file * RANK_LEN + rank


    @staticmethod
    def code_to_sq_obj(code):
        """1a を Square(0) に変換するといった操作"""
        global _rank_to_num

        file_num = int(code[0:1]) - 1
        rank_num = _rank_to_num[code[1:2]]

        return Square(Square.file_rank_to_sq(file_num, rank_num))


class SquareCursor():
    """盤上のマスを指すカーソル
    進行方向は、盤の左上から始まって右へ、右端から１段下の左端へ"""


    def __init__(self):
        self._file = 0
        self._rank = 0


    @property
    def file(self):
        return self._file


    @property
    def rank(self):
        return self._rank


    def file_forward(self):
        """カーソルを１つ進める"""
        if self._file < FILE_LEN - 1:
            self._file += 1
        
        # 改行
        else:
            self._file = 0
            self._rank += 1


    def get_sq(self):
        """マス番号を返す"""
        return Square.file_rank_to_sq(self._file, self._rank)


class Axis():
    """軸

    例： '1',  '2', '3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'f'
    """

    _code_to_axis_obj = None

    def __init__(self, axis_id, number):
        """初期化
        Parameters
        ----------
        axis_id : int
            1: file
            2: rank
        """

        if axis_id not in (FILE_ID, RANK_ID):
            raise ValueError(f"undefined axis id: {axis_id}")

        self._axis_id = axis_id
        self._number = number


    @property
    def axis_id(self):
        return self._axis_id


    @property
    def number(self):
        return self._number


    @classmethod
    def code_to_axis(clazz, code):
        """生成

        Parameters
        ----------
        code : str
            "1" ～ "7"、 "a" ～ "f"
        """

        # フォーマットチェック
        result = re.match(r"^[1234567abcdef]$", code)
        if result is None:
            raise ValueError(f"format error.  axis_u:`{code}`")


        if clazz._code_to_axis_obj is None:
            clazz._code_to_axis_obj = {
                '1': Axis(FILE_ID, 0),
                '2': Axis(FILE_ID, 1),
                '3': Axis(FILE_ID, 2),
                '4': Axis(FILE_ID, 3),
                '5': Axis(FILE_ID, 4),
                '6': Axis(FILE_ID, 5),
                '7': Axis(FILE_ID, 6),
                'a': Axis(RANK_ID, 0),
                'b': Axis(RANK_ID, 1),
                'c': Axis(RANK_ID, 2),
                'd': Axis(RANK_ID, 3),
                'e': Axis(RANK_ID, 4),
                'f': Axis(RANK_ID, 5),
            }


        if code in clazz._code_to_axis_obj:
            return clazz._code_to_axis_obj[code]

        raise ValueError(f"not found axis.  code:{code}")


    def to_code(self):
        """
        Returns
        -------
        '1' ～ '7' や、 'a' ～ 'f' といった文字
        """
        global _num_to_rank

        if self._axis_id == FILE_ID:
            return str(self._number + 1)

        if self._axis_id == RANK_ID:
            return _num_to_rank[self._number]
        
        raise ValueError(f"axis_id:{self._axis_id}  number:{self._number}")


    def low_axis(self, diff = 1):
        """１つ小さい方の軸"""
        if self._number < diff:
            return None
        
        return Axis(self._axis_id, self._number - diff)


    def high_axis(self, diff = 1):
        """１つ大きい方の軸"""
        if self._axis_id == FILE_ID:
            if self._number < FILE_LEN - diff:
                return Axis(self._axis_id, self._number + diff)
            else:
                return None

        elif self._axis_id == RANK_ID:
            if self._number < RANK_LEN - diff:
                return Axis(self._axis_id, self._number + diff)
            else:
                return None

        raise ValueError(f"{self._axis_id=}")


class Operator():
    """演算子

    例： `4n` - 4筋に Not 演算を用いて New するケース

    主な演算子の語幹：
        c : Cut the edge 対象軸上の全石を削除
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
    ただし、 c, ze, on は対局中は使わない。盤面編集用
    
    ただし、SHIFT はさらに、ずらすビット数が後ろに付く：
        s0
        s1
        s2
        s3
        s4
        s5
        s6
    筋の場合は上から下へ、段の場合は左から右へ、が順方向

    NOT は単項演算子なので、Reverse するときは、 In が Low, High のどちらか指定する必要がある
        n
        nL
        nH
    
    強制的にロックを外したい場合、末尾に `#` を付ける。これは盤面操作のためのもので、対局での使用は想定していない
        例： `7c#` - ７筋の全石を取り除き、ロックも外す
    """

    def __init__(self, stem_u, parameter_length, force_unlock=False):
        """初期化
        
        Parameters
        ----------
        stem_u : str
            演算子語幹部のUSI書式文字列（軸ロック指定を除く）
        parameter_length: int
            引数の個数
        force_unlock : bool
        	強制アンロック
        	True:  強制的にロックを解除する。盤面編集時に利用
        	False: 対局ルールにある動作をする。遊び方に従ってロックがかかるか、遊び方に従ってロックをかけないかのどちらか
        """
        self._stem_u = stem_u
        self._parameter_length = parameter_length
        self._force_unlock = force_unlock


    @property
    def stem_u(self):
        return self._stem_u


    @property
    def parameter_length(self):
        return self._parameter_length


    @property
    def force_unlock(self):
        return self._force_unlock


    @staticmethod
    def code_to_obj(code):
        """コードからオブジェクトへ変換
        
        Parameters
        ----------
        code : str
            コード（演算子語幹部、軸ロック指定含む）
        """
        # フォーマットチェック
        #
        #   文字数が短い方が先にマッチしてしまうかもしれないので、短い文字列は右に置くように並び順に注意
        #
        result = re.match(r"^(na|nH|nL|no|on|s0|s1|s2|s3|s4|s5|s6|xn|xo|ze|a|c|n|o)(#)?$", code)
        if result is None:
            raise ValueError(f"format error.  operator_u:`{code}`")

        stem_u = result.group(1)
        force_unlock = result.group(2) == '#'

        # 零項演算子（nullary）か？
        if stem_u in ['s0', 's1', 's2', 's3', 's4', 's5', 's6', 'c']:
            parameter_length = 0

        # 単項演算子（unarry）か？
        elif stem_u in ['nH', 'nL', 'n']:
            parameter_length = 1

        # 二項演算子（binary）か？
        elif stem_u in ['na', 'no', 'on', 'xn', 'xo', 'ze', 'a', 'o']:
            parameter_length = 2
        
        else:
            raise ValueError(f"undefined operator: {code=}")

        return Operator(
            stem_u=stem_u,
            parameter_length=parameter_length,
            force_unlock=force_unlock)


    @property
    def code(self):
        if self._force_unlock:
            force_unlock_str = '#'
        else:
            force_unlock_str = ''
    
        return f"{self._stem_u}{force_unlock_str}"


    @property
    def force_unlock(self):
        """強制アンロック
        	True:  強制的にロックを解除する。盤面編集時に利用
        	False: 対局ルールにある動作をする。遊び方に従ってロックがかかるか、遊び方に従ってロックをかけないかのどちらか
        """
        return self._force_unlock


    def unary_operate(self, stone):
        """単項演算する

        Parameters
        ----------
        stone : int
            石の種類
        """

        # ノット（単項演算子 New）
        if self._stem_u in ['nH', 'nL', 'n']:
            if stone == PC_BLACK:
                return PC_WHITE
            
            if stone == PC_WHITE:
                return PC_BLACK
            
            if stone == PC_EMPTY:
                return PC_EMPTY
        
        raise ValueError(f"undefined operator  stem_u:{self._stem_u}  stone:{stone}")


    def binary_operate(self, left_operand, right_operand):
        """二項演算する
        
        Parameters
        ----------
        left_operand : int
            左項
        right_operand : int
            右項
        
        Returns
        -------
        stone : int
            PC_BLACK, PC_WHITE のいずれかを返す
        """

        global _bool_to_pc

        # 変数名を縮める
        l = left_operand
        r = right_operand
        stem_u = self._stem_u

        # ゼロ
        if stem_u == 'ze':
            # 常に白石を返す
            return PC_WHITE
        
        # ノア
        if stem_u == 'no':
            return _bool_to_pc[not(l == 1 or r == 1)]
        
        # エクソア
        if stem_u == 'xo':
            return _bool_to_pc[(l ^ r) == 1]
        
        # ナンド
        if stem_u == 'na':
            return _bool_to_pc[not(l == 1 and r == 1)]
        
        # アンド
        if stem_u == 'a':
            return _bool_to_pc[l == 1 and r == 1]
        
        # エクスノア
        if stem_u == 'xn':
            return _bool_to_pc[(l ^ r) != 1]
        
        # オア
        if stem_u == 'o':
            return _bool_to_pc[l == 1 or r == 1]
        
        # ワン
        if stem_u == 'on':
            # 常に黒石を返す
            return PC_BLACK

        raise ValueError(f"undefined operator  stem_u:{stem_u}  {l=}  {r=}")


class Move():
    """指し手

    対局棋譜での例：
        "4n", "dn", "5o"
    
    盤面編集履歴での例：
        "&7c#"

    アンドゥ操作での例：
        "4c#$01" - TODO 変更前の石の連情報を、$記号の後ろに付加する

    盤面編集フラグ、出力軸（axis）、演算子（operator）
        ※演算子にロックフラグ含む
    """

    def __init__(self, axis, operator, when_edit=False):
        """初期化
        
        Parameters
        ----------
        axis : Axis
            軸オブジェクト
        operator : str
            演算子
        when_edit : bool
            盤面編集か？
        """
        self._axis = axis
        self._operator = operator
        self._when_edit = when_edit


    @property
    def axis(self):
        """軸オブジェクト"""
        return self._axis


    @property
    def operator(self):
        """演算子オブジェクト"""
        return self._operator


    @property
    def when_edit(self):
        """盤面編集か？"""
        return self._when_edit


    @staticmethod
    def code_to_obj(code):

        result = re.match(r"^(&)?([1234567abcdef])(.+)$", code)
        if result is None:
            raise ValueError(f"format error.  move_u:`{code}`")


        return Move(
            # 軸
            axis=Axis.code_to_axis(code=result.group(2)),
            # 演算子
            operator=Operator.code_to_obj(code=result.group(3)),
            # 盤面編集フラグ
            when_edit=result.group(1) is not None)


    def to_code(self):
        if self._when_edit:
            edit_mark = '&'
        else:
            edit_mark = ''

        return f"{edit_mark}{self.axis.to_code()}{self.operator.code}"


class MoveHelper():
    """指し手の計算"""

    @staticmethod
    def let_inverse_move(move, stones_before_change):
        """逆操作を算出する

        Parameters
        ----------
        move : str
            順操作
        stones_before_change : str
            操作する前の連の状態

        Returns
        -------
        inverse_move : Move
            逆操作
        """

        # 変数名を縮める
        op = move.operator.stem_u
        axis = move.axis

        # TODO 逆操作 カットザエッジ
        if op == 'c':
            # カットザエッジされた軸に、消された石を戻す
            print("[逆操作] c")

            # move = ""

            # if stones_before_change != '':
            #     # TODO 指し手に＄記号を付加し、その後ろに変更前の石の連の情報を付加する
            #     move += f"${stones_before_change}"

            return None


        # TODO 逆操作 0ビットシフト
        elif op == 's0':
            print("[逆操作] s0")
            return None


        # TODO 逆操作 1ビットシフト
        elif op == 's1':
            print("[逆操作] s1")
            return None


        # TODO 逆操作 2ビットシフト
        elif op == 's2':
            print("[逆操作] s2")
            return None


        # TODO 逆操作 3ビットシフト
        elif op == 's3':
            print("[逆操作] s3")
            return None


        # TODO 逆操作 4ビットシフト
        elif op == 's4':
            print("[逆操作] s4")
            return None


        # TODO 逆操作 5ビットシフト
        elif op == 's5':
            print("[逆操作] s5")
            return None


        # TODO 逆操作 6ビットシフト
        elif op == 's6':
            print("[逆操作] s6")
            return None


        # ノット・ニュー --逆操作--> カットザエッジ＃
        elif op == 'n':
            return Move.code_to_obj(f"{axis.to_code()}c#")


        # TODO 逆操作 ノットＬ
        elif op == 'nL':
            print("[逆操作] nL")
            return None


        # TODO 逆操作 ノットＨ
        elif op == 'nH':
            print("[逆操作] nH")
            return None


        # TODO 逆操作 ゼロ
        elif op == 'ze':
            print("[逆操作] ze")
            return None


        # TODO 逆操作 ノア
        elif op == 'no':
            print("[逆操作] no")
            return None


        # TODO 逆操作 エクソア
        elif op == 'xo':
            print("[逆操作] xo")
            return None


        # TODO 逆操作 ナンド
        elif op == 'na':
            print("[逆操作] na")
            return None


        # TODO 逆操作 アンド
        elif op == 'a':
            print("[逆操作] a")
            return None


        # TODO 逆操作 エクスノア
        elif op == 'xn':
            print("[逆操作] xn")
            return None


        # TODO 逆操作 オア
        elif op == 'o':
            print("[逆操作] o")
            return None


        # TODO 逆操作 ワン
        elif op == 'on':
            print("[逆操作] on")
            return None


        else:
            raise ValueError(f"undefined operator:{op}")


class BoardEditingItem():
    """盤面編集記録"""

    def __init__(self, move, stones_before_change=''):
        """初期化
        
        Parameters
        ----------
        move : Move
            指し手
        stones_before_change : str
            裏返して消えた石
        """
        self._move = move
        self._stones_before_change = stones_before_change


    @property
    def move(self):
        """指し手"""
        return self._move


    @property
    def stones_before_change(self):
        """裏返して消えた石"""
        return self._stones_before_change


class BoardEditingHistory():
    """盤面編集履歴"""

    def __init__(self):
        # 盤面編集履歴（対局棋譜を含む）
        self._items = []

        # 対局棋譜に限定
        self._game_items = []


    @property
    def items(self):
        return self._items


    @property
    def game_items(self):
        return self._game_items


    def append(self, board_editing_item):
        self._items.append(board_editing_item)

        if not board_editing_item.move.when_edit:
            self._game_items.append(board_editing_item)


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
        # 初期化
        self.subinit()


    def subinit(self):
        """（サブ部分として）盤をクリアーする"""

        # 初期局面の各マス
        #
        #   SFENで初期局面を出力するためのもの
        #
        self._squares_at_init = None

        # 初期局面での手番
        #
        #   平手初期局面の先手は必ず黒番（将棋と違って上手、下手が無いので）。
        #   ただし、途中局面は自由に設定できるので、白番から始めるように変更したいときがある
        #
        self._turn_at_init = PC_BLACK

        # 現局面の各マス
        self._squares = [PC_EMPTY] * BOARD_AREA

        # 現局面の合法手
        self._legal_moves = []

        # 現局面の盤面編集用の手（合法手除く）
        self._moves_for_edit = []

        # 現局面での軸ロック
        self._axis_locks = {
            '1' : False,
            '2' : False,
            '3' : False,
            '4' : False,
            '5' : False,
            '6' : False,
            '7' : False,
            'a' : False,
            'b' : False,
            'c' : False,
            'd' : False,
            'e' : False,
            'f' : False,
        }

        # 初期局面での軸ロック
        self._axis_locks_at_init = dict(self._axis_locks)

        # 盤面編集履歴（対局棋譜を含む）
        self._board_editing_history = BoardEditingHistory()

        # 終局理由。無ければ空文字列
        self._gameover_reason = ''

        # 勝利条件をクリアーしたのが何手目か
        self._cleared_targets = [-1, -1, -1, -1, -1, -1]


    @property
    def gameover_reason(self):
        """終局理由"""
        return self._gameover_reason


    @property
    def legal_moves(self):
        """合法手一覧
        
        moves は、同じ局面での指し手の選択肢方向に長い
        """
        return self._legal_moves


    @property
    def moves_for_edit(self):
        """盤面編集用の手（合法手除く）"""
        return self._moves_for_edit


    @property
    def board_editing_history(self):
        """盤面編集履歴（対局棋譜のスーパーセット）

        history は時間方向に長い
        """
        return self._board_editing_history


    def update_squares_at_init(self):
        """初期局面を記憶（SFENで初期局面を出力したいときのためのもの）"""
        if self._squares_at_init is None:
            self._squares_at_init = list(self._squares)


    def clear(self):
        """盤をクリアーする"""
        self.subinit()


    def reset(self):
        """平手初期局面に戻す"""
        self.subinit()

        sq = Square.code_to_sq_obj('3c').as_num
        self._squares[sq] = PC_WHITE

        self.update_legal_moves()


    def set_sfen(self, sfen_u):
        """指定局面に変更

        Parameters
        ----------
        sfen_u : str
            SFEN書式文字列

            例： `7/7/2o4/7/7/7 b - 0`

                    1 2 3 4 5 6 7
                  +---------------+
                a |               |
                b |               |
                c |     0         |
                d |               |
                e |               |
                f |               |
                  +---------------+

            例： `xooooxo/xooxxxo/ooxxooo/xooxxox/xoxxxxx/ooxoooo b 1234567abcdef 0`

                    # # # # # # #
                  +---------------+
                # | 1 0 0 0 0 1 0 |
                # | 1 0 0 1 1 1 0 |
                # | 0 0 1 1 0 0 0 |
                # | 1 0 0 1 1 0 1 |
                # | 1 0 1 1 1 1 1 |
                # | 0 0 1 0 0 0 0 |
                  +---------------+
        """
        global _axis_characters

        # 盤面の初期化
        self.subinit()

        cursor = SquareCursor()

        parts = sfen_u.split(' ')

        # 盤面
        # ----
        numeric = 0
        for ch in parts[0]:
            if ch in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                numeric *= 10
                numeric += int(ch)

            elif ch in ['x', 'o']:
                # 空白の数をフラッシュ
                while 0 < numeric:
                    # フォワード
                    cursor.file_forward()
                    numeric -= 1

                sq = cursor.get_sq()

                if ch == 'x':
                    self._squares[sq] = PC_BLACK
                else:
                    self._squares[sq] = PC_WHITE

                # フォワード
                cursor.file_forward()

            elif ch == '/':
                pass

            else:
                raise ValueError(f"undefined sfen character on board:`{ch}`")

        # 添付盤面での手番
        # ---------------
        if parts[1] == 'b':
            self._turn_at_init = PC_BLACK
        elif parts[1] == 'w':
            self._turn_at_init = PC_WHITE
        else:
            raise ValueError(f"undefined sfen character on turn:`{ch}`")

        # 軸ロック
        # --------
        for axis_u in parts[2]:
            if axis_u in _axis_characters:
                self._axis_locks[axis_u] = True
                self._axis_locks_at_init[axis_u] = True

            else:
                raise ValueError(f"undefined sfen character on locks:`{axis_u}`")

        # TODO 手数の解析
        pass


    def exists_stone_on_axis(self, axis):
        """指定の軸に石が置いてあるか？
        
        Parameters
        ----------
        axis : Axis
            軸オブジェクト
        """

        # 筋
        if axis.axis_id == FILE_ID:
            for rank in range(0, RANK_LEN):
                sq = Square.file_rank_to_sq(axis.number, rank)
                stone = self._squares[sq]

                if stone != PC_EMPTY:
                    return True
                
            return False

        # 段
        if axis.axis_id == RANK_ID:
            for file in range(0, FILE_LEN):
                sq = Square.file_rank_to_sq(file, axis.number)
                stone = self._squares[sq]

                if stone != PC_EMPTY:
                    return True
                
            return False

        raise ValueError(f"undefined axis_id: {axis.axis_id}")


    def get_position_on_axis(self, axis):
        """軸を指定すると、そこにある石の連なりの開始位置と長さを返す

        例えば：

            1 2 3 4 5 6 7
          +---------------+
        a | . . . . . . . |
        b | . . . . . . . |
        c | . . 0 1 0 1 . |
        d | . . . . . . . |
        e | . . . . . . . |
        f | . . . . . . . |
          +---------------+

        上図の c 段を指定すると、 start:2, length:4 のような数を返す
        """
        # 入力筋を探索
        if axis.axis_id == FILE_ID:
            src_dst_file = axis.number

            # 入力軸から、出力軸へ、評価値を出力
            #
            #   必要な変数を調べる：
            #       最初のマージン（空欄）は無視する
            #       最初の石の位置を覚える。変数名を begin とする
            #       連続する石の長さを覚える。変数名を length とする
            #       最後のマージン（空欄）は無視する
            source_stones = [PC_EMPTY] * RANK_LEN
            state = 0
            begin = 0
            length = 0
            for rank in range(0, RANK_LEN):
                src_sq = Square.file_rank_to_sq(src_dst_file, rank)
                stone = self._squares[src_sq]
                source_stones[rank] = stone

                if state == 0:
                    if stone != PC_EMPTY:
                        begin = rank
                        state = 1
                elif state == 1:
                    if stone == PC_EMPTY:
                        length = rank - begin
                        state = 2

            if state == 1:
                length = RANK_LEN - begin
                state = 2

            return (begin, length)

        # 入力段を探索
        if axis.axis_id == RANK_ID:
            src_dst_rank = axis.number

            # 入力軸から、出力軸へ、評価値を出力
            #
            #   必要な変数を調べる：
            #       最初のマージン（空欄）は無視する
            #       最初の石の位置を覚える。変数名を begin とする
            #       連続する石の長さを覚える。変数名を length とする
            #       最後のマージン（空欄）は無視する
            source_stones = [PC_EMPTY] * FILE_LEN
            state = 0
            begin = 0
            length = 0
            for file in range(0, FILE_LEN):
                src_sq = Square.file_rank_to_sq(file, src_dst_rank)
                stone = self._squares[src_sq]
                source_stones[file] = stone

                if state == 0:
                    if stone != PC_EMPTY:
                        begin = file
                        state = 1
                elif state == 1:
                    if stone == PC_EMPTY:
                        length = file - begin
                        state = 2

            if state == 1:
                length = FILE_LEN - begin
                state = 2

            return (begin, length)

        raise ValueError(f"undefined axis_id:{axis.axis_id}")


    def copy_stones_on_line_unary(self, move, overwrite=False):
        """入力軸 a を単項演算して、 b 軸へ出力

        例えば：
        
            1 2 3 4 5 6 7
          +---------------+
        a | . . . . . . . |
        b | . . . . . . . |
        c | a a a a a a a |
        d | b b b b b b b |
        e | . . . . . . . |
        f | . . . . . . . |
          +---------------+

        上図の a を単項演算した結果を b へ出力
        """

        stones_before_change = ''

        # 筋方向
        if move.axis.axis_id == FILE_ID:
            for rank in range(0, RANK_LEN):

                dst_sq = Square.file_rank_to_sq(move.axis.number, rank)
                old_stone = self._squares[dst_sq]

                if overwrite and old_stone != PC_EMPTY:
                    stones_before_change += _pc_to_str[old_stone]

                self._squares[dst_sq] = move.operator.unary_operate(
                    stone=self._squares[Square.file_rank_to_sq(move.axis.number + 1, rank)])

            return stones_before_change


        # 段方向
        if move.axis.axis_id == RANK_ID:
            for file in range(0, FILE_LEN):

                dst_sq = Square.file_rank_to_sq(file, move.axis.number)
                old_stone = self._squares[dst_sq]

                if overwrite and old_stone != PC_EMPTY:
                    stones_before_change += _pc_to_str[old_stone]

                self._squares[dst_sq] = move.operator.unary_operate(
                    stone=self._squares[Square.file_rank_to_sq(file, move.axis.number + 1)])

            return stones_before_change


        raise ValueError(f"undefined axis_id:{move.axis.axis_id}")


    def copy_stones_on_line_binary(self, move):
        """入力軸 a, b を二項演算して、 c 軸へ出力

        例えば：
        
            1 2 3 4 5 6 7
          +---------------+
        a | . . . . . . . |
        b | . . . . . . . |
        c | a a a a a a a |
        d | c c c c c c c |
        e | b b b b b b b |
        f | . . . . . . . |
          +---------------+

        上図の a, b を二項演算した結果を c へ出力

        Parameters
        ----------
        move : Move
            指し手
        """

        global _pc_to_binary

        stones_before_change = ''

        # 筋方向
        if move.axis.axis_id == FILE_ID:
            opponent_axis_length = RANK_LEN
            swap = False
        
        # 段方向
        elif move.axis.axis_id == RANK_ID:
            opponent_axis_length = FILE_LEN
            swap = True

        else:
            raise ValueError(f"undefined axis_id  {move.axis.axis_id=}")


        (input_axis_1, input_axis_2) = self.get_input_axes_by_binary_operation(move.axis)


        # 対象の軸に石が置いてある --> Reverse 操作
        if self.exists_stone_on_axis(move.axis):
            print(f"[push_usi] 対象の軸に石が置いてある  {move.axis.number=}  {input_axis_1.number=}  {input_axis_2.number=}")
            overwrite=True

        # 対象の軸に石が置いてない ---> New 操作
        else:
            print(f"[push_usi] 対象の軸に石が置いてない  {move.axis.number=}  {input_axis_1.number=}  {input_axis_2.number=}")
            overwrite=False


        # 筋（段）両用
        for i in range(0, opponent_axis_length):

            dst_sq = Square.file_rank_to_sq(move.axis.number, i, swap=swap)
            old_stone = self._squares[dst_sq]

            if overwrite and old_stone != PC_EMPTY:
                stones_before_change += _pc_to_str[old_stone]

            input_stone_at_first = self._squares[Square.file_rank_to_sq(input_axis_1.number, i, swap=swap)]
            input_stone_at_second = self._squares[Square.file_rank_to_sq(input_axis_2.number, i, swap=swap)]

            #print(f"{move.axis.axis_id=}  {i=}  {input_axis_1.number=}  {input_axis_2.number=}  {input_stone_at_first=}  {input_stone_at_second=}  {dst_sq=}")

            if input_stone_at_first == PC_EMPTY or input_stone_at_second == PC_EMPTY:
                continue

            self._squares[dst_sq] = move.operator.binary_operate(
                left_operand=_pc_to_binary[input_stone_at_first],
                right_operand=_pc_to_binary[input_stone_at_second])

        return stones_before_change


    def push_usi(self, move_u):
        """一手指す

        Parameters
        ----------
        move_u : str
            対局時の例：
            	"4n"
            盤面編集時の例：
            	"&7c#"
        """        
        move = Move.code_to_obj(move_u)
        stones_before_change = ''

        # 演算子の変数名を縮める
        op = move.operator.code
        """
        演算子：
            c : Cut the edge
            s0 ～ s6: Shift
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

        # カットザエッジ演算子
        if op.startswith('c'):

            # 対象の軸に石が置いてある ---> Reverse操作
            if self.exists_stone_on_axis(move.axis):
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    axis_swap = False
                
                # 段方向
                elif move.axis.axis_id == RANK_ID:
                    axis_swap = True
                
                else:
                    raise ValueError(f"undefined axis_id  {move.axis.axis_id=}")


                # 筋（段）方向両用
                (begin, length) = self.get_position_on_axis(move.axis)

                for src_dst_i in range(begin, begin+length):
                    src_dst_sq = Square.file_rank_to_sq(move.axis.number, src_dst_i, swap=axis_swap)

                    # 空欄で上書き
                    stone = self._squares[src_dst_sq]
                    if stone != PC_EMPTY:
                        stones_before_change += _pc_to_str[stone]
                        self._squares[src_dst_sq] = PC_EMPTY


                if move.operator.force_unlock:
                    new_lock = False
                else: 
                    # カットザエッジを対局中に使うことは想定していない。盤面編集時に石を消すことを想定している。暫定的にカットザエッジを使うと軸ロックがかかるものとする
                    new_lock = True

                self._axis_locks[move.axis.to_code()] = new_lock
                self._board_editing_history.append(BoardEditingItem(
                    move=move,
                    stones_before_change=stones_before_change))
                self.update_legal_moves()
                return


            # 対象の軸に石が置いてない ---> イリーガルムーブ
            else:
                print("Illegal move")
                return


        # シフト（単項演算子 shift）
        #
        #   オペレーターの機能というより、ボードの機能
        #   このゲームでのシフトは、入力と出力は同じ筋（段）上で行います（inplace）
        #
        if op.startswith('s'):
            # 何ビットシフトか？
            bit_shift = int(op[1:2])

            # 対象の軸に石が置いてある ---> Shift操作
            if self.exists_stone_on_axis(move.axis):
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    axis_swap = False
                    opponent_axis_length = RANK_LEN
                
                # 段方向
                elif move.axis.axis_id == RANK_ID:
                    axis_swap = True
                    opponent_axis_length = FILE_LEN
                
                else:
                    raise ValueError(f"undefined axis_id  {move.axis.axis_id=}")

                # 筋（段）方向両用

                # 入力軸から、出力軸へ、評価値を出力
                #
                #   (1) 必要な変数を調べる：
                #       最初のマージン（空欄）は無視する
                #       最初の石の位置を覚える。変数名を begin とする
                #       連続する石の長さを覚える。変数名を length とする
                #       最後のマージン（空欄）は無視する
                #   
                #   (2) 石を移す：
                #       石を移す先の配列のインデックスの求め方は以下の通り
                #       dst_index = (src_index - begin + bit_shift) % length + begin

                source_stones = [PC_EMPTY] * opponent_axis_length
                for i in range(0, opponent_axis_length):
                    src_sq = Square.file_rank_to_sq(move.axis.number, i, swap=axis_swap)
                    stone = self._squares[src_sq]
                    source_stones[i] = stone

                # (1)
                (begin, length) = self.get_position_on_axis(move.axis)

                # (2)
                for i in range(begin, begin+length):
                    dst_sq = Square.file_rank_to_sq(
                        file=move.axis.number,
                        rank=(i - begin + bit_shift) % length + begin,
                        swap=axis_swap)

                    # コピー
                    self._squares[dst_sq] = source_stones[i]


                if move.operator.force_unlock:
                    new_lock = False
                else: 
                    # 石のある軸への Shift 演算は Shift なので、軸ロックがかかる
                    new_lock = True

                self._axis_locks[move.axis.to_code()] = new_lock
                self._board_editing_history.append(BoardEditingItem(
                    move=move,
                    stones_before_change=stones_before_change))
                self.update_legal_moves()
                return


            # 対象の軸に石が置いてない ---> イリーガルムーブ
            else:
                print("Illegal move")
                return


        # ノット（単項演算子）
        if op == 'n':

            # 対象の軸に石が置いてある ---> イリーガルムーブ
            if self.exists_stone_on_axis(move.axis):
                print("illegal move: Low, High のどちらかを指定する必要があります")
                return

            # 対象の軸に石が置いてない ---> New 操作
            else:
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    axis_swap = False
                    opponent_axis_length = RANK_LEN
                
                # 段方向
                elif move.axis.axis_id == RANK_ID:
                    axis_swap = True
                    opponent_axis_length = FILE_LEN
                
                else:
                    raise ValueError(f"undefined axis_id  {move.axis.axis_id=}")

                # 筋（段）方向両用
                dst_j = move.axis.number
                if dst_j == 0:
                    src_j = dst_j + 1
                elif dst_j == FILE_LEN - 1:
                    src_j = dst_j - 1
                # 左か右（上か下）で、石が置いてある軸が入力軸
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j - 1)):
                    src_j = dst_j - 1
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j + 1)):
                    src_j = dst_j + 1
                else:
                    raise ValueError("not operator invalid operation")

                # 入力軸から、出力軸へ、評価値を出力
                for i in range(0, opponent_axis_length):
                    stone = self._squares[Square.file_rank_to_sq(src_j, i, swap=axis_swap)]
                    self._squares[Square.file_rank_to_sq(dst_j, i, swap=axis_swap)] = move.operator.unary_operate(stone)


                if move.operator.force_unlock:
                    new_lock = False
                else: 
                    # 対局中に New 操作しても軸ロックはかからない
                    new_lock = False

                self._axis_locks[move.axis.to_code()] = new_lock
                self._board_editing_history.append(BoardEditingItem(
                    move=move))
                self.update_legal_moves()
                return


        # ノット（単項演算子 Reverse）軸上の小さい方
        if op == 'nL':

            # 対象の軸に石が置いてある --> Reverse 操作
            if self.exists_stone_on_axis(move.axis):
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    axis_swap = False
                    opponent_axis_length = RANK_LEN
                
                # 段方向
                elif move.axis.axis_id == RANK_ID:
                    axis_swap = True
                    opponent_axis_length = FILE_LEN

                # 筋（段）方向両用
                dst_j = move.axis.number
                if dst_j == 0:
                    src_j = dst_j + 1
                elif dst_j == FILE_LEN - 1:
                    src_j = dst_j - 1
                # 左か右（上か下）で、石が置いてある軸が入力軸
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j - 1)):
                    src_j = dst_j - 1
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j + 1)):
                    src_j = dst_j + 1
                else:
                    raise ValueError("not operator invalid operation")

                # 入力軸から、出力軸へ、評価値を出力
                for i in range(0, opponent_axis_length):
                    stone = self._squares[Square.file_rank_to_sq(src_j, i, swap=axis_swap)]

                    if stone != PC_EMPTY:
                        stones_before_change += _pc_to_str[stone]
                        self._squares[Square.file_rank_to_sq(dst_j, i, swap=axis_swap)] = move.operator.unary_operate(stone)


                if move.operator.force_unlock:
                    new_lock = False
                else: 
                    # 石のある軸への Not 演算は Reverse なので、軸ロックがかかる
                    new_lock = True

                self._axis_locks[move.axis.to_code()] = new_lock
                self._board_editing_history.append(BoardEditingItem(
                    move=move,
                    stones_before_change=stones_before_change))
                self.update_legal_moves()
                return


            # 対象の軸に石が置いてない ---> New 操作
            else:
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    axis_swap = False
                    opponent_axis_length = RANK_LEN
                
                # 段方向
                elif move.axis.axis_id == RANK_ID:
                    axis_swap = True
                    opponent_axis_length = FILE_LEN

                # 筋（段）方向両用
                dst_j = move.axis.number
                if dst_j == 0:
                    src_j = dst_j + 1
                elif dst_j == FILE_LEN - 1:
                    src_j = dst_j - 1
                # 左か右（上か下）で、石が置いてある軸が入力軸
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j - 1)):
                    src_j = dst_j - 1
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j + 1)):
                    src_j = dst_j + 1
                else:
                    raise ValueError("not operator invalid operation")

                # 入力軸から、出力軸へ、評価値を出力
                for i in range(0, opponent_axis_length):
                    stone = self._squares[Square.file_rank_to_sq(src_j, i, swap=axis_swap)]
                    self._squares[Square.file_rank_to_sq(dst_j, i, swap=axis_swap)] = move.operator.unary_operate(stone)


                if move.operator.force_unlock:
                    new_lock = False
                else: 
                    # 石のある軸への Not 演算は Reverse なので、軸ロックがかかる
                    new_lock = True

                self._axis_locks[move.axis.to_code()] = new_lock
                self._board_editing_history.append(BoardEditingItem(
                    move=move))
                self.update_legal_moves()
                return


        # ノット（単項演算子 Reverse）軸上の大きい方
        if op == 'nH':

            # 対象の軸に石が置いてある --> Reverse 操作
            if self.exists_stone_on_axis(move.axis):
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    axis_swap = False
                    opponent_axis_length = RANK_LEN
                
                # 段方向
                elif move.axis.axis_id == RANK_ID:
                    axis_swap = True
                    opponent_axis_length = FILE_LEN

                # 筋（段）方向両用
                dst_j = move.axis.number
                if dst_j == 0:
                    src_j = dst_j + 1
                elif dst_j == FILE_LEN - 1:
                    src_j = dst_j - 1
                # 左か右（上か下）で、石が置いてある軸が入力軸
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j - 1)):
                    src_j = dst_j - 1
                elif self.exists_stone_on_axis(Axis(move.axis.axis_id, dst_j + 1)):
                    src_j = dst_j + 1
                else:
                    raise ValueError("not operator invalid operation")

                # 入力軸から、出力軸へ、評価値を出力
                for i in range(0, opponent_axis_length):
                    stone = self._squares[Square.file_rank_to_sq(src_j, i, swap=axis_swap)]

                    if stone != PC_EMPTY:
                        stones_before_change += _pc_to_str[stone]
                        self._squares[Square.file_rank_to_sq(dst_j, i, swap=axis_swap)] = move.operator.unary_operate(stone)


                if move.operator.force_unlock:
                    new_lock = False
                else: 
                    # 石のある軸への Not 演算は Reverse なので、軸ロックがかかる
                    new_lock = True

                self._axis_locks[move.axis.to_code()] = new_lock
                self._board_editing_history.append(BoardEditingItem(
                    move=move,
                    stones_before_change=stones_before_change))
                self.update_legal_moves()
                return


            # 対象の軸に石が置いてない ---> New 操作
            else:

                self.copy_stones_on_line_unary(
                    axis_id=move.axis.axis_id)

                if move.operator.force_unlock:
                    new_lock = False
                else: 
                    # 石のある軸への Not 演算は Reverse なので、軸ロックがかかる
                    new_lock = True

                self._axis_locks[move.axis.to_code()] = new_lock
                self._board_editing_history.append(BoardEditingItem(
                    move=move))
                self.update_legal_moves()
                return


        # アンド, オア, ゼロ, ノア, エクソア, ナンド, エクスノア, ワン
        if op in ['a', 'o', 'ze', 'no', 'xo', 'na', 'xn', 'on']:
            self.copy_stones_on_line_binary(move)


            if move.operator.force_unlock:
                new_lock = False
            else: 
                # 石のある軸への And 演算は Reverse なので、軸ロックがかかる
                new_lock = True

            self._axis_locks[move.axis.to_code()] = new_lock
            self._board_editing_history.append(BoardEditingItem(
                move=move))
            self.update_legal_moves()
            return


        raise ValueError(f"undefined operator code: {op}")


    def get_edge_axis_from_adjacent_space(self, space_axis):
        """石のない軸の隣の石のある軸を返す

        Parameters
        ----------
        space_axis : Axis
            石のない軸。ただし、その隣には石があるものとする
        """

        # 筋方向
        if space_axis.axis_id == FILE_ID:
            left_axis = space_axis.low_axis()
            if left_axis is not None:
                (begin, length) = self.get_position_on_axis(left_axis)
                if 0 < length:
                    return left_axis

            right_axis = space_axis.high_axis()
            if right_axis is not None:
                (begin, length) = self.get_position_on_axis(right_axis)
                if 0 < length:
                    return right_axis

        # 段方向
        if space_axis.axis_id == RANK_ID:
            top_axis = space_axis.low_axis()
            if top_axis is not None:
                (begin, length) = self.get_position_on_axis(top_axis)
                if 0 < length:
                    return top_axis

            bottom_axis = space_axis.high_axis()
            if bottom_axis is not None:
                (begin, length) = self.get_position_on_axis(bottom_axis)
                if 0 < length:
                    return bottom_axis

        None


    def pop(self):
        """一手戻す"""
        # 逆操作を算出
        latest_edit = self._board_editing_history[-1]
        inverse_move = MoveHelper.let_inverse_move(
            move=latest_edit.move,
            stones_before_change=latest_edit.stones_before_change)

        if inverse_move is None:
            print(f"[pop] `{latest_edit.move.to_code()}` に逆操作はありません")
            return

        # 盤面編集として、逆操作を実行
        self.push_usi(f"&{inverse_move.to_code()}")

        # 逆操作を履歴から除去
        self._board_editing_history.pop()

        self.update_legal_moves()


    def is_gameover(self):
        """終局しているか？"""
        return self._gameover_reason != ''


    def is_nyugyoku(self):
        """無視。ビナーシに入玉はありません"""
        pass

    def is_check(self):
        """TODO 一手詰めがあるか？"""
        pass

    def mate_move_in_1ply(self):
        """TODO 一手詰めの手を返す"""
        pass


    def get_edges(self):
        """辺を返す
        例えば：
        
            1 2 3 4 5 6 7
          +---------------+
        a | . . . . . . . |
        b | . . . . . . . |
        c | . . 0 1 0 1 . |
        d | . . 1 0 1 0 . |
        e | . . . . . . . |
        f | . . . . . . . |
          +---------------+
        
        上図の場合、 True, 3, 6, c, d の軸オブジェクトを返す

        Returns
        -------
        成功フラグ
        左辺
        右辺
        上辺
        下辺
        """

        left_file = None
        right_file = None
        top_rank = None
        bottom_rank = None

        # とりあえず各筋について
        for dst_file in range(0, FILE_LEN):
            dst_file_axis = Axis(FILE_ID, dst_file)

            # 縦連の場所を調べる
            (begin, length) = self.get_position_on_axis(dst_file_axis)

            # 石が置いてる段
            if 0 < length:
                top_rank = begin
                bottom_rank = begin + length - 1
                break

        
        if top_rank is None:
            return (False, None, None, None, None)


        # とりあえず各段について
        for dst_rank in range(0, RANK_LEN):
            dst_rank_axis = Axis(RANK_ID, dst_rank)

            # 横連の場所を調べる
            (begin, length) = self.get_position_on_axis(dst_rank_axis)

            # 石が置いてる筋
            if 0 < length:
                left_file = begin
                right_file = begin + length - 1
                break


        return (True, left_file, right_file, top_rank, bottom_rank)


    def get_input_axes_by_binary_operation(self, target_axis):
        """二項演算するときの入力軸２つ"""

        # 対象軸にロックが掛かっていたら、二項演算禁止
        if self._axis_locks[target_axis.to_code()]:
            return (None, None)


        # 筋方向
        if target_axis.axis_id == FILE_ID:
            opponent_axis_length = FILE_LEN

        # 段方向
        elif target_axis.axis_id == RANK_ID:
            opponent_axis_length = RANK_LEN

        else:
            raise ValueError(f"undefined axis: {target_axis.axis_id=}")


        # 対称軸に石が置いてあるなら
        if self.exists_stone_on_axis(target_axis):
            # ロウ、ハイの両方に石が置いてある必要がある
            if 0 < target_axis.number and target_axis.number < opponent_axis_length - 1:
                low_axis = target_axis.low_axis()
                high_axis = target_axis.high_axis()
                if self.exists_stone_on_axis(low_axis) and self.exists_stone_on_axis(high_axis):
                    return (low_axis, high_axis)

        # 対象軸に石が置いてないなら
        else:
            # ロウの方に２つ続けて石が置いているか？
            if 1 < target_axis.number:
                first_axis = target_axis.low_axis()
                second_axis = target_axis.low_axis(diff=2)
                if self.exists_stone_on_axis(first_axis) and self.exists_stone_on_axis(second_axis):
                    return (first_axis, second_axis)
            
            # ハイの方に２つ続けて石が置いているか？
            if target_axis.number < opponent_axis_length - 2:
                first_axis = target_axis.high_axis()
                second_axis = target_axis.high_axis(diff=2)
                if self.exists_stone_on_axis(first_axis) and self.exists_stone_on_axis(second_axis):
                    return (first_axis, second_axis)


    def make_legal_moves(self, operator_u):
        """
        Parameters
        ----------
        operator_u : str
            演算子コード
            例： 'o'
        """
        opponent_axis_length_list = [FILE_LEN, RANK_LEN]
        axis_id_list = [FILE_ID, RANK_ID]   # 筋、段
        # 筋（段）両用
        for j in range(0, 1):
            opponent_axis_length = opponent_axis_length_list[j]

            for i in range(0, opponent_axis_length):
                dst_i_axis = Axis(axis_id_list[j], i)

                # 石が置いてある軸
                if self.exists_stone_on_axis(dst_i_axis):

                    # 軸にロックが掛かっていたら Or の Reverse は禁止
                    if self._axis_locks[dst_i_axis.to_code()]:
                        continue

                    # ロウ、ハイの両方に石が置いてある必要がある
                    if 0 < i and i < opponent_axis_length - 1 and self.exists_stone_on_axis(dst_i_axis.low_axis()) and self.exists_stone_on_axis(dst_i_axis.high_axis()):
                        # 対象軸上にある石を Or して Reverse できる
                        self._legal_moves.append(Move(dst_i_axis, Operator.code_to_obj(operator_u)))

                # 石が置いてない軸
                else:
                    # 隣のどちらかに２つ続けて石が置いているか？
                    if ((1 < i and self.exists_stone_on_axis(dst_i_axis.low_axis()) and self.exists_stone_on_axis(dst_i_axis.low_axis(diff=2))) or
                        (i < opponent_axis_length - 2 and self.exists_stone_on_axis(dst_i_axis.high_axis()) and self.exists_stone_on_axis(dst_i_axis.high_axis(diff=2)))):
                        # Or で New できる
                        self._legal_moves.append(Move(dst_i_axis, Operator.code_to_obj(operator_u)))


    def update_legal_moves(self):
        """合法手の一覧生成"""

        self._legal_moves = []
        self._moves_for_edit = []

        (rect_exists, left_file, right_file, top_rank, bottom_rank) = self.get_edges()


        # カットザエッジ（Cut the edge）の合法手生成（盤面編集用）
        if rect_exists:
            if 0 < right_file - left_file:
                self._moves_for_edit.append(Move(Axis(FILE_ID, left_file), Operator.code_to_obj('c')))
                self._moves_for_edit.append(Move(Axis(FILE_ID, right_file), Operator.code_to_obj('c')))
            
            if 0 < bottom_rank - top_rank:
                self._moves_for_edit.append(Move(Axis(RANK_ID, top_rank), Operator.code_to_obj('c')))
                self._moves_for_edit.append(Move(Axis(RANK_ID, bottom_rank), Operator.code_to_obj('c')))


        # シフト（Shift）の合法手生成
        # 筋方向
        for dst_file in range(0, FILE_LEN):
            dst_file_axis = Axis(FILE_ID, dst_file)

            # 軸にロックが掛かっていたら Shift は禁止
            if self._axis_locks[dst_file_axis.to_code()]:
                continue

            (begin, length) = self.get_position_on_axis(dst_file_axis)

            # 石が置いてる軸
            if 0 < length:
                # Shift できる

                # 例えば：
                # 
                #     1 2 3 4 5 6 7
                #   +---------------+
                # a | . . . . . . . |
                # b | . . . . . . . |
                # c | . . 0 1 0 1 . |
                # d | . . . . . . . |
                # e | . . . . . . . |
                # f | . . . . . . . |
                #   +---------------+
                # 
                # 上記 c段の石の長さは４目なので、シフトは s1, s2, s3 だけを合法手とするよう制限する。
                # ゼロビットシフトは禁止する
                # 枝が増えてしまうのを防ぐ

                for i in range(1, length):
                    self._legal_moves.append(Move(dst_file_axis, Operator.code_to_obj(f's{i}')))


        # 段方向
        for dst_rank in range(0, RANK_LEN):
            dst_rank_axis = Axis(RANK_ID, dst_rank)

            # 軸にロックが掛かっていたら Shift は禁止
            if self._axis_locks[dst_rank_axis.to_code()]:
                continue

            (begin, length) = self.get_position_on_axis(dst_rank_axis)

            # 石が置いてる軸
            if 0 < length:
                # Shift できる
                # ゼロビットシフトは禁止する
                for i in range(1, length):
                    self._legal_moves.append(Move(dst_rank_axis, Operator.code_to_obj(f's{i}')))


        # ノット（Not）の合法手生成
        # 筋方向
        for dst_file in range(0, FILE_LEN):
            dst_file_axis = Axis(FILE_ID, dst_file)

            # 石が置いてある軸
            if self.exists_stone_on_axis(dst_file_axis):

                # 軸にロックが掛かっていたら Not の Reverse は禁止
                if self._axis_locks[dst_file_axis.to_code()]:
                    continue

                if 0 < dst_file and self.exists_stone_on_axis(dst_file_axis.low_axis()):
                    # 軸上で小さい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_file_axis, Operator.code_to_obj('nL')))

                if dst_file < FILE_LEN - 1 and self.exists_stone_on_axis(dst_file_axis.high_axis()):
                    # 軸上で大きい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_file_axis, Operator.code_to_obj('nH')))

            # 石が置いてない軸
            else:
                # 隣のどちらかに石が置いているか？
                if 0 < dst_file and self.exists_stone_on_axis(dst_file_axis.low_axis()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_file_axis, Operator.code_to_obj('n')))

                if dst_file < FILE_LEN - 1 and self.exists_stone_on_axis(dst_file_axis.high_axis()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_file_axis, Operator.code_to_obj('n')))


        # 段方向
        for dst_rank in range(0, RANK_LEN):
            dst_rank_axis = Axis(RANK_ID, dst_rank)

            # 石が置いてある軸
            if self.exists_stone_on_axis(dst_rank_axis):

                # 軸にロックが掛かっていたら Not の Reverse は禁止
                if self._axis_locks[dst_rank_axis.to_code()]:
                    continue

                if 0 < dst_rank and self.exists_stone_on_axis(dst_rank_axis.low_axis()):
                    # 軸上で小さい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_rank_axis, Operator.code_to_obj('nL')))

                if dst_rank < RANK_LEN - 1 and self.exists_stone_on_axis(dst_rank_axis.high_axis()):
                    # 軸上で大きい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_rank_axis, Operator.code_to_obj('nH')))

            # 石が置いてない軸
            else:
                # 隣のどちらかに石が置いているか？
                if 0 < dst_rank and self.exists_stone_on_axis(dst_rank_axis.low_axis()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_rank_axis, Operator.code_to_obj('n')))

                if dst_rank < RANK_LEN - 1 and self.exists_stone_on_axis(dst_rank_axis.high_axis()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_rank_axis, Operator.code_to_obj('n')))


        # アンド（AND）の合法手生成
        self.make_legal_moves(operator_u='a')

        # オア（OR）の合法手生成
        self.make_legal_moves(operator_u='o')

        # ゼロ（ZERO）の合法手生成
        self.make_legal_moves(operator_u='ze')

        # ノア（NOR）の合法手生成
        self.make_legal_moves(operator_u='no')

        # エクソア（XOR）の合法手生成
        self.make_legal_moves(operator_u='xo')

        # ナンド（NAND）の合法手生成
        self.make_legal_moves(operator_u='na')

        # エクスノア（XNOR）の合法手生成
        self.make_legal_moves(operator_u='xn')

        # ワン（ONE）の合法手生成
        self.make_legal_moves(operator_u='on')

        # 終局判定を更新
        self.update_gameover()


    def update_gameover(self):
        """終局判定を更新"""

        # ステールメートしている
        if len(self._legal_moves) < 1:
            self._gameover_reason = 'stalemate'
            return

        # TODO クリアー条件はアンドゥしたあと消すよう注意

        # クリアー条件　黒番１　横に３つ 1 が並んでいること
        #   +-------+
        #   |       |
        #   | 1 1 1 |
        #   |       |
        #   +-------+
        def update_cleared_target_1():
            for rank in range(0, RANK_LEN - 2):
                for file in range(0, FILE_LEN - 2):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 1, rank)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 2, rank)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    self._cleared_targets[0] = len(self._board_editing_history.game_items)
                    return

        if self._cleared_targets[0] == -1:
            update_cleared_target_1()


        # クリアー条件　黒番２　斜め（左右反転でも構わない）に４つ 1 が並んでいること
        #   Sinister Diagonal   Baroque Diagonal
        #   +---------+         +---------+
        #   | 1       |         |       1 |
        #   |   1     |         |     1   |
        #   |     1   |         |   1     |
        #   |       1 |         | 1       |
        #   +---------+         +---------+
        def update_cleared_target_2():
            # Sinister Diagonal
            for rank in range(0, RANK_LEN - 3):
                for file in range(0, FILE_LEN - 3):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 1, rank + 1)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 2, rank + 2)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 3, rank + 3)
                    if self._squares[sq] == PC_BLACK:
                        continue

                    self._cleared_targets[1] = len(self._board_editing_history.game_items)
                    return

            # Baroque Diagonal
            for rank in reversed(range(3, RANK_LEN)):
                for file in range(0, FILE_LEN - 3):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 1, rank - 1)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 2, rank - 2)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file + 3, rank - 3)
                    if self._squares[sq] == PC_BLACK:
                        continue

                    self._cleared_targets[1] = len(self._board_editing_history.game_items)
                    return

        if self._cleared_targets[1] == -1:
            update_cleared_target_2()


        # クリアー条件　黒番３　縦に５つ 1 が並んでいること
        #   +-----------+
        #   |     1     |
        #   |     1     |
        #   |     1     |
        #   |     1     |
        #   |     1     |
        #   +-----------+
        def update_cleared_target_3():
            for file in range(0, FILE_LEN - 4):
                for rank in range(0, RANK_LEN - 4):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file, rank + 1)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file, rank + 2)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file, rank + 3)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    sq = Square.file_rank_to_sq(file, rank + 4)
                    if self._squares[sq] != PC_BLACK:
                        continue

                    self._cleared_targets[2] = len(self._board_editing_history.game_items)
                    return

        if self._cleared_targets[2] == -1:
            update_cleared_target_3()



        # クリアー条件　白番１　縦に３つ 0 が並んでいること
        #   +-------+
        #   |   0   |
        #   |   0   |
        #   |   0   |
        #   +-------+
        def update_cleared_target_4():
            for file in range(0, FILE_LEN - 2):
                for rank in range(0, RANK_LEN - 2):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file, rank + 1)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file, rank + 2)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    self._cleared_targets[3] = len(self._board_editing_history.game_items)
                    return

        if self._cleared_targets[3] == -1:
            update_cleared_target_4()


        # クリアー条件　白番２　斜め（左右反転でも構わない）に４つ 0 が並んでいること
        #   Sinister Diagonal   Baroque Diagonal
        #   +---------+         +---------+
        #   | 0       |         |       0 |
        #   |   0     |         |     0   |
        #   |     0   |         |   0     |
        #   |       0 |         | 0       |
        #   +---------+         +---------+
        def update_cleared_target_5():
            # Sinister Diagonal
            for rank in range(0, RANK_LEN - 3):
                for file in range(0, FILE_LEN - 3):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 1, rank + 1)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 2, rank + 2)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 3, rank + 3)
                    if self._squares[sq] == PC_WHITE:
                        continue

                    self._cleared_targets[4] = len(self._board_editing_history.game_items)
                    return

            # Baroque Diagonal
            for rank in reversed(range(3, RANK_LEN)):
                for file in range(0, FILE_LEN - 3):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 1, rank - 1)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 2, rank - 2)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 3, rank - 3)
                    if self._squares[sq] == PC_WHITE:
                        continue

                    self._cleared_targets[4] = len(self._board_editing_history.game_items)
                    return

        if self._cleared_targets[4] == -1:
            update_cleared_target_5()


        # クリアー条件　白番３　横に５つ 0 が並んでいること
        #   +-----------+
        #   |           |
        #   |           |
        #   | 0 0 0 0 0 |
        #   |           |
        #   |           |
        #   +-----------+
        def update_cleared_target_6():
            for rank in range(0, RANK_LEN - 4):
                for file in range(0, FILE_LEN - 4):

                    sq = Square.file_rank_to_sq(file, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 1, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 2, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 3, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    sq = Square.file_rank_to_sq(file + 4, rank)
                    if self._squares[sq] != PC_WHITE:
                        continue

                    self._cleared_targets[5] = len(self._board_editing_history.game_items)
                    return

        if self._cleared_targets[5] == -1:
            update_cleared_target_6()


        # どちらかのプレイヤーが３つのターゲットを完了した
        is_black_win = False
        is_white_win = False
        if self._cleared_targets[0] != -1 and self._cleared_targets[1] != -1 and self._cleared_targets[2] != -1:
            is_black_win = True

        if self._cleared_targets[3] != -1 and self._cleared_targets[4] != -1 and self._cleared_targets[5] != -1:
            is_white_win = True

        if is_black_win and is_white_win:
            # TODO 同着になる手は禁じ手
            self._gameover_reason = 'draw (illegal move)'
            return

        if is_black_win:
            self._gameover_reason = 'black win'
            return

        if is_white_win:
            self._gameover_reason = 'white win'
            return


        # TODO 投了している

        # 終局していない
        self._gameover_reason = ''


    def as_str(self):
        """（拡張仕様）盤のテキスト形式
        例：
            [ 2 moves | moved 3s1]
                1 2 # 4 5 6 7
              +---------------+
            a |               |
            b |               |
            c |     1         |
            d |     0         |
            e |               |
            f |               |
              +---------------+
        """
        global _pc_to_str

        # １行目表示
        # ---------

        moves_num = len(self._board_editing_history.game_items)

        edits_num = len(self._board_editing_history.items)
        if moves_num != edits_num:
            edits_num_str = f"| {edits_num} edits "
        else:
            edits_num_str = ""

        if 0 < edits_num:
            latest_move = self._board_editing_history.items[-1].move
            if latest_move.when_edit:
                latest_move_str = f"edited {latest_move.to_code()}"
            else:
                latest_move_str = f"moved {latest_move.to_code()}"
        else:
            latest_move_str = 'init'


        # クリアーターゲット状況
        cleared_targets_list = []
        if self._cleared_targets[0] != -1:
            cleared_targets_list.append('b3')
        if self._cleared_targets[1] != -1:
            cleared_targets_list.append('b4')
        if self._cleared_targets[2] != -1:
            cleared_targets_list.append('b5')
        if self._cleared_targets[3] != -1:
            cleared_targets_list.append('w3')
        if self._cleared_targets[4] != -1:
            cleared_targets_list.append('w4')
        if self._cleared_targets[5] != -1:
            cleared_targets_list.append('w5')

        if 0 < len(cleared_targets_list):
            cleared_targets_str = f" | {' '.join(cleared_targets_list)}"
        else:
            cleared_targets_str = ''


        # 次の手番、または、終局理由
        if self.is_gameover():
            next_turn_str = self.gameover_reason
        else:
            next_turn = self.get_next_turn(from_present=True)
            if next_turn == PC_BLACK:
                next_turn_str = 'next black'
            else:
                next_turn_str = 'next white'


        print(f"[{moves_num:2} moves {edits_num_str}| {latest_move_str}{cleared_targets_str} | {next_turn_str}]")


        # 盤表示
        # ------

        # 数値を文字列(Str)に変更
        s = [' '] * BOARD_AREA
        for sq in range(0, BOARD_AREA):
            s[sq] = _pc_to_str[self._squares[sq]]

        # 筋（段）の符号、またはロック
        def get_axis_code_2(axis_code):
            if self._axis_locks[axis_code]:
                return '#'

            return axis_code

        # Axis
        a = {
            '1' : get_axis_code_2('1'),
            '2' : get_axis_code_2('2'),
            '3' : get_axis_code_2('3'),
            '4' : get_axis_code_2('4'),
            '5' : get_axis_code_2('5'),
            '6' : get_axis_code_2('6'),
            '7' : get_axis_code_2('7'),
            'a' : get_axis_code_2('a'),
            'b' : get_axis_code_2('b'),
            'c' : get_axis_code_2('c'),
            'd' : get_axis_code_2('d'),
            'e' : get_axis_code_2('e'),
            'f' : get_axis_code_2('f'),
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


    def get_next_turn(self, from_present=False):
        """手番を取得

        現在の盤面から。対局棋譜の指し手番号が奇数なら黒番、偶数なら後手番（将棋と違って上手、下手が無いから）
        ただし、添付局面が先手だった場合

        Parameters
        ----------
        from_present : bool
            現局面からのSFENにしたいなら真。初期局面からのSFENにしたいなら偽
        """

        if from_present:
            # 添付局面が先手番のケース
            if self._turn_at_init == PC_BLACK:
                if len(self._board_editing_history.game_items) % 2 == 0:
                    return PC_BLACK
                
                return PC_WHITE

            # 添付局面が後手番のケース
            if len(self._board_editing_history.game_items) % 2 == 0:
                return PC_WHITE

            return PC_BLACK

        # 初期盤面から
        if self._turn_at_init == PC_BLACK:
            return PC_BLACK
        
        return PC_WHITE


    def as_sfen(self, from_present=False):
        """（拡張仕様）盤のSFEN形式

        空欄： 数に置き換え
        黒石： x
        白石： o

        Parameters
        ----------
        from_present : bool
            現局面からのSFENにしたいなら真。初期局面からのSFENにしたいなら偽
        """
        global _pc_to_str
        global _axis_characters

        buffer = []
        spaces = 0

        # 局面図
        # ------

        # 現在の盤面からのSFEN表示
        if from_present:
            target_squares = self._squares 
            if target_squares is None:
                raise ValueError("self._squares is None")

        # 初期盤面からのSFEN表示
        else:
            target_squares = self._squares_at_init

            # usinewgame コマンドの直後に selfmatch をするとこの例外になる
            if target_squares is None:
                raise ValueError("self._squares_at_init is None")


        for rank in range(0, RANK_LEN):
            for file in range(0, FILE_LEN):
                sq = Square.file_rank_to_sq(file, rank)
                stone = target_squares[sq]

                if stone == PC_EMPTY:
                    spaces += 1
                else:
                    # 空白の数を Flush
                    if 0 < spaces:
                        buffer.append(str(spaces))
                        spaces = 0
                    
                    if stone == PC_BLACK:
                        buffer.append('x')
                    elif stone == PC_WHITE:
                        buffer.append('o')
                    else:
                        raise ValueError(f"undefined stone:'{stone}'")

            # 空白の数を Flush
            if 0 < spaces:
                buffer.append(str(spaces))
                spaces = 0

            if rank != RANK_LEN - 1:
                buffer.append('/')


        # 添付局面図の手番
        # ---------------
        next_turn = self.get_next_turn()
        if next_turn == PC_BLACK:
            buffer.append(' b ')
        elif next_turn == PC_WHITE:
            buffer.append(' w ')
        else:
            raise ValueError(f"undefined next turn  {next_turn=}")
        

        # 添付局面図の筋（段）の符号、またはロック
        # -------------------------------------
        locked = False

        # 現在の盤面から
        if from_present:
            for axis_code in _axis_characters:
                if self._axis_locks[axis_code]:
                    buffer.append(axis_code)
                    locked = True

        # 初期盤面から
        else:
            for axis_code in _axis_characters:
                if self._axis_locks_at_init[axis_code]:
                    buffer.append(axis_code)
                    locked = True

        if not locked:
            buffer.append('-')


        # 添付局面図は何手目のものか
        # ------------------------

        # 現在の盤面からのSFEN表示
        if from_present:
            buffer.append(f' {len(self._board_editing_history.game_items)}')

        # 初期盤面からのSFEN表示
        else:
            buffer.append(' 1')


        # 添付局面図からの指し手
        # ---------------------

        # 現在の盤面からのSFEN表示
        if from_present:
            pass

        # 初期盤面からのSFEN表示
        else:

            move_u_list = []

            # 対局棋譜
            for game_record_item in self._board_editing_history.game_items:
                move_u_list.append(game_record_item.move.to_code())

            if 0 < len(move_u_list):
                moves_u = ' '.join(move_u_list).rstrip()
                buffer.append(f' moves {moves_u}')


        sfen_str = ''.join(buffer)


        # 平手初期局面なら startpos に置換
        result = re.match(r"^7/7/2o4/7/7/7 b - 1(.*)$", sfen_str)
        if result:
            sfen_str = f"startpos{result.group(1)}"


        return sfen_str


    def as_stones_before_change(self, from_present=False):
        """棋譜を再生して初めて分かる情報の表示

        Parameters
        ----------
        from_present : bool
            現局面からのSFENにしたいなら真。初期局面からのSFENにしたいなら偽
        """

        list1 = []

        # 現在の盤面からのSFEN表示
        if from_present:
            pass

        # 初期盤面からのSFEN表示
        else:
            for board_editing_item in self._board_editing_history.game_items:
                if len(board_editing_item.stones_before_change) < 1:
                    list1.append('-')
                else:
                    list1.append(board_editing_item.stones_before_change)

        if 0 < len(list1):
            return ' '.join(list1)
        else:
            return ''
