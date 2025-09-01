from typing import Literal, Union
import pandas as pd
import xml.etree.ElementTree as ET


# DataFrame 관련 메서드
class dataframe():

    def put_DataFrame_text(self, field, text: Union[str, list, tuple, pd.Series] = "", idx=None): # 한글의 메일머지형태로 pd.DataFrame을 필드에 적습니다. ※column의 이름이 완전히 동일해야합니다.
        '한글의 메일머지형태로 pd.DataFrame을 필드에 적습니다. ※column의 이름이 완전히 동일해야합니다.'
        if isinstance(field, str) and (field.endswith(".xlsx") or field.endswith(".xls")):
            field = pd.read_excel(field)

        if isinstance(field, dict):  # dict 자료형의 경우에는 text를 생략하고
            field, text = list(zip(*list(field.items())))
            field_str = ""
            text_str = ""
            if isinstance(idx, int):
                for f_i, f in enumerate(field):
                    field_str += f"{f}{{{{{idx}}}}}\x02"
                    text_str += f"{text[f_i][idx]}\x02"
            else:
                if isinstance(text[0], (list, tuple)):
                    for f_i, f in enumerate(field):
                        for t_i, t in enumerate(text[f_i]):
                            field_str += f"{f}{{{{{t_i}}}}}\x02"
                            text_str += f"{t}\x02"
                elif isinstance(text[0], (str, int, float)):
                    for f_i, f in enumerate(field):
                        field_str += f"{f}\x02"
                    text_str = "\x02".join(text)

            self.hwp.PutFieldText(Field=field_str, Text=text_str)
            return

        if isinstance(field, str) and type(text) in (list, tuple, pd.Series):
            field = [f"{field}{{{{{i}}}}}" for i in range(len(text))]

        if isinstance(field, pd.Series):  # 필드명 리스트를 파라미터로 넣은 경우
            if not text:  # text 파라미터가 입력되지 않았다면
                text_str = "\x02".join([field[i] for i in field.index])
                field_str = "\x02".join([str(i) for i in field.index])  # \x02로 병합
                self.hwp.PutFieldText(Field=field_str, Text=text_str)
                return
            elif type(text) in [list, tuple, pd.Series]:  # 필드 텍스트를 리스트나 배열로 넣은 경우에도
                text = "\x02".join([str(i) for i in text])  # \x02로 병합
            else:
                raise IOError("text parameter required.")

        if isinstance(field, (list, tuple)):

            # field와 text가 [[field0:str, list[text:str]], [field1:str, list[text:str]]] 타입인 경우
            if not text and isinstance(field[0][0], (str, int, float)) and not isinstance(field[0][1], (str, int)) and len(field[0][1]) >= 1:
                text_str = ""
                field_str = "\x02".join(
                    [str(field[i][0]) + f"{{{{{j}}}}}" for j in range(len(field[0][1])) for i in range(len(field))])
                for i in range(len(field[0][1])):
                    text_str += "\x02".join([str(field[j][1][i]) for j in range(len(field))]) + "\x02"
                self.hwp.PutFieldText(Field=field_str, Text=text_str)
                return

            elif isinstance(field, (list, tuple, set)) and isinstance(text, (list, tuple, set)):
                # field와 text가 모두 배열로 만들어져 있는 경우
                field_str = "\x02".join([str(field[i]) for i in range(len(field))])
                text_str = "\x02".join([str(text[i]) for i in range(len(text))])
                self.hwp.PutFieldText(Field=field_str, Text=text_str)
                return
            else:
                # field와 text가 field타입 안에 [[field0:str, text0:str], [field1:str, text1:str]] 형태로 들어간 경우
                field_str = "\x02".join([str(field[i][0]) for i in range(len(field))])
                text_str = "\x02".join([str(field[i][1]) for i in range(len(field))])
                self.hwp.PutFieldText(Field=field_str, Text=text_str)
                return

        if isinstance(field, pd.DataFrame):
            if isinstance(field.columns, pd.core.indexes.range.RangeIndex):
                field = field.T
            text_str = ""
            if isinstance(idx, int):
                field_str = "\x02".join([str(i) + f"{{{{{idx}}}}}" for i in field])  # \x02로 병합
                text_str += "\x02".join([str(t) for t in field.iloc[idx]]) + "\x02"
            else:
                field_str = "\x02".join([str(i) + f"{{{{{j}}}}}" for j in range(len(field)) for i in field])  # \x02로 병합
                for i in range(len(field)):
                    text_str += "\x02".join([str(t) for t in field.iloc[i]]) + "\x02"
            self.hwp.PutFieldText(Field=field_str, Text=text_str)
            return

        if isinstance(text, pd.DataFrame):
            if not isinstance(text.columns, pd.core.indexes.range.RangeIndex):
                text = text.T
            text_str = ""
            if isinstance(idx, int):
                field_str = "\x02".join([i + f"{{{{{idx}}}}}" for i in field.split("\x02")])  # \x02로 병합
                text_str += "\x02".join([str(t) for t in text[idx]]) + "\x02"
            else:
                field_str = "\x02".join([str(i) + f"{{{{{j}}}}}" for i in field.split("\x02") for j in range(len(text.columns))])  # \x02로 병합
                for i in range(len(text)):
                    text_str += "\x02".join([str(t) for t in text.iloc[i]]) + "\x02"
            self.hwp.PutFieldText(Field=field_str, Text=text_str)
            return

        if isinstance(idx, int):
            self.hwp.PutFieldText(Field=field.replace("\x02", f"{{{{{idx}}}}}\x02") + f"{{{{{idx}}}}}", Text=text)
        else:
            self.hwp.PutFieldText(Field=field, Text=text)

    def get_DataFrame_Text(self, n="", cols=0): # Table을 DataFrame 형태로 가져옵니다.
        """
        (2024. 7. 26. xml파싱으로 방법 변경. 결국 기존 방법으로는 간단한 줄바꿈 이슈도 해결 못함.
                    startrow와 columns가 뭔가 중복되는 개념이어서, cols로 통일. 파괴적 업데이트라 죄송..)
        한/글 문서의 n번째 표를 판다스 데이터프레임으로 리턴하는 메서드.
        n을 넣지 않는 경우, 캐럿이 셀에 있다면 해당 표를 df로,
        캐럿이 표 밖에 있다면 첫 번째 표를 df로 리턴한다.
        
        ※주의 : 셀 병합이 있을 때 DataFrame을 제대로 불러오지 못한다.
        :return:
            pd.DataFrame
        :example:
            >>> from pyhwpx import Hwp
            >>>
            >>> hwp = Hwp()
            >>> df = hwp.table_to_df()  # 현재 캐럿이 들어가 있는 표 전체를 df로(1행을 df의 칼럼으로)
            >>> df = hwp.table_to_df(0, cols=2)  # 문서의 첫 번째 표를 df로(2번인덱스행(3행)을 칼럼명으로, 그 아래(4행부터)를 값으로)
            >>>
        """
        if self.SelectionMode != 19:
            start_pos = self.hwp.GetPos()
            ctrl = self.hwp.HeadCtrl
            if isinstance(n, type(ctrl)):
                # 정수인덱스 대신 ctrl 객체를 넣은 경우
                self.set_pos_by_set(n.GetAnchorPos(0))
                self.find_ctrl()
            elif n == "" and self.is_cell():
                self.TableCellBlock()
                self.TableColBegin()
                self.TableColPageUp()
            elif n == "" or isinstance(n, int):
                if n == "":
                    n = 0
                if n >= 0:
                    idx = 0
                else:
                    idx = -1
                    ctrl = self.hwp.LastCtrl

                while ctrl:
                    if ctrl.UserDesc == "표":
                        if n in (0, -1):
                            self.set_pos_by_set(ctrl.GetAnchorPos(0))
                            self.hwp.FindCtrl()
                            break
                        else:
                            if idx == n:
                                self.set_pos_by_set(ctrl.GetAnchorPos(0))
                                self.hwp.FindCtrl()
                                break
                            if n >= 0:
                                idx += 1
                            else:
                                idx -= 1
                    if n >= 0:
                        ctrl = ctrl.Next
                    else:
                        ctrl = ctrl.Prev

                try:
                    self.hwp.SetPosBySet(ctrl.GetAnchorPos(0))
                except AttributeError:
                    raise IndexError(f"해당 인덱스의 표가 존재하지 않습니다."
                                    f"현재 문서에는 표가 {abs(int(idx + 0.1))}개 존재합니다.")
                self.hwp.FindCtrl()
        else:
            selected_range = self.get_selected_range()
        
        xml_data = self.GetTextFile("HWPML2X", option="saveblock")
        root = ET.fromstring(xml_data)

        data = []

        for row in root.findall('.//ROW'):
            row_data = []
            for cell in row.findall('.//CELL'):
                cell_text = ''
                for text in cell.findall('.//TEXT'):
                    for char in text.findall('.//CHAR'):
                        cell_text += char.text
                    cell_text += "\r\n"
                if cell_text.endswith("\r\n"):
                    cell_text = cell_text[:-2]
                row_data.append(cell_text)
            data.append(row_data)
        
        if self.SelectionMode == 19:
            data = self.crop_data_from_selection(data, selected_range)
        
        if type(cols) == int:
            columns = data[cols]
            data = data[cols + 1:]
            df = pd.DataFrame(data, columns=columns)
        elif type(cols) in (list, tuple):
            df = pd.DataFrame(data, columns=cols)
        
        try:
            return df
        finally:
            if self.SelectionMode != 19:
                self.set_pos(*start_pos)

    def get_all_DataFrame(self):
        """
        모든 표의 데이터프레임을 얻습니다.
        여러 개일 경우 딕셔너리 {1: df1, 2: df2, ...} 형태로 리턴하고,
        하나일 경우에는 DataFrame을 그대로 리턴합니다.
        """
        self.data = []
        # 테이블의 첫 번째 컨트롤(HeadCtrl)로 시작
        ctrl = self.hwp.HeadCtrl
        # self.activate()

        # 테이블을 순차적으로 탐색하며 각 테이블 안으로 캐럿을 이동시키는 코드
        while ctrl:
            if ctrl.UserDesc == "표":  # "표"인 컨트롤을 찾음
                disp_val = ctrl.GetAnchorPos(0)  # 테이블의 앵커 위치를 얻음

                # 캐럿을 ParameterSet으로 얻은 위치로 이동
                success = self.set_pos_by_set(disp_val)  # 캐럿을 해당 위치로 이동시킴

                if success:
                    self.hwp.FindCtrl()  # 테이블 내의 컨트롤을 찾아 캐럿을 그 안으로 위치시킴
                    # pyautogui.press('enter')  # 'enter' 키를 눌러 작업을 수행
                    self.hwp.HAction.Run("ShapeObjTableSelCell")
                    self.data.append(self.get_DataFrame_Text())  # 추출한 DataFrame을 리스트에 추가
                # 다음 테이블로 이동
                ctrl = ctrl.Next  # 다음 컨트롤로 이동
            else:
                ctrl = ctrl.Next  # 표가 아닐 경우 다음 컨트롤로 이동

        # DataFrame이 하나일 경우 바로 반환
        if len(self.data) == 1:
            return self.data[0]

        # 여러 DataFrame일 경우 번호로 딕셔너리 반환 (1, 2, 3...)
        data_dict = {i + 1 : df for i, df in enumerate(self.data)}
        
        return data_dict  # 번호로 딕셔너리 반환
