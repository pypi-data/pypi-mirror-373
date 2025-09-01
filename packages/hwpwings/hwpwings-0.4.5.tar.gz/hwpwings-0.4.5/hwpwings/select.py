from typing import Literal

class select:

    def select_ctrl(self, target_index: int = 1):
        """
        번호에 맞는 컨트롤을 선택한다.
        단, 컨트롤 사이에 공간(enter)이 없다면 맨 마지막 컨트롤이 선택된다.
        """
        # 컨트롤 정의 딕셔너리 생성
        ctrl = self.hwp.HeadCtrl
        ctrls_dict = {}
        index = 1

        # 딕셔너리로 저장 (유효한 컨트롤만 필터링)
        while ctrl:
            if ctrl.UserDesc:  # UserDesc가 존재하는 컨트롤만 포함
                ctrls_dict[index] = ctrl.GetAnchorPos(0)
                index += 1
            ctrl = ctrl.Next

        # 번호가 존재하는지 확인 후 선택
        selected_pos = ctrls_dict.get(target_index+2) # 문단 정의와 단 정의 제외로 +2
        if selected_pos:
            # 캐럿을 선택된 위치로 이동
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()

            return True
        else:
            # Target index does not exist
            return False

    
    def select_picture(self, target_index:int=1):
        """
        번호에 맞는 그림을 선택한다.
        """
        # 컨트롤정의 및 그림저장 딕셔너리 생성
        ctrl = self.hwp.HeadCtrl
        picture_dict = {}
        index = 1

        # 그림 객체만 딕셔너리로 저장
        while ctrl:
            if ctrl.UserDesc == '그림':
                picture_dict[index] = ctrl.GetAnchorPos(0)
                index += 1
            ctrl = ctrl.Next

        # 그림 번호가 존재하는지 확인 후 선택
        selected_pos = picture_dict.get(target_index)
        if selected_pos:
            # Move to the selected position and delete the picture
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            
            return True
        else:
            # Target index does not exist
            return False

    def select_table(self, target_index:int=1):
        """
        번호에 맞는 표를 선택한다.
        """
        # 컨트롤정의 및 그림저장 딕셔너리 생성
        ctrl = self.hwp.HeadCtrl
        table_dict = {}
        index = 1

        # 그림 객체만 딕셔너리로 저장
        while ctrl:
            if ctrl.UserDesc == '표':
                table_dict[index] = ctrl.GetAnchorPos(0)
                index += 1
            ctrl = ctrl.Next

        # 그림 번호가 존재하는지 확인 후 선택
        selected_pos = table_dict.get(target_index)
        if selected_pos:
            # Move to the selected position and delete the picture
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            
            return True
        else:
            # Target index does not exist
            return False
    
    def select_to_field(self):
        '선택된 범위를 누름틀 필드로 만듭니다.'
        return self.hwp.CreateField(Direction='', memo='', name='임시필드')

    def select_to_text(self, as_: Literal["list", "str"] = "str"):
        """
        선택된 범위를 텍스트로 반환합니다..
        """
        if self.SelectionMode == 0:
            if self.is_cell():
                self.TableCellBlock()
            else:
                self.Select()
                self.Select()
        if not self.hwp.InitScan(Range=0xff):
            return ""
        if as_ == "list":
            result = []
        else:
            result = ""
        state = 2
        while state not in [0, 1]:
            state, text = self.hwp.GetText()
            if as_ == "list":
                result.append(text)
            else:
                result += text
        self.hwp.ReleaseScan()
        return result if type(result) == str else result[:-1]