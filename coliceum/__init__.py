import pexpect.popen_spawn as psp


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


    def sendline(self, message):
        """子プロセスの標準入力へ文字列を送ります"""

        print(f"[Coliceum > sendline]  {message=}")
        self._proc.sendline(message)


    def readlines(self):
        # FIXME よく分かってない
        return self._proc.before.decode("utf8", errors="ignore")


    def expect_line(self, message, timeout):
        """子プロセスが出力すると想定した文字列
        
        Windows を想定して、改行コードの '\r\n' を末尾に付ける"""

        print(f"[Coliceum > expect_line]  {message=}")
        self._proc.expect(f"{message}\r\n", timeout=timeout)


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
        print("[Coliceum > start]  spawn: python main.py")
        coliceum = Coliceum(
            child_process=psp.PopenSpawn('python main.py'))

        coliceum.sendline("usi")

        coliceum.expect_line("id name KifuwarabeBinarsi", timeout=None)

        coliceum.expect_line("id author Muzudho", timeout=None)

        coliceum.expect_line("usiok", timeout=None)

        coliceum.sendline("isready")

        coliceum.expect_line("readyok", timeout=None)

        coliceum.sendline("usinewgame")

        print(f"""\
Read lines
----------
{coliceum.readlines()}""")

        # 思考エンジンを終了させる
        coliceum.sendline("quit")

