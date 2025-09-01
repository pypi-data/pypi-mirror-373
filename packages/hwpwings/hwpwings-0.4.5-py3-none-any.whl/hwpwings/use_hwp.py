import win32com.client as win32
import os, time
import pythoncom
import win32gui
import requests
import winreg
from .field import field
from .page import page
from .tablecell import tablecell
from .dataframe import dataframe
from .etc_function import etc_function
from .function_parts import function_parts
from .pictures import pictures
from .select import select
from .keyboard import keyboard
from .text import text
from .custom import custom
from .position import position

# 설정
reg_path = r"Software\HNC\HwpAutomation\Modules"
value_name = "FilePathCheckerModule"
file_path = r'C:\Temp\Temp2\FilePathCheckerModule.dll'
dir_path = os.path.dirname(file_path)
download_url = 'https://downapi.cafe.naver.com/v1.0/cafes/article/file/4ebec5bb-3fae-11f0-865d-0050569edfd8/download'

# 레지스트리에 값이 이미 있는지 확인
registry_exists = False
try:
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ)
    winreg.QueryValueEx(key, value_name)
    winreg.CloseKey(key)
    registry_exists = True
except FileNotFoundError:
    registry_exists = False

if registry_exists:
    # print(f'레지스트리에 "{value_name}" 값이 이미 존재합니다. 작업을 건너뜁니다.')
    pass
else:
    # 폴더 없으면 생성
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    # 파일 다운로드
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'origin': 'https://cafe.naver.com',
        'priority': 'u=1, i',
        'referer': 'https://cafe.naver.com/ca-fe/cafes/31023030/articles/344?menuid=15&oldPath=%2FArticleRead.nhn%3Fclubid%3D31023030%26articleid%3D344%26menuid%3D15',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
    }
    response = requests.get(download_url, headers=headers)
    response.raise_for_status()

    # 파일 저장
    with open(file_path, 'wb') as f:
        f.write(response.content)

    # 레지스트리에 등록
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path)
        winreg.SetValueEx(key, value_name, 0, winreg.REG_SZ, file_path)
        winreg.CloseKey(key)
        print(f'''레지스트리에 "{value_name}" 값을 성공적으로 등록했습니다.
              이제 보안경고창이 나오지 않습니다.''')
    except Exception as e:
        print(f"레지스트리 등록 중 오류 발생: {e}")

# COM Type Library 생성
try:
    win32.gencache.EnsureModule(
        '{7D2B6F3C-1D95-4E0C-BF5A-5EE564186FBC}', 0, 1, 0
    )
except ImportError:
    pass
except Exception as e:
    print(f"EnsureModule 오류: {e}")


class HWP(field, page, tablecell, dataframe, etc_function, function_parts, pictures, select, keyboard, text, custom, position):
    def __init__(self) -> None:
        try:
            self.hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
            self.hwp.XHwpWindows.Item(0).Visible = True
            self.num = 0
            try:
                self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
            except:
                pass
        except Exception:
            pythoncom.CoUninitialize()
            pythoncom.CoInitialize()
            
            self.hwp = win32.gencache.EnsureDispatch("hwpframe.hwpobject")
            self.hwp.XHwpWindows.Item(0).Visible = True
            self.num = 0
            try:
                self.hwp.RegisterModule("FilePathCheckDLL", "FilePathCheckerModule")
            except:
                pass

        time.sleep(0.2)

    # 기본조작

    def add_doc(self:None):
        '새 문서를 연다.'
        return self.hwp.XHwpDocuments.Add(0)  # 0은 새 창, 1은 새 탭
    
    def add_tab(self:None):
        '새 탭을 연다.'
        return self.hwp.XHwpDocuments.Add(1)  # 0은 새 창, 1은 새 탭

    def open(self, path:str):
        '기존 한글파일을 연다.'
        return self.hwp.Open(path)

    def close(self:None):
        '''
        활성화된 한글파일을 저장하지 않고 닫는다.
        단 열려있는 문서가 1개라면, 창이 꺼지지 않는다.
        '''
        self.hwp.Clear(1)
        return self.hwp.XHwpDocuments.Active_XHwpDocument.Close(isDirty=False)

    def save_As(self, path, format="HWPX", arg=""):
        """
        현재 편집중인 문서를 지정한 이름으로 저장한다.
        format, arg의 일반적인 개념에 대해서는 Open()참조.
        "Hwp" 포맷으로 파일 저장 시 arg에 지정할 수 있는 옵션은 다음과 같다.
        "lock:true" - 저장한 후 해당 파일을 계속 오픈한 상태로 lock을 걸지 여부
        "backup:false" - 백업 파일 생성 여부
        "compress:true" - 압축 여부
        "fullsave:false" - 스토리지 파일을 완전히 새로 생성하여 저장
        "prvimage:2" - 미리보기 이미지 (0=off, 1=BMP, 2=GIF)
        "prvtext:1" - 미리보기 텍스트 (0=off, 1=on)
        "autosave:false" - 자동저장 파일로 저장할 지 여부 (TRUE: 자동저장, FALSE: 지정 파일로 저장)
        "export" - 다른 이름으로 저장하지만 열린 문서는 바꾸지 않는다.(lock:false와 함께 설정되어 있을 시 동작)
        여러 개를 한꺼번에 할 경우에는 세미콜론으로 구분하여 연속적으로 사용할 수 있다.
        "lock:TRUE;backup:FALSE;prvtext:1"

        :param path:
            문서 파일의 전체경로

        :param format:
            문서 형식. 생략하면 "HWPX"가 지정된다.

        :param arg:
            세부 옵션. 의미는 format에 지정한 파일 형식에 따라 다르다. 생략하면 빈 문자열이 지정된다.

        :return:
            성공하면 True, 실패하면 False
        """
        # 확장자 검사
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        if ext not in [".hwp", ".hwpx"]:
            raise ValueError("올바른 확장자를 붙여주십시오 (.hwp 또는 .hwpx)")
        
        if path.lower()[1] != ":":
            path = os.path.join(os.getcwd(), path)
        return self.hwp.SaveAs(Path=path, Format=format, arg=arg)


# 인터페이스 조작하기
    @property
    def XHwpWindows(self:None):
        return self.hwp.XHwpWindows
    
    @property
    def title(self) -> str:  # self의 타입은 생략하거나 HwpController로 지정할 수 있음
        if self.num == 0:
            self.hwp.XHwpDocuments.Item(self.num).SetActive_XHwpDocument()  
            return self.get_active_window_title()
        else:
            self.hwp.XHwpDocuments.Item(self.num).SetActive_XHwpDocument()
            return self.get_active_window_title()

    def maximize_window(self:None):
        """현재 창 최대화"""
        win32gui.ShowWindow(
            self.XHwpWindows.Active_XHwpWindow.WindowHandle, 3)

    def minimize_window(self:None):
        """현재 창 최소화"""
        win32gui.ShowWindow(
            self.XHwpWindows.Active_XHwpWindow.WindowHandle, 6)
    
    def show_window(self:None):
        """백그라운드의 한글파일을 보여줍니다"""
        win32gui.ShowWindow(
            self.XHwpWindows.Active_XHwpWindow.WindowHandle, 5)
    
    def hide_window(self:None):
        """한글파일을 백그라운드로 숨깁니다"""
        win32gui.ShowWindow(
            self.XHwpWindows.Active_XHwpWindow.WindowHandle, 0)

    def quit(self:None):
        """
        한/글을 종료한다.
        단, 저장되지 않은 변경사항이 있는 경우 팝업이 뜨므로
        clear나 save 등의 메서드를 실행한 후에 quit을 실행해야 한다.
        :return:
        """
        self.hwp.XHwpDocuments.Close(isDirty=False)
        self.hwp.Quit()
        del self.hwp    

    
    
    # HWP 객체가 있어서 분리하지 못한 기타기능
    @staticmethod
    def crop_data_from_selection(data, selection):
        """ 리스트 a의 셀 주소를 바탕으로 데이터 범위를 추출"""
        if not selection:
            return []

        # 셀 주소를 행과 열 인덱스로 변환
        indices = [HWP.cell_to_index(cell) for cell in selection]

        # 범위 계산
        min_row = min(idx[0] for idx in indices)
        max_row = max(idx[0] for idx in indices)
        min_col = min(idx[1] for idx in indices)
        max_col = max(idx[1] for idx in indices)

        # 범위 추출
        result = []
        for row in range(min_row, max_row + 1):
            result.append(data[row][min_col:max_col + 1])

        return result

