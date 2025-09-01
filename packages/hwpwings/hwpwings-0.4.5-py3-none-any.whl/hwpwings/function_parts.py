import win32gui

class function_parts():
# 기타 부품들

    def key_indicator(self) -> tuple:
        """
        상태 바의 정보를 얻어온다.
        (캐럿이 표 안에 있을 때 셀의 주소를 얻어오는 거의 유일한 방법이다.)

        :return:
            튜플(succ, seccnt, secno, prnpageno, colno, line, pos, over, ctrlname)
            succ: 성공하면 True, 실패하면 False (항상 True임..)
            seccnt: 총 구역
            secno: 현재 구역
            prnpageno: 쪽
            colno: 단
            line: 줄
            pos: 칸
            over: 삽입모드 (True: 수정, False: 삽입)
            ctrlname: 캐럿이 위치한 곳의 컨트롤이름

        :example:
            >>> # 현재 셀 주소(표 안에 있을 때)
            >>> from pyhwpx import Hwp
            >>> hwp = Hwp()
            >>> hwp.KeyIndicator()[-1][1:].split(")")[0]
            "A1"
        """
        return self.hwp.KeyIndicator()

    def is_cell(self):
        """
        캐럿이 현재 표 안에 있는지 알려주는 메서드
        :return:
            표 안에 있으면 True, 그렇지 않으면 False를 리턴
        """
        if self.key_indicator()[-1].startswith("("):
            return True
        else:
            return False
        
    @property
    def SelectionMode(self):
        """
        현재 선택모드가 어떤 상태인지 리턴한다.
        :return:
        """
        return self.hwp.SelectionMode
    
    @property
    def HParameterSet(self):
        """
        한/글에서 실행되는 대부분의 액션에 필요한
        다양한 파라미터셋을 제공해주는 속성.
        사용법은 아래와 같다.

        >>> from pyhwpx import Hwp
        >>> hwp = Hwp()
        >>> pset = hwp.HParameterSet.HInsertText
        >>> pset.Text = "Hello world!"
        >>> hwp.HAction.Execute("InsertText", pset.HSet)

        :return:
        """
        return self.hwp.HParameterSet

    @property
    def HAction(self):
        """
        한/글의 액션을 설정하고 실행하기 위한 속성.
        GetDefalut, Execute, Run 등의 메서드를 가지고 있다.
        :return:
        """
        return self.hwp.HAction

    def goto_printpage(self, page_num: int = 1):
        """
        인쇄페이지 기준으로 해당 페이지로 이동
        1페이지의 page_num은 1이다.
        :param page_num: 이동할 페이지번호
        :return: 성공시 True, 실패시 False를 리턴
        """
        pset = self.hwp.HParameterSet.HGotoE
        self.hwp.HAction.GetDefault("Goto", pset.HSet)
        pset.HSet.SetItem("DialogResult", page_num)
        pset.SetSelectionIndex = 1
        return self.hwp.HAction.Execute("Goto", pset.HSet)
    
    def MovePageUp(self):
        """
        뒤 페이지의 시작으로 이동. 현재 탑레벨 리스트가 아니면 탑레벨 리스트로 빠져나온다.
        """
        cwd = self.get_pos()
        self.hwp.HAction.Run("MovePageUp")
        if self.get_pos()[0] != cwd[0] or self.get_pos()[1:] != cwd[1:]:
            return True
        else:
            return False
    
    def MovePageDown(self):
        """
        앞 페이지의 시작으로 이동. 현재 탑레벨 리스트가 아니면 탑레벨 리스트로 빠져나온다.
        """
        cwd = self.get_pos()
        self.hwp.HAction.Run("MovePageDown")
        if self.get_pos()[0] != cwd[0] or self.get_pos()[1:] != cwd[1:]:
            return True
        else:
            return False
    
    @property
    def current_printpage(self):
        """
        현재 쪽번호를 리턴.
        1페이지에 있다면 1을 리턴한다.
        새쪽번호가 적용되어 있다면
        수정된 쪽번호를 리턴한다.
        :return:
        """
        return self.hwp.XHwpDocuments.Active_XHwpDocument.XHwpDocumentInfo.CurrentPrintPage
    
    def mili_to_hwp_unit(self, mili):
        return self.hwp.MiliToHwpUnit(mili=mili)

    def get_pos(self) -> tuple[int]:
        """
        캐럿의 위치를 얻어온다.
        파라미터 중 리스트는, 문단과 컨트롤들이 연결된 한/글 문서 내 구조를 뜻한다.
        리스트 아이디는 문서 내 위치 정보 중 하나로서 SelectText에 넘겨줄 때 사용한다.
        (파이썬 자료형인 list가 아님)

        :return:
            (List, para, pos) 튜플.
            list: 캐럿이 위치한 문서 내 list ID(본문이 0)
            para: 캐럿이 위치한 문단 ID(0부터 시작)
            pos: 캐럿이 위치한 문단 내 글자 위치(0부터 시작)

        """
        return self.hwp.GetPos()
    
    def set_pos_by_set(self, disp_val):
        """
        캐럿을 ParameterSet으로 얻어지는 위치로 옮긴다.

        :param disp_val:
            캐럿을 옮길 위치에 대한 ParameterSet 정보

        :return:
            성공하면 True, 실패하면 False

        :example:
            >>> start_pos = hwp.GetPosBySet()  # 현재 위치를 저장하고,
            >>> hwp.set_pos_by_set(start_pos)  # 특정 작업 후에 저장위치로 재이동
        """
        return self.hwp.SetPosBySet(dispVal=disp_val)

    def get_cur_field_name(self, option=0):
        """
        현재 캐럿이 위치하는 곳의 필드이름을 구한다.
        이 함수를 통해 현재 필드가 셀필드인지 누름틀필드인지 구할 수 있다.
        참고로, 필드 좌측에 커서가 붙어있을 때는 이름을 구할 수 있지만,
        우측에 붙어 있을 때는 작동하지 않는다.
        GetFieldList()의 옵션 중에 hwpFieldSelection(=4)옵션은 사용하지 않는다.


        :param option:
            다음과 같은 옵션을 지정할 수 있다.
            0: 모두 off. 생략하면 0이 지정된다.
            1: 셀에 부여된 필드 리스트만을 구한다. hwpFieldClickHere와는 함께 지정할 수 없다.(hwpFieldCell)
            2: 누름틀에 부여된 필드 리스트만을 구한다. hwpFieldCell과는 함께 지정할 수 없다.(hwpFieldClickHere)

        :return:
            필드이름이 돌아온다.
            필드이름이 없는 경우 빈 문자열이 돌아온다.
        """
        return self.hwp.GetCurFieldName(option=option)
    
    def set_pos(self, list, para, pos):
        """
        캐럿을 문서 내 특정 위치로 옮긴다.
        지정된 위치로 캐럿을 옮겨준다.

        :param list:
            캐럿이 위치한 문서 내 list ID

        :param para:
            캐럿이 위치한 문단 ID. 음수거나, 범위를 넘어가면 문서의 시작으로 이동하며, pos는 무시한다.

        :param pos:
            캐럿이 위치한 문단 내 글자 위치. -1을 주면 해당문단의 끝으로 이동한다.
            단 para가 범위 밖일 경우 pos는 무시되고 문서의 시작으로 캐럿을 옮긴다.

        :return:
            성공하면 True, 실패하면 False
        """
        self.hwp.SetPos(List=list, Para=para, pos=pos)
        if (list, para) == self.get_pos()[:2]:
            return True
        else:
            return False
        
    def find_ctrl(self):
        return self.hwp.FindCtrl()

    def TableCellBlock(self):
        """
        셀 블록
        """
        # return self.hwp.HAction.Run("TableCellBlock")
        pset = self.HParameterSet.HInsertText
        self.HAction.GetDefault("TableCellBlock", pset.HSet)
        return self.HAction.Execute("TableCellBlock", pset.HSet)

    def TableColBegin(self):
        """
        셀 이동: 열 시작
        """
        return self.hwp.HAction.Run("TableColBegin")

    def TableColPageUp(self):
        """
        셀 이동: 페이지 업
        """
        return self.hwp.HAction.Run("TableColPageUp")

    def get_selected_range(self):
        """
        선택한 범위의 셀주소를
        리스트로 리턴함
        """
        if not self.is_cell():
            raise AttributeError("캐럿이 표 안에 있어야 합니다.")
        pset = self.HParameterSet.HFieldCtrl
        self.HAction.GetDefault("TableFormula", pset.HSet)
        return pset.Command[2:-1].split(",")

    def GetTextFile(self, format="UNICODE", option=""):
        
        return self.hwp.GetTextFile(Format=format, option=option)

    @staticmethod
    def cell_to_index(cell):
        """ 엑셀 셀 주소를 행과 열 인덱스로 변환"""
        column = ord(cell[0]) - ord('A')  # 열 인덱스 (0-based)
        row = int(cell[1:]) - 1  # 행 인덱스 (0-based)
        return row, column

    def get_active_window_title(self): # 활성화된 window창의 제목을 리턴한다.
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        return window_title
    
    def addr_to_tuple(self, cell_address:str):
        """
        엑셀 셀 주소 문자열(예: "AAA3")을 받아 (컬럼번호, 행번호)를 반환합니다.
        """
        # 알파벳 부분과 숫자 부분을 분리
        col_str = ''.join(filter(str.isalpha, cell_address))
        row = int(''.join(filter(str.isdigit, cell_address)))

        # 알파벳 부분을 컬럼 번호로 변환
        col = 0
        for i, letter in enumerate(col_str):
            col += (ord(letter.upper()) - ord('A') + 1) * (26 ** (len(col_str) - i - 1))

        return row, col
