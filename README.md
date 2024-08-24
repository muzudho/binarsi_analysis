# ビナーシ解析

**情報処理系しか遊べないリバーシ**  

`binary` （バイナリー） ＋ `riverse` （リバーシ） ＝ `binarsi` （ビナーシ）  


# 実行

```shell
python main.py
```


# 石と盤

コンピュータ将棋プログラミングをベースに、コンピュータ囲碁の知見、および、〇×ゲーム、リバーシ（オセロ）、連珠、そして計算機科学の一般的な知見も混ぜて（影響を受けて）います  


```
    1 2 3 4 5 6 7
  +---------------+
a |               |
b |               |
c |     0 1       |
d |               |
e |               |
f |               |
  +---------------+
```

👆　盤には石を置きます。図面には、石は先手（黒番）が 1、後手（白番）が 0 と書くとします  

慣例的に、動くものは駒（こま）、動かないものは石（いし）と呼ばれることが多いです。  
例えば、象棋（シャンチー）の駒は丸いですが、石ではなく駒と呼ばれています  

また、将棋のように駒をマス（Square）の中に置くか、囲碁のように石を交点上（Node）に置くかは　ゲームによって統一性が見られず　ばらけるようですが、  
〇×ゲームのように　ノートを開いて紙の上で遊ぶゲームでは　マスの中に〇×を書くことは視認性が良いです。  
ビナーシの盤は　〇×ゲームの盤を　横縦に　７：６　にしたものと解釈することにします  


# ゲームの目的（勝ち方の説明）

勝敗判定は３本制です。  

👇　先手は黒番です。以下の３つの図のように、３種類の　棒（同じ石が一列に並んだもの）を作れば勝ちです。  
一度作った棒は、あとで壊したり、壊されたりしても　すでに作ったものとして判定します。  
盤上のどの位置に作っても構いません。作る順番は任意です。同時に作っても構いません  

```
    1 2 3 4 5 6 7          1 2 3 4 5 6 7          1 2 3 4 5 6 7 
  +---------------+      +---------------+      +---------------+
a |               |    a |               |    a |     1         |
b |               |    b |     1         |    b |     1         |
c |     1 1 1     |    c |       1       |    c |     1         |
d |               |    d |         1     |    d |     1         |
e |               |    e |           1   |    e |     1         |
f |               |    f |               |    f |               |
  +---------------+      +---------------+      +---------------+
```

* 横に３つの 1 が並んだ棒
* 斜めに４つの 1 が並んだ棒（左右反転でも可）
* 縦に５つの 1 が並んだ棒

👇　後手は白番です。ルールは同様ですが、作る図面は異なり、以下の３つを作れば勝ちです  

```
    1 2 3 4 5 6 7          1 2 3 4 5 6 7          1 2 3 4 5 6 7 
  +---------------+      +---------------+      +---------------+
a |               |    a |               |    a |               |
b |       1       |    b |     1         |    b |               |
c |       1       |    c |       1       |    c |   1 1 1 1 1   |
d |       1       |    d |         1     |    d |               |
e |               |    e |           1   |    e |               |
f |               |    f |               |    f |               |
  +---------------+      +---------------+      +---------------+
```

* 縦に３つの 1 が並んだ棒
* 斜めに４つの 1 が並んだ棒（左右反転でも可）
* 横に５つの 1 が並んだ棒

TODO ただし、自分と相手が同時に勝つような指し手は禁止します  


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

👆　上図 `*` の場所は d段（d rank）、または d路（d way）と呼びます  


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
    1 2 3 4 5 6 7             1 2 # 4 5 6 7
  +----+-+--------+         +----+-+--------+
a |    | |        |       a |    | |        |
b |    | |        |       b |    | |        |
c |    |0|        |  -->  c |    |0|        |
d |    |1|        |       d |    |0|        |
e |    |0|        |       e |    |1|        |
f |    | |        |       f |    | |        |
  +----+-+--------+         +----+-+--------+
```

２ビットシフトすれば、２つずれます。  
０ビットシフトは禁止します  

また、 3筋の符号が `#` に変わりましたが、これは **路ロック** （Way lock）です。  
同じ路で反対の操作をやり返されると、永遠に局面が進まないので、その路への操作を禁止するものです。  
一度付いた　路ロック　は、同じ対局中に外れることはありません  

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

4路には、石が有っても無くても構いません。上図では 4路に石がなかったケースです。  
もともと石がなかった路に対して操作を行ったケースでは、路ロックは付きません  

👇　次に、単項演算が　**インプレース** （In-place；既に石の置いてあるところ）でもできる例を示します  

```
    1 2 3 4 5 6 7             1 2 3 # 5 6 7  
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
    1 2 3 4 5 6 7             1 2 3 # 5 6 7  
  +------+-+------+         +------+-+------+
a |      | |      |       a |      | |      |
b |      | |      |       b |      | |      |
c |     0|1|0     |  -->  c |     0|0|0     |
d |     1|1|1     |       d |     1|1|1     |
e |     0|0|0     |       e |     0|0|0     |
f |      | |      |       f |      | |      |
  +------+-+------+         +------+-+------+
```


# 付録：　演算子の説明


## SHIFT演算子

👇　１ビット回転論理右（下）シフト

このゲームでのコードは `s1`

|     | Bit field     |
|-----|---------------|
| In  | 0 0 0 0 1 0 0 |
| Out | 0 0 0 0 0 1 0 |


👇　２ビット回転論理右（下）シフト

このゲームでのコードは `s2`

|     | Bit field     |
|-----|---------------|
| In  | 0 0 0 0 1 0 0 |
| Out | 0 0 0 0 0 0 1 |


👇　３ビット回転論理右（下）シフト

このゲームでのコードは `s3`

|     | Bit field     |
|-----|---------------|
| In  | 0 0 0 0 1 0 0 |
| Out | 1 0 0 0 0 0 0 |


👇　４ビット回転論理右（下）シフト

このゲームでのコードは `s4`

|     | Bit field     |
|-----|---------------|
| In  | 0 0 0 0 1 0 0 |
| Out | 0 1 0 0 0 0 0 |


👇　５ビット回転論理右（下）シフト

このゲームでのコードは `s5`

|     | Bit field     |
|-----|---------------|
| In  | 0 0 0 0 1 0 0 |
| Out | 0 0 1 0 0 0 0 |


👇　６ビット回転論理右（下）シフト

このゲームでのコードは `s6`

|     | Bit field     |
|-----|---------------|
| In  | 0 0 0 0 1 0 0 |
| Out | 0 0 0 1 0 0 0 |


## NOT演算子

このゲームでのコードは `n`, `nH`, `nL`  

| In | Out |
|----|-----|
| 0  | 1   |
| 1  | 0   |


## AND演算子

このゲームでのコードは `a`  

In 1 と、 In 2 は、ひっくり返しても Out は同じ（以下同様）  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 0   |
| 0    | 1    | 0   |
| 1    | 1    | 1   |

In 1 と In 2 の **両方が** 1 のとき、 Out は 1  


## OR演算子

このゲームでのコードは `o`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 0   |
| 0    | 1    | 1   |
| 1    | 1    | 1   |

In 1 と In 2 の **いずれかが** 1 のとき、 Out は 1  


## XOR演算子

このゲームでのコードは `xo`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 0   |
| 0    | 1    | 1   |
| 1    | 1    | 0   |

In 1 と In 2 が **異なる** とき、 Out は 1  


## NAND演算子

このゲームでのコードは `na`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 1   |
| 0    | 1    | 1   |
| 1    | 1    | 0   |

AND演算の Out をさらに NOT演算したもの  


## NOR演算子

このゲームでのコードは `no`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 1   |
| 0    | 1    | 0   |
| 1    | 1    | 0   |

OR演算の Out をさらに NOT演算したもの  


## XNOR演算子

このゲームでのコードは `xn`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 1   |
| 0    | 1    | 0   |
| 1    | 1    | 1   |

XOR演算の Out をさらに NOT演算したもの  


## 0埋め

このゲームでのコードは `ze`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 0   |
| 0    | 1    | 0   |
| 1    | 1    | 0   |

プログラム内部的に用意はしていますが、対局で使うのは禁止です  


## 1埋め

このゲームでのコードは `on`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    | 1   |
| 0    | 1    | 1   |
| 1    | 1    | 1   |

プログラム内部的に用意はしていますが、対局で使うのは禁止です  


## 空欄埋め（カットザエッジ）

このゲームでのコードは `c`  

| In 1 | In 2 | Out |
|------|------|-----|
| 0    | 0    |     |
| 0    | 1    |     |
| 1    | 1    |     |

プログラム内部的に用意はしていますが、対局で使うのは禁止です  


# 参考文献

* 📖 [むずでょnote ＞ ビナーシ（Binarsi） を創ろう](https://note.com/muzudho/n/na5dce2824aa4)
* 📖 [やねうら王ブログ ＞ 対局ゲーム標準通信プロトコルの提案](https://yaneuraou.yaneu.com/2022/06/07/standard-communication-protocol-for-games/)
