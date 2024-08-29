# ビナーシ解析

**情報処理系しか遊べないリバーシ**  

`binary` （バイナリー） ＋ `riverse` （リバーシ） ＝ `binarsi` （ビナーシ）  


# 道具の説明

## 盤（board）と石（Stone）

```
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . 0 1 . . . |
d | . . . . . . . |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+
```

👆 横 7 マス、縦 6 マスの盤を使います  

先手は黒石（図では `1`）、後手は白石（図では `0`） が自分の石の色です。  


# ゲームの目的（勝ち方の説明）

細かなことはこれから説明しますが、クリアーターゲットを３本先取した方の勝ちです。（**三本勝負**）  

クリアーターゲットを３本取るするのが同時だった場合（**同着**と呼びます）、または、これ以上プレイを続行できなくなり、どちらのプレイヤーも３本先取できなかった場合（**満局**と呼びます）、盤上の石の数の合計で勝ちを決めます（**点数計算**）  

ビナーシでは、**引き分け**、**千日手**（同じ手順が永遠に繰り返されて終わらないこと）は発生しません  


## 三本勝負

👇 クリアーターゲットは黒番と白番で異なり、それぞれ以下の３つずつあります  

```
黒番のクリアーターゲットの例：

    1 2 3 4 5 6 7          1 2 3 4 5 6 7          1 2 3 4 5 6 7 
  +---------------+      +---------------+      +---------------+
a | . . . . . . . |    a | . . . . . . . |    a | . . 1 . . . . |
b | . . . . . . . |    b | . . 1 . . . . |    b | . . 1 . . . . |
c | . . 1 1 1 . . |    c | . . . 1 . . . |    c | . . 1 . . . . |
d | . . . . . . . |    d | . . . . 1 . . |    d | . . 1 . . . . |
e | . . . . . . . |    e | . . . . . 1 . |    e | . . 1 . . . . |
f | . . . . . . . |    f | . . . . . . . |    f | . . . . . . . |
  +---------------+      +---------------+      +---------------+
       ヨコさん               ナナメよん                タテご


白番のクリアーターゲットの例：

    1 2 3 4 5 6 7          1 2 3 4 5 6 7          1 2 3 4 5 6 7 
  +---------------+      +---------------+      +---------------+
a | . . . . . . . |    a | . . . . . . . |    a | . . . . . . . |
b | . . . 1 . . . |    b | . . 1 . . . . |    b | . . . . . . . |
c | . . . 1 . . . |    c | . . . 1 . . . |    c | . 1 1 1 1 1 . |
d | . . . 1 . . . |    d | . . . . 1 . . |    d | . . . . . . . |
e | . . . . . . . |    e | . . . . . 1 . |    e | . . . . . . . |
f | . . . . . . . |    f | . . . . . . . |    f | . . . . . . . |
  +---------------+      +---------------+      +---------------+
       タテさん               ナナメよん                ヨコご
```

👆 やることは　３目並べ、４目並べ、５目並べ のように **棒** （同じ石が一列に並んだもの）を作ることです。ただし、制限があります。  
タテに作るか、ヨコに作るか、ナナメに作るかの指定があるので従ってください。ナナメは左上がりでも右上がりでもどちらでも構いません。  
また、指定が黒番と白番でクリアーターゲットが異なることに注意してください  

* 一度作った棒は、あとで壊したり、壊されたりしても構いません。既にクリアーしたものとして判定します
* クリアーターゲットを獲得する順番は任意です。同時に獲得しても構いません
* 棒は盤上のどの位置に作っても構いません


## 点数計算

盤上に置いてある石１つが１点です。  
後手（白番）は、盤上の石とは別に、最初から 0.5 点を持っているとします（これを**コミ 0.5**と呼びます）  
点数が多い方の勝ちです


# このPythonスクリプトの実行

```shell
python main.py
```


# 遊び方

Pythonスクリプトを実行してから、ターミナルに以下のコマンドを打鍵して遊んでください  

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
ゲームの対局が始まった状態になっていますが、まだ、このままではゲームは始めることができません  

Input:  

```shell
position startpos
```

👆　上記のコマンドを打鍵してください。 **平手初期局面（ひらてしょききょくめん）** になります。応答はありません  
平手初期局面については、あとで説明します  

Input:  

```shell
board
```

Output:  

```
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

👆　`board` と打鍵すると、現局面が表示されます。  
まっさらな状態から、 3c の位置に `0` が１つ置いてある盤面を　平手初期局面　と呼びます  


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


次に、  

Input:  

```shell
sfen
```

Output:  

```
[from beginning] sfen startpos
[from present]   sfen startpos
```

👆　`sfen` と打鍵すると、２種類の SFEN が表示されます。  
平手初期局面ではどちらも同じですが、局面が進んでいくと、前者の方は棋譜が付き、後者の方は途中図の盤面が付きます  

Input:  

```shell
clear_targets
```

Output:  

```
CLEAR TARGETS
-------------

     [b3]           [b4]           [b5]           [w3]           [w4]           [w5]
+-----------+  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+
| . . . . . |  | 1 . . . . |  | . . 1 . . |  | . . . . . |  | 0 . . . . |  | . . . . . |
| . . . . . |  | . 1 . . . |  | . . 1 . . |  | . . 0 . . |  | . 0 . . . |  | . . . . . |
| . 1 1 1 . |  | . . 1 . . |  | . . 1 . . |  | . . 0 . . |  | . . 0 . . |  | 0 0 0 0 0 |
| . . . . . |  | . . . 1 . |  | . . 1 . . |  | . . 0 . . |  | . . . 0 . |  | . . . . . |
| . . . . . |  | . . . . . |  | . . 1 . . |  | . . . . . |  | . . . . . |  | . . . . . |
+-----------+  +-----------+  +-----------+  +-----------+  +-----------+  +-----------+

    WANTED         WANTED         WANTED         WANTED         WANTED         WANTED
-------------
```

👆 `clear_targets` と打鍵すると、クリアー目標の一覧が表示されます  

次に ...  

Input:  

```shell
legal_moves
```

Output:  

```
LEGAL MOVES
+--------+---+
|Distinct|All| Command
+--------+---+
|       1|  1| play 2n
|       2|  2| play 4n
|       3|  3| play bn
|       4|  4| play dn
+--------+---+
```

👆　`legal_moves` と打鍵すると、合法手の一覧が数字、アルファベット順に表示されます  

局面が進んでいくと、合法手は多いのに、どれを選んでも同じ結果になるケース（この手を**セームムーブ**（Same Move）と呼びます）も出てきます。  

連番の左側は Distinct です。２つ目以降のセームムーブを省いた連番です。  
連番の右側は、すべての合法手の連番です  

Input:  

```shell
play 4n
```

Output:  

```
       ___
      /   |
     /    |
    |__   |
      |   |
      |   |
      |___|
[ 1 moves | moved 4n | next white]
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . 0 1 . . . |
d | . . . . . . . |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+
[from beginning] sfen 7/7/2o4/7/7/7 w - - 0 moves 4n
                 stones_before_change -
[from present]   sfen 7/7/2ox3/7/7/7 w - - 1

     ________   ________    ______  ______   ________
    /   ____|  /   __   |  |   __ |/ __   |  |   __  |
    |  /       |  |  |  |  |  |  |  |  |  |  |  |  |  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  |__/  |
    |  |       |  |  |  |  |  |  |  |  |  |  |  _____/
    |  |____   |  |_/   |  |  |  |  |  |  |  |  |
    |_______|  |_______/   |__|  |__|  |__|  |__|
     ________
    /   __   |
    |  /  |  |
    |  |  |  |
    |  |  |  |
    |  |_/   |
    |_______/
[ 2 moves | moved cs1 | next black]
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
# | . . 1 0 . . . |
d | . . . . . . . |
e | . . . . . . . |
f | . . . . . . . |
  +---------------+
[from beginning] sfen startpos moves 4n cs1
                 stones_before_change - -
[from present]   sfen 7/7/2xo3/7/7/7 b c - 2

     __     ___   ________    __    __ 
    |  |   /  /  /   __   |  |  |  |  |
    |  |__/  /   |  |  |  |  |  |  |  |
    |__    _/    |  |  |  |  |  |  |  |
       |  |      |  |  |  |  |  |  |  |
       |  |      |  |_/   |  |  |_/   |
       |__|      |_______/   |_______/
```

👆　試しに `play 4n` と打鍵してください。  
いろいろと出力が流れていきますが、４筋のc段に `1` が追加されます。  
これは３筋全体を、４筋全体へ **NOT演算（ノットえんざん）** したものです  

NOT演算や、他にどんな演算があるかについては、あとで説明します  

`play` コマンドを打鍵したことで、 **コンピューターがランダムに手を打ち返してくれました。**  
`play` の代わりに `do` と打鍵すれば、コンピューターが手を返すということはありません。自分の研究用に使えます  

例： `do 4n`  


👇 以下に細かな説明を置きますが、読み飛ばしてもらって構いません  
📖 [playコマンドリファレンス](./docs/play_command_reference.md)  

演算子の詳細については、あとで付録として説明します  

👇　いずれの play コマンドでも、指定した路が **対称路** になります。例えば以下のような盤面があるとします  

```
    1 2 3 4 5 6 7
  +---------------+
a | . . . . . . . |
b | . . . . . . . |
c | . . 0 . . . . |
d | . . 1 . . . . |
e | . . 0 . . . . |
f | . . . . . . . |
  +---------------+
```

👇　ここで零項演算で　3路　を指定し、１ビットシフトすると下図のようになります

```
    1 2 3 4 5 6 7             1 2 # 4 5 6 7
  +----+-+--------+         +----+-+--------+
a | . .| |. . . . |       a | . .| |. . . . |
b | . .| |. . . . |       b | . .| |. . . . |
c | . .|0|. . . . |  -->  c | . .|0|. . . . |
d | . .|1|. . . . |       d | . .|0|. . . . |
e | . .|0|. . . . |       e | . .|1|. . . . |
f | . .| |. . . . |       f | . .| |. . . . |
  +----+-+--------+         +----+-+--------+
```

２ビットシフトすれば、２つずれます。  
０ビットシフトは禁じ手です。できません  

また、盤面の 3筋の符号が `#` に変わりましたが、これは **路ロック** （Way lock）です。  
同じ路で反対の操作をやり返されると、永遠に局面が進まないので、その路への操作を禁止するものです。  
一度付いた　路ロック　は、同じ対局中に外れることはありません  

👇　次に、単項演算で　4路　を指定し、 NOT演算した例を示します  

```
    1 2 3 4 5 6 7             1 2 3 4 5 6 7  
  +------+-+------+         +------+-+------+
a | . . .| |. . . |       a | . . .| |. . . |
b | . . .| |. . . |       b | . . .| |. . . |
c | . . 0| |. . . |  -->  c | . . 0|1|. . . |
d | . . 1| |. . . |       d | . . 1|0|. . . |
e | . . 0| |. . . |       e | . . 0|1|. . . |
f | . . .| |. . . |       f | . . .| |. . . |
  +------+-+------+         +------+-+------+
```

4路には、石が有っても無くても構いません。上図では 4路に石がなかったケースです。  
もともと石がなかった路に対して操作を行ったケースでは、路ロックは付きません  

👇　次に、単項演算が　**インプレース** （In-place；既に石の置いてあるところ）でもできる例を示します  

```
    1 2 3 4 5 6 7             1 2 3 # 5 6 7  
  +------+-+------+         +------+-+------+
a | . . .| |. . . |       a | . . .| |. . . |
b | . . .| |. . . |       b | . . .| |. . . |
c | . . 0|1|1 . . |  -->  c | . . 0|0|1 . . |
d | . . 1|1|0 . . |       d | . . 1|1|0 . . |
e | . . 0|0|0 . . |       e | . . 0|1|0 . . |
f | . . .| |. . . |       f | . . .| |. . . |
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
a | . . . .| |. . |       a | . . . .| |. . |
b | . . . .| |. . |       b | . . . .| |. . |
c | . . 0 1| |. . |  -->  c | . . 0 1|0|. . |
d | . . 1 1| |. . |       d | . . 1 1|1|. . |
e | . . 0 0| |. . |       e | . . 0 0|0|. . |
f | . . . .| |. . |       f | . . . .| |. . |
  +--------+-+----+         +--------+-+----+
```

👇　改変する例。  
二項演算で改変する際は、両隣りの路を入力として使います  

```
    1 2 3 4 5 6 7             1 2 3 # 5 6 7  
  +------+-+------+         +------+-+------+
a | . . .| |. . . |       a | . . .| |. . . |
b | . . .| |. . . |       b | . . .| |. . . |
c | . . 0|1|0 . . |  -->  c | . . 0|0|0 . . |
d | . . 1|1|1 . . |       d | . . 1|1|1 . . |
e | . . 0|0|0 . . |       e | . . 0|0|0 . . |
f | . . .| |. . . |       f | . . .| |. . . |
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


## 編集（エディット）

このゲームでのコードは `e`  

| Out |
|-----|
|     |
|  0  |
|  1  |

任意の石、または空欄で上書きします。プログラム内部的に用意はしていますが、対局で使うのは禁止です  


使い方：  

```
do &4e#$..10..

    1 2 3 4 5 6 7             1 2 3 4 5 6 7  
  +------+-+------+         +------+-+------+
a | . . .| |. . . |       a | . . .|.|. . . |
b | . . .| |. . . |       b | . . .|.|. . . |
c | . . 0| |. . . |  -->  c | . . 0|1|. . . |
d | . . 1| |. . . |       d | . . 1|0|. . . |
e | . . .| |. . . |       e | . . .|.|. . . |
f | . . .| |. . . |       f | . . .|.|. . . |
  +------+-+------+         +------+-+------+
```

👆 先頭の `&` は（対局ではなく）盤面編集であることを示します。  
`4` は筋、 `e` は EDIT操作、 `#` は 路ロックをしない指示です。  
`$` 記号の後ろには a段～f段の順で石を並べます。空欄は `.`、黒石は `1`、白石は `0` です  


# 参考文献

* 📖 [むずでょnote ＞ ビナーシ（Binarsi） を創ろう](https://note.com/muzudho/n/na5dce2824aa4)
* 📖 [やねうら王ブログ ＞ 対局ゲーム標準通信プロトコルの提案](https://yaneuraou.yaneu.com/2022/06/07/standard-communication-protocol-for-games/)
