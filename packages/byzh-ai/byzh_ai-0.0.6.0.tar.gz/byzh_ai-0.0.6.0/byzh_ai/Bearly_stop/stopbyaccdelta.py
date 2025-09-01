class B_StopByAccDelta:
    def __init__(self, rounds, delta=0.003):
        '''
        连续rounds次, |before_acc - val_acc| <= delta, 则停止训练
        '''
        self.rounds = rounds
        self.delta = delta
        self.before_acc = 0
        self.cnt = 0
        self.cnt_list = []
    def __call__(self, val_acc):
        if val_acc == 1.0:
            return True

        if -self.delta <= (val_acc - self.before_acc) <= self.delta:
            self.cnt += 1
            self.before_acc = val_acc
        elif self.cnt > 0:
            self.cnt -= 1
            self.before_acc = val_acc
        else:
            self.before_acc = val_acc

        self.cnt_list.append(self.cnt)
        if self.cnt > self.rounds:
            return True
        return False