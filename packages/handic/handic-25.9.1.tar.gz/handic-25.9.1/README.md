# handic-py

![PyPI - Version](https://img.shields.io/pypi/v/handic)

This is a package to install [HanDic](https://github.com/okikirmui/handic), a dictionary for morphological analysis of Korean languages, via pip and use it in Python.

To use this package for morphological analysis, the MeCab wrapper such as [mecab-python3](https://github.com/SamuraiT/mecab-python3) is required.

**[notice]** After v.0.1.0, calendar versioning is used according to the dictionary version.

## Installation

from PyPI:

```Shell
pip install handic
```

## Usage

Since HanDic requires Hangul Jamo(Unicode Hangul Jamo) as input, please convert Hangul (Unicode Hangul Syllables) using modules such as [jamotools](https://pypi.org/project/jamotools/), or `tools/k2jamo.py` script included in HanDic.

### basic

example:

```Python
import MeCab
import handic
import jamotools

mecaboption = f'-r /dev/null -d {handic.DICDIR}'

tokenizer = MeCab.Tagger(mecaboption)
tokenizer.parse('')

# 《표준국어대사전》 "형태소" 뜻풀이
sentence = u'뜻을 가진 가장 작은 말의 단위. ‘이야기책’의 ‘이야기’, ‘책’ 따위이다.'

jamo = jamotools.split_syllables(sentence, jamo_type="JAMO")

node = tokenizer.parseToNode(jamo)
while node:
    print(node.surface, node.feature)
    node = node.next
```

result:

```Shell
BOS/EOS,*,*,*,*,*,*,*,*,*,*
뜻    Noun,普通,*,*,*,뜻,뜻,*,*,B,NNG
을    Ending,助詞,対格,*,*,을02,을,*,*,*,JKO
가지  Verb,自立,*,語基2,*,가지다,가지,*,*,A,VV
ᆫ       Ending,語尾,連体形,*,2接続,ㄴ05,ㄴ,*,*,*,ETM
가장 Adverb,一般,*,*,*,가장01,가장,*,*,A,MAG
작으 Adjective,自立,*,語基2,*,작다01,작으,*,*,A,VA
ᆫ       Ending,語尾,連体形,*,2接続,ㄴ05,ㄴ,*,*,*,ETM
말    Noun,普通,動作,*,*,말01,말,*,*,A,NNG
의     Ending,助詞,属格,*,*,의10,의,*,*,*,JKG
단위 Noun,普通,*,*,*,단위02,단위,單位,*,C,NNG
.       Symbol,ピリオド,*,*,*,.,.,*,*,*,SF
‘      Symbol,カッコ,引用符-始,*,*,‘,‘,*,*,*,SS
이야기책   Noun,普通,*,*,*,이야기책,이야기책,이야기冊,*,*,NNG
’      Symbol,カッコ,引用符-終,*,*,’,’,*,*,*,SS
의     Ending,助詞,属格,*,*,의10,의,*,*,*,JKG
‘      Symbol,カッコ,引用符-始,*,*,‘,‘,*,*,*,SS
이야기       Noun,普通,動作,*,*,이야기,이야기,*,*,A,NNG
’      Symbol,カッコ,引用符-終,*,*,’,’,*,*,*,SS
,       Symbol,コンマ,*,*,*,",",",",*,*,*,SP
‘      Symbol,カッコ,引用符-始,*,*,‘,‘,*,*,*,SS
책    Noun,普通,*,*,*,책01,책,冊,*,A,NNG
’      Symbol,カッコ,引用符-終,*,*,’,’,*,*,*,SS
따위  Noun,依存名詞,*,*,*,따위,따위,*,*,*,NNB
이     Siteisi,非自立,*,語基1,*,이다,이,*,*,*,VCP
다     Ending,語尾,終止形,*,1接続,다06,다,*,*,*,EF
.       Symbol,ピリオド,*,*,*,.,.,*,*,*,SF
BOS/EOS,*,*,*,*,*,*,*,*,*,*
```

### Tokenize

example:

```Python
mecaboption = f'-r /dev/null -d {handic.DICDIR} -Otokenize'
tokenizer = MeCab.Tagger(mecaboption)

print(tokenizer.parse(jamo))
```

result:

```Shell
뜻 을 가지 ㄴ 가장 작으 ㄴ 말 의 단위 . ‘ 이야기책 ’ 의 ‘ 이야기 ’ , ‘ 책 ’ 따위 이 다 .
```

### Extracting specific POS

example:

```Python
mecaboption = f'-r /dev/null -d {handic.DICDIR}'

tokenizer = MeCab.Tagger(mecaboption)
tokenizer.parse('')

node = tokenizer.parseToNode(jamo)
while node:
    # 일반명사(pos-tag: NNG)만 추출
    if node.feature.split(',')[10] in ['NNG']:
        print(node.feature.split(',')[5])
    node = node.next
```

result:

```Shell
뜻
말01
단위02
이야기책
이야기
책01
```

## Features

Here is the list of features included in HanDic. For more information, see the [HanDic 품사 정보](https://github.com/okikirmui/handic/blob/main/docs/pos_detail.md).

  - 품사1, 품사2, 품사3: part of speech(index: 0-2)
  - 활용형: conjugation "base"(ex. `語基1`, `語基2`, `語基3`)(index: 3)
  - 접속 정보: which "base" the ending is attached to(ex. `1接続`, `2接続`, etc.)(index: 4)
  - 사전 항목: base forms(index: 5)
  - 표층형: surface(index: 6)
  - 한자: for sino-words(index: 7)
  - 보충 정보: miscellaneous informations(index: 8)
  - 학습 수준: learning level(index: 9)
  - 세종계획 품사 태그: pos-tag(index: 10)

## License

This code is licensed under the MIT license. HanDic is copyright Yoshinori Sugai and distributed under the [BSD license](./LICENSE.handic). 

## Acknowledgment

This repository is forked from [unidic-lite](https://github.com/polm/unidic-lite) with some modifications and file additions and deletions.
