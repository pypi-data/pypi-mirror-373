# nkhandic-py

![PyPI - Version](https://img.shields.io/pypi/v/nkhandic)

This is a package to install [NK-HanDic](https://github.com/okikirmui/nkhandic), a dictionary for morphological analysis of North Korean languages, via pip and use it in Python.

To use this package for morphological analysis, the MeCab wrapper such as [mecab-python3](https://github.com/SamuraiT/mecab-python3) is required.

**[notice]** After v.0.1.3, calendar versioning is used according to the dictionary version.

## Installation

from PyPI:

```Shell
pip install nkhandic
```

## Usage

Since NK-HanDic requires Hangul Jamo(Unicode Hangul Jamo) as input, please convert Hangul (Unicode Hangul Syllables) using modules such as [jamotools](https://pypi.org/project/jamotools/), or `tools/k2jamo.py` script included in NK-HanDic.

### basic

example:

```Python
import MeCab
import nkhandic
import jamotools

mecaboption = f'-r /dev/null -d {nkhandic.DICDIR}'

tokenizer = MeCab.Tagger(mecaboption)
tokenizer.parse('')

# 로동신문 2024년 5월 1일자 사설
sentence = u'경애하는 총비서동지에 대한 절대적인 충성심을 지니고 당중앙의 구상과 결심을 철저한 실천행동으로 받들어나가야 한다.'

jamo = jamotools.split_syllables(sentence, jamo_type="JAMO")

node = tokenizer.parseToNode(jamo)
while node:
    print(node.surface, node.feature)
    node = node.next
```

result:

```Shell
BOS/EOS,*,*,*,*,*,*,*,*,*,*
경애 Noun,普通,*,*,*,경애01,경애,敬愛,*,*,NNG
하 Suffix,動詞派生,*,語基2,*,하다02,하,*,*,*,XSV
는 Ending,語尾,連体形,*,1接続,는03,는,*,*,*,ETM
총비서 Noun,普通,*,*,*,총비서,총비서,總秘書,*,*,NNG
동지 Noun,普通,*,*,*,동지006,동지,同志,*,*,NNG,&북한어,"이름 아래 쓰여 존경과 흠모의 정을 나타내는 말."
에 Ending,助詞,処格,*,*,에04,에,*,*,*,JKB
대하 Verb,自立,*,語基2,*,대하다02,대하,對하,*,B,VV
ᆫ Ending,語尾,連体形,*,2接続,ㄴ05,ㄴ,*,*,*,ETM
절대 Noun,普通,*,*,*,절대05,절대,絶對,*,C,NNG
적 Suffix,名詞派生,*,*,*,적18,적,的,사상적,*,XSN
이 Siteisi,非自立,*,語基2,*,이다,이,*,*,*,VCP
ᆫ Ending,語尾,連体形,*,2接続,ㄴ05,ㄴ,*,*,*,ETM
충성심 Noun,普通,*,*,*,충성심,충성심,忠誠心,*,*,NNG
을 Ending,助詞,対格,*,*,을02,을,*,*,*,JKO
지니 Verb,自立,*,語基1,*,지니다,지니,*,*,C,VV
고 Ending,語尾,接続形,*,1接続,고25,고,*,*,*,EC
당중앙 Noun,普通,*,*,*,당중앙001,당중앙,黨中央,*,*,NNG,&북한어,"북한에서, 당 대회와 당 대회 사이에 노동당의 노선과 정책을 세우고 그 집행을 조직하고 지도하는 최고 지도 기관."
의 Ending,助詞,属格,*,*,의10,의,*,*,*,JKG
구상 Noun,普通,動作,*,*,구상08,구상,構想,*,*,NNG
과 Ending,助詞,接続助詞,*,*,과12,과,*,*,*,JC
결심 Noun,普通,動作,*,*,결심01,결심,決心,*,C,NNG
을 Ending,助詞,対格,*,*,을02,을,*,*,*,JKO
철저 Noun,普通,状態,*,*,철저,철저,徹底,*,*,NNG
하 Suffix,形容詞派生,*,語基2,*,하다02,하,*,*,*,XSA
ᆫ Ending,語尾,連体形,*,2接続,ㄴ05,ㄴ,*,*,*,ETM
실천 Noun,普通,動作,*,*,실천01,실천,實踐,*,C,NNG
행동 Noun,普通,動作,*,*,행동,행동,行動,*,B,NNG
으로 Ending,助詞,具格,*,*,으로,으로,*,*,*,JKB
받들어 Verb,自立,ㄹ語幹,語基3,*,받들다,받들어,*,*,*,VV
나가 Verb,非自立,*,語基1,3接続,나가다,나가,*,*,A,VX
야 Ending,語尾,接続形,*,3接続,야80,야,*,"-아야/어야",*,EC
하 Verb,非自立,*,語基2,*,하다01,하,*,*,A,VX
ᆫ다 Ending,語尾,終止形,*,2接続,ㄴ다01,ㄴ다,*,*,*,EF
. Symbol,ピリオド,*,*,*,.,.,*,*,*,SF
BOS/EOS,*,*,*,*,*,*,*,*,*,*
```

### Extracting specific POS

example:

```Python
# 일반명사(pos-tag: NNG)만 추출
node = tokenizer.parseToNode(jamo)
while node:
    if node.feature.split(',')[10] in ['NNG']:
        # 사전 항목(base forms)을 출력
        print(node.feature.split(',')[5])
    node = node.next
```

result:

```Shell
경애01
총비서
동지006
절대05
충성심
당중앙001
구상08
결심01
철저
실천01
행동
```

### Tokenize

example:

```Python
mecaboption = f'-r /dev/null -d {nkhandic.DICDIR} -Otokenize'
tokenizer = MeCab.Tagger(mecaboption)

print(tokenizer.parse(jamo))
```

result:

```Shell
경애 하 는 총비서 동지 에 대하 ㄴ 절대 적 이 ㄴ 충성심 을 지니 고 당중앙 의 구상 과 결심 을 철저 하 ㄴ 실천 행동 으로 받들어 나가 야 하 ㄴ다 .
```

## Features

Here is the list of features included in NK-HanDic. For more information, see the [NK-HanDic 품사 정보](https://github.com/okikirmui/nkhandic/blob/main/docs/pos_detail.md).

  - 품사1, 품사2, 품사3: part of speech(index: 0-2)
  - 활용형: conjugation "base"(ex. `語基1`, `語基2`, `語基3`)(index: 3)
  - 접속 정보: which "base" the ending is attached to(ex. `1接続`, `2接続`, etc.)(index: 4)
  - 사전 항목: base forms(index: 5)
  - 표층형: surface(index: 6)
  - 한자: for sino-words(index: 7)
  - 보충 정보: miscellaneous informations(index: 8)
  - 학습 수준: learning level(index: 9)
  - 세종계획 품사 태그: pos-tag(index: 10)
  - 조선어 표시(optional): for North Korean words(index: 11)
  - 뜻풀이(optional): for North Korean words(index: 12)

## License

This code is licensed under the MIT license. NK-HanDic is copyright Yoshinori Sugai and distributed under the [BSD license](./LICENSE.nkhandic). 

## Acknowledgment

This repository is forked from [unidic-lite](https://github.com/polm/unidic-lite) with some modifications and file additions and deletions.
