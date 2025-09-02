import os
import sys

import gradio as gr
from tqdm import tqdm

from finter.api.quanda_bot_api import QuandaBotApi


class gr_qb(QuandaBotApi):
    def __init__(self):
        self.thread_id = 0

    def quanda_bot(self, message, history):
        res = QuandaBotApi().gpt_quanda_bot_retrieve(user_chat=message, thread_id=self.thread_id) # api
        self.set_thread_id(res['thread_id'])
        answer = res["response"]
        # chat_history.append((message, answer))
        return answer
    
    def set_thread_id(self, new_thread_id=0):
        self.thread_id=new_thread_id

    def run(self):
        with gr.Blocks(
            theme=gr.themes.Soft(),
            title="QuandaBot",
        ) as demo:
            ci = gr.ChatInterface(
                fn=self.quanda_bot,
                title="Quanda Bot",
                description="""
                    * Dataset : price_volume, financial, ratio
                    * 금융 데이터를 기반으로 질문에 답변합니다.
                    * 질문 소요시간 : 최대 60초.
                    * 데이터 제공기간 2020.01 ~ 2024.01
                    """,
                theme="soft",
                examples=[
                    "삼성전자, 네이버, sk하이닉스 주가 그래프 그려줘",
                    "카카오 주가랑 거래량 그래프 그려줘",
                    "PER(주가수익비율)이 10 이하인 종목들 중, 총자산 대비 총부채 비율이 가장 낮은 종목은?",
                    "시가총액 기준 상위 10개 종목 중, 순이익(net_income)과 영업이익(operating_income)가 가장 긍정적인 종목은 무엇인가?",
                ],
                retry_btn=None,
                undo_btn=None,
                clear_btn=None,
            )

            clear_btn = gr.ClearButton([ci.chatbot, ci.chatbot_state, ci.saved_input], size='sm')
            clear_btn.click(fn=self.set_thread_id)
        return demo


def execute_quanda_bot():
    k = os.environ.get("FINTER_API_KEY", None)
    if not k:
        sys.stderr.write("Quanda Bot needs FINTER_API_KEY")
        sys.stderr.write(f"Your api key is '{k}'")
    else:
        print("RUNNING QUANDA_BOT")

    demo = gr_qb().run()
    demo.launch(share=True)
