

from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import warnings
from linebot import LineBotSdkDeprecatedIn30

app = Flask(__name__)

@app.route("/send")
def home():
  line_bot_api = LineBotApi('你的密碼')
  try:
    # 網址被執行時，等同使用 GET 方法發送 request，觸發 LINE Message API 的 push_message 方法 userID=='Uaf1c91579f554baa611bd9218ef373fa'
    line_bot_api.push_message('你的密碼', TextSendMessage(text=exsmall60))
    return 'OK'
  except:
    print('error')

if __name__ == "__main__":
  
    warnings.filterwarnings("ignore", category=LineBotSdkDeprecatedIn30)
    
    app.run()