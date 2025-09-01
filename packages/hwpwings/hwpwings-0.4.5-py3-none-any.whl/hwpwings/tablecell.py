# 표(셀) 조작하기
class tablecell():

    def insert_table(self, rows, cols, treat_as_char: bool = True, width_type=0, height_type=0, header=True, height=0):
        """
        표를 생성하는 메서드.
        기본적으로 rows와 cols만 지정하면 되며,
        용지여백을 제외한 구간에 맞춰 표 너비가 결정된다.
        이는 일반적인 표 생성과 동일한 수치이다.

        아래의 148mm는 종이여백 210mm에서 60mm(좌우 각 30mm)를 뺀 150mm에다가,
        표 바깥여백 각 1mm를 뺀 148mm이다. (TableProperties.Width = 41954)
        각 열의 너비는 5개 기준으로 26mm인데 이는 셀마다 안쪽여백 좌우 각각 1.8mm를 뺀 값으로,
        148 - (1.8 x 10 =) 18mm = 130mm
        그래서 셀 너비의 총 합은 130이 되어야 한다.
        아래의 라인28~32까지 셀너비의 합은 16+36+46+16+16=130
        표를 생성하는 시점에는 표 안팎의 여백을 없애거나 수정할 수 없으므로
        이는 고정된 값으로 간주해야 한다.

        :return:
            표 생성 성공시 True, 실패시 False를 리턴한다.
        """

        pset = self.hwp.HParameterSet.HTableCreation
        self.hwp.HAction.GetDefault("TableCreate", pset.HSet)  # 표 생성 시작
        pset.Rows = rows  # 행 갯수
        pset.Cols = cols  # 열 갯수
        pset.WidthType = width_type  # 너비 지정(0:단에맞춤, 1:문단에맞춤, 2:임의값)
        pset.HeightType = height_type  # 높이 지정(0:자동, 1:임의값)

        sec_def = self.hwp.HParameterSet.HSecDef
        self.hwp.HAction.GetDefault("PageSetup", sec_def.HSet)
        total_width = (
                sec_def.PageDef.PaperWidth - sec_def.PageDef.LeftMargin - sec_def.PageDef.RightMargin - sec_def.PageDef.GutterLen - self.mili_to_hwp_unit(
            2))

        pset.WidthValue = total_width  # 표 너비(근데 영향이 없는 듯)
        if height and height_type == 1:  # 표높이가 정의되어 있으면
            # 페이지 최대 높이 계산
            total_height = (
                    sec_def.PageDef.PaperHeight - sec_def.PageDef.TopMargin - sec_def.PageDef.BottomMargin - sec_def.PageDef.HeaderLen - sec_def.PageDef.FooterLen - self.mili_to_hwp_unit(
                2))
            pset.HeightValue = min(self.hwp.MiliToHwpUnit(height), total_height)  # 표 높이
            pset.CreateItemArray("RowHeight", rows)  # 행 m개 생성
            each_row_height = min((self.mili_to_hwp_unit(height) - self.mili_to_hwp_unit((0.5 + 0.5) * rows)) // rows,
                                  (total_height - self.mili_to_hwp_unit((0.5 + 0.5) * rows)) // rows)
            for i in range(rows):
                pset.RowHeight.SetItem(i, each_row_height)  # 1열
            pset.TableProperties.Height = min(self.MiliToHwpUnit(height),
                                              total_height - self.mili_to_hwp_unit((0.5 + 0.5) * rows))

        pset.CreateItemArray("ColWidth", cols)  # 열 n개 생성
        each_col_width = total_width - self.mili_to_hwp_unit(3.6 * cols)
        for i in range(cols):
            pset.ColWidth.SetItem(i, each_col_width)  # 1열
        # pset.TableProperties.TreatAsChar = treat_as_char  # 글자처럼 취급
        pset.TableProperties.Width = total_width  # self.hwp.MiliToHwpUnit(148)  # 표 너비
        self.hwp.HAction.Execute("TableCreate", pset.HSet)  # 위 코드 실행

        # 글자처럼 취급 여부 적용(treat_as_char)
        ctrl = self.hwp.CurSelectedCtrl or self.hwp.ParentCtrl
        pset = self.hwp.CreateSet("Table")
        pset.SetItem("TreatAsChar", treat_as_char)
        ctrl.Properties = pset

        # 제목 행 여부 적용(header)
        pset = self.hwp.HParameterSet.HShapeObject
        self.hwp.HAction.GetDefault("TablePropertyDialog", pset.HSet)
        pset.ShapeTableCell.Header = header
        # try:
        #     self.hwp.HAction.Execute("TablePropertyDialog", pset.HSet)
        # except:
        #     pass

    def insert_cellfield(self, field : str, option=0, direction="", memo=""):
        """
        현재 마우스커서(캐럿)가 깜빡이는 표의 셀에 셀필드를 생성한다.
        커서상태 or 회색선택상태(F5)에서만 필드삽입이 가능하다.
        필드가 생성되어있다면, 기존 필드에 덮어쓴다.
        :return:
            성공하면 True, 실패하면 False
        """
        if not self.is_cell():
            raise AssertionError("마우스 커서가 표 안에 있지 않습니다.")
        if self.SelectionMode == 0x13:
            pset = self.HParameterSet.HShapeObject
            self.HAction.GetDefault("TablePropertyDialog", pset.HSet)
            pset.HSet.SetItem("ShapeType", 3)
            pset.HSet.SetItem("ShapeCellSize", 0)
            pset.ShapeTableCell.CellCtrlData.name = field
            return self.HAction.Execute("TablePropertyDialog", pset.HSet)
        else:
            return self.hwp.SetCurFieldName(Field=field, option=option, Direction=direction, memo=memo)

    def goto_table(self, table_index:int=1, start_cell:str=''):
        '''
        특정 표 안으로 이동한다.
        index 기본값은 1으로 설정되어있으며,
        다른 표로 이동 시 index값을 늘려주면 된다.

        만약 캐럿을 특정 셀에서 시작하고싶다면,
        위치에 해당하는 A1, B2, C5 등의 엑셀좌표를 넣어주면
        캐럿을 해당 좌표로 옮길 수 있다.
        '''
        ctrl = self.hwp.HeadCtrl
        table_dict = {}
        index = 1

        # 모든 표를 탐색하며 인덱스와 위치를 저장
        while ctrl:
            if ctrl.UserDesc == '표':
                table_dict[index] = ctrl.GetAnchorPos(0)
                # print(f"Table {index}: Position {ctrl.GetAnchorPos(0)}")
                index += 1
            ctrl = ctrl.Next

        # 선택한 인덱스가 존재하는지 확인하고 이동
        selected_pos = table_dict.get(table_index)
        if selected_pos:
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            self.hwp.HAction.Run('ShapeObjTableSelCell')
            # cell_address가 입력된 경우 해당 셀 주소로 캐럿을 이동
            if start_cell:
                row, col = self.addr_to_tuple(start_cell)  # cell_address를 튜플로 변환

                # 행과 열을 이동
                for move_col in range(col - 1):  # 열 이동
                    self.cell_right()

                for move_row in range(row - 1):  # 행 이동
                    self.cell_down()
            return True
        else:
            print("유효하지 않은 표 인덱스입니다.")

    def delete_table(self, table_index: int = 1):
        '''
        특정 표를 삭제한다.
        기본값은 첫 번째 표(index=1)이며,
        다른 표를 삭제하려면 table_index 값을 조정하면 된다.
        '''
        ctrl = self.hwp.HeadCtrl
        table_dict = {}
        index = 1

        # 모든 표를 탐색하며 인덱스와 위치를 저장
        while ctrl:
            if ctrl.UserDesc == '표':
                table_dict[index] = ctrl.GetAnchorPos(0)
                # print(f"Table {index}: Position {ctrl.GetAnchorPos(0)}")
                index += 1
            ctrl = ctrl.Next

        # 선택한 인덱스가 존재하는지 확인하고 삭제
        selected_pos = table_dict.get(table_index)
        if selected_pos:
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            self.hwp.HAction.Run('Delete')  # 표 삭제 명령 실행
            return True
        else:
            print("유효하지 않은 표 인덱스입니다.")
            return False

    # @property
    def cell_address(self):
        '현재 캐럿위치의 셀 주소를 반환한다.'
        return self.hwp.KeyIndicator()[-1].split(":")[0].replace('(','').replace(')','')

    def cell_text(self):
        '''
        현재 지정된 범위의 text를 가져온다.
        만약 2줄 이상일 경우 
        각 문단별 리스트로 배출한다.
        '''
        self.hwp.InitScan(Range=0xff)
        text_list = []

        while True: # 지정된 범위 모든 문단글자를 스캔해서
            state, text = self.hwp.GetText()
            text_list.append(text)
            if state == 1: # 문단이 끝날경우 함수를 종료하고
                break
        self.hwp.ReleaseScan()

        if len(text_list) == 2 and text_list[-1] == '': # 만약 글자가 한줄이라면
            return text_list[0] # 그 한줄만 배출하고
        else:
            # '\r\n' 제거
            cleaned_list = [item.replace("\r\n", "") for item in text_list]
            return cleaned_list # 아닐경우 전체 리스트를 배출할 것
    
    def cell_block(self):
        """
        현재 캐럿이 있는 위치의 셀을 선택한다.
        단축키는 F5이다.
        """
        # return self.hwp.HAction.Run("TableCellBlock")
        pset = self.HParameterSet.HInsertText
        self.HAction.GetDefault("TableCellBlock", pset.HSet)
        return self.HAction.Execute("TableCellBlock", pset.HSet)

    def cell_block_red(self):
        """
        현재 캐럿이 있는 위치의 셀을 선택한다.
        단축키는 F5 + F5이다.
        """
        # return self.hwp.HAction.Run("TableCellBlock")
        pset = self.HParameterSet.HInsertText
        self.HAction.GetDefault("TableCellBlock", pset.HSet)
        self.HAction.Execute("TableCellBlock", pset.HSet)
        self.HAction.GetDefault("TableCellBlockExtend", pset.HSet)
        return self.HAction.Execute("TableCellBlockExtend", pset.HSet)


    def cell_out(self):
        '표 내부에 있을 때, 표 밖으로 나간다.'       
        return self.hwp.HAction.Run('Close')
        
    def cell_left(self):
        '표 내부 캐럿을 좌측으로 한칸 이동한다.'
        return self.hwp.HAction.Run("TableLeftCell")

    def cell_right(self):
        '표 내부 캐럿을 우측으로 한칸 이동한다.'
        return self.hwp.HAction.Run("TableRightCell")

    def cell_rightAdd(self):
        '''
        표 내부 캐럿을 우측으로 한칸 이동한다.
        만약 표의 마지막 문단이라면 표를 추가한다.
        '''
        return self.hwp.HAction.Run("TableRightCellAppend")

    def cell_up(self):
        '표 내부 캐럿을 위로 한칸 이동한다.'
        return self.hwp.HAction.Run("TableUpperCell")

    def cell_down(self):
        '표 내부 캐럿을 아래로 한칸 이동한다.'
        return self.hwp.HAction.Run("TableLowerCell")

    def cell_left_end(self):
        '현재 캐럿이 있는 위치를 기준으로 캐럿을 왼쪽 끝으로 이동시킨다.'
        return self.hwp.HAction.Run("TableColBegin")

    def cell_up_end(self):
        '현재 캐럿이 있는 위치를 기준으로 캐럿을 위쪽 끝으로 이동시킨다.'
        return self.hwp.HAction.Run("TableColPageUp")

    def cell_right_end(self):
        '현재 캐럿이 있는 위치를 기준으로 캐럿을 오른쪽 끝으로 이동시킨다.'
        return self.hwp.HAction.Run("TableColEnd")

    def cell_down_end(self):
        '현재 캐럿이 있는 위치를 기준으로 캐럿을 아래쪽 끝으로 이동시킨다.'
        return self.hwp.HAction.Run("TableColPageDown")