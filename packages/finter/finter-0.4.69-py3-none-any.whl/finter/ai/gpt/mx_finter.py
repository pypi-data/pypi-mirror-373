import json
from typing import List

import nbformat
import requests
from IPython import get_ipython
from nbformat.notebooknode import NotebookNode


class MxFinter:
    def __init__(self, filename: str) -> None:
        self.url = "https://mx-finter.finter.bot/invoke"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer quantitisbravo!!12331$$",
        }

        if not filename.endswith(".ipynb"):
            raise Exception("The filename must have the .ipynb extension.")

        print(
            "MxFinter.say() method를 실행하기 전에 꼭 현재 ipynb 파일을 저장해 주세요.\nBe sure to save the current ipynb file before running the MxFinter.say() method."
        )

        self.filename = filename
        self.payload = {"notebook": [], "message": ""}

    @staticmethod
    def normalize_cells(cells: List[NotebookNode]) -> List[NotebookNode]:
        """
        1. 실행된 cell 보다 execution count가 더 큰 cell은 제거
        2. execution count가 None 이면 제거 (어떤 이유로 실행되지 않고, cell에 코드만 존재하는 상태)
        2. say() method가 실행된 cell의 output은 제거
        3. cell이 너무 많은 경우에 대한 필터링도 필요할 것 같은데 .. (이건 추후 고민)
        """
        curr_execution_count = get_ipython().execution_count
        norm_cells = [
            x
            for x in cells
            if x.cell_type != "code"
            or x.execution_count
            and x.execution_count <= curr_execution_count
        ]

        for x in norm_cells:
            if x.cell_type != "code" or not x.outputs:
                continue

            output = str(x.outputs[0])
            if output.find("# MxFinter is an assistant for Alpha Modeling.") > -1:
                x.outputs = []

        return norm_cells

    def get_payload(self):
        return self.payload

    def say(self, text: str):
        with open(self.filename, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)

        cells = self.normalize_cells(nb.cells)
        payload = json.dumps({"notebook": str(cells), "message": text})

        self.payload = {"notebook": cells, "message": text}

        response = requests.request(
            "POST", self.url, headers=self.headers, data=payload
        )

        message = response.json().get("message")
        print(message)
