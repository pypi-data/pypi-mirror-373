![GitHub Workflow Status](https://github.com/metaboatrace/scrapers/actions/workflows/publish.yml/badge.svg)
![GitHub Workflow Status](https://github.com/metaboatrace/scrapers/actions/workflows/tests.yml/badge.svg)
![GitHub Workflow Status](https://github.com/metaboatrace/scrapers/actions/workflows/lint.yml/badge.svg)
![Coverage](https://img.shields.io/codecov/c/github/metaboatrace/scrapers.svg)
![PyPI version](https://img.shields.io/pypi/v/metaboatrace.scrapers.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python version](https://img.shields.io/badge/python-3.11-blue.svg)
![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)

## 概要

ボートレース関連の WEB サイトのスクレイピングライブラリ

以下の機能を備える

- [ボートレース公式サイト](https://boatrace.jp/) に対応する下記
  - URL の生成
  - スクレイピング

## パッケージの構成

名前空間パッケージになっており、共通の名前空間 (`metaboatrace`) を保持する同種のパッケージがある。

- [metaboatrace.models](https://github.com/metaboatrace/models)

### ボートレース公式サイトに対応する規約

名前空間は以下のように切られている。

- metaboatrace.scrapers.official.website.v1707

この `v1707` の部分はボートレース公式サイトのバージョンに対応している。

バージョニングは、Ubuntu でのそれに近い。  
Ubuntu は 22.04 のように年と月という形でバージョニングされている（22.04.1 のようセキュリティパッチのリビジョンも付くことがある）。

ボートレースの公式サイトが現行のものになったのは 2017 年の 7 月なので、それに合わせてここでは `v1707` としている。

## 機能

`metaboatrace/scrapers/official/website/v1707/pages` 直下に、公式サイトのページに対応した名前空間がある。  
例えば、[公式サイトの月間スケジュール](https://boatrace.jp/owpc/pc/race/monthlyschedule)に対応するものは `monthly_schedule_page` である。

これらの配下に `location` と `scraping` というモジュールがある。

前者は引数（日付など）をもとに公式サイトの URL を生成するような責務を負った関数が包含されている。  
例えば、年と月を与えたら "https://boatrace.jp/owpc/pc/race/monthlyschedule?ym=202209" といったそのデータに対応する公式サイトの月間スケジュールの URL を返すような関数が入っている。

後者は、公式サイトの HTML ファイルをスクレイピングのモジュールである。  
例えば、ここに入ってる関数は "https://boatrace.jp/owpc/pc/race/monthlyschedule?ym=202209" のファイルをスクレイピングして[エンティティ](https://github.com/metaboatrace/models)を返すような処理を行う。

※ ここでいうエンティティはクリーンアーキテクチャの定義上のエンティティのことであり、[metaboatrace.models](https://github.com/metaboatrace/models)はそういったものを提供しているパッケージ
