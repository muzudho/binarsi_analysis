# ビナーシ解析

**情報処理系しか遊べないリバーシ**  

`binary` （バイナリー） ＋ `riverse` （リバーシ） ＝ `binarsi` （ビナーシ）  


# 実行

```shell
python main.py
```


# 遊び方

Input:  

```shell
usi
```

Output:  

```
id name KifuwarabeBinarsi
usiok
```

👆　まず `usi` と打鍵してください。 `usiok` が返ってきたらオーケーです

Input:  

```shell
isready
```

Output:  

```
readyok
```

👆　次に `isready` と打鍵してください。 `readyok` が返ってきたらオーケーです。  
これでゲームエンジンの準備ができました  

Input:  

```shell
usinewgame
```

Output:  

```
[2024-08-24 15:30:59.301810] usinewgame end
```

👆　対局開始時には必ず `usinewgame` と打鍵してください。 何かログが返ってきたらオーケーです。  
ゲームの盤がまっさらな状態になっていますが、このままではゲームは始めることができません  

Input:  

```shell
position startpos
```

👆　上記のコマンドを打鍵してください。平手初期局面になります。応答はありません

Input:  

```shell
board
```

Output:  

```
[ 0 moves | init | next black]
    1 2 3 4 5 6 7
  +---------------+
a |               |
b |               |
c |     0         |
d |               |
e |               |
f |               |
  +---------------+
```

👆　`board` と打鍵すると、現局面が表示されます


各部名称：  

```
    1 2 3 4 5 6 7
  +---------------+
a |       *       |
b |       *       |
c |       *       |
d |       *       |
e |       *       |
f |       *       |
  +---------------+
```

👆　上図 `*` の場所は 4筋（4th file）、または 4路（4th way）と呼びます  

```
    1 2 3 4 5 6 7
  +---------------+
a |               |
b |               |
c |               |
d | * * * * * * * |
e |               |
f |               |
  +---------------+
```

👆　上図 `*` の場所は d筋（d file）、または d路（d way）と呼びます  

次に、  

Input:  

```shell
sfen
```

Output:  

```
[from beginning] sfen startpos
[from present]   sfen 7/7/2o4/7/7/7 b - 0
```

👆　`sfen` と打鍵すると、２種類の SFEN が表示されます。  
どちらも同じですが、前者の方は局面が進むと棋譜が付き、後者の方は途中図の盤面が付きます  

Input:  

```shell
legal_moves
```

Output:  

```
LEGAL MOVES
-----------
    ( 1) do 2n
    ( 2) do 4n
    ( 3) do bn
    ( 4) do dn
-----------
```

👆　`legal_moves` と打鍵すると、合法手の一覧が表示されます

Input:  

```shell
do 4n
```

Output:  

```
[ 1 moves | moved 4n | next white]
    1 2 3 4 5 6 7
  +---------------+
a |               |
b |               |
c |     0 1       |
d |               |
e |               |
f |               |
  +---------------+
[from beginning] sfen startpos moves 4n
                 stones_before_change -
[from present]   sfen 7/7/2ox3/7/7/7 b - 1
```

👆　試しに `do 4n` と打鍵してください。４筋に 1 が追加されます。  
これは３筋全体を、４筋全体へ NOT演算したものです  

```
COMMAND:
    do [move]

STRUCTURES:

    move = [way][operator]

        way = [1, 2, 3, 4, 5, 6, 7, a, b, c, d, e, f]
        operator = [
            # 零項演算子（Nullary operator）
            s0 = 0-bit rotational logic higher **S**HIFT
            s1 = 1-bit rotational logic higher **S**HIFT
            s2 = 2-bit rotational logic higher **S**HIFT
            s3 = 3-bit rotational logic higher **S**HIFT
            s4 = 4-bit rotational logic higher **S**HIFT
            s5 = 5-bit rotational logic higher **S**HIFT
            s6 = 6-bit rotational logic higher **S**HIFT

            # 単項演算子（Unary operator）
            n  = **N**OT operation
            nH = **N**OT operation from **H**IGHER side
            nL = **N**OT operation from **L**OWER side

            # 二項演算子（Binary operator）
            a  = **A**ND operation
            o  = **O**R operation
            xo = **XO**R operation

            na = **NA**ND operation
            no = **NO**R operation
            xn = **XN**OR operation

            on = fill **ON**E operation
            ze = fill **ZE**RO operation
            c  = **C**UT of the edge operation
        ]
```

👆 `4n` は、 **ムーブ** （Move）コマンドと呼びます。  
`4n` は、 4 という **路** （Way） と、 n という **演算子** (Operator) で構成されています  


👇　いずれの演算でも、指定した路が **対称路** になります。例えば以下のような盤面があるとします  

```
    1 2 3 4 5 6 7
  +---------------+
a |               |
b |               |
c |     0         |
d |     1         |
e |     0         |
f |               |
  +---------------+
```

👇　ここで零項演算で　3路　を指定し、１ビットシフトすると下図のようになります

```
    1 2 3 4 5 6 7             1 2 3 4 5 6 7
  +----+-+--------+         +----+-+--------+
a |    | |        |       a |    | |        |
b |    | |        |       b |    | |        |
c |    |0|        |  -->  c |    |0|        |
d |    |1|        |       d |    |0|        |
e |    |0|        |       e |    |1|        |
f |    | |        |       f |    | |        |
  +----+-+--------+         +----+-+--------+
```

👇　次に、単項演算で　4路　を指定し、 NOT演算した例を示します  

```
    1 2 3 4 5 6 7             1 2 3 4 5 6 7  
  +------+-+------+         +------+-+------+
a |      | |      |       a |      | |      |
b |      | |      |       b |      | |      |
c |     0| |      |  -->  c |     0|1|      |
d |     1| |      |       d |     1|0|      |
e |     0| |      |       e |     0|1|      |
f |      | |      |       f |      | |      |
  +------+-+------+         +------+-+------+
```

4路には、石が有っても無くても構いません  

👇　次に、単項演算が　**インプレース** （In-place；既に石の置いてあるところ）でもできる例を示します  

```
    1 2 3 4 5 6 7             1 2 3 4 5 6 7  
  +------+-+------+         +------+-+------+
a |      | |      |       a |      | |      |
b |      | |      |       b |      | |      |
c |     0|1|1     |  -->  c |     0|0|1     |
d |     1|1|0     |       d |     1|1|0     |
e |     0|0|0     |       e |     0|1|0     |
f |      | |      |       f |      | |      |
  +------+-+------+         +------+-+------+
```

単項演算をインプレースで行う場合、左側（上側）と右側（下側）のどちらを元にするか判断できないケースがあります。  
その場合、 （`n` ではなく、） `nL` や `nH` のように、 Lower （路の番号が小さい、前方の方）か Higher （路の番号が大きい、後ろの方）かを明示するようにします  

石がないところに石を置くのは　**ニューする** （New）とか、 **新規作成** と呼ぶことにします。  
既にある石をひっくり返したり、ひっくり返さなかったりすることは　**モディファイする** （Modify）とか、 **改変** と呼ぶことにします  


👇　次に二項演算の説明です。  
二項演算にも　新規作成と改変があります。二項演算で 5路 を指定し AND演算する例を示します  

```
    1 2 3 4 5 6 7             1 2 3 4 5 6 7  
  +--------+-+----+         +--------+-+----+
a |        | |    |       a |        | |    |
b |        | |    |       b |        | |    |
c |     0 1| |    |  -->  c |     0 1|0|    |
d |     1 1| |    |       d |     1 1|1|    |
e |     0 0| |    |       e |     0 0|0|    |
f |        | |    |       f |        | |    |
  +--------+-+----+         +--------+-+----+
```

👇　改変する例。  
二項演算で改変する際は、両隣りの路を入力として使います  

```
    1 2 3 4 5 6 7             1 2 3 4 5 6 7  
  +------+-+------+         +------+-+------+
a |      | |      |       a |      | |      |
b |      | |      |       b |      | |      |
c |     0|1|0     |  -->  c |     0|0|0     |
d |     1|1|1     |       d |     1|1|1     |
e |     0|0|0     |       e |     0|0|0     |
f |      | |      |       f |      | |      |
  +------+-+------+         +------+-+------+
```


# 参考文献

* 📖 [むずでょnote ＞ ビナーシ（Binarsi） を創ろう](https://note.com/muzudho/n/na5dce2824aa4)
* 📖 [やねうら王ブログ ＞ 対局ゲーム標準通信プロトコルの提案](https://yaneuraou.yaneu.com/2022/06/07/standard-communication-protocol-for-games/)
