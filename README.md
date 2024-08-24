# binarsi_analysis

ビナーシ解析


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

# 参考文献

* 📖 [むずでょnote ＞ ビナーシ（Binarsi） を創ろう](https://note.com/muzudho/n/na5dce2824aa4)
* 📖 [やねうら王ブログ ＞ 対局ゲーム標準通信プロトコルの提案](https://yaneuraou.yaneu.com/2022/06/07/standard-communication-protocol-for-games/)
