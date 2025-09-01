# 페이지 조작하기
class page():
    @property
    def page_Count(self): # 제어중인 한글 페이지수를 리턴합니다
        """
        현재 문서의 총 페이지 수를 리턴한다.
        :return:
        """
        return self.hwp.PageCount
    
    @property
    def current_page(self):
        """
        현재 쪽번호를 리턴.
        1페이지에 있다면 1을 리턴한다.
        새쪽번호가 적용되어 있어도
        페이지의 인덱스를 리턴한다.
        :return:
        """
        return self.hwp.XHwpDocuments.Active_XHwpDocument.XHwpDocumentInfo.CurrentPage + 1

    @property
    def page_source(self, format="HWPML2X", option=""):
        '''
        현재 열려있는 한글파일의 xml을 얻어온다.
        soup.select("TEXT > CHAR") 로 모든 텍스트를 추출할 수 있다.
        
        from bs4 import BeautifulSoup

        # XML 데이터를 파싱
        xml = hwp.page_source
        soup = BeautifulSoup(xml, 'xml')

        # 전체 TEXT > CHAR 요소 추출
        all_chars = soup.select("TEXT > CHAR")

        # 표(TABLE) 내부의 TEXT > CHAR 요소 추출
        table_chars = []
        for table in soup.select("TABLE"):
            table_chars.extend(table.select("TEXT > CHAR"))

        # all_chars에서 table_chars에 속하지 않는 요소들만 선택
        outside_table_chars = []

        # all_chars 리스트를 하나씩 순회
        for char in all_chars:
            # 만약 char가 table_chars에 포함되지 않으면
            if char not in table_chars:
                # outside_table_chars 리스트에 추가
                outside_table_chars.append(char)

        # 결과 출력
        for char in outside_table_chars:
            print(char.text)
        '''
        return self.hwp.GetTextFile(Format=format, option=option)

    def page_Copy(self:None):
        """
        쪽 복사
        """
        return self.hwp.HAction.Run("CopyPage")
    
    def page_Paste(self:None):
        """
        쪽 붙여넣기
        """
        return self.hwp.HAction.Run("PastePage")
    
    def page_Delete(self:None):
        """
        쪽 지우기
        """
        return self.hwp.HAction.Run("DeletePage")
    
    def goto_Startpage(self:None):
        '문서의 시작으로 이동한다'
        return self.hwp.HAction.Run("MoveDocBegin")
    
    def goto_Endpage(self:None):
        '문서의 끝으로 이동한다'
        return self.hwp.HAction.Run("MoveDocEnd")

    def goto_page(self, page_index: int | str = 1) -> tuple[int, int]: # 지정한 페이지로 이동합니다.
        """
        새쪽번호와 관계없이 페이지 순서를 통해
        특정 페이지를 찾아가는 메서드.
        1이 1페이지임.
        :param page_index:
        :return: tuple(인쇄기준페이지, 페이지인덱스)
        """
        if int(page_index) > self.hwp.PageCount:
            raise ValueError("입력한 페이지 인덱스가 문서 총 페이지보다 큽니다.")
        elif int(page_index) < 1:
            raise ValueError("1 이상의 값을 입력해야 합니다.")
        self.goto_printpage(page_index)
        cur_page = self.current_page
        if page_index == cur_page:
            pass
        elif page_index < cur_page:
            for _ in range(cur_page - page_index):
                self.MovePageUp()
        else:
            for _ in range(page_index - cur_page):
                self.MovePageDown()
        return self.current_printpage, self.current_page