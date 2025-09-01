class text():

    def find_text(self, find_string:str, Direction:int=0):
        """
        찾는 글자를 select 합니다. 정규 표현식도 사용가능합니다.
        
        :param find_string: 찾을 문자열, 정규표현식 패턴

        :param Direction: 찾기방향 -> 0:아래로, 1:위로, 2:전체방향
        기본적인 찾기방향은 아래 방향이다
        :return: 찾기 작업의 성공 여부 (True 또는 False)
        """
        # RepeatFind 기본 설정 가져오기
        self.hwp.HAction.GetDefault("RepeatFind", self.hwp.HParameterSet.HFindReplace.HSet)

        # 찾기 및 바꾸기 파라미터 설정
        self.hwp.HParameterSet.HFindReplace.FindString = find_string  # 정규표현식 패턴
        self.hwp.HParameterSet.HFindReplace.Direction = Direction  # 방향: 0:아래로, 1:위로, 2:전체방향
        self.hwp.HParameterSet.HFindReplace.IgnoreMessage = 1  # 메시지 무시
        self.hwp.HParameterSet.HFindReplace.FindType = 1  # 찾기 유형 고정
        self.hwp.HParameterSet.HFindReplace.FindRegExp = 1  # 정규표현식 사용

        # 설정된 찾기 작업 실행하고 결과 반환
        return self.hwp.HAction.Execute("RepeatFind", self.hwp.HParameterSet.HFindReplace.HSet)

    def text_to_field(self):
        '선택된 범위를 누름틀 필드로 만듭니다.'
        return self.hwp.CreateField(Direction='', memo='', name='임시필드')