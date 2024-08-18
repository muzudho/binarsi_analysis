import re

# 石（PieCe）番号
PC_EMPTY = 0
PC_BLACK = 1
PC_WHITE = 2

_pc_to_str = {
    0 : ' ',
    1 : '1',
    2 : '0',
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
    def file_rank_to_sq(file, rank):
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
    def code_to_axis_obj(clazz, code):
        """生成

        Parameters
        ----------
        code : str
            "1" ～ "7"、 "a" ～ "f"
        """

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


class Operator():
    """演算子

    例： `4n` - 4筋に Not 演算を用いて New するケース

    演算子：
        c : Clear 対象軸上の全石を削除
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
    """

    def __init__(self, stem_u):
        self._stem_u = stem_u


    @property
    def code(self):
        return self._stem_u


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


    def binary_operate(self, left_stone, right_stone):
        """二項演算する
        
        Parameters
        ----------
        left_stone : int
            軸上の数字が小さい方の石の種類
        right_stone : int
            軸上の数字が大きい方の石の種類
        """

        # 変数名を縮める
        stem_u = self._stem_u

        # TODO ゼロ
        if stem_u == 'ze':
            return
        
        # TODO ノア
        if stem_u == 'no':
            return
        
        # TODO エクソア
        if stem_u == 'xo':
            return
        
        # TODO ナンド
        if stem_u == 'na':
            return
        
        # TODO アンド
        if stem_u == 'a':
            return
        
        # TODO エクスノア
        if stem_u == 'xn':
            return
        
        # TODO オア
        if stem_u == 'o':
            return
        
        # TODO ワン
        if stem_u == 'on':
            return

        raise ValueError(f"undefined operator  stem_u:{stem_u}  left_stone:{left_stone}  right_stone:{right_stone}")


class Move():
    """指し手

    例： "4n", "dn", "5o"

    出力軸（axis）、演算子（operator）
    """

    def __init__(self, axis, operator):
        """初期化
        
        Parameters
        ----------
        axis : Axis
            軸オブジェクト
        operator : str
            演算子
        """
        self._axis = axis
        self._operator = operator


    @property
    def axis(self):
        """軸オブジェクト"""
        return self._axis


    @property
    def operator(self):
        """演算子オブジェクト"""
        return self._operator


    @staticmethod
    def code_to_move_obj(move_u):

        # フォーマットチェック
        #
        #   文字数が短い方が先にマッチしてしまうかもしれないので、短い文字列は右に置くように並び順に注意
        #
        result = re.match(r"^[1234567abcdef](na|nH|nL|no|on|s0|s1|s2|s3|s4|s5|s6|xn|xo|ze|a|c|n|o)$", move_u)
        if result is None:
            raise ValueError(f"format error.  move_u:`{move_u}`")

        axis_u = move_u[0:1]
        
        if len(move_u) == 2:
            operator_u = move_u[1:2]
        else:
            operator_u = move_u[1:3]

        return Move(Axis.code_to_axis_obj(axis_u), Operator(operator_u))


    def to_code(self):
        return f"{self.axis.to_code()}{self.operator.code}"


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
        # 各マス
        self._squares = [PC_EMPTY] * BOARD_AREA
        # 現局面の合法手
        self._legal_moves = []
        # 軸ロック
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
        # 棋譜（Move のリスト）
        self._game_record = []


    @property
    def legal_moves(self):
        """合法手一覧"""
        return self._legal_moves

    @property
    def game_record(self):
        """棋譜"""
        return self._game_record


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
        """TODO 指定局面に変更

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

        # 盤面の解析
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

        # TODO 手番の解析
        if parts[1] == 'b':
            pass
        elif parts[1] == 'w':
            pass
        else:
            raise ValueError(f"undefined sfen character on turn:`{ch}`")

        # ロックの解析
        for axis_u in parts[2]:
            if axis_u in _axis_characters:
                self._axis_locks[axis_u] = True

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


    def push_usi(self, move_u):
        """一手指す

        Parameters
        ----------
        move_u : str
            例： "4n"
        """
        move = Move.code_to_move_obj(move_u)

        # 対象の軸に石が置いてある ---> Shift操作、または Reverse操作
        if self.exists_stone_on_axis(move.axis):
            # 演算子の変数名を縮める
            op = move.operator.code
            """
            演算子：
                c : Clear
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

            # TODO クリアー演算子
            if op.startswith('c'):
                # 筋を対象にした Clear
                if move.axis.axis_id == FILE_ID:
                    src_dst_file = move.axis.number

                    (begin, length) = self.get_position_on_axis(move.axis)

                    for src_dst_rank in range(begin, begin+length):
                        src_dst_sq = Square.file_rank_to_sq(src_dst_file, src_dst_rank)

                        # 空欄で上書き
                        self._squares[src_dst_sq] = PC_EMPTY

                # 段を対象にした Clear
                elif move.axis.axis_id == RANK_ID:
                    src_dst_rank = move.axis.number

                    (begin, length) = self.get_position_on_axis(move.axis)

                    for src_dst_file in range(begin, begin+length):
                        src_dst_sq = Square.file_rank_to_sq(src_dst_file, src_dst_rank)

                        # 空欄で上書き
                        self._squares[src_dst_sq] = PC_EMPTY
                
                else:
                    raise ValueError(f"undefined axis_id:{move.axis.axis_id}")


                # Clear を対局中に使うことは想定していない。盤面編集時に石を消すことを想定している。暫定的に Clear を使うと軸ロックも外れるものとする
                self._axis_locks[move.axis.to_code()] = False
                self.update_legal_moves()
                return


            # シフト（単項演算子 shift）
            #
            #   オペレーターの機能というより、ボードの機能
            #   このゲームでのシフトは、入力と出力は同じ筋（段）上で行います（inplace）
            #
            if op.startswith('s'):
                # 何ビットシフトか？
                bit_shift = int(op[1:2])

                # 筋を対象にした Shift
                if move.axis.axis_id == FILE_ID:
                    src_dst_file = move.axis.number

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

                    source_stones = [PC_EMPTY] * RANK_LEN
                    for rank in range(0, RANK_LEN):
                        src_sq = Square.file_rank_to_sq(src_dst_file, rank)
                        stone = self._squares[src_sq]
                        source_stones[rank] = stone

                    # (1)
                    (begin, length) = self.get_position_on_axis(move.axis)

                    # (2)
                    for src_rank in range(begin, begin+length):
                        dst_rank = (src_rank - begin + bit_shift) % length + begin
                        dst_sq = Square.file_rank_to_sq(src_dst_file, dst_rank)

                        # コピー
                        self._squares[dst_sq] = source_stones[src_rank]

                    # Shift 演算なので、軸にロックをかける
                    self._axis_locks[move.axis.to_code()] = True

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return

                # 石のある段を対象にした Shift
                if move.axis.axis_id == RANK_ID:
                    src_dst_rank = move.axis.number

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

                    source_stones = [PC_EMPTY] * FILE_LEN
                    for file in range(0, FILE_LEN):
                        src_sq = Square.file_rank_to_sq(file, src_dst_rank)
                        stone = self._squares[src_sq]
                        source_stones[file] = stone

                    # (1)
                    (begin, length) = self.get_position_on_axis(move.axis)

                    # (2)
                    for src_file in range(begin, begin+length):
                        dst_file = (src_file - begin + bit_shift) % length + begin
                        dst_sq = Square.file_rank_to_sq(dst_file, src_dst_rank)

                        # コピー
                        self._squares[dst_sq] = source_stones[src_file]

                    # 石のある軸への Shift 演算は Shift なので、軸にロックをかける
                    self._axis_locks[move.axis.to_code()] = True

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return

                raise ValueError(f"undefined axis_id:{move.axis.axis_id}")


            # TODO 軸上の小さい方の数から、対象の石のある数へ Not の評価を出力する
            if op == 'nL':
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    dst_file = move.axis.number

                    # 入力軸から、出力軸へ、評価値を出力
                    for rank in range(0, RANK_LEN):
                        src_sq = Square.file_rank_to_sq(dst_file - 1, rank)
                        dst_sq = Square.file_rank_to_sq(dst_file, rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                        # 石のある軸への Not 演算は Reverse なので、軸にロックをかける
                        self._axis_locks[move.axis.to_code()] = True

                        self._game_record.append(move)
                        self.update_legal_moves()
                        return

                # 段方向
                if move.axis.axis_id == RANK_ID:
                    dst_rank = move.axis.number

                    # 入力軸から、出力軸へ、評価値を出力
                    for file in range(0, FILE_LEN):
                        src_sq = Square.file_rank_to_sq(file, dst_rank - 1)
                        dst_sq = Square.file_rank_to_sq(file, dst_rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                        # 石のある軸への Not 演算は Reverse なので、軸にロックをかける
                        self._axis_locks[move.axis.to_code()] = True

                        self._game_record.append(move)
                        self.update_legal_moves()
                        return


            # TODO 軸上の大きい方の数から、対象の数へ Not の評価を出力する
            if op == 'nH':
                # 筋方向
                if move.axis.axis_id == FILE_ID:
                    dst_file = move.axis.number

                    # 入力軸から、出力軸へ、評価値を出力
                    for rank in range(0, RANK_LEN):
                        src_sq = Square.file_rank_to_sq(dst_file + 1, rank)
                        dst_sq = Square.file_rank_to_sq(dst_file, rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                        # 石のある軸への Not 演算は Reverse なので、軸にロックをかける
                        self._axis_locks[move.axis.to_code()] = True

                        self._game_record.append(move)
                        self.update_legal_moves()
                        return

                # 段方向
                if move.axis.axis_id == RANK_ID:
                    dst_rank = move.axis.number

                    # 入力軸から、出力軸へ、評価値を出力
                    for file in range(0, FILE_LEN):
                        src_sq = Square.file_rank_to_sq(file, dst_rank + 1)
                        dst_sq = Square.file_rank_to_sq(file, dst_rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                        # 石のある軸への Not 演算は Reverse なので、軸にロックをかける
                        self._axis_locks[move.axis.to_code()] = True

                        self._game_record.append(move)
                        self.update_legal_moves()
                        return


            raise ValueError(f"undefined operator code:{op}")

        # 対象の軸に石が置いてない ---> New操作
        else:
            # 演算子の変数名を縮める
            op = move.operator.code
            """
            演算子：
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

            if op.startswith('s'):
                # 石が無いところでシフトをするのは禁じ手
                raise ValueError(f"石が無いところでシフトをするのは禁じ手  op:{op}")


            # ノット（単項演算子 New）
            if op == 'n':
                # 入力筋
                if move.axis.axis_id == FILE_ID:
                    dst_file = move.axis.number
                    if dst_file == 0:
                        src_file = dst_file + 1
                    elif dst_file == FILE_LEN - 1:
                        src_file = dst_file - 1
                    # 左か右で、石が置いてある軸が入力軸
                    elif self.exists_stone_on_axis(Axis(FILE_ID, dst_file - 1)):
                        src_file = dst_file - 1
                    elif self.exists_stone_on_axis(Axis(FILE_ID, dst_file + 1)):
                        src_file = dst_file + 1
                    else:
                        raise ValueError("not operator invalid operation")

                    # 入力軸から、出力軸へ、評価値を出力
                    for rank in range(0, RANK_LEN):
                        src_sq = Square.file_rank_to_sq(src_file, rank)
                        dst_sq = Square.file_rank_to_sq(dst_file, rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                    # New にはロックがかからない

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return

                # 入力段
                if move.axis.axis_id == RANK_ID:
                    dst_rank = move.axis.number
                    if dst_rank == 0:
                        src_rank = dst_rank + 1
                    elif dst_rank == FILE_LEN - 1:
                        src_rank = dst_rank - 1
                    # 上か下で、石が置いてある軸が入力軸
                    elif self.exists_stone_on_axis(Axis(RANK_ID, dst_rank - 1)):
                        src_rank = dst_rank - 1
                    elif self.exists_stone_on_axis(Axis(RANK_ID, dst_rank + 1)):
                        src_rank = dst_rank + 1
                    else:
                        raise ValueError("not operator invalid operation")

                    # 入力軸から、出力軸へ、評価値を出力
                    for file in range(0, FILE_LEN):
                        src_sq = Square.file_rank_to_sq(file, src_rank)
                        dst_sq = Square.file_rank_to_sq(file, dst_rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                    # New にはロックはかからない

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return


            # ノット（単項演算子 Reverse）軸上の小さい方
            if op == 'nL':
                # 入力筋
                if move.axis.axis_id == FILE_ID:
                    dst_file = move.axis.number
                    src_file = dst_file - 1

                    # 入力軸から、出力軸へ、評価値を出力
                    for rank in range(0, RANK_LEN):
                        src_sq = Square.file_rank_to_sq(src_file, rank)
                        dst_sq = Square.file_rank_to_sq(dst_file, rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                    # 軸にロックをかける
                    self._axis_locks[move.axis.to_code()] = True

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return

                # 入力段
                if move.axis.axis_id == RANK_ID:
                    dst_rank = move.axis.number
                    src_rank = dst_rank - 1

                    # 入力軸から、出力軸へ、評価値を出力
                    for file in range(0, FILE_LEN):
                        src_sq = Square.file_rank_to_sq(file, src_rank)
                        dst_sq = Square.file_rank_to_sq(file, dst_rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                    # 軸にロックをかける
                    self._axis_locks[move.axis.to_code()] = True

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return


            # ノット（単項演算子 Reverse）軸上の大きい方
            if op == 'nH':
                # 入力筋
                if move.axis.axis_id == FILE_ID:
                    dst_file = move.axis.number
                    src_file = dst_file + 1

                    # 入力軸から、出力軸へ、評価値を出力
                    for rank in range(0, RANK_LEN):
                        src_sq = Square.file_rank_to_sq(src_file, rank)
                        dst_sq = Square.file_rank_to_sq(dst_file, rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                    # 軸にロックをかける
                    self._axis_locks[move.axis.to_code()] = True

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return

                # 入力段
                if move.axis.axis_id == RANK_ID:
                    dst_rank = move.axis.number
                    src_rank = dst_rank + 1

                    # 入力軸から、出力軸へ、評価値を出力
                    for file in range(0, FILE_LEN):
                        src_sq = Square.file_rank_to_sq(file, src_rank)
                        dst_sq = Square.file_rank_to_sq(file, dst_rank)

                        stone = self._squares[src_sq]
                        self._squares[dst_sq] = move.operator.unary_operate(stone)

                    # 軸にロックをかける
                    self._axis_locks[move.axis.to_code()] = True

                    self._game_record.append(move)
                    self.update_legal_moves()
                    return


            # TODO ゼロ
            if op == 'ze':
                return
            
            # TODO ノア
            if op == 'no':
                return
            
            # TODO エクソア
            if op == 'xo':
                return
            
            # TODO ナンド
            if op == 'na':
                return
            
            # TODO アンド
            if op == 'a':
                return
            
            # TODO エクスノア
            if op == 'xn':
                return
            
            # TODO オア
            if op == 'o':
                return
            
            # TODO ワン
            if op == 'on':
                return

            raise ValueError(f"undefined operator code: {op}")


    def pop(self, move_u):
        """一手戻す"""
        self._game_record.pop()
        self.update_legal_moves()


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


    def update_legal_moves(self):
        """TODO 合法手の一覧生成"""

        self._legal_moves = []


        # とりあえず Shift ができる出力筋を探す（Shift に Rev, New は無い）
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
                    self._legal_moves.append(Move(dst_file_axis, Operator(f's{i}')))


        # とりあえず Shift ができる出力段を探す（Shift に Rev, New は無い）
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
                    self._legal_moves.append(Move(dst_rank_axis, Operator(f's{i}')))


        # とりあえず Not ができる出力筋を探す
        for dst_file in range(0, FILE_LEN):
            dst_file_axis = Axis(FILE_ID, dst_file)

            # 石が置いてある軸
            if self.exists_stone_on_axis(dst_file_axis):

                # 軸にロックが掛かっていたら Not の Reverse は禁止
                if self._axis_locks[dst_file_axis.to_code()]:
                    continue

                if 0 < dst_file:
                    lower_src_file_axis = Axis(FILE_ID, dst_file - 1)
                    if self.exists_stone_on_axis(lower_src_file_axis):
                        # 軸上で小さい方にある石を Not して Reverse できる
                        self._legal_moves.append(Move(dst_file_axis, Operator('nL')))

                if dst_file < FILE_LEN - 1:
                    higher_src_file_axis = Axis(FILE_ID, dst_file + 1)
                    if self.exists_stone_on_axis(higher_src_file_axis):
                        # 軸上で大きい方にある石を Not して Reverse できる
                        self._legal_moves.append(Move(dst_file_axis, Operator('nH')))

            # 石が置いてない軸
            else:
                # 隣のどちらかに石が置いているか？
                if 0 < dst_file:
                    younger_src_file_axis = Axis(FILE_ID, dst_file - 1)
                    if self.exists_stone_on_axis(younger_src_file_axis):
                        # Not で New できる
                        self._legal_moves.append(Move(dst_file_axis, Operator('n')))

                if dst_file < FILE_LEN - 1:
                    elder_src_file_axis = Axis(FILE_ID, dst_file + 1)
                    if self.exists_stone_on_axis(elder_src_file_axis):
                        # Not で New できる
                        self._legal_moves.append(Move(dst_file_axis, Operator('n')))


        # とりあえず Not ができる出力段を探す
        for dst_rank in range(0, RANK_LEN):
            dst_rank_axis = Axis(RANK_ID, dst_rank)

            # 石が置いてある軸
            if self.exists_stone_on_axis(dst_rank_axis):

                # 軸にロックが掛かっていたら Not の Reverse は禁止
                if self._axis_locks[dst_rank_axis.to_code()]:
                    continue

                if 0 < dst_rank:
                    lower_src_rank_axis = Axis(RANK_ID, dst_rank - 1)
                    if self.exists_stone_on_axis(lower_src_rank_axis):
                        # 軸上で小さい方にある石を Not して Reverse できる
                        self._legal_moves.append(Move(dst_rank_axis, Operator('nL')))

                if dst_rank < RANK_LEN - 1:
                    higher_src_rank_axis = Axis(RANK_ID, dst_rank + 1)
                    if self.exists_stone_on_axis(higher_src_rank_axis):
                        # 軸上で大きい方にある石を Not して Reverse できる
                        self._legal_moves.append(Move(dst_rank_axis, Operator('nH')))

            # 石が置いてない軸
            else:
                # 隣のどちらかに石が置いているか？
                if 0 < dst_rank:
                    younger_src_rank_axis = Axis(RANK_ID, dst_rank - 1)
                    if self.exists_stone_on_axis(younger_src_rank_axis):
                        # Not で New できる
                        self._legal_moves.append(Move(dst_rank_axis, Operator('n')))

                if dst_rank < RANK_LEN - 1:
                    elder_src_rank_axis = Axis(RANK_ID, dst_rank + 1)
                    if self.exists_stone_on_axis(elder_src_rank_axis):
                        # Not で New できる
                        self._legal_moves.append(Move(dst_rank_axis, Operator('n')))

        # TODO とりあえず ZERO ができる出力筋を探す(Rev)(New)

        # TODO とりあえず ZERO ができる出力段を探す(Rev)(New)

        # TODO とりあえず NOR ができる出力筋を探す(Rev)(New)

        # TODO とりあえず NOR ができる出力段を探す(Rev)(New)

        # TODO とりあえず XOR ができる出力筋を探す(Rev)(New)

        # TODO とりあえず XOR ができる出力段を探す(Rev)(New)

        # TODO とりあえず NAND ができる出力筋を探す(Rev)(New)

        # TODO とりあえず NAND ができる出力段を探す(Rev)(New)

        # TODO とりあえず AND ができる出力筋を探す(Rev)(New)

        # TODO とりあえず AND ができる出力段を探す(Rev)(New)

        # TODO とりあえず XNOR ができる出力筋を探す(Rev)(New)

        # TODO とりあえず XNOR ができる出力段を探す(Rev)(New)

        # TODO とりあえず OR ができる出力筋を探す(Rev)(New)

        # TODO とりあえず OR ができる出力段を探す(Rev)(New)

        # TODO とりあえず ONE ができる出力筋を探す(Rev)(New)

        # TODO とりあえず ONE ができる出力段を探す(Rev)(New)


    def as_str(self):
        """（拡張仕様）盤のテキスト形式
        例：
            [  2 moves | moved 3s1]
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

        moves_num = len(self._game_record)

        if 0 < len(self._game_record):
            latest_move_str = f"moved {self._game_record[-1].to_code()}"
        else:
            latest_move_str = 'init'

        print(f"[{moves_num:3} moves | {latest_move_str}]")

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


    def as_sfen(self):
        """（拡張仕様）盤のSFEN形式

        空欄： 数に置き換え
        黒石： x
        白石： o
        """
        global _pc_to_str
        global _axis_characters

        buffer = []
        spaces = 0

        # 盤面
        for rank in range(0, RANK_LEN):
            for file in range(0, FILE_LEN):
                sq = Square.file_rank_to_sq(file, rank)
                stone = self._squares[sq]

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

        # TODO 手番
        buffer.append(' b ')

        # 筋（段）の符号、またはロック
        locked = False
        for axis_code in _axis_characters:
            if self._axis_locks[axis_code]:
                buffer.append(axis_code)
                locked = True

        if not locked:
            buffer.append('-')

        # TODO 何手目か
        buffer.append(' 0')

        return ''.join(buffer)
