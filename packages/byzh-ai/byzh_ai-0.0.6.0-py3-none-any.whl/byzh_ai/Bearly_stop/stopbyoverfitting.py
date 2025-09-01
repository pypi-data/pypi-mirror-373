class B_StopByOverfitting:
    def __init__(self, rounds, delta=0.1):
        '''
        连续rounds次, train_acc - val_acc > delta, 则停止训练
        '''
        self.rounds = rounds
        self.delta = delta
        self.cnt = 0
        self.cnt_list = []
    def __call__(self, train_acc, val_acc):
        if train_acc - val_acc > self.delta:
            self.cnt += 1
        else:
            self.cnt = 0

        self.cnt_list.append(self.cnt)
        if self.cnt > self.rounds:
            return True
        return False