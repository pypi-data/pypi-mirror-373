import os

import pandas as pd

from finter import NotebookSubmissionHelper
from finter.data import ContentFactory

# Todo: Check Unique Symbol
from finter.modeling.saa_temp import SYMBOL_DICT


class StrategicAssetAllocation:
    def __init__(
        self,
        model_universe="kr_stock",
        model_type="alpha",
        start=20200101,
        end=20240101,
    ):
        self.model_universe = model_universe
        self.model_type = model_type
        self.start, self.end = start, end
        cf = ContentFactory(self.model_universe, self.start, self.end)
        self.stock_price = cf.get_df("price_close")

    def show(self):
        import matplotlib.pyplot as plt
        from ipywidgets import (
            Button,
            FloatText,
            Layout,
            Output,
            VBox,
            interact,
            widgets,
        )

        stock_price = self.stock_price

        tags = widgets.TagsInput(
            value=[], allowed_tags=list(SYMBOL_DICT.values()), allow_duplicates=False
        )

        input_form = Output()
        output = Output()
        results_output = Output()

        def plot_prices(entity_names):
            output.clear_output(wait=True)
            with output:
                if entity_names:
                    plt.figure(figsize=(10, 4))
                    for entity_name in entity_names:
                        ccid = next(
                            (k for k, v in SYMBOL_DICT.items() if v == entity_name),
                            None,
                        )
                        plt.plot(
                            stock_price.index, stock_price[ccid], label=entity_name
                        )
                    plt.title("Price Data")
                    plt.legend()
                    plt.xlabel("Date")
                    plt.ylabel("Price")
                    plt.grid(True)
                    plt.show()
                    create_input_form(entity_names)

        def update_allocation(inputs):
            total = sum(input.value for input in inputs)
            if total != 100:
                remaining = 100 - total + inputs[-1].value
                inputs[-1].value = max(0, remaining)

        def create_input_form(entity_names):
            input_form.clear_output()
            with input_form:
                style = {"description_width": "initial"}
                inputs = [
                    FloatText(
                        description=name,
                        value=0,
                        layout=Layout(width="300px"),
                        style=style,
                    )
                    for name in entity_names
                ]
                for input_widget in inputs:
                    input_widget.observe(
                        lambda change, inputs=inputs: update_allocation(inputs),
                        names="value",
                    )
                display(VBox(inputs))
                calculate_button = widgets.Button(description="Calculate Returns")
                calculate_button.on_click(
                    lambda b: calculate_returns(inputs, entity_names)
                )
                display(calculate_button)

        def calculate_returns(inputs, entity_names):
            global global_ccids
            allocations = {input.description: input.value for input in inputs}
            ccids = {
                next((k for k, v in SYMBOL_DICT.items() if v == key), None): value
                for key, value in allocations.items()
            }
            global_ccids = ccids

            position = pd.DataFrame(
                index=stock_price.index,
                data={k: [v] * len(stock_price.index) for k, v in ccids.items()},
            )
            position = position * stock_price[list(ccids.keys())].notna()
            start_dt = stock_price[list(ccids.keys())].notna().all(axis=1).idxmax()
            portfolio_returns = (
                1
                + (
                    position
                    * stock_price[list(ccids.keys())].pct_change(fill_method=None)
                ).sum(axis=1)
                / 100
            )[start_dt:].cumprod()

            results_output.clear_output(wait=True)
            with results_output:
                plt.figure(figsize=(10, 5))
                for entity_name in entity_names:
                    ccid = next(
                        (k for k, v in SYMBOL_DICT.items() if v == entity_name), None
                    )
                    plt.plot(
                        stock_price[start_dt:].index,
                        (
                            1
                            + stock_price[ccid].pct_change(fill_method=None)[start_dt:]
                        ).cumprod(),
                        label=entity_name,
                    )
                portfolio_returns.plot(label="portfolio")
                plt.title("Cumulative Portfolio Returns")
                plt.ylabel("Cumulative Returns")
                plt.xlabel("Date")
                plt.grid(True)
                plt.legend()
                plt.show()

                # 모델 이름 입력을 위한 텍스트 필드 추가
                model_name_input = widgets.Text(
                    value="",
                    placeholder="Enter model name",
                    description="Model Name:",
                    style={"description_width": "initial"},
                )
                display(model_name_input)

                # Submit 버튼 생성 및 이벤트 핸들러 설정
                submit_button = widgets.Button(description="Submit Model")
                submit_button.on_click(lambda b: self.submit(model_name_input.value))
                display(submit_button)

        # 인터랙션 위젯 설정 및 출력
        interact(plot_prices, entity_names=tags)
        display(output, input_form, results_output)

    def code(self):
        return f"""
from finter import BaseAlpha
from finter.data import ContentFactory
import pandas as pd

class Alpha(BaseAlpha):
    def get(self, start, end):
        cf = ContentFactory('kr_stock', start, end)
        sp = cf.get_df('price_close')
        ccids = {global_ccids}
        position = pd.DataFrame(index=sp.index, data={{k: [v] * len(sp.index) for k, v in ccids.items()}}) * 1e6
        return position
            """

    def submit(self, model_name, benchmark=None):
        nb = NotebookSubmissionHelper(
            notebook_name=None,
            model_name=model_name,
            model_universe=self.model_universe,
            model_type=self.model_type,
            benchmark=benchmark,
        )

        directory = os.path.dirname(nb.output_file_path)

        # 해당 디렉터리가 존재하지 않는 경우, 디렉터리 생성
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 파일 쓰기
        with open(nb.output_file_path, "w") as f:
            f.write(self.code())

        nb.process(
            self.start,
            self.end,
            position=True,
            simulation=True,
            validation=False,
            submit=True,
            git=False,
        )
