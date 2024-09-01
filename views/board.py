from py_binarsi import C_BLACK, C_WHITE, BOARD_AREA, Colors


class BoardViews():
    """盤面のテキスト形式の表示はたくさんの種類があるので、１つのファイルに分けた"""


    @staticmethod
    def stringify_board_header(board, searched_clear_targets=None):
        """盤面のヘッダー
                
        Parameters
        ----------
        searched_clear_targets : SearchedClearTargets
            クリアーターゲット
            指し手生成中はナン
        """

        edits_num = len(board.board_editing_history.items)
        if board.moves_number != edits_num:
            edits_num_str = f"| {edits_num} edits "
        else:
            edits_num_str = ""

        if 0 < edits_num:
            latest_move = board.board_editing_history.items[-1].move
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
        next_turn = board.get_next_turn()
        if next_turn == C_BLACK:
            next_turn_str = 'next black'
        elif next_turn == C_WHITE:
            next_turn_str = 'next white'
        else:
            raise ValueError(f"unsupported turn  {next_turn}")


        return f"[{board.moves_number:2} moves {edits_num_str}| {latest_move_str}{clear_targets_list_str} | {next_turn_str}]"



    @staticmethod
    def stringify_board_normal(board):
        """通常の盤面

        例：
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

        # 数値を表示用文字列(Str)に変更
        s = [' '] * BOARD_AREA
        for sq in range(0, BOARD_AREA):
            s[sq] = Colors.as_string_board(board.get_color(sq))

        # 筋（段）の符号、またはロック
        def get_way_code_2(way_code):
            if board.way_locks[way_code]:
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
