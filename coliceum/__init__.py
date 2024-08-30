import pexpect


class Coliceum():
    """対局コロシアム"""

    @staticmethod
    def start():
        """TODO 開始"""

        # NOTE Python の subprocess はパイプのことだ。アプリケーションが終了して結果をリターンすることを前提としている
        # NOTE Python の multiprocessing は、外部プロセスを起動するものではない。プロセスを生成することを前提としている
        # NOTE Python の pexpect ライブラリーは、メッセージループで入力を待機するアプリケーションに向いているが、UNIX 系に限られる。公式で Windows には対応していないアナウンスがある
        # NOTE Socket 通信は、サーバー・クライアント型を想定している。標準入出力で通信を行う想定の外部プロセスに対応したものではない
        # NOTE Elixier を使うしかないのでは？

        # binarsi_analisis リポジトリー直下の main.py を起動しています
        # engine は対局エンジンプロセス
        engine = pexpect.spawn('python main.py')

        engine.sendline("usi")

        engine.expect("usiok\n", timeout=None)

        engine.sendline("isready")

        print(engine.before.decode(encoding='utf-8'))

        engine.close()
