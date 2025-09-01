import os

# 기타 기능
class etc_function():

    def switch_to(self, num:int): 
        '''
        두개 이상의 문서를 다룰 때, 
        제어 한글창을 전환한다.
        0부터 시작한다.
        '''
        self.num = num
        return self.hwp.XHwpDocuments.Item(self.num).SetActive_XHwpDocument()

    def activate(self:None):
        '제어중인 한글창을 활성화한다'
        return self.hwp.XHwpDocuments.Item(0).SetActive_XHwpDocument()
    
    def insert_text(self, text : str): # 진짜 글자 삽입하는 메서드임
        """
        한/글 문서 내 캐럿 위치에 문자열을 삽입하는 메서드.
        :return:
            삽입 성공시 True, 실패시 False를 리턴함.
        :example:
            >>> from pyhwpx import Hwp
            >>> hwp = Hwp()
            >>> hwp.insert_text('Hello world!')
            >>> hwp.BreakPara()
        """
        param = self.hwp.HParameterSet.HInsertText
        self.hwp.HAction.GetDefault("InsertText", param.HSet)
        param.Text = text
        return self.hwp.HAction.Execute("InsertText", param.HSet)
    
    def to_PDF(self, path):
        """
        HWP 문서를 PDF로 저장하는 메서드.

        :param path: 저장할 PDF 파일의 경로 (절대경로 또는 상대경로)
        :return: 작업 실행 결과
        """
        # 상대경로를 절대경로로 변환
        if path.lower()[1] != ":":
            path = os.path.join(os.getcwd(), path)

        # FileSaveAsPdf 기본 설정 가져오기
        self.hwp.HAction.GetDefault("FileSaveAsPdf", self.hwp.HParameterSet.HFileOpenSave.HSet)
        
        # FileSaveAsPdf 파라미터 설정
        self.hwp.HParameterSet.HFileOpenSave.filename = path  # 저장할 PDF 파일 절대경로
        self.hwp.HParameterSet.HFileOpenSave.Format = "PDF"  # 파일 형식
        self.hwp.HParameterSet.HFileOpenSave.Attributes = 16384  # 속성 설정

        # 설정된 FileSaveAsPdf 작업 실행
        return self.hwp.HAction.Execute("FileSaveAsPdf", self.hwp.HParameterSet.HFileOpenSave.HSet)    
        
    def set_password(self, password: str):
        """
        HWP 문서에 파일 비밀번호를 설정하는 메서드.
        한글 2024이상 버젼에서 적용된다.
        
        Parameters:
            password (str): 설정할 비밀번호.
        """
        # FilePassword 작업 기본 설정 가져오기
        self.hwp.HAction.GetDefault("FilePassword", self.hwp.HParameterSet.HPassword.HSet)
        
        # FilePassword 파라미터 설정
        self.hwp.HParameterSet.HPassword.string = password   # 비밀번호 설정
        self.hwp.HParameterSet.HPassword.Level = 1       # 보안 수준 설정
        self.hwp.HParameterSet.HPassword.DialogType = 2 # 대화 상자 유형 설정
        
        # 설정된 FilePassword 작업 실행
        return self.hwp.HAction.Execute("FilePassword", self.hwp.HParameterSet.HPassword.HSet)

    def set_font_style(self, fontstyle: str = "굴림"):
        '블럭으로 잡은 글자의 글꼴을 변경한다.'
        
        # 문자 모양 설정을 초기화합니다.
        self.hwp.HAction.GetDefault("CharShape", self.hwp.HParameterSet.HCharShape.HSet)

        # 글꼴 설정
        self.hwp.HParameterSet.HCharShape.FaceNameUser = fontstyle
        self.hwp.HParameterSet.HCharShape.FontTypeUser = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FaceNameSymbol = fontstyle
        self.hwp.HParameterSet.HCharShape.FontTypeSymbol = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FaceNameOther = fontstyle
        self.hwp.HParameterSet.HCharShape.FontTypeOther = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FaceNameJapanese = fontstyle
        self.hwp.HParameterSet.HCharShape.FontTypeJapanese = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FaceNameHanja = fontstyle
        self.hwp.HParameterSet.HCharShape.FontTypeHanja = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FaceNameLatin = fontstyle
        self.hwp.HParameterSet.HCharShape.FontTypeLatin = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FaceNameHangul = fontstyle
        self.hwp.HParameterSet.HCharShape.FontTypeHangul = self.hwp.FontType("TTF")

        # 설정한 문자 모양을 실행하여 적용합니다.
        return self.hwp.HAction.Execute("CharShape", self.hwp.HParameterSet.HCharShape.HSet)

    def set_font_size(self, height : int = 10): 
        '블럭으로 잡은 글자의 크기를 변경한다'

        # 문자 모양 설정을 초기화합니다.
        self.hwp.HAction.GetDefault("CharShape", self.hwp.HParameterSet.HCharShape.HSet)

        # 글꼴 유형 및 크기 설정
        self.hwp.HParameterSet.HCharShape.FontTypeUser = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeSymbol = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeOther = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeJapanese = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeHanja = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeLatin = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeHangul = self.hwp.FontType("TTF")

        # 글꼴 크기 설정
        self.hwp.HParameterSet.HCharShape.Height = self.hwp.PointToHwpUnit(float(height))

        # 설정한 문자 모양을 실행하여 적용합니다.
        self.hwp.HAction.Execute("CharShape", self.hwp.HParameterSet.HCharShape.HSet)

        # 문자 모양 설정을 다시 초기화합니다.
        self.hwp.HAction.GetDefault("CharShape", self.hwp.HParameterSet.HCharShape.HSet)

        # 동일한 글꼴 유형 설정
        self.hwp.HParameterSet.HCharShape.FontTypeUser = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeSymbol = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeOther = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeJapanese = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeHanja = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeLatin = self.hwp.FontType("TTF")
        self.hwp.HParameterSet.HCharShape.FontTypeHangul = self.hwp.FontType("TTF")

        # 설정한 문자 모양을 실행하여 적용합니다.
        return self.hwp.HAction.Execute("CharShape", self.hwp.HParameterSet.HCharShape.HSet)
