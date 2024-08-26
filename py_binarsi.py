import re
import copy


# 石（PieCe）番号
#   コンピュータ将棋プログラミングの Piece という変数名を踏襲
PC_EMPTY = 0
PC_BLACK = 1
PC_WHITE = 2

# 盤面表示用文字列。SFENにも使用
_pc_to_str = {
    0 : '.',
    1 : '1',
    2 : '0',
}

_str_to_pc = {
    '.' : 0,
    '1' : 1,
    '0' : 2,
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

# 路の符号
_way_characters = ['1', '2', '3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'f']

# クリアーターゲットの数
CLEAR_TARGETS_LEN = 6


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


class AxesAbsorber():
    """筋と段のコードを共通化する仕掛け"""


    def __init__(self, swap_axes, opponent_axis_length):
        """初期化"""
        self._swap_axes = swap_axes
        self._opponent_axis_length = opponent_axis_length


    @property
    def swap_axes(self):
        """筋と段を入れ替える"""
        return self._swap_axes


    @property
    def opponent_axis_length(self):
        """反対の路の長さ"""
        return self._opponent_axis_length


class Way():
    """路符号

    例： '1',  '2', '3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'f'
    """

    _code_to_obj = None

    def __init__(self, axis_id, number):
        """初期化

        Parameters
        ----------
        axis_id : int
            軸Ｉｄ
            1: file
            2: rank
        """

        if axis_id not in (FILE_ID, RANK_ID):
            raise ValueError(f"undefined axis  {axis_id=}")

        self._axis_id = axis_id
        self._number = number


    @property
    def axis_id(self):
        return self._axis_id


    @property
    def number(self):
        return self._number


    @classmethod
    def code_to_obj(clazz, code):
        """生成

        Parameters
        ----------
        code : str
            "1" ～ "7"、 "a" ～ "f"
        """

        # フォーマットチェック
        result = re.match(r"^[1234567abcdef]$", code)
        if result is None:
            raise ValueError(f"format error.  way_u:`{code}`")


        if clazz._code_to_obj is None:
            clazz._code_to_obj = {
                '1': Way(FILE_ID, 0),
                '2': Way(FILE_ID, 1),
                '3': Way(FILE_ID, 2),
                '4': Way(FILE_ID, 3),
                '5': Way(FILE_ID, 4),
                '6': Way(FILE_ID, 5),
                '7': Way(FILE_ID, 6),
                'a': Way(RANK_ID, 0),
                'b': Way(RANK_ID, 1),
                'c': Way(RANK_ID, 2),
                'd': Way(RANK_ID, 3),
                'e': Way(RANK_ID, 4),
                'f': Way(RANK_ID, 5),
            }


        if code in clazz._code_to_obj:
            return clazz._code_to_obj[code]

        raise ValueError(f"not found way.  code:{code}")


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


    def low_way(self, diff = 1):
        """１つ小さい方の路"""
        if self._number < diff:
            return None
        
        return Way(self._axis_id, self._number - diff)


    def high_way(self, diff = 1):
        """１つ大きい方の路"""
        if self._axis_id == FILE_ID:
            if self._number < FILE_LEN - diff:
                return Way(self._axis_id, self._number + diff)
            else:
                return None

        elif self._axis_id == RANK_ID:
            if self._number < RANK_LEN - diff:
                return Way(self._axis_id, self._number + diff)
            else:
                return None

        raise ValueError(f"{self._axis_id=}")


    def absorb_axes(self):
        """筋と段のコードを共通化する仕掛け"""
        # 筋方向
        if self.axis_id == FILE_ID:
            return AxesAbsorber(
                swap_axes=False,
                opponent_axis_length=RANK_LEN)
        
        # 段方向
        if self.axis_id == RANK_ID:
            return AxesAbsorber(
                swap_axes=True,
                opponent_axis_length=FILE_LEN)
        
        raise ValueError(f"undefined axis_id  {self.axis_id=}")


class Operator():
    """演算子

    例： `4n` - 4筋に Not 演算を用いて New するケース

    主な演算子の語幹：
        c : Cut the edge 対象路上の全石を削除
        e : Edit
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
        s1
        s2
        s3
        s4
        s5
        s6
    筋の場合は上から下へ、段の場合は左から右へ、が順方向。
    ０ビットシフトは禁じ手とします

    NOT は単項演算子なので、Reverse するときは、 In が Low, High のどちらか指定する必要がある
        n
        nL
        nH

    現局面と変わらない、あるいは現局面を示す方法として内部的に使うかも
        pass
    """

    def __init__(self, stem_u, parameter_length):
        """初期化
        
        Parameters
        ----------
        stem_u : str
            演算子語幹部のUSI書式文字列（路ロック指定を除く）
        parameter_length: int
            引数の個数
        """
        self._stem_u = stem_u
        self._parameter_length = parameter_length


    @property
    def stem_u(self):
        return self._stem_u


    @property
    def parameter_length(self):
        return self._parameter_length


    @staticmethod
    def code_to_obj(code):
        """コードからオブジェクトへ変換
        
        Parameters
        ----------
        code : str
            コード（演算子語幹部、路ロック指定は含まない）
        """
        # フォーマットチェック
        #
        #   文字数が短い方が先にマッチしてしまうかもしれないので、短い文字列は右に置くように並び順に注意
        #
        result = re.match(r"^(na|nH|nL|no|on|s1|s2|s3|s4|s5|s6|xn|xo|ze|a|c|e|n|o)$", code)
        if result is None:
            raise ValueError(f"format error.  operator_u:`{code}`")

        stem_u = result.group(1)

        # 零項演算子（nullary）か？
        if stem_u in ['s1', 's2', 's3', 's4', 's5', 's6', 'c', 'e']:
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
            parameter_length=parameter_length)


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
        
        raise ValueError(f"undefined operator  {self._stem_u=}  {stone=}")


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
        "4c#$01" - 石の並びを、$記号の後ろに付加することができる

    盤面編集フラグ、出力路（way）、演算子（operator）、路ロック解除フラグ（way_unlock）、変更前の石の状態（stones_before_change）
    
    強制的にロックを外したい場合、末尾に `#` を付ける。これは盤面操作のためのもので、対局での使用は想定していない
        例： `7c#` - ７筋の全石を取り除き、ロックも外す
    """

    def __init__(self, way, operator, is_way_unlock=False, option_stones='', when_edit=False, same_move_u=''):
        """初期化
        
        Parameters
        ----------
        way : Way
            路オブジェクト
        operator : str
            演算子
        is_way_unlock : bool
            路ロック解除フラグ
        	True:  強制的に 路ロックを解除する
        	False: 強制的に 路ロックする
        option_stones : str
            石の並び。必要なければ空文字列
        when_edit : bool
            盤面編集か？
        same_move_u : str
            この指し手を指した結果は、他の合法手と同じ結果になる。合法手ではあるが、解析では省きたい
        """
        self._way = way
        self._operator = operator
        self._is_way_unlock = is_way_unlock
        self._option_stones = option_stones
        self._when_edit = when_edit
        self._same_move_u = same_move_u


    @property
    def way(self):
        """路オブジェクト"""
        return self._way


    @property
    def operator(self):
        """演算子オブジェクト"""
        return self._operator


    @property
    def is_way_unlock(self):
        """路ロック解除フラグ
        True:  強制的に 路ロックを解除する
        False: 強制的に 路ロックする
        """
        return self._is_way_unlock


    @property
    def option_stones(self):
        """石の並び。必要なければ空文字列"""
        return self._option_stones


    @property
    def when_edit(self):
        """盤面編集か？"""
        return self._when_edit


    @property
    def same_move_u(self):
        """この指し手を指した結果は、他の合法手と同じ結果になる。合法手ではあるが、解析では省きたい"""
        return self._same_move_u


    @staticmethod
    def code_to_obj(code):

        result = re.match(r"^(&)?([1234567abcdef])(na|nH|nL|no|on|s1|s2|s3|s4|s5|s6|xn|xo|ze|a|c|e|n|o)(#)?(\$[.01]+)?$", code)
        if result is None:
            raise ValueError(f"format error.  move_u:`{code}`")


        # 路ロック解除フラグ
        if result.group(4) == '#':
            is_way_unlock = True
        else:
            is_way_unlock = False


        # 石の並び
        option_stones_str = result.group(5)
        if option_stones_str is None:
            option_stones_str = ''
        else:
            # 頭の `$` を外す
            option_stones_str = option_stones_str[1:]


        return Move(
            # 路
            way=Way.code_to_obj(code=result.group(2)),
            # 演算子
            operator=Operator.code_to_obj(code=result.group(3)),
            # 路ロック解除フラグ
            is_way_unlock=is_way_unlock,
            # 石の並び
            option_stones=option_stones_str,
            # 盤面編集フラグ
            when_edit=result.group(1) is not None)


    def to_code(self):
        # 盤面編集フラグ
        if self._when_edit:
            edit_mark = '&'
        else:
            edit_mark = ''

        # 路ロック解除フラグ
        if self._is_way_unlock:
            way_unlock_str = '#'
        else:
            way_unlock_str = ''

        # 石の並び
        if self._option_stones == '':
            option_stones_str = ''
        else:
            option_stones_str = f'${self._option_stones}'

        return f"{edit_mark}{self.way.to_code()}{self.operator.code}{way_unlock_str}{option_stones_str}"


    def to_edit_mode(self):
        """編集モードのフラグを立てたコピー・オブジェクトを返却します"""
        instance = copy.copy(self)
        instance._when_edit = True
        return instance


    def to_unlock_mode(self):
        """開錠フラグを立てたコピー・オブジェクトを返却します"""
        instance = copy.copy(self)
        instance._is_way_unlock = True
        return instance


    def replaced_by_same(self, same_move_u):
        """冗長フラグを立てたコピー・オブジェクトを返却します
        
        Parameters
        ----------
        same_move_u : str
            同じ結果になる既存の指し手のコード
        """
        instance = copy.copy(self)
        instance._same_move_u = same_move_u
        return instance


class MoveHelper():
    """指し手の計算"""

    @staticmethod
    def inverse_move(board, move, stones_before_change=''):
        """逆操作を算出する

        Parameters
        ----------
        board : Board
            盤
        move : str
            順操作
        stones_before_change : str
            操作によって上書きされた石の並び。無ければ空文字列

        Returns
        -------
        inverse_move : Move
            逆操作
        """

        # 変数名を縮める
        op = move.operator.stem_u
        way = move.way

        # TODO 逆操作 カットザエッジ
        if op == 'c':
            # カットザエッジされた路に、消された石を戻す
            print("[逆操作] c")

            # move = ""

            # if move.option_stones != '':
            #     # TODO 指し手に＄記号を付加し、その後ろに変更前の石の連の情報を付加する
            #     move += f"${move.option_stones}"

            # TODO 任意の石列を置く命令が必要になるのでは？
            return None


        # TODO 逆操作 エディット
        if op == 'e':
            print(f"[逆操作] e  move_u:{move.to_code()}")
            return None


        # シフト
        if op in ['s1', 's2', 's3', 's4', 's5', 's6']:
            (begin, length) = board.get_position_on_way(way)

            # 1ビットシフト --Inverse--> (対象路の石の長さ - 1)ビットシフト
            if op == 's1':
                shift_bits = 1

            # 2ビットシフト --Inverse--> (対象路の石の長さ - 2)ビットシフト
            elif op == 's2':
                shift_bits = 2

            # 3ビットシフト --Inverse--> (対象路の石の長さ - 3)ビットシフト
            elif op == 's3':
                shift_bits = 3

            # 4ビットシフト --Inverse--> (対象路の石の長さ - 4)ビットシフト
            elif op == 's4':
                shift_bits = 4

            # 5ビットシフト --Inverse--> (対象路の石の長さ - 5)ビットシフト
            elif op == 's5':
                shift_bits = 5

            # 6ビットシフト --Inverse--> (対象路の石の長さ - 6)ビットシフト
            elif op == 's6':
                shift_bits = 6

            # TODO 目的のシフトにはなるが、結果が同じシフトの集合は Distinct したい
            return Move.code_to_obj(f"{way.to_code()}s{length-shift_bits}#")


        # ノット・ニュー --Inverse--> カットザエッジ＃
        if op == 'n':
            return Move.code_to_obj(f"{way.to_code()}c#")


        # ノットＬ --Inverse--> エディット＃
        # ノットＨ --Inverse--> エディット＃
        if op in ['nL', 'nH']:
            # {路}e#${石}
            if stones_before_change == '':
                raise ValueError(f"stones error  {op=}  {move.option_stones=}  {stones_before_change=}")

            # stones_before_change と move.option_stones は別物なので要注意
            return Move.code_to_obj(f"{way.to_code()}e#${stones_before_change}")


        # 逆操作 アンド、オア、エクソア、ナンド、ノア、エクスノア、ゼロ、ワン
        if op in ['a', 'o', 'xo', 'na', 'no', 'xn', 'ze', 'on']:
            # stones_before_change と move.option_stones は別物なので要注意

            # New
            if stones_before_change == '':
                return Move.code_to_obj(f"{way.to_code()}c#")

            # Modify {路}e#${石}
            return Move.code_to_obj(f"{way.to_code()}e#${stones_before_change}")


        raise ValueError(f"undefined operator:{op}")


class Sfen():
    """SFEN形式文字列"""


    def __init__(self, from_present, squares, next_turn, way_locks, move_number, move_u_list):
        """初期化"""

        # （初期局面からではなく）現局面のSFEN形式なら真
        self._from_present = from_present

        # 盤面
        self._squares = squares

        # 手番
        self._next_turn = next_turn

        # 添付局面図での路ロック
        self._way_locks = way_locks
        #self._way_locks = {
        #    '1' : False,
        #    '2' : False,
        #    '3' : False,
        #    '4' : False,
        #    '5' : False,
        #    '6' : False,
        #    '7' : False,
        #    'a' : False,
        #    'b' : False,
        #    'c' : False,
        #    'd' : False,
        #    'e' : False,
        #    'f' : False,
        #}

        self._move_number = move_number
        self._move_u_list = move_u_list

        # キャッシュ
        self._code_cached = None


    def to_code(self, without_move_number=False):
        """コード

        Parameters
        ----------
        without_move_number : bool
            SFEN に［何手目］を含まないようにするフラグです。
            同じ局面をチェックしたいとき、［何手目］が異なるかは無視したいという要望があります
        """
        global _way_characters

        if self._code_cached is None:

            buffer = []

            # [盤面]

            # usinewgame コマンドの直後に selfmatch をするとこの例外になる
            if self._squares  is None:
                raise ValueError("self._squares is None")

            spaces = 0

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


            # ［添付図の手番］
            if self._next_turn == PC_BLACK:
                buffer.append(' b ')
            elif self._next_turn == PC_WHITE:
                buffer.append(' w ')
            else:
                raise ValueError(f"undefined next turn  {self._next_turn=}")


            # ［添付図の路ロック］
            locked = False

            for way_code in _way_characters:
                if self._way_locks[way_code]:
                    buffer.append(way_code)
                    locked = True

            if not locked:
                buffer.append('-')


            # ［添付図は何手目か？］
            if not without_move_number:
                buffer.append(f' {self._move_number}')


            # ［添付図からの棋譜］
            if 0 < len(self._move_u_list):
                moves_u = ' '.join(self._move_u_list)
                buffer.append(f' moves {moves_u}')


            sfen_str = ''.join(buffer)

            # 平手初期局面なら startpos に置換
            result = re.match(r"^7/7/2o4/7/7/7 b - 1(.*)$", sfen_str)
            if result:
                sfen_str = f"startpos{result.group(1)}"

            self._code_cached = sfen_str

        return self._code_cached


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
        # これが元データ（対局棋譜を含む）
        self._items = []

        # これはキャッシュ。対局棋譜に限定
        self._cached_game_items = None


    @property
    def items(self):
        return self._items


    @property
    def game_items(self):
        if self._cached_game_items is None:
            self._cached_game_items = []
            for item in self._items:
                if not item.move.when_edit:
                    self._cached_game_items.append(item)

        return self._cached_game_items


    def append(self, item):
        """要素を追加"""
        self._items.append(item)

        # キャッシュを破棄
        self._cached_game_items = None


    def pop(self):
        """要素を削除"""
        item = self._items.pop()

        # キャッシュを破棄
        self._cached_game_items = None

        return item


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

        # 現局面での路ロック
        self._way_locks = {
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

        # 初期局面での路ロック
        self._way_locks_at_init = dict(self._way_locks)

        # 盤面編集履歴（対局棋譜を含む）
        self._board_editing_history = BoardEditingHistory()

        # 終局理由。無ければ空文字列
        self._gameover_reason = ''

        # 勝利条件をクリアーしたのが何手目か
        self._clear_targets = [-1, -1, -1, -1, -1, -1]


    @property
    def clear_targets(self):
        """クリアーターゲット"""
        return self._clear_targets


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


    @property
    def move_number(self):
        """指し手が何手目か（盤面編集操作除く）"""
        return len(self._board_editing_history.game_items)


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


    def set_way_lock_by_code(self, way_u, value, is_it_init=False):
        """路ロックする"""
        self._way_locks[way_u] = value
        if is_it_init:
            self._way_locks_at_init[way_u] = value


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
        global _way_characters

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
            
            else:
                # フラッシュ。空白が何個あるかで１回ずつカーソルを進める
                while 0 < numeric:
                    # フォワード
                    cursor.file_forward()
                    numeric -= 1

                if ch in ['x', 'o']:

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

        # 路ロック
        # --------
        if parts[2] != '-':
            for way_u in parts[2]:
                if way_u in _way_characters:
                    self.set_way_lock_by_code(way_u, True, is_it_init=True)

                else:
                    raise ValueError(f"undefined sfen character on locks:`{way_u}`")

        # TODO 手数の解析
        pass


    def exists_stone_on_way(self, way):
        """指定の路に石が置いてあるか？
        
        Parameters
        ----------
        way : Way
            路オブジェクト
        """

        # 筋
        if way.axis_id == FILE_ID:
            for rank in range(0, RANK_LEN):
                sq = Square.file_rank_to_sq(way.number, rank)
                stone = self._squares[sq]

                if stone != PC_EMPTY:
                    return True
                
            return False

        # 段
        if way.axis_id == RANK_ID:
            for file in range(0, FILE_LEN):
                sq = Square.file_rank_to_sq(file, way.number)
                stone = self._squares[sq]

                if stone != PC_EMPTY:
                    return True
                
            return False

        raise ValueError(f"undefined axis_id: {way.axis_id}")


    def get_position_on_way(self, way):
        """路を指定すると、そこにある石の連なりの開始位置と長さを返す

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
        if way.axis_id == FILE_ID:
            src_dst_file = way.number

            # 入力路から、出力路へ、評価値を出力
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
        if way.axis_id == RANK_ID:
            src_dst_rank = way.number

            # 入力路から、出力路へ、評価値を出力
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

        raise ValueError(f"undefined axis_id:{way.axis_id}")


    def set_stones_on_way(self, target_way, stones_str):
        """指定の路に、指定の石の列を上書きします"""

        stones_before_change = ''
        stones_str_len = len(stones_str)

        # 筋（段）方向両用
        axes_absorber = target_way.absorb_axes()

        # 幅いっぱい使う
        if stones_str_len == axes_absorber.opponent_axis_length:
            begin = 0
            end = axes_absorber.opponent_axis_length

        # 置いてある石の位置に合わせる
        else:
            (begin, length) = self.get_position_on_way(target_way)

            if length != stones_str_len:
                raise ValueError(f"length error  {length=}  {stones_str_len=}")

            end = begin + length


        for i in range(begin, end):

            dst_sq = Square.file_rank_to_sq(target_way.number, i, swap=axes_absorber.swap_axes)
            old_stone = self._squares[dst_sq]

            if old_stone != PC_EMPTY:
                stones_before_change += _pc_to_str[old_stone]

            self._squares[dst_sq] = _str_to_pc[stones_str[i - begin]]

        return stones_before_change


    def copy_stones_on_line_unary(self, move, overwrite=False):
        """入力路 a を単項演算して、 b 路へ出力

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

        # 筋（段）方向両用
        axes_absorber = move.way.absorb_axes()

        for i in range(0, axes_absorber.opponent_axis_length):

            dst_sq = Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)
            old_stone = self._squares[dst_sq]

            if overwrite and old_stone != PC_EMPTY:
                stones_before_change += _pc_to_str[old_stone]

            self._squares[dst_sq] = move.operator.unary_operate(
                stone=self._squares[Square.file_rank_to_sq(move.way.number + 1, i, swap=axes_absorber.swap_axes)])

        return stones_before_change


    def copy_stones_on_line_binary(self, move):
        """入力路 a, b を二項演算して、 c 路へ出力

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

        (input_way_1, input_way_2) = self.get_input_ways_by_binary_operation(move.way)

        # 対象の路に石が置いてあれば上書きフラグをOn、そうでなければOff
        overwrite = self.exists_stone_on_way(move.way)

        # 筋（段）方向両用
        axes_absorber = move.way.absorb_axes()

        for i in range(0, axes_absorber.opponent_axis_length):

            dst_sq = Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)
            old_stone = self._squares[dst_sq]

            if overwrite and old_stone != PC_EMPTY:
                stones_before_change += _pc_to_str[old_stone]

            input_stone_at_first = self._squares[Square.file_rank_to_sq(input_way_1.number, i, swap=axes_absorber.swap_axes)]
            input_stone_at_second = self._squares[Square.file_rank_to_sq(input_way_2.number, i, swap=axes_absorber.swap_axes)]

            #print(f"{move.way.axis_id=}  {i=}  {input_way_1.number=}  {input_way_2.number=}  {input_stone_at_first=}  {input_stone_at_second=}  {dst_sq=}")

            if input_stone_at_first == PC_EMPTY or input_stone_at_second == PC_EMPTY:
                continue

            self._squares[dst_sq] = move.operator.binary_operate(
                left_operand=_pc_to_binary[input_stone_at_first],
                right_operand=_pc_to_binary[input_stone_at_second])

        return stones_before_change


    def on_exit_push_usi(self, move, way_lock, stones_before_change=''):
        """push_usi() 関数から抜けるときに実行する定型処理

        Parameters
        ----------
        move : Move
            指し手。履歴に記憶します
        way_lock : bool
            路ロックを掛けるか外すかの２択
        stones_before_change : str
            変更前の石の状態
        """
        self.set_way_lock_by_code(move.way.to_code(), way_lock)

        self._board_editing_history.append(BoardEditingItem(
            move=move,
            stones_before_change=stones_before_change))


    def get_unary_src_way_1_number(self, way):
        # 左（上）端なら、右（下）側確定
        if way.number == 0:
            return way.number + 1

        # 右（下）端なら、左（上）側確定
        if way.number == FILE_LEN - 1:
            return way.number - 1
        
        # 左か右（上か下）で、石が置いてある路が入力路
        if self.exists_stone_on_way(Way(way.axis_id, way.number - 1)):
            return way.number - 1

        if self.exists_stone_on_way(Way(way.axis_id, way.number + 1)):
            return way.number + 1

        raise ValueError("not operator invalid operation")


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
            e : Edit
            s1 ～ s6: Shift
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

            # 対象の路に石が置いてある
            if self.exists_stone_on_way(move.way):

                # 筋（段）方向両用
                axes_absorber = move.way.absorb_axes()
                (begin, length) = self.get_position_on_way(move.way)

                # 盤面更新 --> 空欄で上書き
                for src_dst_i in range(begin, begin+length):
                    src_dst_sq = Square.file_rank_to_sq(move.way.number, src_dst_i, swap=axes_absorber.swap_axes)
                    stone = self._squares[src_dst_sq]
                    if stone != PC_EMPTY:
                        stones_before_change += _pc_to_str[stone]
                        self._squares[src_dst_sq] = PC_EMPTY

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:
                raise ValueError("c演算では、石の置いてない対象路を指定してはいけません")


        # エディット演算子
        #
        #   零項演算子
        #   既に石があるところに上書きすることを想定している
        #
        if op.startswith('e'):

            #print(f"Edit operator  move_u={move.to_code()}  way_u={move.way.to_code()}  {move.option_stones=}")

            # 盤面更新前
            exists_stone_on_way_before_change = self.exists_stone_on_way(move.way)

            # 盤面更新
            stones_before_change = self.set_stones_on_way(
                target_way=move.way,
                stones_str=move.option_stones)

            # もともとは、対象の路に石が置いてあった
            if exists_stone_on_way_before_change:
                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # もともとは、対象の路に石が置いてなかった
            else:
                # 新規作成操作では
                #   路ロックは掛からない（外れる）
                #   変更前の石は無し
                self.on_exit_push_usi(move, way_lock=False)
                return


        # シフト（単項演算子 shift）
        #
        #   オペレーターの機能というより、ボードの機能
        #   このゲームでのシフトは、入力と出力は同じ筋（段）上で行います（inplace）
        #
        if op.startswith('s'):
            # 何ビットシフトか？
            bit_shift = int(op[1:2])

            # 対象の路に石が置いてある
            if self.exists_stone_on_way(move.way):

                # 筋（段）方向両用
                axes_absorber = move.way.absorb_axes()

                # 入力路から、出力路へ、評価値を出力
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

                source_stones = [PC_EMPTY] * axes_absorber.opponent_axis_length
                for i in range(0, axes_absorber.opponent_axis_length):
                    src_sq = Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)
                    stone = self._squares[src_sq]
                    source_stones[i] = stone

                # (1)
                (begin, length) = self.get_position_on_way(move.way)

                # (2)
                for i in range(begin, begin+length):
                    dst_sq = Square.file_rank_to_sq(
                        file=move.way.number,
                        rank=(i - begin + bit_shift) % length + begin,
                        swap=axes_absorber.swap_axes)

                    # コピー
                    self._squares[dst_sq] = source_stones[i]

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:
                raise ValueError("s演算では、石の置いてない対象路を指定してはいけません")


        # ノット（単項演算子）
        if op == 'n':

            # 対象の路に石が置いてある
            if self.exists_stone_on_way(move.way):
                raise ValueError("n演算では、石の置いている対象路を指定してはいけません。nL, nH を参考にしてください")

            # 対象の路に石が置いてない
            else:

                # 筋（段）方向両用
                axes_absorber = move.way.absorb_axes()

                # 入力路から、出力路へ、評価値を出力
                for i in range(0, axes_absorber.opponent_axis_length):
                    src_stone = self._squares[Square.file_rank_to_sq(
                        self.get_unary_src_way_1_number(move.way), i, swap=axes_absorber.swap_axes)]
                    self._squares[Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)] = move.operator.unary_operate(src_stone)

                # 新規作成操作では
                #   路ロックは掛からない（外れる）
                #   変更前の石は無し
                self.on_exit_push_usi(move, way_lock=False)
                return


        # ノット（単項演算子 Reverse）路上の小さい方
        if op == 'nL':

            # 対象の路に石が置いてある
            if self.exists_stone_on_way(move.way):

                # 筋（段）方向両用
                axes_absorber = move.way.absorb_axes()

                # 入力路から、出力路へ、評価値を出力
                for i in range(0, axes_absorber.opponent_axis_length):
                    src_stone = self._squares[Square.file_rank_to_sq(
                        self.get_unary_src_way_1_number(move.way), i, swap=axes_absorber.swap_axes)]

                    if src_stone != PC_EMPTY:
                        dst_stone = self._squares[Square.file_rank_to_sq(
                            move.way.number, i, swap=axes_absorber.swap_axes)]

                        stones_before_change += _pc_to_str[dst_stone]
                        self._squares[Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)] = move.operator.unary_operate(src_stone)

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:
                raise ValueError("nL演算では、石の置いてない対象路を指定してはいけません")


        # ノット（単項演算子 Reverse）路上の大きい方
        if op == 'nH':

            # 対象の路に石が置いてある
            if self.exists_stone_on_way(move.way):

                # 筋（段）方向両用
                axes_absorber = move.way.absorb_axes()

                # 入力路から、出力路へ、評価値を出力
                for i in range(0, axes_absorber.opponent_axis_length):
                    src_stone = self._squares[Square.file_rank_to_sq(
                        self.get_unary_src_way_1_number(move.way), i, swap=axes_absorber.swap_axes)]

                    if src_stone != PC_EMPTY:
                        dst_stone = self._squares[Square.file_rank_to_sq(
                            move.way.number, i, swap=axes_absorber.swap_axes)]

                        stones_before_change += _pc_to_str[dst_stone]
                        self._squares[Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)] = move.operator.unary_operate(src_stone)

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:
                raise ValueError("nH演算では、石の置いてない対象路を指定してはいけません")


        # アンド, オア, ゼロ, ノア, エクソア, ナンド, エクスノア, ワン
        if op in ['a', 'o', 'ze', 'no', 'xo', 'na', 'xn', 'on']:

            # 盤面更新前
            exists_stone_on_way_before_change = self.exists_stone_on_way(move.way)

            # 盤面更新
            stones_before_change = self.copy_stones_on_line_binary(move)

            # もともとは、対象の路に石が置いてあった
            if exists_stone_on_way_before_change:
                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # もともとは、対象の路に石が置いてなかった
            else:
                # 新規作成操作では
                #   路ロックは掛からない（外れる）
                #   変更前の石は無し
                self.on_exit_push_usi(move, way_lock=False)
                return


        raise ValueError(f"undefined operator code: {op}")


    def get_edge_way_from_adjacent_space(self, space_way):
        """石のない路の隣の石のある路を返す

        Parameters
        ----------
        space_way : Way
            石のない路。ただし、その隣には石があるものとする
        """

        # 筋方向
        if space_way.axis_id == FILE_ID:
            left_way = space_way.low_way()
            if left_way is not None:
                (begin, length) = self.get_position_on_way(left_way)
                if 0 < length:
                    return left_way

            right_way = space_way.high_way()
            if right_way is not None:
                (begin, length) = self.get_position_on_way(right_way)
                if 0 < length:
                    return right_way

        # 段方向
        if space_way.axis_id == RANK_ID:
            top_way = space_way.low_way()
            if top_way is not None:
                (begin, length) = self.get_position_on_way(top_way)
                if 0 < length:
                    return top_way

            bottom_way = space_way.high_way()
            if bottom_way is not None:
                (begin, length) = self.get_position_on_way(bottom_way)
                if 0 < length:
                    return bottom_way

        None


    def pop(self):
        """一手戻す"""
        # 最後の指し手を取得
        latest_edit = self._board_editing_history.items[-1]

        # 最後の指し手の逆操作を算出
        inverse_move = MoveHelper.inverse_move(
            board=self,
            move=latest_edit.move,
            stones_before_change=latest_edit.stones_before_change)

        if inverse_move is None:
            raise ValueError(f"[pop] {latest_edit.move.to_code()=} に逆操作がなく、pop に失敗しました")

        # 逆操作には、盤面編集フラグ、開錠フラグを立てる
        inverse_move_for_edit = inverse_move.to_edit_mode().to_unlock_mode()
        inverse_move_for_edit_u = inverse_move_for_edit.to_code()

        #print(f"[pop] 盤面編集として、逆操作を実行  {inverse_move_for_edit_u=}  {inverse_move_for_edit.is_way_unlock=}")
        self.push_usi(inverse_move_for_edit_u)
        #self._board.update_legal_moves()

        # さっきの逆操作を履歴から除去
        popped_item = self._board_editing_history.pop()
        #print(f"[pop] 逆操作を履歴から除去  {popped_item.move.to_code()=}")

        # 最後の指し手も履歴から除去
        popped_item = self._board_editing_history.pop()
        #print(f"[pop] 最後の指し手も履歴から除去  {popped_item.move.to_code()=}")


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
        
        上図の場合、 True, 3, 6, c, d の路オブジェクトを返す

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
            dst_file_way = Way(FILE_ID, dst_file)

            # 縦連の場所を調べる
            (begin, length) = self.get_position_on_way(dst_file_way)

            # 石が置いてる段
            if 0 < length:
                top_rank = begin
                bottom_rank = begin + length - 1
                break

        
        if top_rank is None:
            return (False, None, None, None, None)


        # とりあえず各段について
        for dst_rank in range(0, RANK_LEN):
            dst_rank_way = Way(RANK_ID, dst_rank)

            # 横連の場所を調べる
            (begin, length) = self.get_position_on_way(dst_rank_way)

            # 石が置いてる筋
            if 0 < length:
                left_file = begin
                right_file = begin + length - 1
                break


        return (True, left_file, right_file, top_rank, bottom_rank)


    def get_input_ways_by_binary_operation(self, target_way):
        """二項演算するときの入力路２つ"""

        # 対象路にロックが掛かっていたら、二項演算禁止
        if self._way_locks[target_way.to_code()]:
            return (None, None)


        # 筋方向
        if target_way.axis_id == FILE_ID:
            opponent_axis_length = FILE_LEN

        # 段方向
        elif target_way.axis_id == RANK_ID:
            opponent_axis_length = RANK_LEN

        else:
            raise ValueError(f"undefined way: {target_way.axis_id=}")


        # 対称路に石が置いてあるなら
        if self.exists_stone_on_way(target_way):
            # ロウ、ハイの両方に石が置いてある必要がある
            if 0 < target_way.number and target_way.number < opponent_axis_length - 1:
                low_way = target_way.low_way()
                high_way = target_way.high_way()
                if self.exists_stone_on_way(low_way) and self.exists_stone_on_way(high_way):
                    return (low_way, high_way)

        # 対象路に石が置いてないなら
        else:
            # ロウの方に２つ続けて石が置いているか？
            if 1 < target_way.number:
                first_way = target_way.low_way()
                second_way = target_way.low_way(diff=2)
                if self.exists_stone_on_way(first_way) and self.exists_stone_on_way(second_way):
                    return (first_way, second_way)
            
            # ハイの方に２つ続けて石が置いているか？
            if target_way.number < opponent_axis_length - 2:
                first_way = target_way.high_way()
                second_way = target_way.high_way(diff=2)
                if self.exists_stone_on_way(first_way) and self.exists_stone_on_way(second_way):
                    return (first_way, second_way)


    def make_legal_moves(self, operator_u, for_edit_mode=False):
        """
        Parameters
        ----------
        operator_u : str
            演算子コード
            例： 'o'
        for_edit_mode : bool
            盤面編集用
        """
        opponent_axis_length_list = [FILE_LEN, RANK_LEN]
        axis_id_list = [FILE_ID, RANK_ID]   # 筋、段
        # 筋（段）両用
        for j in range(0, 1):
            opponent_axis_length = opponent_axis_length_list[j]

            for i in range(0, opponent_axis_length):
                dst_i_way = Way(axis_id_list[j], i)

                # 石が置いてある路
                if self.exists_stone_on_way(dst_i_way):

                    # 路にロックが掛かっていたら Or の Reverse は禁止
                    if self._way_locks[dst_i_way.to_code()]:
                        continue

                    # ロウ、ハイの両方に石が置いてある必要がある
                    if 0 < i and i < opponent_axis_length - 1 and self.exists_stone_on_way(dst_i_way.low_way()) and self.exists_stone_on_way(dst_i_way.high_way()):
                        # 対象路上にある石を Or して Reverse できる
                        move = Move(dst_i_way, Operator.code_to_obj(operator_u))
                        if for_edit_mode:
                            self._moves_for_edit.append(move)
                        else:
                            self._legal_moves.append(move)

                # 石が置いてない路
                else:
                    # 隣のどちらかに２つ続けて石が置いているか？
                    if ((1 < i and self.exists_stone_on_way(dst_i_way.low_way()) and self.exists_stone_on_way(dst_i_way.low_way(diff=2))) or
                        (i < opponent_axis_length - 2 and self.exists_stone_on_way(dst_i_way.high_way()) and self.exists_stone_on_way(dst_i_way.high_way(diff=2)))):
                        # Or で New できる
                        move = Move(dst_i_way, Operator.code_to_obj(operator_u))
                        if for_edit_mode:
                            self._moves_for_edit.append(move)
                        else:
                            self._legal_moves.append(move)


    def update_legal_moves(self):
        """合法手の一覧生成"""

        #print("[update_legal_moves] 実行")

        self._legal_moves = []
        self._moves_for_edit = []

        (rect_exists, left_file, right_file, top_rank, bottom_rank) = self.get_edges()


        # カットザエッジ（Cut the edge）の合法手生成（盤面編集用）
        if rect_exists:
            if 0 < right_file - left_file:
                self._moves_for_edit.append(Move(Way(FILE_ID, left_file), Operator.code_to_obj('c')))
                self._moves_for_edit.append(Move(Way(FILE_ID, right_file), Operator.code_to_obj('c')))
            
            if 0 < bottom_rank - top_rank:
                self._moves_for_edit.append(Move(Way(RANK_ID, top_rank), Operator.code_to_obj('c')))
                self._moves_for_edit.append(Move(Way(RANK_ID, bottom_rank), Operator.code_to_obj('c')))


        # シフト（Shift）の合法手生成
        #
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

        # 筋（段）方向両用
        for way_u in _way_characters:
            way = Way.code_to_obj(way_u)

            # 路にロックが掛かっていたら Shift は禁止
            if self._way_locks[way.to_code()]:
                continue

            (begin, length) = self.get_position_on_way(way)

            # 石が置いてる路
            if 0 < length:
                # Shift できる
                for i in range(1, length):
                    move = Move(way, Operator.code_to_obj(f's{i}'))

                    # 合法手として記憶
                    self._legal_moves.append(move)


        # ノット（Not）の合法手生成
        # 筋方向
        for dst_file in range(0, FILE_LEN):
            dst_file_way = Way(FILE_ID, dst_file)

            # 石が置いてある路
            if self.exists_stone_on_way(dst_file_way):

                # 路にロックが掛かっていたら Not の Reverse は禁止
                if self._way_locks[dst_file_way.to_code()]:
                    continue

                if 0 < dst_file and self.exists_stone_on_way(dst_file_way.low_way()):
                    # 路上で小さい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_file_way, Operator.code_to_obj('nL')))

                if dst_file < FILE_LEN - 1 and self.exists_stone_on_way(dst_file_way.high_way()):
                    # 路上で大きい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_file_way, Operator.code_to_obj('nH')))

            # 石が置いてない路
            else:
                # 隣のどちらかに石が置いているか？
                if 0 < dst_file and self.exists_stone_on_way(dst_file_way.low_way()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_file_way, Operator.code_to_obj('n')))

                if dst_file < FILE_LEN - 1 and self.exists_stone_on_way(dst_file_way.high_way()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_file_way, Operator.code_to_obj('n')))


        # 段方向
        for dst_rank in range(0, RANK_LEN):
            dst_rank_way = Way(RANK_ID, dst_rank)

            # 石が置いてある路
            if self.exists_stone_on_way(dst_rank_way):

                # 路にロックが掛かっていたら Not の Reverse は禁止
                if self._way_locks[dst_rank_way.to_code()]:
                    continue

                if 0 < dst_rank and self.exists_stone_on_way(dst_rank_way.low_way()):
                    # 路上で小さい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_rank_way, Operator.code_to_obj('nL')))

                if dst_rank < RANK_LEN - 1 and self.exists_stone_on_way(dst_rank_way.high_way()):
                    # 路上で大きい方にある石を Not して Reverse できる
                    self._legal_moves.append(Move(dst_rank_way, Operator.code_to_obj('nH')))

            # 石が置いてない路
            else:
                # 隣のどちらかに石が置いているか？
                if 0 < dst_rank and self.exists_stone_on_way(dst_rank_way.low_way()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_rank_way, Operator.code_to_obj('n')))

                if dst_rank < RANK_LEN - 1 and self.exists_stone_on_way(dst_rank_way.high_way()):
                    # Not で New できる
                    self._legal_moves.append(Move(dst_rank_way, Operator.code_to_obj('n')))


        # アンド（AND）の合法手生成
        self.make_legal_moves(operator_u='a')

        # オア（OR）の合法手生成
        self.make_legal_moves(operator_u='o')

        # ゼロ（ZERO）の合法手生成
        self.make_legal_moves(operator_u='ze', for_edit_mode=True)

        # ノア（NOR）の合法手生成
        self.make_legal_moves(operator_u='no')

        # エクソア（XOR）の合法手生成
        self.make_legal_moves(operator_u='xo')

        # ナンド（NAND）の合法手生成
        self.make_legal_moves(operator_u='na')

        # エクスノア（XNOR）の合法手生成
        self.make_legal_moves(operator_u='xn')

        # ワン（ONE）の合法手生成
        self.make_legal_moves(operator_u='on', for_edit_mode=True)

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
        #
        #          [b3]
        #       1 2 3 4 5 6 7  
        #     +---------------+
        #   a | 1 1 1 ^ ^ . . |
        #   b | ^ ^ ^ ^ ^ . . |
        #   c | ^ ^ ^ ^ ^ . . |
        #   d | ^ ^ ^ ^ ^ . . |
        #   e | ^ ^ ^ ^ ^ . . |
        #   f | ^ ^ ^ ^ ^ . . |
        #     +---------------+
        #
        # 図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        #
        def update_clear_target_b3():
            # 棒サイズ
            line_length = 3
            my_stone_color = PC_BLACK
            is_not_hit = False  # 外側の file ループを続行

            for rank in range(0, RANK_LEN):
                #             0,        6

                for file in range(0, FILE_LEN-line_length+1):
                    #             0,        7-          3+1
                    #             0,       =5 

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file + i, rank)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        continue

                    self._clear_targets[0] = self.move_number
                    return

        if self._clear_targets[0] == -1:
            update_clear_target_b3()


        # クリアー条件　黒番２　斜め（左右反転でも構わない）に４つ 1 が並んでいること
        #
        #   Sinister Diagonal     Baroque Diagonal
        #           [b4]
        #      1 2 3 4 5 6 7          1 2 3 4 5 6 7
        #    +---------------+      +---------------+
        #  a | 1 ^ ^ ^ . . . |    a | . . . 1 ^ ^ ^ |
        #  b | ^ 1 ^ ^ . . . |    b | . . 1 ^ ^ ^ ^ |
        #  c | ^ ^ 1 ^ . . . |    c | . 1 . ^ ^ ^ ^ |
        #  d | . . . 1 . . . |    d | 1 . . . . . . |
        #  e | . . . . . . . |    e | . . . . . . . |
        #  f | . . . . . . . |    f | . . . . . . . |
        #    +---------------+      +---------------+
        #
        # 図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        #
        def update_clear_target_b4():
            # 棒サイズ
            line_length = 4
            my_stone_color = PC_BLACK
            is_not_hit = False  # 外側の file ループを続行

            # Sinister Diagonal
            for rank in range(0, RANK_LEN-line_length+1):
                #             0,        6-          4+1
                #             0,       =3

                for file in range(0, FILE_LEN-line_length+1):
                    #             0,        7-          4+1
                    #             0,       =4

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file + i, rank + i)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        continue

                    self._clear_targets[1] = self.move_number
                    return

            # Baroque Diagonal
            for rank in range(0, RANK_LEN-(RANK_LEN-line_length)-1):
                #             0,        6-(       6-          4)-1
                #             0,       =3 
                for file in range(line_length-1, FILE_LEN):
                    #                       4-1,        7
                    #                      =3  ,        7

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file - i, rank + i)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        break

                    self._clear_targets[1] = self.move_number
                    return

        if self._clear_targets[1] == -1:
            update_clear_target_b4()


        # クリアー条件　黒番３　縦に５つ 1 が並んでいること
        #
        #          [b5]
        #       1 2 3 4 5 6 7
        #     +---------------+
        #   a | 1 ^ ^ ^ ^ ^ ^ |
        #   b | 1 ^ ^ ^ ^ ^ ^ |
        #   c | 1 . . . . . . |
        #   d | 1 . . . . . . |
        #   e | 1 . . . . . . |
        #   f | . . . . . . . |
        #     +---------------+
        #
        # 図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        #
        def update_clear_target_b5():
            # 棒サイズ
            line_length = 5
            my_stone_color = PC_BLACK
            is_not_hit = False  # 外側の file ループを続行

            for rank in range(0, RANK_LEN-line_length+1):
                #             0,        6-          5+1
                #             0,       =2

                for file in range(0, FILE_LEN):
                    #             0,        7

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file, rank + i)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        continue

                    self._clear_targets[2] = self.move_number
                    return

        if self._clear_targets[2] == -1:
            update_clear_target_b5()



        # クリアー条件　白番１　縦に３つ 0 が並んでいること
        #          [w3]
        #       1 2 3 4 5 6 7
        #     +---------------+
        #   a | 0 ^ ^ ^ ^ ^ ^ |
        #   b | 0 ^ ^ ^ ^ ^ ^ |
        #   c | 0 ^ ^ ^ ^ ^ ^ |
        #   d | ^ ^ ^ ^ ^ ^ ^ |
        #   e | . . . . . . . |
        #   f | . . . . . . . |
        #     +---------------+
        #
        # 図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        #
        def update_clear_target_w3():
            # 棒サイズ
            line_length = 3
            my_stone_color = PC_WHITE
            is_not_hit = False  # 外側の file ループを続行

            for rank in range(0, RANK_LEN-line_length+1):
                #             0,        6-          3+1
                #             0,       =4

                for file in range(0, FILE_LEN):
                    #             0,        7

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file, rank + i)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        continue

                    self._clear_targets[3] = self.move_number
                    return

        if self._clear_targets[3] == -1:
            update_clear_target_w3()


        # クリアー条件　白番２　斜め（左右反転でも構わない）に４つ 0 が並んでいること
        #
        #   Sinister Diagonal     Baroque Diagonal
        #           [w4]
        #      1 2 3 4 5 6 7          1 2 3 4 5 6 7
        #    +---------------+      +---------------+
        #  a | 0 ^ ^ ^ . . . |    a | . . . 0 ^ ^ ^ |
        #  b | ^ 0 ^ ^ . . . |    b | . . 0 ^ ^ ^ ^ |
        #  c | ^ ^ 0 ^ . . . |    c | . 0 . ^ ^ ^ ^ |
        #  d | . . . 0 . . . |    d | 0 . . . . . . |
        #  e | . . . . . . . |    e | . . . . . . . |
        #  f | . . . . . . . |    f | . . . . . . . |
        #    +---------------+      +---------------+
        #
        # 図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        #
        def update_clear_target_w4():
            # 棒サイズ
            line_length = 4
            my_stone_color = PC_WHITE
            is_not_hit = False  # 外側の file ループを続行

            # Sinister Diagonal
            for rank in range(0, RANK_LEN-line_length+1):
                #             0,        6-          4+1
                #             0,       =3

                for file in range(0, FILE_LEN-line_length+1):
                    #             0,        7-          4+1
                    #             0,       =4

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file + i, rank + i)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        continue

                    self._clear_targets[4] = self.move_number
                    return

            # Baroque Diagonal
            for rank in range(0, RANK_LEN-(RANK_LEN-line_length)-1):
                #             0,        6-(       6-          4)-1
                #             0,       =3

                for file in range(line_length-1, FILE_LEN):
                    #                       4-1,        7
                    #                      =3  ,        7

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file - i, rank + i)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        break

                    self._clear_targets[4] = self.move_number
                    return

        if self._clear_targets[4] == -1:
            update_clear_target_w4()


        # クリアー条件　白番３　横に５つ 0 が並んでいること
        #
        #          [w5]
        #       1 2 3 4 5 6 7
        #     +---------------+
        #   a | 0 0 0 0 0 . . |
        #   b | ^ ^ ^ . . . . |
        #   c | ^ ^ ^ . . . . |
        #   d | ^ ^ ^ . . . . |
        #   e | ^ ^ ^ . . . . |
        #   f | ^ ^ ^ . . . . |
        #     +---------------+
        #
        # 図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        #
        def update_clear_target_w5():
            # 棒サイズ
            line_length = 5
            my_stone_color = PC_WHITE
            is_not_hit = False  # 外側の file ループを続行

            for rank in range(0, RANK_LEN):
                #             0,        6

                for file in range(0, FILE_LEN-line_length+1):
                    #             0,        7-          5+1
                    #             0,       =3

                    for i in range(0, line_length):
                        if self._squares[Square.file_rank_to_sq(file + i, rank)] != my_stone_color:
                            is_not_hit = True
                            break

                    if is_not_hit:
                        is_not_hit = False
                        continue

                    self._clear_targets[5] = self.move_number
                    return

        if self._clear_targets[5] == -1:
            update_clear_target_w5()


        # どちらかのプレイヤーが３つのターゲットを完了した
        is_black_win = False
        is_white_win = False
        if self._clear_targets[0] != -1 and self._clear_targets[1] != -1 and self._clear_targets[2] != -1:
            is_black_win = True

        if self._clear_targets[3] != -1 and self._clear_targets[4] != -1 and self._clear_targets[5] != -1:
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


    def distinct_legal_moves(self):
        """指してみると結果が同じになる指し手は、印をつけたい

        左右反転、上下反転で同形のものも弾きたい。
        縦横比が異なるので、９０°回転は対象外とする。
        上下左右反転の形を作る操作は、対局中にはないはずなので対象外とする
        """

        sfen_memory_dict = {}

        # 一手指す前に、現局面が載っている sfen を取得しておく
        #
        #   例： 7/7/2o4/2x4/7/7 b - 1
        #
        #   ここで、末尾の［何手目か？］は必ず変わってしまうので、それは省いておく
        #
        sub_sfen_before_push = self.as_sfen(from_present=True).to_code(without_move_number=True)
        #print(f"[distinct_legal_moves] {sub_sfen_before_push=}")

        for i in range(0, len(self._legal_moves)):
            move = self._legal_moves[i]

            # TODO とりあえず、逆操作が実装されている演算だけ調べる
            # １～６ビットシフト、ノット、ノットＬ、ノットＨ、アンド、オア、エクソア、ナンド、ノア、エクスノア、ゼロ、ワン
            if move.operator.code not in ['s1', 's2', 's3', 's4', 's5', 's6', 'n', 'nH', 'nL', 'a', 'o', 'xo', 'na', 'no', 'xn', 'ze', 'on']:
                continue

            # FIXME パスという指し手はないが、現局面と同じになる指し手も省きたいので、暫定で追加している
            sfen_memory_dict[sub_sfen_before_push] = 'pass'

            # 試しに一手指してみる
            #print(f"試しに一手指してみる  {move.to_code()=}")
            self.push_usi(move.to_code())

            # 一般的に長さが短い方の形式の SFEN を記憶
            #
            #   例： 7/7/2x4/2o4/7/7 b 3 2
            #
            #   ここで、末尾の［何手目か？］は必ず変わってしまうので、それは省いておく
            #
            sub_sfen_after_push = self.as_sfen(from_present=True).to_code(without_move_number)
            #print(f"一般的に長さが短い方の形式の SFEN を記憶  {sub_sfen_after_push=}")
            
            # 既に記憶している SFEN と重複すれば、演算した結果が同じだ。重複を記憶しておく
            if sub_sfen_after_push in sfen_memory_dict.keys():
                same_move_u = sfen_memory_dict[sub_sfen_after_push]
                #print(f"[distinct_legal_moves] 既に記憶している SFEN と重複した。演算した結果が同じだ。重複を記憶しておく  {same_move_u=}  {sub_sfen_after_push=}")
                replaced_move = move.replaced_by_same(same_move_u)

                # 格納し直す
                # FIXME 一手進んだ局面のリーガルムーブを設定しても意味ないのでは？ 一手進んだり、戻ったりするたびにリセットしないように要注意
                #print(f"[distinct_legal_moves] 格納し直す  {replaced_move.to_code()}  {replaced_move.same_move_u=}")
                self._legal_moves[i] = replaced_move
                #print(f"[distinct_legal_moves] 格納し直した  {self._legal_moves[i].to_code()}  {self._legal_moves[i].same_move_u=}")
            
            # 重複していなければ、一時記憶する
            #
            #   例： 7/7/2x4/2o4/7/7 b 3 2
            #
            #   ここで、末尾の［何手目か？］は必ず変わってしまうので、スプリットして省いておく
            #
            else:
                move_u = move.to_code()
                #print(f"[distinct_legal_moves] 重複していないので、一時記憶する  {move_u=}  {sub_sfen_after_push=}")
                sfen_memory_dict[sub_sfen_after_push] = move_u
            
            # 一手戻す
            #print(f"[distinct_legal_moves] 一手戻す")
            self.pop()

            # DEBUG 一手戻した後に、現局面が載っている sfen を取得しておく
            rollbacked_sfen = self.as_sfen(from_present=True).to_code(without_move_number=False)
            #
            #   例： 7/7/2o4/2x4/7/7 b - 1
            #
            #   ここで、末尾の［何手目か？］は必ず変わってしまうので、それは省いておく
            #

            # DEBUG 巻き戻せていなければ例外を投げる
            if sub_sfen_before_push != rollbacked_sfen:
                raise ValueError(f"undo error  {sub_sfen_before_push=}  {rollbacked_sfen=}")


    def as_str(self):
        """（拡張仕様）盤のテキスト形式
        例：
            [ 2 moves | moved 3s1]
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
        global _pc_to_str

        # １行目表示
        # ---------
        edits_num = len(self._board_editing_history.items)
        if self.move_number != edits_num:
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
        clear_targets_list = []
        if self._clear_targets[0] != -1:
            clear_targets_list.append('b3')
        if self._clear_targets[1] != -1:
            clear_targets_list.append('b4')
        if self._clear_targets[2] != -1:
            clear_targets_list.append('b5')
        if self._clear_targets[3] != -1:
            clear_targets_list.append('w3')
        if self._clear_targets[4] != -1:
            clear_targets_list.append('w4')
        if self._clear_targets[5] != -1:
            clear_targets_list.append('w5')

        if 0 < len(clear_targets_list):
            cleared_targets_str = f" | {' '.join(clear_targets_list)}"
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


        print(f"[{self.move_number:2} moves {edits_num_str}| {latest_move_str}{cleared_targets_str} | {next_turn_str}]")


        # 盤表示
        # ------

        # 数値を表示用文字列(Str)に変更
        s = [' '] * BOARD_AREA
        for sq in range(0, BOARD_AREA):
            s[sq] = _pc_to_str[self._squares[sq]]

        # 筋（段）の符号、またはロック
        def get_way_code_2(way_code):
            if self._way_locks[way_code]:
                return '#'

            return way_code

        # Way
        a = {
            '1' : get_way_code_2('1'),
            '2' : get_way_code_2('2'),
            '3' : get_way_code_2('3'),
            '4' : get_way_code_2('4'),
            '5' : get_way_code_2('5'),
            '6' : get_way_code_2('6'),
            '7' : get_way_code_2('7'),
            'a' : get_way_code_2('a'),
            'b' : get_way_code_2('b'),
            'c' : get_way_code_2('c'),
            'd' : get_way_code_2('d'),
            'e' : get_way_code_2('e'),
            'f' : get_way_code_2('f'),
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
                if self.move_number % 2 == 0:
                    return PC_BLACK
                
                return PC_WHITE

            # 添付局面が後手番のケース
            if self.move_number % 2 == 0:
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

        # 局面図
        # ------

        # 現在の盤面からのSFEN表示
        if from_present:
            squares = self._squares 

        # 初期盤面からのSFEN表示
        else:
            squares = self._squares_at_init


        # 添付局面図の手番
        # ---------------
        next_turn = self.get_next_turn()


        # 路ロックされている添付局面図の路の符号
        # -----------------------------------
        #
        #   筋、段の順
        #

        # 現在の盤面から
        if from_present:
            way_locks = self._way_locks

        # 初期盤面から
        else:
            way_locks = self._way_locks_at_init


        # 添付局面図は何手目のものか
        # ------------------------

        # 現在の盤面からのSFEN表示
        if from_present:
            move_number = self.move_number

        # 初期盤面からのSFEN表示
        else:
            move_number = 1


        # 添付局面図からの指し手
        # ---------------------
        move_u_list = []

        # 現在の盤面からのSFEN表示
        if from_present:
            pass

        # 初期盤面からのSFEN表示
        else:
            # 対局棋譜
            for game_record_item in self._board_editing_history.game_items:
                move_u_list.append(game_record_item.move.to_code())


        return Sfen(
            from_present=from_present,
            squares=squares,
            next_turn=next_turn,
            way_locks=way_locks,
            move_number=move_number,
            move_u_list=move_u_list)


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
