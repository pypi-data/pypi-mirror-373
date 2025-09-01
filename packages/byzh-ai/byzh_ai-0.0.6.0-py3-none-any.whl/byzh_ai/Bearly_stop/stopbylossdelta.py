class B_StopByLossDelta:
    def __init__(self, rounds, delta=0.002):
        '''
        连续rounds次, |before_loss - now_loss| <= delta, 则停止训练
        '''
        self.rounds = rounds
        self.delta = delta
        self.before_loss = float('inf')
        self.cnt = 0
        self.cnt_list = []
    def __call__(self, train_loss):
        if -self.delta <= (train_loss - self.before_loss) <= self.delta:
            self.cnt += 1
            self.before_loss = train_loss
        else:
            if self.cnt > 0:
                self.cnt -= 1
            self.before_loss = train_loss

        self.cnt_list.append(self.cnt)
        if self.cnt > self.rounds:
            return True
        return False