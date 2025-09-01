# 필드 조작하기
class field():
    
    def insert_field(self, field_Name:str, Name:str): # 누름틀 필드 생성
        """
        누름틀 필드를 삽입하는 메서드입니다.

        Parameters:
            field_Name (str): 필드의 이름 
            Name (str): 필드의 내용 또는 방향 
        """
        # InsertFieldTemplate 액션의 기본값을 가져옵니다.
        self.hwp.HAction.GetDefault("InsertFieldTemplate", self.hwp.HParameterSet.HInsertFieldTemplate.HSet)
        
        # 필드 설정
        self.hwp.HParameterSet.HInsertFieldTemplate.TemplateDirection = Name  # 필드의 내용 또는 방향 설정
        self.hwp.HParameterSet.HInsertFieldTemplate.TemplateName = field_Name  # 필드의 이름 설정
        
        # 액션 실행하여 누름틀 필드 삽입
        self.hwp.HAction.Execute("InsertFieldTemplate", self.hwp.HParameterSet.HInsertFieldTemplate.HSet)


    def put_field_text(self, field_Name:str, Text:str):
        '지정한 필드에 넣고싶은 text를 넣습니다'
        return self.hwp.PutFieldText(f"{field_Name}", f"{Text}")  
    
    def get_field_list(self:None):
        '현재 한글파일에 생성된 모든 필드를 리스트로 보여줍니다.'
        return self.hwp.GetFieldList(1).split('')
    
    def get_field_text(self, field_Name:str):
        '선택된 필드의 text를 추출합니다.'
        return self.hwp.GetFieldText(f'{field_Name}')
    
    def goto_field(self, field_Name:str):
        '선택된 필드로 커서(캐럿)를 이동시킵니다.'
        return self.hwp.MoveToField(f'{field_Name}')
    
    def delete_field(self:None): 
        '''
        현재 캐럿위치의 누름틀 필드를 제거한다.
        누름틀 필드에 삽입된 텍스트는 남는다.
        '''
        return self.hwp.HAction.Run("DeleteField")

    def delete_all_fields(self:None): # 한글 문서 내부의 모든 누름틀 필드 제거
        '''
        한글문서 내부의 모든 누름틀 필드를 제거한다.
        누름틀 필드에 삽입된 텍스트는 남는다.
        '''
        start_pos = self.get_pos()
        ctrl = self.hwp.HeadCtrl
        while ctrl:
            if ctrl.CtrlID == "%clk":
                self.hwp.DeleteCtrl(ctrl)
            ctrl = ctrl.Next
        for field in self.get_field_list():
            self.rename_field(field, "")
        return self.set_pos(*start_pos)
