# インポートするライブラリ
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)
import os
import re
import datetime
import time

# 軽量なウェブアプリケーションフレームワーク:Flask
app = Flask(__name__)

#環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
#環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 以下変更箇所

# 応答メッセージを送信する
def reply(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message)
    )

# @remindでタグ付けされたメッセージを処理
def set_remind(event, content):
    try:
        # 時刻指定を抽出
        remind_time = re.match(
            r'\d{4}/\d{1,2}/\d{1,2}\s\d{1,2}:\d{2}',
            content
        ).group()
        # イベント名を抽出
        event_name = content[len(remind_time):].strip()
        # 時刻指定をdatetimeオブジェクトに変換
        remind_time = datetime.datetime.strptime(remind_time, '%Y/%m/%d %H:%M')
        # 現在時刻を取得
        now = datetime.datetime.now()
        # 指定時刻と現在時刻の差分を取得
        diff_time = remind_time - now
        diff_time = int(diff_time.total_seconds())
        # 指定時刻が現在時刻より後の場合
        if 0 < diff_time:
            # 受理した場合の処理
            reply(event, remind_time.strftime("【お知らせ】\n%-m月%-d日 の %-H:%M ") + f"に {event_name} をお知らせします")
            # 指定時刻まで待機
            time.sleep(diff_time)
            # リマインドする
            remind(event, event_name)
        # 指定時刻が現在時刻より前の場合
        else:
            # エラーを送信
            reply(event, "現在時刻より後に設定してください")
    except:
        # @remind以降のフォーマットが合っていない場合の処理
        # フォーマットのテンプレートを送信
        reply(event, "@remind\nYYYY/MM/DD HH:MM\nイベント名")

# リマインドを送信する
def remind(event, event_name):
    try:
        # グループ・トークルームから送信された場合
        id = event.source.group_id
    except:
        # 個人から送信された場合
        profile = line_bot_api.get_profile(event.source.user_id)
        id = profile.user_id
    # メッセージ内容を作成
    message = TextSendMessage(
        text=f"【お知らせ】\n{event_name} の時間です"
    )
    # リマインドを送信
    line_bot_api.push_message(id, message)

# MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # @remindが文頭に付いている場合
    if event.message.text[:7] == "@remind":
        # @remindを除いたメッセージを渡して処理
        set_remind(event, event.message.text[7:].strip())

# 以上変更箇所

if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
