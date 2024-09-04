# ビナーシ解析

**情報処理系しか遊べないリバーシ**  

`binary` （バイナリー） ＋ `riverse` （リバーシ） ＝ `binarsi` （ビナーシ）  

👇　ビナーシの遊び方は note で説明しています  
📖　[ビナーシ（Binarsi）の遊び方説明](https://note.com/muzudho/n/n58c1db0dce14)  

👇　ビナーシのプログラムは以下で説明しています  
📖 [ビナーシ USI エンジン](./usi_engine/README.md)  

以下は、対局ツールの使い方を説明します  


# 対局ツールの使い方

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
(2) quit
(3) selfmatch

please input number(1-3):
```

👆 `human VS computer` を遊ぶなら、 `1` と打鍵してエンターキーを押してください  


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


# 参考文献

* 📖 [むずでょnote ＞ ビナーシ（Binarsi） を創ろう](https://note.com/muzudho/n/na5dce2824aa4)
* 📖 [ビナーシ（Binarsi）の遊び方説明](https://note.com/muzudho/n/n58c1db0dce14)
* 📖 [やねうら王ブログ ＞ 対局ゲーム標準通信プロトコルの提案](https://yaneuraou.yaneu.com/2022/06/07/standard-communication-protocol-for-games/)
