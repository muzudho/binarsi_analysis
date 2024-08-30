# python coliceum.py
import subprocess, sys


class Coliceum():
    """対局コロシアム"""

    @staticmethod
    def start():
        """TODO 開始"""

        with subprocess.Popen(
                ['python', 'main.py'],
                #encoding='cp932',   # Windows のターミナルが古い
                encoding='UTF-8',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE) as game_engine_process:

            # if game_engine_process.returncode != 0:
            #     print('subprocess open failed.', file=sys.stderr)
            #     sys.exit(1)        

            stdout, stderr = game_engine_process.communicate(input='usi\n')

            if stderr:
                print(f"Standard Error: {stderr=}")

            #print(f"Standard Output: {stdout=}")
            print(f"""\
Standard Output
---------------
{stdout}""")


            # print(f'usi', file=game_engine_process.stdin, flush=True)

            # while True:
            #     message = game_engine_process.stdout.readline()
            #     print(f"{message=}")
            #     if message == 'usiok':
            #         break

            # print("this is USI supported program")

        # 対局エンジンにコマンドを送るには？



if __name__ == '__main__':
    """コマンドから実行時"""
    try:
        Coliceum.start()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise

