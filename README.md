# Message Reminder
## 概要
指定した時刻にリマインドしてくれるLINE Botです。

## 動作環境
- Python3
- Heroku
- LINE Messaging API

## 仕様
LINE Bot「Message Reminder」に個人またはグループで、
```
@remind
YYYY/MM/DD HH/MM
イベント名
```
と送信すると指定した時刻にイベントをリマインドします。
