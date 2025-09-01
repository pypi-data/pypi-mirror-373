class B_StopByLoss:
    def __init__(self, rounds, delta=.0, target=0.1):
        '''
        连续rounds次, train_loss > min_train_loss - delta, 则停止训练\n
        若train_loss < target_loss, 则停止训练
        '''
        self.rounds = rounds
        self.delta = delta
        self.min_loss = float('inf')
        self.target_loss = target
        self.cnt = 0

        self.cnt_list = []
    def __call__(self, train_loss):
        if train_loss < self.target_loss:
            return True

        if train_loss >= self.min_loss - self.delta:
            self.cnt += 1
        elif train_loss < self.min_loss - self.delta:
            self.min_loss = train_loss
            self.cnt -= int(self.rounds/2)
            if self.cnt < 0:
                self.cnt = 0

        self.cnt_list.append(self.cnt)
        if self.cnt > self.rounds:
            return True
        return False