import openai
import whisper
import json
import requests
import wave
import time # タイムラグをつける
import pyaudio
import speech_recognition as sr
from io import BytesIO

# OpenAI API認証の設定
openai.api_key = "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"

def generate_wav(text, speaker=1, filepath='./audio.wav'):
    host = 'localhost'
    port = 50021
    params = (
        ('text', text),
        ('speaker', speaker),
    )
    response1 = requests.post(
        f'http://{host}:{port}/audio_query',
        params=params
    )
    headers = {'Content-Type': 'application/json',}
    response2 = requests.post(
        f'http://{host}:{port}/synthesis',
        headers=headers,
        params=params,
        data=json.dumps(response1.json())
    )
    data = response2.content
    # PyAudioのインスタンスを生成
    p = pyaudio.PyAudio()
    # ストリームを開く
    stream = p.open(format=pyaudio.paInt16,  # 16ビット整数で表されるWAVデータ
                    channels=1,  # モノラル
                    rate=24000,  # サンプリングレート
                    output=True)
    # 再生を少し遅らせる（開始時ノイズが入るため）
    time.sleep(0.2) # 0.2秒遅らせる
    # WAV データを直接再生する
    stream.write(data)  
    # ストリームを閉じる
    stream.stop_stream()
    stream.close()
    # PyAudio のインスタンスを終了する
    p.terminate()

r = sr.Recognizer()
with sr.Microphone(sample_rate=16_000) as source:
    print("なにか話してください")
    audio = r.listen(source)
    print("音声を取得しました")

audio_data = BytesIO(audio.get_wav_data())
audio_data.name = "from_mic.wav"
transcript = openai.Audio.transcribe("whisper-1", audio_data)
# print(transcript["text"])

print("リクエスト")
print(transcript["text"])

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        # {"role": "user", "content": "あなたはとても友好的な英会話の講師です"}, 
        {"role": "user", "content": transcript["text"]}, #※1後述
    ]
)
result_text = response["choices"][0]["message"]["content"]
result_text = result_text.replace("。", "。\n")
print("レスポンス")
print(result_text)
generate_wav(result_text)
