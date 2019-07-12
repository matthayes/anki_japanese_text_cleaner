# Anki Japanese Text Cleaner

[![Build Status](https://travis-ci.org/matthayes/anki_japanese_text_cleaner.svg?branch=master)](https://travis-ci.org/matthayes/anki_japanese_text_cleaner.svg?branch=master)
[![Release](https://img.shields.io/badge/release-v0.1-brightgreen.svg)](https://github.com/matthayes/anki_japanese_text_cleaner/releases/tag/v0.1)

This is a plugin for [Anki](http://ankisrs.net/) that can help clean up Japanese text in the following ways:

**Clean unnecessary spaces**, while preserving those spaces that are necessary for indicating the start of a Japanese reading (as in the [Japanese Support plugin](https://ankiweb.net/shared/info/3918629684)).

```
<b> 一[いち]</b>から 始[はじ]めましょう。
=>
<b>一[いち]</b>から 始[はじ]めましょう。

彼女[かのじょ]はイタリア 語[ご]が<b> できます</b>。
=>
彼女[かのじょ]はイタリア 語[ご]が<b>できます</b>。
```

**Clean unnecessary furigana** from the beginning, end, or within individual readings within text.

```
別に[べつに]
=>
別[べつ]に

世の中[よのなか]
=>
世[よ]の 中[なか]
```

Both are designed to:

* Properly handle text with multiples lines
* Properly handle text with HTML markup by allowing HTML tags to pass through unchanged

In addition, there are some features to guard against accidental changes or bugs in the plugin:

* A `Check` action logs all changes that would be made without taking any action.
* A `Diff` action produces a colorful HTML diff highlighting in green what will been added and in red what will be removed for each note.
* A 'Fix' action actually performs the changes.
* Each batch of changes is recorded in the undo history within Anki.
* A full change log is kept in a SQLite database within the plugin's local directory.  Recent changes can be viewed in the UI and the full history of changes can be exported to a CSV file.  This enables you to recover any previous values altered by the plugin.

Despite these safety features, it's a good idea to back up or export your collection before using this plugin just to be safe.

You can access the dialogs by clicking *Browse* to open the card browser and then clicking Edit -> Japanese Text Cleaner.  The fixer dialgos require you to select some cards first.  These are the cards that will be checked.

## Testing

I have tested against the following shared decks which I found on Anki's [Japanese shared decks page](https://ankiweb.net/shared/decks/japanese).  Below I include some stats as of July 10, 2019 when I lasted tested the plugin against the decks.

| Deck | Notes | Field | Spacing Fixes | Furigana Fixes |
| ---- | ----- | ----- | ------------- | -------------- |
|[Japanese Core 2000 2k - Sorted w/ Audio](https://ankiweb.net/shared/info/2141233552)|2007|Reading|266|1|
|[Japanese Visual Novel, Anime, Manga, LN Vocab - V2K](https://ankiweb.net/shared/info/1434910726)|1988|Reading|4|55|

To get a better idea about how the plugin works, I've included some examples from each deck.

### Examples: Japanese Core 2000 2k

Unnecessary space removed from beginning of line:

```
<b> 一[いち]</b>から 始[はじ]めましょう。
=>
<b>一[いち]</b>から 始[はじ]めましょう。
```

```
<b> 月曜日[げつようび]</b>に 会[あ]いましょう。
=>
<b>月曜日[げつようび]</b>に 会[あ]いましょう。
```

Unnecessary space removed from within line:

```
彼女[かのじょ]はイタリア 語[ご]が<b> できます</b>。
=>
彼女[かのじょ]はイタリア 語[ご]が<b>できます</b>。
```

Redundant furigana removed from end of word:

```
彼女[かのじょ]はよく<b>喋る[しゃべる]</b>ね。
=>
彼女[かのじょ]はよく<b>喋[しゃべ]る</b>ね。
```

### Examples: Japanese Visual Novel, Anime, Manga, LN Vocab

Redundant furigana removed from the end:

```
別に[べつに]
=>
別[べつ]に
```

```
疲れる[つかれる]
=>
疲[つか]れる
```

```
相変わらず[あいかわらず]
=>
相変[あいか]わらず
```

Redunant furigana removed from the middle:

```
当たり前[あたりまえ]
=>
当[あ]たり 前[まえ]
```

```
振り返る[ふりかえる]
=>
振[ふ]り 返[かえ]る
```

```
世の中[よのなか]
=>
世[よ]の 中[なか]
```

Unnecessary space removed:

```
杯[はい],   杯[さかずき]
=>
杯[はい], 杯[さかずき]
```

## Version History

* 0.1: Initial Release

## License

Copyright 2019 Matthew Hayes

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
