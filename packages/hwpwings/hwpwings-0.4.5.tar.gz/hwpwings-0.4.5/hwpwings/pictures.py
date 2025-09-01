class pictures:
    
    def insert_picture(self, path: str, sizeoption: int=0):
        """
        HWP 문서에 그림을 삽입하는 메서드입니다.

        Parameters:
            path (str): 삽입할 그림 파일의 경로입니다.
            sizeoption (int): 그림의 크기 옵션을 지정합니다.
                - 0: 이미지 원래 크기로 삽입합니다.
                - 2: 셀 안에 있을 때 셀을 채웁니다 (그림 비율 무시).
                - 3: 셀에 맞추되 그림 비율을 유지하여 크기를 변경합니다.

        Returns:
            삽입된 그림 객체를 반환합니다.
        """
        return self.hwp.InsertPicture(path, sizeoption=sizeoption)
    
    def delete_picture(self, target_index:int=1):
        """
        번호에 맞는 그림을 삭제한다
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

        # 그림 번호가 존재하는지 확인 후 삭제
        selected_pos = picture_dict.get(target_index)
        if selected_pos:
            # Move to the selected position and delete the picture
            self.hwp.SetPosBySet(selected_pos)
            self.hwp.FindCtrl()
            self.hwp.HAction.Run("Delete")
            return True
        else:
            # Target index does not exist
            return False

    def delete_all_pictures(self):
        """
        삽입된 모든 그림을 삭제합니다.
        """
        ctrl = self.hwp.HeadCtrl
        picture_deleted = False

        # Iterate through all controls to find and delete pictures
        while ctrl:
            if ctrl.UserDesc == '그림':
                self.hwp.SetPosBySet(ctrl.GetAnchorPos(0))  # 그림객체로 이동
                self.hwp.FindCtrl()
                self.hwp.HAction.Run("Delete")
                picture_deleted = True
            ctrl = ctrl.Next

        return picture_deleted