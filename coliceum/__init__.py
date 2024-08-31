import pexpect.popen_spawn as psp
import re
from py_binarsi import Board, SearchedClearTargets, PositionCommand
from views import Views


class Coliceum():
    """対局コロシアム"""


    def __init__(self, child_process):
        """初期化

        Parameters
        ----------
        child_process : object
            このプロセスからオープンした新しいプロセス。このプロセスの子プロセスとしてぶら下げたもの。
            このプロセス自体をクローズさせる方法が分からない
        """

        self._proc = child_process
        self._board = Board()

        # 終局判定を新規作成
        self._searched_clear_targets = SearchedClearTargets.make_new_obj()


    def sendline(self, message):
        """子プロセスの標準入力へ文字列を送ります"""

        print(f"Coliceum said> {message}")
        self._proc.sendline(message)


    @property
    def messages_until_match(self):
        """expect() でマッチするまでの間に無視した文字列を返す"""
        return self._proc.before.decode('utf-8', errors="ignore")


    @property
    def matched_message(self):
        """expect() にマッチした文字列を返す"""

        # after は bytes オブジェクト
        return self._proc.after.decode('utf-8', errors="ignore")


    @property
    def match_obj(self):
        """expect() にマッチしたときの match オブジェクトを返す"""
        return self._proc.match


    def group(self, index):
        """expect() にマッチしたときの match オブジェクトを返す"""

        # group() の返却値はバイト文字列で、 b'word' のように b が付いてくるので、 decode() する必要がある
        return self._proc.match.group(index).decode('utf-8')


    def expect_line(self, format, timeout, end='\r\n'):
        """子プロセスが出力すると想定した文字列
        
        Windows を想定して、改行コードの '\r\n' を末尾に付ける
        
        Parameters
        ----------
        message : str
            文字列。正規表現で書く
        """

        print(f"The engine would say: {format}")
        self._proc.expect(f"{format}{end}", timeout=timeout)


    def go_computer(self):
        """コンピューターに１手指させる～盤表示まで"""
        self.sendline("go")

        # Engine said
        self.expect_line(r"bestmove ([\w\s]+)", timeout=None)
#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}""")
        # [2024-08-31 01:45:38.237119] usinewgame end
        # info depth 0 seldepth 0 time 1 nodes 0 score cp 0 string I'm random move

        # print(f"{self.matched_message=}")   # "bestmove 4n\r\n"
        # print(f"{self.group(1)=}")    # 4n
        bestmove_str = self.group(1)
        self.sendline(f"do {bestmove_str}")

        # Engine said
        # NOTE `.*` では最右マッチしてしまうので、 `.*?` にして最左マッチにする
        self.expect_line("\\[from beginning\\](.*?)", timeout=None)
        position_command_str = f"position{self.group(1)}"
        print(f"(debug 98) {position_command_str=}")
        position_command = PositionCommand.parse_and_update_board(self._board, position_command_str)
#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}
#
# Matched message
# ---------------
# [from beginning]{position_args}""")
        # もう１行 stones_before_change が続く可能性もある

        # Engine said
        self.expect_line("\\[from present\\](.*?)", timeout=None)
        position_args = self.group(1)

#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}
#
# Matched message
# ---------------
# [from present]{position_args}""")
        # もう１行 stones_before_change が続く可能性もある

        # 盤表示
        print() # 改行
        print(self._board.as_str(position_command.searched_clear_targets))
        print() # 改行

        # 今クリアーしたものがあれば、クリアー目標表示
        Views.print_clear_target_if_it_now(self._board, position_command.searched_clear_targets)


    def go_you(self):
        """あなたに１手指させる～盤表示まで"""

        # 合法手メニューの表示
        legal_move_code_help_list = Views.create_legal_move_code_help_list(self._board)
        Views.print_legal_moves_menu(legal_move_code_help_list)

        print(f"Please input No(1-{len(legal_move_code_help_list)}) or Code:")

        input_str = input()
        result = re.match(r"^[0-9]+$", input_str)
        if result:
            input_num = int(input_str)

            move_code_help = legal_move_code_help_list[input_num - 1]
            do_command = f"do {move_code_help.code}" # message

        else:
            # FIXME 入力チェック要るか？
            do_command = f"do {input_str}"


        # Coliceum said
        self.sendline(do_command)

        # Engine said
        # NOTE `.*` では最右マッチしてしまうので、 `.*?` にして最左マッチにする
        self.expect_line("\\[from beginning\\](.*?)", timeout=None)

        print(f"""\
Ignored lines
-------------
{self.messages_until_match}

Matched message (Debug 1)
---------------
{self.matched_message}""")

        position_command_str = f"position{self.group(1)}"
        print(f"(Debug 163) {position_command_str=}")
        position_command = PositionCommand.parse_and_update_board(self._board, position_command_str)

        # Engine said
        self.expect_line("\\[from present\\](.*?)", timeout=None)
        position_args = self.group(1)
#         print(f"""\
# Ignored lines
# -------------
# {self.messages_until_match}""")

        # 盤表示
        print() # 改行
        print(self._board.as_str(position_command.searched_clear_targets))
        print() # 改行

        # 今クリアーしたものがあれば、クリアー目標表示
        Views.print_clear_target_if_it_now(self._board, position_command.searched_clear_targets)


    @staticmethod
    def start():
        """TODO 開始

        # NOTE Python の subprocess はパイプのことだ。アプリケーションが終了して結果をリターンすることを前提としている
        # NOTE Python の multiprocessing は、外部プロセスを起動するものではない。プロセスを生成することを前提としている
        # NOTE Python の pexpect ライブラリーは、メッセージループで入力を待機するアプリケーションに向いているが、UNIX 系に限られる。公式で Windows には対応していないアナウンスがある
        # NOTE Socket 通信は、サーバー・クライアント型を想定している。標準入出力で通信を行う想定の外部プロセスに対応したものではない
        # NOTE Windows で pexpect ライブラリーを使ってみたという記事がある
        # 📖 [Windowsでpexpectを利用する](https://qiita.com/shita_fontaine/items/c2ceb1e66450d7e09490)
        """

        # binarsi_analisis リポジトリー直下の main.py を起動しています
        # engine は対局エンジンプロセス
        print("Coliceum> python main.py")
        coliceum = Coliceum(
            child_process=psp.PopenSpawn('python main.py'))

        # 以下、基本的に expect_line、 print、 sendline、 を対話１回分として繰り返します

        # Coliceum said
        coliceum.sendline("usi")

        # Engine said
        coliceum.expect_line(r"id name (\w+)", timeout=None)
        print(f"{coliceum.messages_until_match=}")  # ""
        print(f"{coliceum.matched_message=}")       # "id name KifuwarabeBinarsi\r\n"
        print(f"{coliceum.group(0)=}")    # "id name KifuwarabeBinarsi\r\n"
        print(f"{coliceum.group(1)=}")    # "KifuwarabeBinarsi"

        # Engine said
        coliceum.expect_line("id author Muzudho", timeout=None)

        # Engine said
        coliceum.expect_line("usiok", timeout=None)
        coliceum.sendline("isready")

        # Engine said
        coliceum.expect_line("readyok", timeout=None)
        coliceum.sendline("usinewgame")
        coliceum.sendline("position startpos")

        # TODO どちらの先手かは決められるようにしたい

        # TODO 終わりを知りたい
        while True:
            # Coliceum said
            coliceum.go_computer()

            # Colosseum asks
            coliceum.go_you()

        # 思考エンジンを終了させる
        coliceum.sendline("quit")

