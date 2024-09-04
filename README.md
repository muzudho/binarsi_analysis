# ビナーシ解析

**情報処理系しか遊べないリバーシ**  

`binary` （バイナリー） ＋ `riverse` （リバーシ） ＝ `binarsi` （ビナーシ）  


📖　[note > ビナーシ（Binarsi）の遊び方説明](https://note.com/muzudho/n/n58c1db0dce14)  
　👆　まずは、ビナーシの遊び方を読んでください  

📖 [ビナーシ USI エンジン](./usi_engine/README.md)  
　👆　コンピューター・ビナーシの思考エンジンに関心がある方は、上記のリンクから進んでください。それ以外の方は無視してください  


以下は、対局ツールの使い方（コロシアム）を説明します  


# 対局ツール（コロシアム）の使い方

Input:  

```shell
python coliceum.py
```

Output:

```plaintext
 ^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^
<   ______                                                          >
 >  |  __  |   __   _______     ______    _______    ______   __   <
<   | |__| |  |__| |   __  |_  |  ___ |_ |   ____| /   ____/ |__|   >
 >  |  __ /_   __  |  |  |  |  |  _____| |  |      |_____  |  __   <
<   | |__|  | |  | |  |  |  |  | |_____  |  |       ____/ /  |  |   >
 >  |______/  |__| |__|  |__|  |_______| |__|      |_____/   |__|  <
<                                                                   >
 v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v^v

(1) human VS computer
(2) human VS human
(3) computer VS computer
(4) quit

please input number(1-3):
```

👆 対コンピューター戦を遊ぶなら、 `1` と打鍵してエンターキーを押してください  


Output:  

```plaintext
CHOOSE
---------
(1) sente
(2) gote
---------
Do you play sente or gote(1-2)?>
```

👆 先手か後手を選んでください。先手なら `1` を、後手なら `2` を打鍵してエンターキーを押してください。  
ここでは `1` を選んだとします  


Output:  

```plaintext
[ 0 moves | init | next black]
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . 0 . . . . |
d | . . . . . . . |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+

     __     ___   ________    __    __ 
    |  |   /  /  /   __   |  |  |  |  |
    |  |__/  /   |  |  |  |  |  |  |  |
    |__    _/    |  |  |  |  |  |  |  |
       |  |      |  |  |  |  |  |  |  |
       |  |      |  |_/   |  |  |_/   |
       |__|      |_______/   |_______/

LEGAL MOVES
-----------

+--+----+------------------------------------+
|No|Code|Description                         |
+--+----+------------------------------------+--+----+------------------------------------+--+----+------------------------------------+
| 1|2n  | 2-file <-        NOT  3-file       | 3|bn  | b-rank <-        NOT  c-rank       |  |    |                                    |
| 2|4n  | 4-file <-        NOT  3-file       | 4|dn  | d-rank <-        NOT  c-rank       |  |    |                                    |
+--+----+------------------------------------+--+----+------------------------------------+--+----+------------------------------------+
Please input No(1-4) or Code or "help":
```

👆　平手初期局面と、合法手一覧が表示されます。  
ここでは `4` または `dn` と打鍵してエンターキーを押してください  


Output:  

```plaintext
[ 1 moves | moved dn | next white]
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . 0 . . . . |
d | . . 1 . . . . |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+

     ________   ________    ______  ______   ________
    /   ____|  /   __   |  |   __ |/ __   |  |   __  |
    |  /       |  |  |  |  |  |  |  |  |  |  |  |  |  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  |__/  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  _____/
    |  |____   |  |_/   |  |  |  |  |  |  |  |  |
    |_______|  |_______/   |__|  |__|  |__|  |__|


[ 2 moves | moved 3s1 | next black]
    1 2 # 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . 1 . . . . |
d | . . 0 . . . . |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+

     __     ___   ________    __    __ 
    |  |   /  /  /   __   |  |  |  |  |
    |  |__/  /   |  |  |  |  |  |  |  |
    |__    _/    |  |  |  |  |  |  |  |
       |  |      |  |  |  |  |  |  |  |
       |  |      |  |_/   |  |  |_/   |
       |__|      |_______/   |_______/

LEGAL MOVES
-----------

+--+----+------------------------------------+
|No|Code|Description                         |
+--+----+------------------------------------+--+----+------------------------------------+--+----+------------------------------------+
| 1|2n  | 2-file <-        NOT  3-file       | 7|bo  | b-rank <- c-rank OR   d-rank       |13|ea  | e-rank <- d-rank AND  c-rank       |
| 2|4n  | 4-file <-        NOT  3-file       | 8|bxn | b-rank <- c-rank XNOR d-rank       |14|ena | e-rank <- d-rank NAND c-rank       |
| 3|bn  | b-rank <-        NOT  c-rank       | 9|bxo | b-rank <- c-rank XOR  d-rank       |15|eno | e-rank <- d-rank NOR  c-rank       |
| 4|ba  | b-rank <- c-rank AND  d-rank       |10|cnH | c-rank <-        NOT  d-rank       |16|eo  | e-rank <- d-rank OR   c-rank       |
| 5|bna | b-rank <- c-rank NAND d-rank       |11|dnL | d-rank <-        NOT  c-rank       |17|exn | e-rank <- d-rank XNOR c-rank       |
| 6|bno | b-rank <- c-rank NOR  d-rank       |12|en  | e-rank <-        NOT  d-rank       |18|exo | e-rank <- d-rank XOR  c-rank       |
+--+----+------------------------------------+--+----+------------------------------------+--+----+------------------------------------+
Please input No(1-18) or Code or "help":
```

👆 コンピューターの手番のあと、また、あなたのターンが回ってきます  

何を打てばいいか分からない場合は `1` を打鍵してエンターキーを押していけば進みます  


Output:  

```plaintext
     ________   ________    ______  ______   ________
    /   ____|  /   __   |  |   __ |/ __   |  |   __  |
    |  /       |  |  |  |  |  |  |  |  |  |  |  |  |  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  |__/  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  _____/
    |  |____   |  |_/   |  |  |  |  |  |  |  |  |
    |_______|  |_______/   |__|  |__|  |__|  |__|


[16 moves | moved aa | b3 b4 w3 w4 w5 | next black]
    # # # # # 6 7
  +---------------+
a | 0 0 0 0 0 . . |
b | 1 1 1 0 1 . . |
# | 0 0 0 1 0 . . |
# | 1 0 1 0 1 . . |
# | 0 0 1 0 1 . . |
f | . . . . . . . |
  +---------------+

CLEAR TARGETS
----------------------------------------------------------------------------------------

     [b3]           [b4]           [b5]           [w3]           [w4]           [w5]
+-----------+  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+
| . . . . . |  | 1 . . . . |  | . . 1 . . |  | . . . . . |  | 0 . . . . |  | . . . . . |
| . . . . . |  | . 1 . . . |  | . . 1 . . |  | . . 0 . . |  | . 0 . . . |  | . . . . . |
| . 1 1 1 . |  | . . 1 . . |  | . . 1 . . |  | . . 0 . . |  | . . 0 . . |  | 0 0 0 0 0 |
| . . . . . |  | . . . 1 . |  | . . 1 . . |  | . . 0 . . |  | . . . 0 . |  | . . . . . |
| . . . . . |  | . . . . . |  | . . 1 . . |  | . . . . . |  | . . . . . |  | . . . . . |
+-----------+  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+
 CLEAR in 10    CLEAR in 13                   CLEAR in 14    CLEAR in 12    CLEAR in 16
                                  WANTED

----------------------------------------------------------------------------------------

     __     ___   ________    __    __
    |  |   /  /  /   __   |  |  |  |  |
    |  |__/  /   |  |  |  |  |  |  |  |
    |__    _/    |  |  |  |  |  |  |  |
       |  |      |  |  |  |  |  |  |  |
       |  |      |  |_/   |  |  |_/   |
       |__|      |_______/   |_______/
     __          ________    _______    ________
    |  |        /   __   |  /   ____|  |   __   |
    |  |        |  |  |  |  |  /____   |  |__|  |
    |  |        |  |  |  |  |____   |  |   _____/
    |  |_____   |  |  |  |       |  |  |  |   ___
    |        |  |  |_/   |   ___/   /  |  |__/  /
    |________|  |_______/   |______/   |_______/
```

👆 勝敗判定が出て、タイトル画面へ戻ります  


## コロシアムのその他のコマンド

Output:  

```plaintext
LEGAL MOVES
-----------

+--+----+------------------------------------+
|No|Code|Description                         |
+--+----+------------------------------------+--+----+------------------------------------+--+----+------------------------------------+
| 1|2n  | 2-file <-        NOT  3-file       | 3|bn  | b-rank <-        NOT  c-rank       |  |    |                                    |
| 2|4n  | 4-file <-        NOT  3-file       | 4|dn  | d-rank <-        NOT  c-rank       |  |    |                                    |
+--+----+------------------------------------+--+----+------------------------------------+--+----+------------------------------------+
Please input No(1-4) or Code or "help":
```

👆 指し手の入力を促されたときに `help` と打鍵してエンターキーを押すと、その他のコマンドの一覧が表示されます  


input:  

```plaintext
help
```

Output:  

```plaintext
`quit` - Exit the application.
`board` - Display the board.
`sfen` - Display the sfen.
`clear_targets` - Display the clear targets.
`legal_moves` - Display the legal moves.
`mate1` - Display the 1 move in mate 1 ply.
`distinct_legal_moves` - Display the distinct legal moves.
`history` - Display the input command list.
`moves_for_edit` - Display the operation for edit.
`test_board` - Test to display the new board (under development).
`inverse 4n` - Displays the inverse operation. The argument must be a move code.
```


### quit コマンド

コロシアムを終了します  

### board コマンド

盤を表示します  

例：  

```plaintext
[ 0 moves | init | next black]
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . 0 . . . . |
d | . . . . . . . |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+
```

👆 まっさらな状態から、 3c の位置に `0` が１つ置いてある盤面を　平手初期局面（ひらてしょききょくめん；Start position）　と呼びます  

各部名称：  

```
    1 2 3 4 5 6 7
  +---------------+
a | . . . * . . . |
b | . . . * . . . |
c | . . . * . . . |
d | . . . * . . . |
e | . . . * . . . |
f | . . . * . . . |
  +---------------+
```

👆　上図 `*` の場所は **4筋（すじ）**（4th file）、または **4路（ろ）**（4th way）と呼びます  

```
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . . . . . . |
d | * * * * * * * |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+
```

👆　上図 `*` の場所は **d段（だん）**（d rank）、または **d路（ろ）**（d way）と呼びます  

### sfen コマンド

Output Example 1:  

```plaintext
[from beginning] startpos
[from present]   startpos
```

👆 平手初期局面では `startpos` と返ってきます  


Output Example 2:  

```plaintext
[from beginning] startpos moves 2n cs1 1n 4o 1nH 3a 2nL dn
                 stones_before_change - - - - 1 1 0 -
[from present]   sfen 7/7/xoox3/oxxo3/7/7 b 123c - 8
```

👆 `[from beginning]` は、初期局面と棋譜が付いています。  
`[from present]` は、現在の局面が付いています。  
`stones_before_change` は、盤上で上書きされて消えた石が記録されています（SFENには含まれません）  


### board コマンド

TODO board コマンド  

### clear_targets コマンド

TODO clear_targets コマンド  

### legal_moves コマンド

TODO legal_moves コマンド  

### mate1 コマンド

TODO mate1 コマンド  

### distinct_legal_moves コマンド

TODO distinct_legal_moves コマンド  

### history コマンド

TODO history コマンド  

### moves_for_edit コマンド

TODO moves_for_edit コマンド  

### test_board コマンド

TODO test_board コマンド

### inverse 4n コマンド

TODO inverse 4n コマンド


# 参考文献

* 📖 [むずでょnote ＞ ビナーシ（Binarsi） を創ろう](https://note.com/muzudho/n/na5dce2824aa4)
* 📖 [ビナーシ（Binarsi）の遊び方説明](https://note.com/muzudho/n/n58c1db0dce14)
* 📖 [やねうら王ブログ ＞ 対局ゲーム標準通信プロトコルの提案](https://yaneuraou.yaneu.com/2022/06/07/standard-communication-protocol-for-games/)
