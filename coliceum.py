from coliceum import Coliceum


if __name__ == '__main__':
    """コマンドから実行時"""
    try:
        Coliceum.start()

    except Exception as err:
        print(f"[unexpected error] {err=}, {type(err)=}")
        raise

