# do コマンドリファレンス


## コマンドの書式

例：  

```
do 4n
```

書式：  

```
do [move]
```

👆 `do 4n` は、 ドゥー（Do）コマンドと呼びます  
また、コンピューターに指し手を選ばせる `go` コマンドというのもあるのでインターネットから USI プロトコルを調べてみてください  


## ムーブの書式

指し手（ムーブ；Move）の書式の説明です  

例：  

```
4n
```

書式：  

```
[way][operator]
```

👆 `4n` は、 **ムーブ** （Move）のコード（Code）と呼びます。  
`4n` は、 4 という **路** （ろ；Way） と、 n という **演算子** (えんざんし；Operator) の２つで構成されています  


👇 路には以下のものがあります（カンマで区切って１３個並べました）  

```
1, 2, 3, 4, 5, 6, 7, a, b, c, d, e, f
```

👇 演算には以下の２０個があります

```
零項演算（Nullary operation）
----------------------------

    s1
        右（下）回転論理１ビットシフト。
        Shift の頭文字 S と、１ビットの１から取って s1
        以下、s2 ～ s6 も同様

    s2
        ※ s1 演算参照

    s3
        ※ s1 演算参照

    s4
        ※ s1 演算参照

    s5
        ※ s1 演算参照

    s6
        ※ s1 演算参照

    c
        大石の辺を切り落とす操作。
        Cut of the edge の頭文字 C から取って c
    
    e
        編集（エディット）
        任意の石を指定して置くという操作です
        ※ 対局中に使うと反則です


単項演算（Unary operation）
--------------------------

    n
        否定（ノット）
        NOT operation の頭文字 N から取って n

    nH
        否定（ノットハイ）
        接尾辞の H は、 from Higher side の H から取ったもの

    nL
        否定（ノットロウ）
        接尾辞の L は、 from Lower side の L から取ったもの


二項演算（Binary operation）
---------------------------

    a
        論理積（アンド）
        AND operation の頭文字 A から取って a

    o
        論理和（オア）
        OR operation の頭文字 O から取って o

    xo
        排他的論理和（エクソア）
        一般的には、エクスクルーシブオアと呼びます。
        XOR operation の語頭 XO から取って xo

    na
        否定論理積（ナンド）
        NAND operation の語頭 NA から取って na

    no
        否定論理和（ノア）
        一般的には、ノットオアと呼びます。
        NOR operation の語頭 NO から取って no

    xn
        否定排他的論理和（エクスノア）
        一般的には、エクスクルーシブノットオアと呼びます。
        XNOR operation の語頭 XN から取って xn

    ze  識別子０（アイデンティティゼロ）
        常に０を返すという操作です
        英語で０を意味する zero の語頭 ze から取って ze
        ※ 対局中に使うと反則です

    on
        識別子１（アイデンティティワン）
        常に１を返すという操作です
        英語で１を意味する one の語頭 on から取って on
        ※ 対局中に使うと反則です
```


# 零項演算の説明

👇　いずれの do コマンドでも、指定した路（**対称路**と呼びます）の石が変更されます。例えば以下のような盤面があるとします  

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


# 単項演算の説明

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


# 二項演算の説明

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

