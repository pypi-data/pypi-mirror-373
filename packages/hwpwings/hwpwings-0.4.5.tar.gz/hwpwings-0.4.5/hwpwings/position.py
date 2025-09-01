class position():

    def save_pos(self):
        """
        현재 캐럿 위치의 좌표(List, Para, Pos)를 가져옵니다. 
        """
        return self.hwp.GetPos()

    def load_pos(self, save_pos:tuple):
        'save_pos에 저장된 좌표로 캐럿을 옮깁니다.'
        List, Para, Pos = save_pos[0], save_pos[1], save_pos[2]
        return self.hwp.SetPos(List, Para, Pos)