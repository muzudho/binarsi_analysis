import re
import copy


# コミ
#
#   コミは囲碁で使われている。
#   先後の勝率を五分五分に調整するために、黒番か白番の不利な方に多めに点数を最初から持たせておくもの。
#   0.5 という端数を付けておくことで、引き分けになるのを防ぐ。
#   プレイヤーの強さを調整するためのハンディキャップとは異なる
#
BLACK_KOMI = 0.5
WHITE_KOMI = 0

# 石の色
#
#   盤のマスの状態を　石の色　と呼ぶことにする。
#   空欄、黒石、白石の３色がある。略記は C_
#
C_EMPTY = 0
C_BLACK = 1
C_WHITE = 2

# 盤面表示用文字列。SFENにも使用
_color_to_str = {
    0 : '.',
    1 : '1',
    2 : '0',
}

_str_to_color = {
    '.' : 0,
    '1' : 1,
    '0' : 2,
}

_color_to_binary = {
    1: 1,
    2: 0,
}

_bool_to_color = {
    True: C_BLACK,
    False: C_WHITE,
}

# 軸
EMPTY_AXIS = 0
FILE_AXIS = 1
RANK_AXIS = 2

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

_num_to_rank_str = {
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


class Colors():
    """石の色"""

    _opponent_turn = {
        C_EMPTY : C_EMPTY,
        C_BLACK : C_WHITE,
        C_WHITE : C_BLACK,
    }

    @classmethod
    def Opponent(clazz, color):
        """反対の色"""
        return clazz._opponent_turn[color]


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


    def __init__(self, swap_axes, axis_length, opponent_axis_length):
        """初期化"""
        self._swap_axes = swap_axes
        self._axis_length = axis_length
        self._opponent_axis_length = opponent_axis_length


    @property
    def swap_axes(self):
        """筋と段を入れ替える"""
        return self._swap_axes


    @property
    def axis_length(self):
        """路の長さ"""
        return self._axis_length


    @property
    def opponent_axis_length(self):
        """反対の路の長さ"""
        return self._opponent_axis_length


class Way():
    """路符号

    例： '1',  '2', '3', '4', '5', '6', '7', 'a', 'b', 'c', 'd', 'e', 'f'

    存在しない路の場合：
        '-'
    """


    _code_to_obj = None
    _to_human_presentable_text = None


    def __init__(self, axis_id, number):
        """初期化

        Parameters
        ----------
        axis_id : int
            軸Ｉｄ
            1: file
            2: rank
        """

        if axis_id not in (EMPTY_AXIS, FILE_AXIS, RANK_AXIS):
            raise ValueError(f"undefined axis  {axis_id=}")

        self._axis_id = axis_id
        self._number = number


    @property
    def is_empty(self):
        return self._axis_id == EMPTY_AXIS


    @property
    def is_file(self):
        return self._axis_id == FILE_AXIS


    @property
    def is_rank(self):
        return self._axis_id == RANK_AXIS


    @property
    def axis_id(self):
        return self._axis_id


    @property
    def number(self):

        if self.is_empty:
            raise ValueError("unsupported number. this is empty")

        return self._number


    @classmethod
    def code_to_obj(clazz, code):
        """生成

        Parameters
        ----------
        code : str
            '-'、 '1' ～ '7'、 'a' ～ 'f'
        """

        # フォーマットチェック
        result = re.match(r"^[-1234567abcdef]$", code)
        if result is None:
            raise ValueError(f"format error.  way_u:`{code}`")


        if clazz._code_to_obj is None:
            clazz._code_to_obj = {
                '-': Way(EMPTY_AXIS, -1),
                '1': Way(FILE_AXIS, 0),
                '2': Way(FILE_AXIS, 1),
                '3': Way(FILE_AXIS, 2),
                '4': Way(FILE_AXIS, 3),
                '5': Way(FILE_AXIS, 4),
                '6': Way(FILE_AXIS, 5),
                '7': Way(FILE_AXIS, 6),
                'a': Way(RANK_AXIS, 0),
                'b': Way(RANK_AXIS, 1),
                'c': Way(RANK_AXIS, 2),
                'd': Way(RANK_AXIS, 3),
                'e': Way(RANK_AXIS, 4),
                'f': Way(RANK_AXIS, 5),
            }


        if code in clazz._code_to_obj:
            return clazz._code_to_obj[code]

        raise ValueError(f"not found way.  code:{code}")


    @staticmethod
    def _to_code(axis_id, number):
        global _num_to_rank_str

        if axis_id == EMPTY_AXIS:
            return '-'
        
        if axis_id == FILE_AXIS:
            return str(number + 1)

        if axis_id == RANK_AXIS:
            return _num_to_rank_str[number]

        raise ValueError(f"{axis_id=}  {number=}")


    def to_code(self):
        """
        Returns
        -------
        '-' や '1' ～ '7'、 'a' ～ 'f' といった文字
        """
        return Way._to_code(self._axis_id, self._number)


    def to_human_presentable_text(self):

        if Way._to_human_presentable_text is None:
            Way._to_human_presentable_text = {
                '-': 'no way',
                '1': '1-file',
                '2': '2-file',
                '3': '3-file',
                '4': '4-file',
                '5': '5-file',
                '6': '6-file',
                '7': '7-file',
                'a': 'a-rank',
                'b': 'b-rank',
                'c': 'c-rank',
                'd': 'd-rank',
                'e': 'e-rank',
                'f': 'f-rank',
            }
        
        return Way._to_human_presentable_text[self.to_code()]


    def low_way(self, diff = 1):
        """１つ小さい方の路"""

        if self.is_empty:
            return '-'

        if self._number < diff:
            return Way.code_to_obj('-')
        
        # code_to_obj() を仲介させることで、インスタンスの増加のし過ぎを防ぐ
        return Way.code_to_obj(Way._to_code(self._axis_id, self._number - diff))


    def high_way(self, diff = 1):
        """１つ大きい方の路"""

        if self.is_empty:
            return '-'

        if self.is_file:
            if self._number < FILE_LEN - diff:
                # code_to_obj() を仲介させることで、インスタンスの増加のし過ぎを防ぐ
                return Way.code_to_obj(Way._to_code(self._axis_id, self._number + diff))

            return Way.code_to_obj('-')

        if self.is_rank:
            if self._number < RANK_LEN - diff:
                # code_to_obj() を仲介させることで、インスタンスの増加のし過ぎを防ぐ
                return Way.code_to_obj(Way._to_code(self._axis_id, self._number + diff))

            return Way.code_to_obj('-')

        raise ValueError(f"{self._axis_id=}")


    def absorb_axes(self):
        """筋と段のコードを共通化する仕掛け"""
        # 筋方向
        if self.is_file:
            return AxesAbsorber(
                swap_axes=False,
                axis_length=FILE_LEN,
                opponent_axis_length=RANK_LEN)
        
        # 段方向
        if self.is_rank:
            return AxesAbsorber(
                swap_axes=True,
                axis_length=RANK_LEN,
                opponent_axis_length=FILE_LEN)
        
        raise ValueError(f"unsupported axis_id  {self._axis_id=}  {self._number=}")


# 全ての種類の路を生成
_all_ways = []
for way_u in _way_characters:
    _all_ways.append(Way.code_to_obj(way_u))


class WaySegment():
    """路上の線分"""


    def __init__(self, begin, length):
        """初期化"""
        self._begin = begin
        self._length = length


    @property
    def begin(self):
        return self._begin


    @property
    def end(self):
        return self._begin + self._length


    @property
    def length(self):
        return self._length


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


    _human_presentable_text_1 = {
        'na' : 'NAND',
        'nH' : 'NOT High', # NOT on 2 file -> Put it in 1 file
        'nL' : 'NOT Low',
        'no' : 'NOR',
        'on' : 'One',
        's1' : 'Shift', # Shift the 1 file 1 bit to the forward
        's2' : 'Shift',
        's3' : 'shift',
        's4' : 'shift',
        's5' : 'shift',
        's6' : 'shift',
        'xn' : 'XNOR',
        'xo' : 'XOR',
        'ze' : 'Zero',
        'a' : 'AND',
        'c' : 'Cut',
        'e' : 'Edit',
        'n' : 'NOT',
        'o' : 'OR',
    }

    _human_presentable_text_2 = {
        'na' : '',
        'nH' : 'High',
        'nL' : 'Low',
        'no' : '',
        'on' : '',
        's1' : '1-bit', # Shift the 1 file 1 bit to the forward
        's2' : '2-bit',
        's3' : '3-bit',
        's4' : '4-bit',
        's5' : '5-bit',
        's6' : '6-bit',
        'xn' : '',
        'xo' : '',
        'ze' : '',
        'a' : '',
        'c' : '',
        'e' : '',
        'n' : '',
        'o' : '',
    }


    def to_human_presentable_text(self):
        """人間が読めるような指し手の名前"""
        return Operator._human_presentable_text[self.code]


    def unary_operate(self, stone):
        """単項演算する

        Parameters
        ----------
        stone : int
            石の種類
        """

        # ノット（単項演算子 New）
        if self._stem_u in ['nH', 'nL', 'n']:
            if stone == C_BLACK:
                return C_WHITE
            
            if stone == C_WHITE:
                return C_BLACK
            
            if stone == C_EMPTY:
                return C_EMPTY
        
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
            C_BLACK, C_WHITE のいずれかを返す
        """

        global _bool_to_color

        # 変数名を縮める
        l = left_operand
        r = right_operand
        stem_u = self._stem_u

        # ゼロ
        if stem_u == 'ze':
            # 常に白石を返す
            return C_WHITE
        
        # ノア
        if stem_u == 'no':
            return _bool_to_color[not(l == 1 or r == 1)]
        
        # エクソア
        if stem_u == 'xo':
            return _bool_to_color[(l ^ r) == 1]
        
        # ナンド
        if stem_u == 'na':
            return _bool_to_color[not(l == 1 and r == 1)]
        
        # アンド
        if stem_u == 'a':
            return _bool_to_color[l == 1 and r == 1]
        
        # エクスノア
        if stem_u == 'xn':
            return _bool_to_color[(l ^ r) != 1]
        
        # オア
        if stem_u == 'o':
            return _bool_to_color[l == 1 or r == 1]
        
        # ワン
        if stem_u == 'on':
            # 常に黒石を返す
            return C_BLACK

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
    
    対局の棋譜には使えないが、パスも用意しておく
        例： `pass`
        内部的には、 way を None にしたらパス扱いとする。盤面編集扱いになる。'&' や '#'、 '$' は付加できない
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


    @property
    def is_pass(self):
        """パスか？"""
        return self._way is None


    _re_move = re.compile(r"^(&)?([1234567abcdef])(na|nH|nL|no|on|s1|s2|s3|s4|s5|s6|xn|xo|ze|a|c|e|n|o)(#)?(\$[.01]+)?$")


    @classmethod
    def validate_code(clazz, code, no_panic=False):
        result = clazz._re_move.match(code)

        if not no_panic:
            if result is None:
                raise ValueError(f"format error.  move_u:`{code}`")

        return result is not None


    @classmethod
    def code_to_obj(clazz, code):

        # パス
        if code == 'pass':
            return Move(
                # 路
                way=None,
                # 演算子
                operator=None,
                # 路ロック解除フラグ
                is_way_unlock=None,
                # 石の並び
                option_stones=None,
                # 盤面編集フラグ
                when_edit=True)

        result = clazz._re_move.match(code)
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
        """SFEN形式での指し手コード"""

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


    def new_with_same(self, same_move_u):
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
            way_segment = board.get_stone_segment_on_way(way)

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

            move_u = f"{way.to_code()}s{way_segment.length-shift_bits}#"
            Move.validate_code(move_u)
            return Move.code_to_obj(move_u)


        # ノット・ニュー --Inverse--> カットザエッジ＃
        if op == 'n':
            move_u = f"{way.to_code()}c#"
            Move.validate_code(move_u)
            return Move.code_to_obj(move_u)


        # ノットＬ --Inverse--> エディット＃
        # ノットＨ --Inverse--> エディット＃
        if op in ['nL', 'nH']:
            # {路}e#${石}
            if stones_before_change == '':
                raise ValueError(f"stones error  {op=}  {move.option_stones=}  {stones_before_change=}")

            # stones_before_change と move.option_stones は別物なので要注意

            move_u = f"{way.to_code()}e#${stones_before_change}"
            Move.validate_code(move_u)
            return Move.code_to_obj(move_u)


        # 逆操作 アンド、オア、エクソア、ナンド、ノア、エクスノア、ゼロ、ワン
        if op in ['a', 'o', 'xo', 'na', 'no', 'xn', 'ze', 'on']:
            # stones_before_change と move.option_stones は別物なので要注意

            # New
            if stones_before_change == '':

                move_u = f"{way.to_code()}c#"
                Move.validate_code(move_u)
                return Move.code_to_obj(move_u)

            # Modify {路}e#${石}

            move_u = f"{way.to_code()}e#${stones_before_change}"
            Move.validate_code(move_u)
            return Move.code_to_obj(move_u)


        raise ValueError(f"undefined operator:{op}")


class Sfen():
    """SFEN形式文字列
    
    空欄： 数に置き換え
    黒石： x
    白石： o
    """


    def __init__(self, from_present, squares, next_turn, way_locks, clear_targets_list, moves_number, move_u_list):
        """初期化

        Parameters
        ----------
        clear_targets_list : list
            クリアーターゲット一覧
            盤面の情報しか要らないときなど、クリアーターゲットはナンが指定されるケースがある
        """

        # （初期局面からではなく）現局面のSFEN形式なら真
        self._from_present = from_present

        # 盤面
        self._squares = squares

        # 手番
        self._next_turn = next_turn

        # 添付局面図での路ロックのリスト
        self._way_locks = way_locks

        # クリアーターゲットをクリアした何手目が入っているリスト
        self._clear_targets_list = clear_targets_list

        # 何手目
        self._moves_number = moves_number

        # 指し手のリスト
        self._move_u_list = move_u_list

        # キャッシュ
        self._code_cached = None


    def get_color(self, sq):
        return self._squares[sq]


    def set_color(self, sq, value):
        self._squares[sq] = value


    def to_code(self, without_way_lock=False, without_clear_targets_list=False, without_moves_number=False):
        """コード

        Parameters
        ----------
        without_way_lock : bool
            SFEN に［路ロック一覧］を含まないようにするフラグです。
            同じ盤面をチェックしたいとき、［路ロック一覧］が異なるかは無視したいという要望があります
        without_clear_targets_list : bool
            SFEN に［クリアー済ターゲット一覧］を含まないようにするフラグです。
            同じ盤面をチェックしたいとき、［クリアー済ターゲット一覧］が異なるかは無視したいという要望があります
        without_moves_number : bool
            SFEN に［何手目］を含まないようにするフラグです。
            同じ盤面をチェックしたいとき、［何手目］が異なるかは無視したいという要望があります
        """
        global _way_characters

        if self._code_cached is None:

            buffer = []

            # [盤面]

            # usinewgame コマンドの直後に selfmatch をするとこの例外になる。暫定で position startpos まで打鍵してほしい
            if self._squares is None:
                raise ValueError(f"{self._squares=}")

            spaces = 0

            for rank in range(0, RANK_LEN):
                for file in range(0, FILE_LEN):
                    sq = Square.file_rank_to_sq(file, rank)
                    stone = self.get_color(sq)

                    if stone == C_EMPTY:
                        spaces += 1
                    else:
                        # 空白の数を Flush
                        if 0 < spaces:
                            buffer.append(str(spaces))
                            spaces = 0
                        
                        if stone == C_BLACK:
                            buffer.append('x')
                        elif stone == C_WHITE:
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
            if self._next_turn == C_BLACK:
                buffer.append(' b')
            elif self._next_turn == C_WHITE:
                buffer.append(' w')
            else:
                raise ValueError(f"undefined next turn  {self._next_turn=}")


            # ［添付図の路ロック一覧］
            if not without_way_lock:
                locked = False

                for way_code in _way_characters:
                    if self._way_locks[way_code]:

                        if not locked:
                            # ［手番］と［路ロック一覧］の区切りの空白
                            buffer.append(' ')

                        buffer.append(way_code)
                        locked = True

                if not locked:
                    buffer.append(' -')


            # ［添付図のクリアー済みターゲット一覧］
            if not without_clear_targets_list:
                # 全ての要素が -1 かどうか確認
                all_empty = True

                # ［路ロック一覧］と［クリアー済ターゲット一覧］の区切りの空白を先頭に付ける
                u_list = []
                for i in range(0, CLEAR_TARGETS_LEN):

                    # 盤面の情報しか要らないときなど、クリアーターゲットはナンが指定されるケースがある
                    # その場合は without_clear_targets_list フラグを偽にしてエラーを回避してほしい
                    move_number = self._clear_targets_list[i]

                    if move_number == -1:
                        u_list.append('')
                    else:
                        all_empty = False
                        u_list.append(str(move_number))

                if all_empty:
                    buffer.append(' -')
                else:
                    buffer.append(f" {'/'.join(u_list)}")


            # ［添付図は何手目か？］
            if not without_moves_number:
                buffer.append(f' {self._moves_number}')


            # ［添付図からの棋譜］
            if 0 < len(self._move_u_list):
                moves_u = ' '.join(self._move_u_list)
                buffer.append(f' moves {moves_u}')


            sfen_str = ''.join(buffer)

            # 平手初期局面なら startpos に置換
            result = re.match(r"^7/7/2o4/7/7/7 b - - 0(.*)$", sfen_str)
            if result:
                self._code_cached = f"startpos{result.group(1)}"            

            else:
                self._code_cached = f"sfen {sfen_str}"

        return self._code_cached


    def to_upside_down(self):
        """盤面を上下反転した SFEN オブジェクトを返す"""

        instance = copy.copy(self)

        # キャッシュ・クリアー
        instance._code_cached = None

        # 参照ではなく、コピーに変更する
        instance._squares = copy.copy(self._squares)

        for file in range(0, FILE_LEN):
            for rank in range(0, (RANK_LEN+1)//2):
                src_sq = Square.file_rank_to_sq(file, rank)
                dst_sq = Square.file_rank_to_sq(file, RANK_LEN-rank-1)

                temp = instance.get_color(dst_sq)
                instance.set_color(dst_sq, instance.get_color(src_sq))
                instance.set_color(src_sq, temp)

        return instance


    def to_flip_left_and_right(self):
        """盤面を左右反転した SFEN オブジェクトを返す"""

        instance = copy.copy(self)

        # キャッシュ・クリアー
        instance._code_cached = None

        # 参照ではなく、コピーに変更する
        instance._squares = copy.copy(self._squares)

        for rank in range(0, RANK_LEN):
            for file in range(0, (FILE_LEN+1)//2):
                src_sq = Square.file_rank_to_sq(file, rank)
                dst_sq = Square.file_rank_to_sq(FILE_LEN-file-1, rank)

                temp = instance.get_color(dst_sq)
                instance.set_color(dst_sq, instance.get_color(src_sq))
                instance.set_color(src_sq, temp)

        return instance


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


class LegalMoves():
    """合法手"""


    def __init__(self, board):
        self._items = []

        # 現局面の盤面編集用の手（合法手除く）
        self._items_for_edit = []

        # 指してみると結果が同じになる指し手は、印をつけたい
        #
        # 左右反転、上下反転で同形のものも弾きたい。
        # 縦横比が異なるので、９０°回転は対象外とする。
        # 上下左右反転の形を作る操作は、対局中にはないはずなので対象外とする
        #
        # 結果が同じになる指し手を除外した指し手のリスト
        self._distinct_items = []

        # 一手指す前に、現局面が載っている sfen を取得しておく
        #
        #   例： 7/7/2o4/2x4/7/7 b - - 1
        #
        #   ここで、末尾の［何手目か？］は必ず変わってしまうので、それは省いておく
        #
        sub_sfen_1_before_push = board.as_sfen(from_present=True)
        sub_sfen_2_before_push = sub_sfen_1_before_push.to_upside_down()
        sub_sfen_3_before_push = sub_sfen_1_before_push.to_flip_left_and_right()

        # 現局面で指す前の盤面の部分SFEN文字列
        self._sub_sfen_u_before_push_normal = sub_sfen_1_before_push.to_code(without_way_lock=True, without_clear_targets_list=True, without_moves_number=True)

        # 現局面で指す前の盤面の部分SFEN文字列（上下反転）
        self._sub_sfen_u_before_push_upside_down = sub_sfen_2_before_push.to_code(without_way_lock=True, without_clear_targets_list=True, without_moves_number=True)

        # 現局面で指す前の盤面の部分SFEN文字列（左右反転）
        self._sub_sfen_u_before_push_flip_left_and_right = sub_sfen_3_before_push.to_code(without_way_lock=True, without_clear_targets_list=True, without_moves_number=True)

        #print(f"[LegalMoves > __init__] {self._sub_sfen_u_before_push_normal=}")
        #print(f"[LegalMoves > __init__] {self._sub_sfen_u_before_push_upside_down=}")
        #print(f"[LegalMoves > __init__] {self._sub_sfen_u_before_push_flip_left_and_right=}")

        self._sfen_memory_dict = {}

        # 現局面と同じになる指し手も省きたいので、内部的に pass として追加している
        self._sfen_memory_dict[self._sub_sfen_u_before_push_normal] = 'pass'
        self._sfen_memory_dict[self._sub_sfen_u_before_push_upside_down] = 'pass'
        self._sfen_memory_dict[self._sub_sfen_u_before_push_flip_left_and_right] = 'pass'


    @property
    def items(self):
        return self._items


    @property
    def items_for_edit(self):
        """盤面編集用の手（合法手除く）"""
        return self._items_for_edit


    @property
    def distinct_items(self):
        """結果が同じになる指し手を除外した指し手のリスト"""
        return self._distinct_items


    def append(self, board, move, for_edit=False):
        """指し手の追加

        Parameters
        ----------
        board : Board
            盤。一手指した結果を事前に調べるために使う
        move : Move
            指し手
        for_edit : bool
            盤面編集用
        """

        if for_edit:
            self._items_for_edit.append(move)

        else:
            # TODO とりあえず、逆操作が実装されている演算だけ調べる
            # １～６ビットシフト、ノット、ノットＬ、ノットＨ、アンド、オア、エクソア、ナンド、ノア、エクスノア、ゼロ、ワン
            if move.operator.code in ['s1', 's2', 's3', 's4', 's5', 's6', 'n', 'nH', 'nL', 'a', 'o', 'xo', 'na', 'no', 'xn', 'ze', 'on']:

                # DO 一手指す
                #print(f"[LegalMoves > append] 一手指す  {move.to_code()=}  \n{board.as_str()}")
                board.push_usi(move.to_code())  # 指し手生成中では、クリアーターゲットは更新しません

                # DO 一般的に長さが短い方の形式の SFEN を記憶
                #
                #   例： 7/7/2x4/2o4/7/7 b 3 2
                #
                #   ここで、末尾の［何手目か？］は必ず変わってしまうので、それは省いておく
                #
                sub_sfen_after_push_u = board.as_sfen(from_present=True).to_code(without_way_lock=True, without_clear_targets_list=True, without_moves_number=True)
                #print(f"[LegalMoves > append] 一般的に長さが短い方の形式の SFEN を記憶  {sub_sfen_after_push_u=}")

                # DO 既に記憶している SFEN と重複すれば、演算した結果が同じだ。重複を記憶しておく
                if sub_sfen_after_push_u in self._sfen_memory_dict.keys():
                    same_move_u = self._sfen_memory_dict[sub_sfen_after_push_u]
                    #print(f"[LegalMoves > append] 既に記憶している SFEN と重複した。演算した結果が同じだ。重複を記憶して差し替える  {same_move_u=}  {sub_sfen_after_push_u=}")

                    # 差し替え
                    move = move.new_with_same(same_move_u)


                # DO 重複していなければ、一時記憶する
                #
                #   例： 7/7/2x4/2o4/7/7 b 3 2
                #
                #   ここで、末尾の［何手目か？］は必ず変わってしまうので、スプリットして省いておく
                #
                else:
                    self._distinct_items.append(move)

                    move_u = move.to_code()
                    #print(f"[LegalMoves > append] 重複していないので、一時記憶する  {move_u=}  {sub_sfen_after_push_u=}")
                    self._sfen_memory_dict[sub_sfen_after_push_u] = move_u

                # DO 一手戻す
                #print(f"[LegalMoves > append] 一手戻す")
                board.pop() # 指し手生成中では、クリアーターゲットは更新しません
                #print(f"[LegalMoves > append] 一手戻した  {board.as_str()}")

                # DEBUG 一手戻した後に、現局面が載っている sfen を取得する
                rollbacked_sfen_u = board.as_sfen(from_present=True).to_code(without_way_lock=True, without_clear_targets_list=True, without_moves_number=True)
                #
                #   例： 7/7/2o4/2x4/7/7 b - 1
                #
                #   ここで、末尾の［何手目か？］は必ず変わってしまうので、それは省いておく
                #

                # DEBUG 巻き戻せていなければ例外を投げる
                if self._sub_sfen_u_before_push_normal != rollbacked_sfen_u:
                    raise ValueError(f"undo error  {self._sub_sfen_u_before_push_normal=}  {rollbacked_sfen_u=}")


            # move は差し替えしたり、しなかったりされている
            self._items.append(move)


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

        global BLCK_KOMI, WHITE_KOMI

        # 初期局面の各マス
        #
        #   SFENで初期局面を出力するためのもの。未設定のときナン
        #
        self._squares_at_init = None
        self._black_count_with_komi_at_init = None
        self._white_count_with_komi_at_init = None

        # 初期局面での手数
        #
        #   途中局面から開始したのでもなければ、手数は 0 で始まります
        #
        self._moves_number_at_init = 0

        # 初期局面での手番
        #
        #   平手初期局面の手番（Next Turn）、つまり先手は必ず黒番（将棋と違って上手、下手が無いので）。
        #   ただし、途中局面は自由に設定できるので、白番から始めるように変更したいときがある
        #
        self._next_turn_at_init = C_BLACK

        # 現局面の各マス
        self._squares = [C_EMPTY] * BOARD_AREA
        self._black_count_with_komi = BLACK_KOMI  # 予めコミを持たせる
        self._white_count_with_komi = WHITE_KOMI

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


    @property
    def black_count_with_komi(self):
        return self._black_count_with_komi


    @property
    def white_count_with_komi(self):
        return self._white_count_with_komi


    def get_color(self, sq):
        """マス上の石の色を取得"""
        return self._squares[sq]


    def set_color(self, sq, value):
        """マス上の石の色を設定"""

        # 盤上から消える石
        old_color = self._squares[sq]

        if old_color == C_BLACK:
            self._black_count_with_komi -= 1
        elif old_color == C_WHITE:
            self._white_count_with_komi -= 1

        # 盤上に増える石
        self._squares[sq] = value

        if value == C_BLACK:
            self._black_count_with_komi += 1
        elif value == C_WHITE:
            self._white_count_with_komi += 1


    @property
    def moves_number_at_init(self):
        """初期局面での手数
        
        途中局面から開始したのでもなければ、手数は 0 で始まります
        """        
        return self._moves_number_at_init


    @property
    def board_editing_history(self):
        """盤面編集履歴（対局棋譜のスーパーセット）

        history は時間方向に長い
        """
        return self._board_editing_history


    @property
    def moves_number(self):
        """指し手が何手目か（盤面編集操作除く）"""
        return self._moves_number_at_init + len(self._board_editing_history.game_items)


    def update_squares_at_init(self):
        """初期局面を記憶（SFENで初期局面を出力したいときのためのもの）"""
        if self._squares_at_init is None:
            self._squares_at_init = list(self._squares)
            self._black_count_with_komi_at_init = self._black_count_with_komi
            self._white_count_with_komi_at_init = self._white_count_with_komi


    def clear(self):
        """盤をクリアーする"""
        self.subinit()


    def reset(self):
        """平手初期局面に戻す"""
        self.subinit()

        # 石の初期配置
        self.set_color(Square.code_to_sq_obj('3c').as_num, C_WHITE)


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

            例： `7/7/2o4/7/7/7 b - - 0`

                    1 2 3 4 5 6 7
                  +---------------+
                a |               |
                b |               |
                c |     0         |
                d |               |
                e |               |
                f |               |
                  +---------------+

            例： `xooooxo/xooxxxo/ooxxooo/xooxxox/xoxxxxx/ooxoooo b 1234567abcdef 1/2//3/4/ 0`

                    # # # # # # #
                  +---------------+
                # | 1 0 0 0 0 1 0 |
                # | 1 0 0 1 1 1 0 |
                # | 0 0 1 1 0 0 0 |
                # | 1 0 0 1 1 0 1 |
                # | 1 0 1 1 1 1 1 |
                # | 0 0 1 0 0 0 0 |
                  +---------------+
        
        Returns
        -------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
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
                        self.set_color(sq, C_BLACK)
                    else:
                        self.set_color(sq, C_WHITE)

                    # フォワード
                    cursor.file_forward()

                elif ch == '/':
                    pass

                else:
                    raise ValueError(f"undefined sfen character on board:  {ch=}  {sfen_u=}")

        # 添付盤面での手番
        # ---------------
        if parts[1] == 'b':
            self._next_turn_at_init = C_BLACK
        elif parts[1] == 'w':
            self._next_turn_at_init = C_WHITE
        else:
            raise ValueError(f"undefined sfen character on turn:  {ch=}  {sfen_u=}")

        # 添付盤面での路ロック一覧
        # ----------------------
        if parts[2] != '-':
            for way_u in parts[2]:
                if way_u in _way_characters:
                    self.set_way_lock_by_code(way_u, True, is_it_init=True)

                else:
                    raise ValueError(f"undefined sfen character on locks:  {way_u=}  {sfen_u=}")

        # 添付盤面でのクリアー済ターゲット一覧
        # ---------------------------------
        clear_targets_list = [-1] * CLEAR_TARGETS_LEN

        if parts[3] != '-':
            # 勝利条件をクリアーしたのが何手目か、６つの要素がスラッシュ区切りで入っている。クリアーしていなければ空文字列
            tokens = parts[3].split('/')

            for i in range(0, CLEAR_TARGETS_LEN):
                token = tokens[i]

                if 0 < len(token):
                    clear_targets_list[i] = int(token)

        searched_clear_targets = SearchedClearTargets(
            clear_targets_list=clear_targets_list)

        # 手数の解析
        # ---------
        self._moves_number_at_init = int(parts[4])


        return searched_clear_targets


    def exists_stone_on_way(self, way):
        """指定の路に石が置いてあるか？
        
        get_stone_segment_on_way() よりは高速と思います

        Parameters
        ----------
        way : Way
            路オブジェクト
        """

        if way.is_empty:
            return False

        # 筋（段）方向両用
        axes_absorber = way.absorb_axes()

        for i in range(0, axes_absorber.opponent_axis_length):
            sq = Square.file_rank_to_sq(way.number, i, swap=axes_absorber.swap_axes)
            stone = self.get_color(sq)

            if stone != C_EMPTY:
                return True
            
        return False


    def get_stone_segment_on_way(self, way):
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

        上図の c 段を指定すると、 begin:2, length:4 のような数を返す

        `-` 路を指定すると、 begin:0, length:0 のような数を返す
        """

        if way.is_empty:
            return WaySegment(0, 0)


        # 筋（段）方向両用
        axes_absorber = way.absorb_axes()

        # 入力路から、出力路へ、評価値を出力
        #
        #   必要な変数を調べる：
        #       最初のマージン（空欄）は無視する
        #       最初の石の位置を覚える。変数名を begin とする
        #       連続する石の長さを覚える。変数名を length とする
        #       最後のマージン（空欄）は無視する
        source_stones = [C_EMPTY] * axes_absorber.opponent_axis_length
        state = 0
        begin = 0
        length = 0
        for i in range(0, axes_absorber.opponent_axis_length):
            src_sq = Square.file_rank_to_sq(way.number, i, swap=axes_absorber.swap_axes)
            stone = self.get_color(src_sq)
            source_stones[i] = stone

            if state == 0:
                # 石を見っけ
                if stone != C_EMPTY:
                    begin = i
                    state = 1

            elif state == 1:
                # 石が切れた
                if stone == C_EMPTY:
                    length = i - begin
                    state = 2

        if state == 1:
            length = axes_absorber.opponent_axis_length - begin
            state = 2

        return WaySegment(begin, length)


    def get_colors_on_way(self, target_way, way_segment):
        """指定の路の、指定のセグメントの、石または空欄の並びを取得します
        
        Parameters
        ----------
        target_way : Way
            対象路
        way_segment : WaySegment
            路上の線分
        
        Returns
        -------
        colors : list
            石の並び
        """

        colors = []

        # 筋（段）方向両用
        axes_absorber = target_way.absorb_axes()

        for i in range(way_segment.begin, way_segment.end):
            colors.append(self.get_color(Square.file_rank_to_sq(target_way.number, i, swap=axes_absorber.swap_axes)))

        return colors


    def set_colors_on_way(self, target_way, stones_str):
        """指定の路に、指定の石の列を上書きします"""

        stones_before_change = ''
        stones_str_len = len(stones_str)

        # 筋（段）方向両用
        axes_absorber = target_way.absorb_axes()

        # 幅いっぱい使う
        if stones_str_len == axes_absorber.opponent_axis_length:
            way_segment = WaySegment(0, axes_absorber.opponent_axis_length)

        # 置いてある石の位置に合わせる
        else:
            way_segment = self.get_stone_segment_on_way(target_way)

            if way_segment.length != stones_str_len:
                raise ValueError(f"length error  {way_segment.length=}  {stones_str_len=}")


        for i in range(way_segment.begin, way_segment.end):

            dst_sq = Square.file_rank_to_sq(target_way.number, i, swap=axes_absorber.swap_axes)
            old_stone = self.get_color(dst_sq)

            if old_stone != C_EMPTY:
                stones_before_change += _color_to_str[old_stone]

            self.set_color(
                sq=dst_sq,
                value=_str_to_color[stones_str[i - way_segment.begin]])

        return stones_before_change


    def binary_operate_on_way(self, move):
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

        global _color_to_binary

        stones_before_change = ''

        (input_way_1, input_way_2, error_reason) = self.get_input_ways_by_binary_operation(move.way)

        if input_way_1.is_empty or input_way_2.is_empty:

            # DEBUG 盤面出力
            print(f"[binary_operate_on_way] error  {error_reason=}  {move.to_code()=}  {input_way_1.to_code()=}  {input_way_2.to_code()=}  {self._way_locks=}")
            print(self.as_str())

            raise ValueError(f"out of bounds  {move.to_code()=}  {input_way_1.to_code()=}  {input_way_2.to_code()=}  {self._way_locks=}")


        # 対象の路に石が置いてあれば上書きフラグをOn、そうでなければOff
        overwrite = self.exists_stone_on_way(move.way)

        # 筋（段）方向両用
        axes_absorber = move.way.absorb_axes()

        for i in range(0, axes_absorber.opponent_axis_length):

            dst_sq = Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)
            old_stone = self.get_color(dst_sq)

            if overwrite and old_stone != C_EMPTY:
                stones_before_change += _color_to_str[old_stone]

            input_stone_at_first = self.get_color(Square.file_rank_to_sq(input_way_1.number, i, swap=axes_absorber.swap_axes))
            input_stone_at_second = self.get_color(Square.file_rank_to_sq(input_way_2.number, i, swap=axes_absorber.swap_axes))

            #print(f"{move.way.axis_id=}  {i=}  {input_way_1.number=}  {input_way_2.number=}  {input_stone_at_first=}  {input_stone_at_second=}  {dst_sq=}")

            if input_stone_at_first == C_EMPTY or input_stone_at_second == C_EMPTY:
                continue

            self.set_color(
                sq=dst_sq,
                value=move.operator.binary_operate(
                    left_operand=_color_to_binary[input_stone_at_first],
                    right_operand=_color_to_binary[input_stone_at_second]))

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


    def get_src_way_by_unary_operation(self, way):
        """単項演算の入力路を取得"""

        # 左（上）端なら、右（下）側確定
        if way.number == 0:
            return way.high_way()

        # 右（下）端なら、左（上）側確定
        if way.number == FILE_LEN - 1:
            return way.low_way()
        
        # 左か右（上か下）で、石が置いてある路が入力路
        low_way = way.low_way()
        if self.exists_stone_on_way(low_way):
            return low_way

        high_way = way.high_way()
        if self.exists_stone_on_way(high_way):
            return high_way

        raise ValueError("not operator invalid operation")


    # TODO イリーガルムーブを弾くために、バリデーションができたい
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
        Move.validate_code(move_u)
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
                way_segment = self.get_stone_segment_on_way(move.way)

                # 盤面更新 --> 空欄で上書き
                for src_dst_i in range(way_segment.begin, way_segment.end):
                    src_dst_sq = Square.file_rank_to_sq(move.way.number, src_dst_i, swap=axes_absorber.swap_axes)
                    stone = self.get_color(src_dst_sq)
                    if stone != C_EMPTY:
                        stones_before_change += _color_to_str[stone]
                        self.set_color(src_dst_sq, C_EMPTY)

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:

                # # DEBUG ブレークポイントを置いてもう一回
                # print(f"[push_usi]  {move.to_code()=}  {move.way.to_code()=}  {move.operator.code=}")
                # print(self.as_str())
                # self.exists_stone_on_way(move.way)

                # 対局中に c演算を使ってはいけないことに注意
                # 盤面編集中であってもここを通るのはおかしい
                raise ValueError(f"c演算では、石の置いてない対象路を指定してはいけません  {move.to_code()=}  {move.way.to_code()=}  {move.operator.code=}")


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
            stones_before_change = self.set_colors_on_way(
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

                source_stones = [C_EMPTY] * axes_absorber.opponent_axis_length
                for i in range(0, axes_absorber.opponent_axis_length):
                    src_sq = Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes)
                    stone = self.get_color(src_sq)
                    source_stones[i] = stone

                # (1)
                way_segment = self.get_stone_segment_on_way(move.way)

                # (2)
                for i in range(way_segment.begin, way_segment.end):
                    dst_sq = Square.file_rank_to_sq(
                        file=move.way.number,
                        rank=(i - way_segment.begin + bit_shift) % way_segment.length + way_segment.begin,
                        swap=axes_absorber.swap_axes)

                    self.set_color(dst_sq, source_stones[i])

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:
                raise ValueError(f"s演算では、石の置いてない対象路を指定してはいけません  {move.to_code()=}")


        # ノット（単項演算子）
        #
        #   ノット演算では、対象路に石が置いてあるケースは非対応です
        #   対象の路に石が置いてないものとします
        #
        if op == 'n':
            # 筋（段）方向両用
            axes_absorber = move.way.absorb_axes()

            # 入力路から、出力路へ、評価値を出力
            for i in range(0, axes_absorber.opponent_axis_length):
                src_stone = self.get_color(Square.file_rank_to_sq(
                    self.get_src_way_by_unary_operation(move.way).number, i, swap=axes_absorber.swap_axes))
                self.set_color(
                    sq=Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes),
                    value=move.operator.unary_operate(src_stone))

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
                    src_stone = self.get_color(Square.file_rank_to_sq(
                        self.get_src_way_by_unary_operation(move.way).number, i, swap=axes_absorber.swap_axes))

                    if src_stone != C_EMPTY:
                        dst_stone = self.get_color(Square.file_rank_to_sq(
                            move.way.number, i, swap=axes_absorber.swap_axes))

                        stones_before_change += _color_to_str[dst_stone]
                        self.set_color(
                            sq=Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes),
                            value=move.operator.unary_operate(src_stone))

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:
                raise ValueError(f"nL演算では、石の置いてない対象路を指定してはいけません  {move.to_code()=}")


        # ノット（単項演算子 Reverse）路上の大きい方
        if op == 'nH':

            # 対象の路に石が置いてある
            if self.exists_stone_on_way(move.way):

                # 筋（段）方向両用
                axes_absorber = move.way.absorb_axes()

                # 入力路から、出力路へ、評価値を出力
                for i in range(0, axes_absorber.opponent_axis_length):
                    src_stone = self.get_color(Square.file_rank_to_sq(
                        self.get_src_way_by_unary_operation(move.way).number, i, swap=axes_absorber.swap_axes))

                    if src_stone != C_EMPTY:
                        dst_stone = self.get_color(Square.file_rank_to_sq(
                            move.way.number, i, swap=axes_absorber.swap_axes))

                        stones_before_change += _color_to_str[dst_stone]
                        self.set_color(
                            sq=Square.file_rank_to_sq(move.way.number, i, swap=axes_absorber.swap_axes),
                            value=move.operator.unary_operate(src_stone))

                # 改変操作では
                #   開錠指定があれば開錠、なければ 路ロックを掛ける
                self.on_exit_push_usi(move, not move.is_way_unlock, stones_before_change)
                return

            # 対象の路に石が置いてない
            else:
                raise ValueError(f"nH演算では、石の置いてない対象路を指定してはいけません  {move.to_code()=}")


        # アンド, オア, ゼロ, ノア, エクソア, ナンド, エクスノア, ワン
        if op in ['a', 'o', 'ze', 'no', 'xo', 'na', 'xn', 'on']:

            # 盤面更新前
            exists_stone_on_way_before_change = self.exists_stone_on_way(move.way)

            # 盤面更新
            stones_before_change = self.binary_operate_on_way(move)

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


        raise ValueError(f"undefined operator code.  {op=}  {move.to_code()=}")


    def get_edge_way_from_adjacent_space(self, space_way):
        """石のない路の隣の石のある路を返す

        Parameters
        ----------
        space_way : Way
            石のない路。ただし、その隣には石があるものとする
        """

        # 筋（段）方向両用
        adjacent_way = space_way.low_way()
        way_segment = self.get_stone_segment_on_way(adjacent_way)
        if 0 < way_segment.length:
            return adjacent_way

        adjacent_way = space_way.high_way()
        way_segment = self.get_stone_segment_on_way(adjacent_way)
        if 0 < way_segment.length:
            return adjacent_way

        return None


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

        #print(f"[pop] 盤面編集として、逆操作を実行  {latest_edit.move.to_code()=}  {inverse_move.to_code()=}  {inverse_move_for_edit.is_way_unlock=}  {inverse_move_for_edit_u=}")
        self.push_usi(inverse_move_for_edit_u)

        # さっきの逆操作を履歴から除去
        popped_item = self._board_editing_history.pop()
        #print(f"[pop] 逆操作を履歴から除去  {popped_item.move.to_code()=}")

        # 最後の指し手も履歴から除去
        popped_item = self._board_editing_history.pop()
        #print(f"[pop] 最後の指し手も履歴から除去  {popped_item.move.to_code()=}")


    def is_nyugyoku(self):
        """無視。ビナーシに入玉はありません"""
        pass


    def is_check(self):
        """王手を食らっているか？"""
        raise ValueError("このゲームに王手はありません")


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
            dst_file_way = Way(FILE_AXIS, dst_file)

            # 縦連の場所を調べる
            way_segment = self.get_stone_segment_on_way(dst_file_way)

            # 石が置いてる段
            if 0 < way_segment.length:
                top_rank = way_segment.begin
                bottom_rank = way_segment.end - 1
                break

        
        if top_rank is None:
            return (False, None, None, None, None)


        # とりあえず各段について
        for dst_rank in range(0, RANK_LEN):
            dst_rank_way = Way(RANK_AXIS, dst_rank)

            # 横連の場所を調べる
            way_segment = self.get_stone_segment_on_way(dst_rank_way)

            # 石が置いてる筋
            if 0 < way_segment.length:
                left_file = way_segment.begin
                right_file = way_segment.end - 1
                break


        return (True, left_file, right_file, top_rank, bottom_rank)


    def get_input_ways_by_binary_operation(self, target_way):
        """二項演算するときの入力路２つ
        
        Returns
        -------
        input_way_1 : Way
            路１
        input_way_2 : Way
            路２
        reason : str
            説明
        """


        # 二項演算が禁止のケース
        #   - 路を指定していない
        if target_way.is_empty:
            return (Way.code_to_obj('-'), Way.code_to_obj('-'), 'no way')


        #   - 対象路にロックが掛かっている
        if self._way_locks[target_way.to_code()]:
            return (Way.code_to_obj('-'), Way.code_to_obj('-'), 'way locked')


        # 筋（段）方向両用
        axes_absorber = target_way.absorb_axes()


        # 対称路に石が置いてあるなら
        if self.exists_stone_on_way(target_way):

            # 盤の端ならエラー
            if target_way.number in [0, axes_absorber.axis_length - 1]:
                return (Way.code_to_obj('-'), Way.code_to_obj('-'), f'there was stone on target way. but should not be at both end edge.  {target_way.to_code()=}  {target_way.number=}  {axes_absorber.axis_length=}')

            # ロウ、ハイの両方に石が置いてある必要がある
            low_way = target_way.low_way()
            high_way = target_way.high_way()

            if self.exists_stone_on_way(low_way) and self.exists_stone_on_way(high_way):
                return (low_way, high_way, '')

            return (Way.code_to_obj('-'), Way.code_to_obj('-'), 'there was stone on target way. but should be stones at low and high')

        # 対象路に石が置いてないなら
        # ------------------------

        # ロウの方に２つ続けて石が置いているか？
        if 1 < target_way.number:
            first_way = target_way.low_way()
            second_way = target_way.low_way(diff=2)
            if self.exists_stone_on_way(first_way) and self.exists_stone_on_way(second_way):
                return (first_way, second_way, '')
        
        # ハイの方に２つ続けて石が置いているか？
        if target_way.number < axes_absorber.opponent_axis_length - 2:
            first_way = target_way.high_way()
            second_way = target_way.high_way(diff=2)
            if self.exists_stone_on_way(first_way) and self.exists_stone_on_way(second_way):
                return (first_way, second_way, '')

        return (Way.code_to_obj('-'), Way.code_to_obj('-'), 'there is not 2 stones')


    def is_gameover(self, searched_gameover):
        """終局しているか？
        
        cshogi では is_gameover() は board のメソッドあり、引数はありませんが、ビナーシでは引数を受け取ります

        Parameters
        ----------
        searched_gameover : SearchedGameover
            ゲームオーバー探索
        """

        return searched_gameover.is_black_win or searched_gameover.is_white_win


    def as_str(self, searched_clear_targets=None):
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
        
        Parameters
        ----------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
            指し手生成中はナン
        """
        
        global _color_to_str

        # １行目表示
        # ---------
        edits_num = len(self._board_editing_history.items)
        if self.moves_number != edits_num:
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
        if searched_clear_targets is None:
            clear_targets_list_str = ''

        else:
            clear_targets_u_list = []
            if searched_clear_targets.clear_targets_list[0] != -1:
                clear_targets_u_list.append('b3')
            if searched_clear_targets.clear_targets_list[1] != -1:
                clear_targets_u_list.append('b4')
            if searched_clear_targets.clear_targets_list[2] != -1:
                clear_targets_u_list.append('b5')
            if searched_clear_targets.clear_targets_list[3] != -1:
                clear_targets_u_list.append('w3')
            if searched_clear_targets.clear_targets_list[4] != -1:
                clear_targets_u_list.append('w4')
            if searched_clear_targets.clear_targets_list[5] != -1:
                clear_targets_u_list.append('w5')

            if 0 < len(clear_targets_u_list):
                clear_targets_list_str = f" | {' '.join(clear_targets_u_list)}"
            else:
                clear_targets_list_str = ''


        # 次の手番
        # NOTE 終局理由を取得するには、一手指していないと分からない。盤を表示するだけなのに一手指すのは激重すぎる。したがって終局理由は盤表示には含めないことにする
        next_turn = self.get_next_turn()
        if next_turn == C_BLACK:
            next_turn_str = 'next black'
        elif next_turn == C_WHITE:
            next_turn_str = 'next white'
        else:
            raise ValueError(f"unsupported turn  {next_turn}")


        print(f"[{self.moves_number:2} moves {edits_num_str}| {latest_move_str}{clear_targets_list_str} | {next_turn_str}]")


        # 盤表示
        # ------

        # 数値を表示用文字列(Str)に変更
        s = [' '] * BOARD_AREA
        for sq in range(0, BOARD_AREA):
            s[sq] = _color_to_str[self.get_color(sq)]

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


    def get_next_turn(self):
        """手番を取得

        Parameters
        ----------
        from_present : bool
            現局面からのSFENにしたいなら真。初期局面からのSFENにしたいなら偽
        """

        # 添付局面が先手番のケース
        if self._next_turn_at_init == C_BLACK:

            # 添付局面が偶数のケース
            if self._moves_number_at_init % 2 == 0:
                # 現在の［手目］が偶数のケース
                if self.moves_number % 2 == 0:
                    return C_BLACK
                
                # 現在の［手目］が奇数のケース
                return C_WHITE
                
            # 添付局面が奇数のケース
            # --------------------

            # 現在の［手目］が偶数のケース
            if self.moves_number % 2 == 0:
                return C_WHITE
            
            # 現在の［手目］が奇数のケース
            return C_BLACK

        # 添付局面が後手番のケース
        # ----------------------

        # 添付局面が偶数のケース
        if self._moves_number_at_init % 2 == 0:
            # 現在の［手目］が偶数のケース
            if self.moves_number % 2 == 0:
                return C_WHITE

            # 現在の［手目］が奇数のケース
            return C_BLACK

        # 添付局面が奇数のケース
        # --------------------

        # 現在の［手目］が偶数のケース
        if self.moves_number % 2 == 0:
            return C_BLACK

        # 現在の［手目］が奇数のケース
        return C_WHITE


    def as_sfen(self, searched_clear_targets=None, from_present=False):
        """（拡張仕様）盤のSFEN形式

        Parameters
        ----------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
            盤面の情報しか要らないときなど、クリアーターゲットはナンが指定されるケースがある
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
            moves_number = self.moves_number

        # 初期盤面からのSFEN表示
        else:
            moves_number = 0


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


        if searched_clear_targets is None:
            clear_targets_list = None
        else:
            clear_targets_list = searched_clear_targets.clear_targets_list


        return Sfen(
            from_present=from_present,
            squares=squares,
            next_turn=next_turn,
            way_locks=way_locks,
            # 盤面の情報しか要らないときなど、クリアーターゲットはナンが指定されるケースがある
            clear_targets_list=clear_targets_list,
            moves_number=moves_number,
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


class SearchedClearTargets():
    """クリアーターゲット探索"""


    def __init__(self, clear_targets_list):
        self._clear_targets_list = clear_targets_list


    @property
    def clear_targets_list(self):
        """勝利条件をクリアーしたのが何手目かの一覧"""
        return self._clear_targets_list


    @staticmethod
    def make_new_obj():
        return SearchedClearTargets(
            clear_targets_list=[-1] * CLEAR_TARGETS_LEN)


    @staticmethod
    def update_clear_target_b3(board, clear_targets_list):
        """クリアー条件　黒番１　横に３つ 1 が並んでいること
        
                 [b3]
              1 2 3 4 5 6 7  
            +---------------+
          a | 1 1 1 ^ ^ . . |
          b | ^ ^ ^ ^ ^ . . |
          c | ^ ^ ^ ^ ^ . . |
          d | ^ ^ ^ ^ ^ . . |
          e | ^ ^ ^ ^ ^ . . |
          f | ^ ^ ^ ^ ^ . . |
            +---------------+
        
        図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        """

        # 棒サイズ
        line_length = 3
        my_stone_color = C_BLACK
        is_not_hit = False  # 外側の file ループを続行

        for rank in range(0, RANK_LEN):
            #             0,        6

            for file in range(0, FILE_LEN-line_length+1):
                #             0,        7-          3+1
                #             0,       =5 

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file + i, rank)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    continue

                clear_targets_list[0] = board.moves_number
                return


    @staticmethod
    def update_clear_target_b4(board, clear_targets_list):
        """クリアー条件　黒番２　斜め（左右反転でも構わない）に４つ 1 が並んでいること
        
          Sinister Diagonal     Baroque Diagonal
                  [b4]
             1 2 3 4 5 6 7          1 2 3 4 5 6 7
           +---------------+      +---------------+
         a | 1 ^ ^ ^ . . . |    a | . . . 1 ^ ^ ^ |
         b | ^ 1 ^ ^ . . . |    b | . . 1 ^ ^ ^ ^ |
         c | ^ ^ 1 ^ . . . |    c | . 1 . ^ ^ ^ ^ |
         d | . . . 1 . . . |    d | 1 . . . . . . |
         e | . . . . . . . |    e | . . . . . . . |
         f | . . . . . . . |    f | . . . . . . . |
           +---------------+      +---------------+
        
        図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        
        """

        # 棒サイズ
        line_length = 4
        my_stone_color = C_BLACK
        is_not_hit = False  # 外側の file ループを続行

        # Sinister Diagonal
        for rank in range(0, RANK_LEN-line_length+1):
            #             0,        6-          4+1
            #             0,       =3

            for file in range(0, FILE_LEN-line_length+1):
                #             0,        7-          4+1
                #             0,       =4

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file + i, rank + i)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    continue

                clear_targets_list[1] = board.moves_number
                return

        # Baroque Diagonal
        for rank in range(0, RANK_LEN-(RANK_LEN-line_length)-1):
            #             0,        6-(       6-          4)-1
            #             0,       =3 
            for file in range(line_length-1, FILE_LEN):
                #                       4-1,        7
                #                      =3  ,        7

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file - i, rank + i)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    break

                clear_targets_list[1] = board.moves_number
                return


    @staticmethod
    def update_clear_target_b5(board, clear_targets_list):
        """クリアー条件　黒番３　縦に５つ 1 が並んでいること
        
                 [b5]
              1 2 3 4 5 6 7
            +---------------+
          a | 1 ^ ^ ^ ^ ^ ^ |
          b | 1 ^ ^ ^ ^ ^ ^ |
          c | 1 . . . . . . |
          d | 1 . . . . . . |
          e | 1 . . . . . . |
          f | . . . . . . . |
            +---------------+
        
        図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        
        """

        # 棒サイズ
        line_length = 5
        my_stone_color = C_BLACK
        is_not_hit = False  # 外側の file ループを続行

        for rank in range(0, RANK_LEN-line_length+1):
            #             0,        6-          5+1
            #             0,       =2

            for file in range(0, FILE_LEN):
                #             0,        7

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file, rank + i)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    continue

                clear_targets_list[2] = board.moves_number
                return


    @staticmethod
    def update_clear_target_w3(board, clear_targets_list):
        """クリアー条件　白番１　縦に３つ 0 が並んでいること

                 [w3]
              1 2 3 4 5 6 7
            +---------------+
          a | 0 ^ ^ ^ ^ ^ ^ |
          b | 0 ^ ^ ^ ^ ^ ^ |
          c | 0 ^ ^ ^ ^ ^ ^ |
          d | ^ ^ ^ ^ ^ ^ ^ |
          e | . . . . . . . |
          f | . . . . . . . |
            +---------------+
        
        図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        """

        # 棒サイズ
        line_length = 3
        my_stone_color = C_WHITE
        is_not_hit = False  # 外側の file ループを続行

        for rank in range(0, RANK_LEN-line_length+1):
            #             0,        6-          3+1
            #             0,       =4

            for file in range(0, FILE_LEN):
                #             0,        7

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file, rank + i)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    continue

                clear_targets_list[3] = board.moves_number
                return


    @staticmethod
    def update_clear_target_w4(board, clear_targets_list):
        """クリアー条件　白番２　斜め（左右反転でも構わない）に４つ 0 が並んでいること
        
          Sinister Diagonal     Baroque Diagonal
                  [w4]
             1 2 3 4 5 6 7          1 2 3 4 5 6 7
           +---------------+      +---------------+
         a | 0 ^ ^ ^ . . . |    a | . . . 0 ^ ^ ^ |
         b | ^ 0 ^ ^ . . . |    b | . . 0 ^ ^ ^ ^ |
         c | ^ ^ 0 ^ . . . |    c | . 0 . ^ ^ ^ ^ |
         d | . . . 0 . . . |    d | 0 . . . . . . |
         e | . . . . . . . |    e | . . . . . . . |
         f | . . . . . . . |    f | . . . . . . . |
           +---------------+      +---------------+
        
        図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        """

        # 棒サイズ
        line_length = 4
        my_stone_color = C_WHITE
        is_not_hit = False  # 外側の file ループを続行

        # Sinister Diagonal
        for rank in range(0, RANK_LEN-line_length+1):
            #             0,        6-          4+1
            #             0,       =3

            for file in range(0, FILE_LEN-line_length+1):
                #             0,        7-          4+1
                #             0,       =4

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file + i, rank + i)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    continue

                clear_targets_list[4] = board.moves_number
                return

        # Baroque Diagonal
        for rank in range(0, RANK_LEN-(RANK_LEN-line_length)-1):
            #             0,        6-(       6-          4)-1
            #             0,       =3

            for file in range(line_length-1, FILE_LEN):
                #                       4-1,        7
                #                      =3  ,        7

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file - i, rank + i)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    break

                clear_targets_list[4] = board.moves_number
                return


    @staticmethod
    def update_clear_target_w5(board, clear_targets_list):
        """クリアー条件　白番３　横に５つ 0 が並んでいること
        
                 [w5]
              1 2 3 4 5 6 7
            +---------------+
          a | 0 0 0 0 0 . . |
          b | ^ ^ ^ . . . . |
          c | ^ ^ ^ . . . . |
          d | ^ ^ ^ . . . . |
          e | ^ ^ ^ . . . . |
          f | ^ ^ ^ . . . . |
            +---------------+
        
        図中の ^ は、ループでスキャンする開始地点の範囲を表現している
        """

        # 棒サイズ
        line_length = 5
        my_stone_color = C_WHITE
        is_not_hit = False  # 外側の file ループを続行

        for rank in range(0, RANK_LEN):
            #             0,        6

            for file in range(0, FILE_LEN-line_length+1):
                #             0,        7-          5+1
                #             0,       =3

                for i in range(0, line_length):
                    if board.get_color(Square.file_rank_to_sq(file + i, rank)) != my_stone_color:
                        is_not_hit = True
                        break

                if is_not_hit:
                    is_not_hit = False
                    continue

                clear_targets_list[5] = board.moves_number
                return


    @staticmethod
    def update_clear_targets(board, clear_targets_list):
        """クリアーターゲット判定を更新
        
        先に generate_legal_moves() メソッドを呼び出すように働きます

        Parameters
        ----------
        clear_targets_list : list
            引き継ぐ（変更しません）
        """

        # NOTE 元のリストを変更しないように注意
        new_clear_targets_list = list(clear_targets_list)

        if new_clear_targets_list[0] == -1:
            SearchedClearTargets.update_clear_target_b3(board, new_clear_targets_list)

        if new_clear_targets_list[1] == -1:
            SearchedClearTargets.update_clear_target_b4(board, new_clear_targets_list)

        if new_clear_targets_list[2] == -1:
            SearchedClearTargets.update_clear_target_b5(board, new_clear_targets_list)

        if new_clear_targets_list[3] == -1:
            SearchedClearTargets.update_clear_target_w3(board, new_clear_targets_list)

        if new_clear_targets_list[4] == -1:
            SearchedClearTargets.update_clear_target_w4(board, new_clear_targets_list)

        if new_clear_targets_list[5] == -1:
            SearchedClearTargets.update_clear_target_w5(board, new_clear_targets_list)

        # TODO 投了しているケースに対応したい

        return SearchedClearTargets(
            clear_targets_list=new_clear_targets_list)


class SearchLegalMoves():
    """探索部
    
    cshogi では board が legal_moves を持っているが、ビナーシでは search が legal_moves を生成するという違いがある
    """


    @staticmethod
    def _append_binary_operation(board, legal_moves, operator_u, for_edit_mode=False):
        """
        Parameters
        ----------
        legal_moves : LegalMoves
            合法手一覧
        board : Board
            盤
        operator_u : str
            演算子コード
            例： 'o'
        for_edit_mode : bool
            盤面編集用
        """

        ## DEBUG ブレークポイントを付ける
        #if operator_u=='xo':
        #    pass

        # 全ての種類の路
        global _all_ways

        for way in _all_ways:
            axes_absorber = way.absorb_axes()

            # 石が置いてある路
            if board.exists_stone_on_way(way):

                # 路にロックが掛かっていたら Or の Reverse は禁止
                if board._way_locks[way.to_code()]:
                    continue

                ## DEBUG 表示抑制
                #if operator_u=='xo':
                #    print(f"[_append_binary_operation] modify  {way.number=}  {axes_absorber.axis_length=}  {way.low_way().to_code()=}  {way.high_way().to_code()=}")

                # ロウ、ハイの両方に石が置いてある必要がある
                if 0 < way.number and way.number < axes_absorber.axis_length - 1 and board.exists_stone_on_way(way.low_way()) and board.exists_stone_on_way(way.high_way()):
                    # modify 操作追加

                    move = Move(way, Operator.code_to_obj(operator_u))

                    ## DEBUG 表示抑制
                    #if operator_u=='xo':
                    #    print(f"[_append_binary_operation] append modify  {move.to_code()=}  {for_edit_mode=}")

                    legal_moves.append(board, move, for_edit=for_edit_mode)

            # 石が置いてない路
            else:

                ## DEBUG 表示抑制
                #if operator_u=='xo':
                #    print(f"[_append_binary_operation] new  {way.number=}  {axes_absorber.axis_length=}  {way.low_way().to_code()=}  {way.low_way(diff=2).to_code()=}  {way.high_way().to_code()=}  {way.high_way(diff=2).to_code()=}")

                # 隣のどちらかに２つ続けて石が置いているか？
                if ((1 < way.number and board.exists_stone_on_way(way.low_way()) and board.exists_stone_on_way(way.low_way(diff=2))) or
                    (way.number < axes_absorber.axis_length - 2 and board.exists_stone_on_way(way.high_way()) and board.exists_stone_on_way(way.high_way(diff=2)))):
                    # new 操作追加

                    move = Move(way, Operator.code_to_obj(operator_u))

                    ## DEBUG 表示抑制
                    #if operator_u=='xo':
                    #    print(f"[_append_binary_operation] append new  {move.to_code()=}  {for_edit_mode=}")

                    legal_moves.append(board, move, for_edit=for_edit_mode)


    def _append_cut_the_edge_operation(board, legal_moves):
        """カットザエッジ（Cut the edge）の合法手生成（盤面編集用）"""
        (rect_exists, left_file, right_file, top_rank, bottom_rank) = board.get_edges()

        if rect_exists:
            if 0 < right_file - left_file:
                legal_moves.append(board=board, move=Move(Way(FILE_AXIS, left_file), Operator.code_to_obj('c')), for_edit=True)
                legal_moves.append(board=board, move=Move(Way(FILE_AXIS, right_file), Operator.code_to_obj('c')), for_edit=True)
            
            if 0 < bottom_rank - top_rank:
                legal_moves.append(board=board, move=Move(Way(RANK_AXIS, top_rank), Operator.code_to_obj('c')), for_edit=True)
                legal_moves.append(board=board, move=Move(Way(RANK_AXIS, bottom_rank), Operator.code_to_obj('c')), for_edit=True)


    def _append_shift_operation(board, legal_moves):
        """シフト（Shift）の合法手生成
        
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
        
        上記 c段の石の長さは４目なので、シフトは s1, s2, s3 だけを合法手とするよう制限する。
        ゼロビットシフトは禁止する
        枝が増えてしまうのを防ぐ
        """
        global _way_characters

        # 筋（段）方向両用
        for way_u in _way_characters:
            way = Way.code_to_obj(way_u)

            # 路にロックが掛かっていたら Shift は禁止
            if board._way_locks[way.to_code()]:
                continue

            way_segment = board.get_stone_segment_on_way(way)

            # 石が置いてる路
            if 0 < way_segment.length:
                # Shift できる
                for i in range(1, way_segment.length):
                    move = Move(way, Operator.code_to_obj(f's{i}'))

                    # 合法手として記憶
                    legal_moves.append(board=board, move=move)


    def _append_not_operation(board, legal_moves):
        """ノット（Not）の合法手生成"""

        # 全ての種類の路
        global _all_ways

        for way in _all_ways:
            axes_absorber = way.absorb_axes()

            # 石が置いてある路
            if board.exists_stone_on_way(way):

                # 路にロックが掛かっていたら Not の Reverse は禁止
                if board._way_locks[way.to_code()]:
                    continue

                if 0 < way.number and board.exists_stone_on_way(way.low_way()):
                    # 路上で小さい方にある石を Not して Reverse できる
                    legal_moves.append(board=board, move=Move(way, Operator.code_to_obj('nL')))

                if way.number < axes_absorber.axis_length - 1 and board.exists_stone_on_way(way.high_way()):
                    # 路上で大きい方にある石を Not して Reverse できる
                    legal_moves.append(board=board, move=Move(way, Operator.code_to_obj('nH')))

            # 石が置いてない路
            else:
                # 隣のどちらかに石が置いているか？
                if 0 < way.number and board.exists_stone_on_way(way.low_way()):
                    # Not で New できる
                    legal_moves.append(board=board, move=Move(way, Operator.code_to_obj('n')))

                if way.number < axes_absorber.axis_length - 1 and board.exists_stone_on_way(way.high_way()):
                    # Not で New できる
                    legal_moves.append(board=board, move=Move(way, Operator.code_to_obj('n')))


    @staticmethod
    def generate_legal_moves(board):
        """現局面から合法手一覧を生成する
        
        Returns
        -------
        legal_moves : LegalMoves
            合法手一覧
        """

        #print("[SearchLegalMoves > generate_legal_moves] 実行")

        # 現局面から合法手を生成する
        legal_moves = LegalMoves(board)

        # カットザエッジ（Cut the edge）の合法手生成（盤面編集用）
        SearchLegalMoves._append_cut_the_edge_operation(board, legal_moves)

        # シフト（Shift）の合法手生成
        SearchLegalMoves._append_shift_operation(board, legal_moves)

        # ノット（Not）の合法手生成
        SearchLegalMoves._append_not_operation(board, legal_moves)

        # アンド（AND）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='a')

        # オア（OR）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='o')

        # ゼロ（ZERO）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='ze', for_edit_mode=True)

        # ノア（NOR）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='no')

        # エクソア（XOR）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='xo')

        # ナンド（NAND）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='na')

        # エクスノア（XNOR）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='xn')

        # ワン（ONE）の合法手生成
        SearchLegalMoves._append_binary_operation(board, legal_moves, operator_u='on', for_edit_mode=True)

        return legal_moves


class SearchMateMoveIn1Play():
    """１手詰め探索"""


    @staticmethod
    def find_mate_move_in_1ply(board, move_list, searched_clear_targets):
        """１手詰めがあるか調べる
        
        cshogi では Board のメソッド mate_move_in_1ply()。ビナーシでは変更した

        Return
        ------
        mate_move_in_1ply : Move
            １手詰めの指し手。１手詰めが無ければナンを返す
        """

        current_turn = board.get_next_turn()

        found_move = None

        for move in move_list:

            # DO 試しに一手指す
            board.push_usi(move.to_code())

            # 新規合法手生成
            next_legal_moves = SearchLegalMoves.generate_legal_moves(board)

            # 未来のクリアーターゲット新規作成
            next_searched_clear_targets = SearchedClearTargets.update_clear_targets(
                board=board,
                # 引き継ぎ
                clear_targets_list=searched_clear_targets.clear_targets_list)

            # 未来の終局判定新規作成
            next_searched_gameover = SearchedGameover.search(board, next_legal_moves, next_searched_clear_targets.clear_targets_list)

            # DO 勝ちかどうか判定する。自分に勝ちが有ったら真を返す
            if board.is_gameover(next_searched_gameover):

                if next_searched_gameover.is_black_win and current_turn == C_BLACK:
                    # You win!  ※一手戻すまでループから抜けないこと
                    found_move = move

                elif next_searched_gameover.is_white_win and current_turn == C_WHITE:
                    # You win!  ※一手戻すまでループから抜けないこと
                    found_move = move

            # DO 一手戻す
            board.pop()

            # （一手戻してから）ループから抜ける
            if found_move is not None:
                break


        # 一手詰めの手
        return found_move


class SearchedGameover():
    """ゲームオーバー探索"""


    def __init__(self, is_black_win, is_white_win, is_simultaneous_clearing, black_count_with_komi, white_count_with_komi, reason):
        """初期化
        
        Parameters
        ----------
        is_black_win : bool
            黒勝ち
        is_white_win : bool
            白勝ち
        is_simultaneous_clearing : bool
            同時条件クリアー
            これが偽なら満局
        black_count_with_komi : bool
            点数勝負の場合の黒石の数
        white_count_with_komi : bool
            点数勝負の場合の白石の数
            囲碁を踏襲してコミを含む。
            コミは先後の勝率を五分五分に調整するためのもの。プレイヤーの強さを調整するためのハンディキャップとは異なる
        reason : str
            ゲームオーバーと判定された理由の説明
        """

        self._is_black_win = is_black_win
        self._is_white_win = is_white_win
        self._is_simultaneous_clearing = is_simultaneous_clearing
        self._black_count_with_komi = black_count_with_komi
        self._white_count_with_komi = white_count_with_komi
        self._reason = reason


    @property
    def is_black_win(self):
        """黒勝ち"""
        return self._is_black_win


    @property
    def is_white_win(self):
        """白勝ち"""
        return self._is_white_win


    @property
    def is_simultaneous_clearing(self):
        """同時条件クリアー
        これが偽なら満局"""
        return self._is_simultaneous_clearing


    @property
    def black_count_with_komi(self):
        """点数勝負の場合の黒石の数"""
        return self._black_count_with_komi


    @property
    def white_count_with_komi(self):
        """点数勝負の場合の白石の数

        囲碁を踏襲してコミを含む。        
        コミは先後の勝率を五分五分に調整するためのもの。プレイヤーの強さを調整するためのハンディキャップとは異なる"""
        return self._white_count_with_komi


    @property
    def is_playing(self):
        """終局していません"""
        return not self._is_black_win and not self._is_white_win


    @property
    def reason(self):
        """ゲームオーバーと判定された理由の説明"""
        return self._reason


    @staticmethod
    def _point_playoff(board, is_simultaneous_clearing):
        """盤上の石を数えて点数勝負"""

        # 点数の差分計算があってるかチェック
        # global BLACK_KOMI, WHITE_KOMI
        #
        # black_count_with_komi = BLACK_KOMI # 予めコミを含めておく
        # white_count_with_komi = WHITE_KOMI
        #
        # for i in range(0, BOARD_AREA):
        #     stone = board.get_color(i)
        #     if stone == C_BLACK:
        #         black_count_with_komi += 1
        #
        #     elif stone == C_WHITE:
        #         white_count_with_komi += 1
        #
        #     elif stone == C_EMPTY:
        #         pass
        #
        #     else:
        #         raise ValueError(f"{stone=}")
        #
        # if board.black_count_with_komi != black_count_with_komi or board.white_count_with_komi != white_count_with_komi:
        #     raise ValueError(f"点数の差分計算ミス  {board.black_count_with_komi=}  {black_count_with_komi=}  {board.white_count_with_komi=}  {white_count_with_komi=}")

        if board.white_count_with_komi < board.black_count_with_komi:
            if is_simultaneous_clearing:
                reason_of_when = f'simultaneous clearing'
            else:
                reason_of_when = f'stalemate'

            return SearchedGameover(
                is_black_win=True,
                is_white_win=False,
                is_simultaneous_clearing=is_simultaneous_clearing,
                black_count_with_komi = board.black_count_with_komi,
                white_count_with_komi = board.white_count_with_komi,
                reason=f'black {board.black_count_with_komi-board.white_count_with_komi} win when {reason_of_when}')

        elif board.black_count_with_komi < board.white_count_with_komi:
            if is_simultaneous_clearing:
                reason_of_when = f'simultaneous clearing'
            else:
                reason_of_when = f'stalemate'

            return SearchedGameover(
                is_black_win=False,
                is_white_win=True,
                is_simultaneous_clearing=is_simultaneous_clearing,
                black_count_with_komi = board.black_count_with_komi,
                white_count_with_komi = board.white_count_with_komi,
                reason=f'white {board.white_count_with_komi-board.black_count_with_komi} win when {reason_of_when}')

        # 後手の白番にコミがあるので引き分けにはならない
        else:
            raise ValueError(f"{board.black_count_with_komi=}  {board.white_count_with_komi=}")


    @staticmethod
    def search(board, legal_moves, clear_targets_list):

        # どちらかのプレイヤーが３つのターゲットを完了した
        is_black_win = False
        is_white_win = False
        
        if clear_targets_list[0] != -1 and clear_targets_list[1] != -1 and clear_targets_list[2] != -1:
            is_black_win = True

        if clear_targets_list[3] != -1 and clear_targets_list[4] != -1 and clear_targets_list[5] != -1:
            is_white_win = True

        if is_black_win and is_white_win:
            # 両者が同時にクリアーターゲットを全て揃えた場合、点数勝負
            return SearchedGameover._point_playoff(board, is_simultaneous_clearing=True)

        if is_black_win:
            # 黒勝ち
            return SearchedGameover(
                is_black_win=is_black_win,
                is_white_win=is_white_win,
                is_simultaneous_clearing=False,
                black_count_with_komi = -1,
                white_count_with_komi = -1,
                reason='black win')

        if is_white_win:
            # 白勝ち
            return SearchedGameover(
                is_black_win=is_black_win,
                is_white_win=is_white_win,
                is_simultaneous_clearing=False,
                black_count_with_komi = -1,
                white_count_with_komi = -1,
                reason='white win')

        # ステールメートしている
        if len(legal_moves.distinct_items) < 1:
            # 点数勝負
            return SearchedGameover._point_playoff(board, is_simultaneous_clearing=False)


        # TODO 投了しているケースに対応したい

        # 終局していない
        return SearchedGameover(
            is_black_win=is_black_win,
            is_white_win=is_white_win,
            is_simultaneous_clearing=False,
            black_count_with_komi = -1,
            white_count_with_komi = -1,
            reason='playing')


class PositionCommand():
    """position コマンド"""


    def __init__(self, board):
        """初期化
        
        Parameters
        ----------
        board : Board
            盤
        """
        self._board = board
        self._searched_clear_targets = None


    @property
    def searched_clear_targets(self):
        return self._searched_clear_targets


    def position_detail(self, sfen_u, move_u_list):
        """局面データ解析

        Parameters
        ----------
        sfen_u : str
            SFEN文字列
        move_u_list : list
            盤面編集履歴。実体は指し手コードの空白区切りリスト。対局棋譜のスーパーセット
        """

        print(f"[PositionCommand > position_detail (debug 3679)] {sfen_u=}")

        # NOTE 'sfen startpos' という書き方は間違いです。 'startpos' は SFEN ではありません
        # 平手初期局面に変更
        if sfen_u == 'startpos':
            self._board.reset()
            self._searched_clear_targets = SearchedClearTargets.make_new_obj()

        # 指定局面に変更
        elif sfen_u[:5] == 'sfen ':
            self._searched_clear_targets = self._board.set_sfen(sfen_u[5:])
        
        else:
            raise ValueError(f"unsupported position  {sfen_u=}")


        # 初期局面を記憶（SFENで初期局面を出力したいときのためのもの）
        self._board.update_squares_at_init()

        # 盤面編集履歴（対局棋譜のスーパーセット）再生
        for move_u in move_u_list:
            self._board.push_usi(move_u)


    @staticmethod
    def parse_and_update_board(board, input_str):
        """盤を変更します"""

        position_command = PositionCommand(board)

        cmd = input_str.split(' ', 1)

        # 余計な半角空白は入っていない前提
        pos_list = cmd[1].split(' moves ')
        sfen_text = pos_list[0]
        print(f"[PositionCommand > parse_and_update_board (debug 3711)] {sfen_text=}")

        #print(f"[position] {pos_list=}")

        # 区切りは半角空白１文字とします
        move_u_list = (pos_list[1].split(' ') if len(pos_list) > 1 else [])

        position_command.position_detail(sfen_text, move_u_list)

        return position_command
