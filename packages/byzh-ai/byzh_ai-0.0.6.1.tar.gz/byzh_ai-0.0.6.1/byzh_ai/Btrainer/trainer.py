import os
import time
from pathlib import Path
from typing import Literal

import copy
import torch
from torch import nn
import numpy as np

from byzh_core.Btqdm import B_Tqdm
from byzh_core.Bwriter import B_Writer
from byzh_core.Butils import B_Color, B_Appearance

from ..Bearly_stop import *
from ..Butils import b_get_device, b_get_gpu_nvidia


def get_total_and_correct(outputs, labels) -> tuple[int, int]:
    total = labels.size(0)
    _, predicted = torch.max(outputs.data, 1)
    # print(f'predict: {predicted.cpu().numpy()}')
    # print(f'labels: {labels.cpu().numpy()}')
    correct = (predicted == labels).sum().item()
    # print(f'correct/total: {correct}/{total}')
    return total, correct

class _saveBestDuringTrain:
    def __init__(self, path, rounds):
        self.path = path
        self.rounds = rounds
        self.cnt = 0
    def __call__(self):
        self.cnt += 1
        if self.cnt > self.rounds:
            self.cnt = 0
            return True
        return False

class _Func:
    def __init__(self, func=None):
        self.func = func
    def set_func(self, func):
        self.func = func
    def __call__(self, **kwargs):
        if self.func is None:
            return None
        result = self.func(**kwargs)
        return result


class B_Trainer:
    def __init__(
        self,
        model,
        optimizer,
        criterion,
        train_loader,
        val_loader,
        test_loader=None,
        device=None,
        inputs_func=lambda inputs: inputs,
        outputs_func=lambda outputs: outputs,
        labels_func=lambda labels: labels,
        total_and_correct_func=get_total_and_correct,
        lrScheduler=None,
        isParallel:bool=False,
        isSpikingjelly12:bool=False,
        isSpikingjelly14:bool=False,
    ):
        '''
        训练:\n
        train_eval_s\n
        训练前函数:\n
        load_model, load_optimizer, load_lrScheduler, set_writer, set_stop_by_acc\n
        训练后函数:\n
        save_latest_checkpoint, save_best_checkpoint, calculate_model
        :param model:
        :param optimizer:
        :param criterion:
        :param train_loader:
        :param val_loader:
        :param test_loader:
        :param device: 若不指定, 则自动判断
        :param inputs_func:
        :param outputs_func:
        :param labels_func:
        :param total_and_correct_func: 如何通过模型得到的 outputs, labels 计算 total, correct
        :param lrScheduler:
        :param isParallel: 是否启用多GPU
        :param isSpikingjelly12: 是否为SNN
        :param isSpikingjelly14: 是否为SNN
        '''
        super().__init__()
        self.train_loss_batches_lst = []
        self.train_loss_epoch_lst = []
        self.train_acc_lst = []
        self.val_acc_lst = []

        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.test_loader = test_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device if device else b_get_device()
        self.lrScheduler = lrScheduler
        self.isParallel = isParallel
        self.isSpikingjelly12 = isSpikingjelly12
        self.isSpikingjelly14 = isSpikingjelly14
        self.epoch = 0
        self.writer = None

        if not callable(inputs_func) or not callable(outputs_func) or not callable(labels_func):
            raise ValueError("inputs_func, outputs_func, labels_func必须为可调用对象")
        self.inputs_func = inputs_func
        self.outputs_func = outputs_func
        self.labels_func = labels_func
        self.total_and_correct_func = total_and_correct_func

        # 设置设备
        self.model.to(self.device)

        # early stop
        self._stop_by_acc = _Func()
        self._stop_by_acc_delta = _Func()
        self._stop_by_loss = _Func()
        self._stop_by_loss_delta = _Func()
        self._stop_by_overfitting = _Func()
        # early reload
        self._reload_by_loss = _Func()

        # save_temp
        self._save_best_during_train = None
        # save_best
        self._best_acc = 0
        self._best_model_state_dict = None
        self._best_optimizer_state_dict = None
        self._best_lrScheduler_state_dict = None

        if self.isParallel:
            if str(self.device) == str(torch.device("cuda")):
                if torch.cuda.device_count() > 1:
                    print(f"[set] 当前cuda数量:{torch.cuda.device_count()}, 使用多GPU训练")
                    self.model = nn.DataParallel(self.model)
                else:
                    print(f"[set] 当前cuda数量:{torch.cuda.device_count()}, 使用单GPU训练")

    def save_latest_checkpoint(self, path):
        '''
        字典checkpoint包含net, optimizer, lrScheduler
        '''
        parent_path = Path(path).parent
        os.makedirs(parent_path, exist_ok=True)

        checkpoint = {}
        if self.model:
            checkpoint['model'] = self.model.state_dict()
        if self.optimizer:
            checkpoint['optimizer'] = self.optimizer.state_dict()
        if self.lrScheduler:
            checkpoint['lrScheduler'] = self.lrScheduler.state_dict()

        torch.save(checkpoint, path)
        print(f"[save] latest_checkpoint 已保存到 {path}")

    def save_best_checkpoint(self, path):
        '''
        字典checkpoint包含net, optimizer, lrScheduler
        '''
        parent_path = Path(path).parent
        os.makedirs(parent_path, exist_ok=True)

        checkpoint = {}
        if self._best_model_state_dict:
            checkpoint['model'] = self._best_model_state_dict
        if self._best_optimizer_state_dict:
            checkpoint['optimizer'] = self._best_optimizer_state_dict
        if self._best_lrScheduler_state_dict:
            checkpoint['lrScheduler'] = self._best_lrScheduler_state_dict

        torch.save(checkpoint, path)
        print(f"[save] best_checkpoint 已保存到 {path}")
    def load_model(self, path):
        checkpoint = torch.load(path, map_location='cpu')
        model_state_dict = checkpoint['model']

        flag_model = isinstance(self.model, nn.DataParallel)
        flag_dict = list(model_state_dict.keys())[0].startswith('module.')
        if (not flag_model) and flag_dict:
            model_state_dict = {k[7:]: v for k, v in model_state_dict.items()}
        if flag_model and (not flag_dict):
            model_state_dict = {'module.' + k: v for k, v in model_state_dict.items()}

        self.model.load_state_dict(model_state_dict)
        self.model.to(self.device)
        print(f"[load] model 已从 {path} 加载")

    def load_optimizer(self, path):
        checkpoint = torch.load(path)
        optimizer_state_dict = checkpoint['optimizer']
        self.optimizer.load_state_dict(optimizer_state_dict)
        print(f"[load] optimizer 已从{path}加载")

    def load_lrScheduler(self, path):
        checkpoint = torch.load(path)
        lrScheduler_state_dict = checkpoint['lrScheduler']
        if self.lrScheduler is not None and lrScheduler_state_dict is not None:
            self.lrScheduler.load_state_dict(lrScheduler_state_dict)
            print(f"[load] lrScheduler 已从{path}加载")
        else:
            print(f"[load] path中的lrScheduler为None, 加载失败")

    def get_confusion_matrix(self, y_true, y_pred):
        from sklearn.metrics import confusion_matrix
        result = confusion_matrix(y_true, y_pred)
        return result

    def get_f1_score(self, y_true, y_pred, average='macro'):
        from sklearn.metrics import f1_score
        result = f1_score(y_true, y_pred, average=average)
        return result

    def set_writer1(self, path: Path|str, mode: Literal["a", "w"] = "a"):
        '''
        请在训练前设置set_writer
        '''
        self.writer = B_Writer(path, mode=mode, time_file=True)

        self.writer.toFile("[dataset] -> " + self.train_loader.dataset.__class__.__name__, ifTime=False)
        self.writer.toFile("[batch_size] -> " + str(self.train_loader.batch_size), ifTime=False)
        self.writer.toFile("[lr] -> " + str(self.optimizer.param_groups[0]['lr']), ifTime=False)
        self.writer.toFile("[criterion] -> " + str(self.criterion), ifTime=False)
        self.writer.toFile("[optimizer] -> " + str(self.optimizer), ifTime=False)
        if self.lrScheduler is not None:
            self.writer.toFile("[lrScheduler] -> " + str(self.lrScheduler), ifTime=False)
        self.writer.toFile("[model] -> " + str(self.model), ifTime=False)

        print(f'[set] 日志将保存到{path}')
        return self.writer

    def set_writer2(self, writer: B_Writer):
        '''
        请在训练前设置set_writer
        '''
        self.writer = writer

        self.writer.toFile("[dataset] -> " + self.train_loader.dataset.__class__.__name__, ifTime=False)
        self.writer.toFile("[batch_size] -> " + str(self.train_loader.batch_size), ifTime=False)
        self.writer.toFile("[lr] -> " + str(self.optimizer.param_groups[0]['lr']), ifTime=False)
        self.writer.toFile("[criterion] -> " + str(self.criterion), ifTime=False)
        self.writer.toFile("[optimizer] -> " + str(self.optimizer), ifTime=False)
        if self.lrScheduler is not None:
            self.writer.toFile("[lrScheduler] -> " + str(self.lrScheduler), ifTime=False)
        self.writer.toFile("[model] -> " + str(self.model), ifTime=False)

        print(f'[set] 日志将保存到{self.writer.path}')
        return self.writer

    def set_save_during_train(self, path: Path|str, rounds=10):
        '''
        请在训练前设置set_save_during_train
        :param path: 保存路径
        :param rounds: 每rounds次, 保存一次
        '''
        self._save_best_during_train = _saveBestDuringTrain(path, rounds)
        self._print_and_toWriter(f"[set] save_best_during_train")
    def set_stop_by_acc(self, rounds=10, delta=0.01):
        '''
        请在训练前设置set_stop_by_acc
        :param rounds: 连续rounds次, val_acc - max_val_acc > delta, 则停止训练
        '''
        self._stop_by_acc.func = B_StopByAcc(rounds=rounds, delta=delta)
        self._print_and_toWriter(f"[set] stop_by_acc")
    def set_stop_by_overfitting(self, rounds=10, delta=0.1):
        '''
        请在训练前设置set_stop_by_overfitting
        :param rounds: 连续rounds次, train_acc - val_acc > delta, 则停止训练
        '''
        self._stop_by_overfitting.func = B_StopByOverfitting(rounds=rounds, delta=delta)
        self._print_and_toWriter(f"[set] stop_by_overfitting")
    def set_stop_by_acc_delta(self, rounds=10, delta=0.003):
        '''
        请在训练前设置set_stop_by_acc_delta
        :param rounds: 连续rounds次, |before_acc - val_acc| <= delta, 则停止训练
        '''
        self._stop_by_acc_delta.func = B_StopByAccDelta(rounds=rounds, delta=delta)
        self._print_and_toWriter(f"[set] stop_by_acc_delta")
    def set_stop_by_loss(self, rounds=10, delta=.0, target_loss=0.01):
        '''
        请在训练前设置set_stop_by_loss
        :param rounds: 连续rounds次, train_loss > min_train_loss - delta, 则停止训练
        '''
        self._stop_by_loss.func = B_StopByLoss(rounds=rounds, delta=delta, target=target_loss)
        self._print_and_toWriter(f"[set] stop_by_loss")
    def set_stop_by_loss_delta(self, rounds=10, delta=0.002):
        '''
        请在训练前设置set_stop_by_loss_delta
        :param rounds: 连续rounds次, |before_loss - now_loss| <= delta, 则停止训练
        '''
        self._stop_by_loss_delta.func = B_StopByLossDelta(rounds=rounds, delta=delta)
        self._print_and_toWriter(f"[set] stop_by_loss_delta")
    def set_reload_by_loss(self, max_reload_count=5, reload_rounds=10, delta=0.01):
        '''
        请在训练前设置set_reload_by_loss\n
        :param reload_rounds: 连续reload_rounds次都是train_loss > min_train_loss + delta
        '''
        self._reload_by_loss.func = B_ReloadByLoss(max_reload_count, reload_rounds, delta)
        self._print_and_toWriter(f"[set] reload_by_loss")

    def draw_loss_acc(self, path: Path|str, if_show=False):
        """
        :param path: 如果以.csv结尾, 则保存为csv文件, 否则保存为图片
        :param if_show:
        :return:
        """
        from ..Bvisual import b_draw_loss_acc
        b_draw_loss_acc(self.train_loss_batches_lst, self.train_acc_lst, self.val_acc_lst, path, if_show)

    def get_metric_lists(self):
        result = (
            self.train_loss_batches_lst,
            self.train_loss_epoch_lst,
            self.train_acc_lst,
            self.val_acc_lst
        )
        return result

    def calculate_model(self, dataloader=None, model=None, inputs_func=None, outputs_func=None, labels_func=None):
        '''
        如果不指定, 则用类内的
        :param dataloader: 默认self.val_loader
        :param model: 默认self.model
        :return: accuracy, inference_time, params, outputs_list, labels_list
        '''
        if dataloader==None:
            dataloader = self.val_loader
        if model==None:
            model = self.model
        model.eval()

        if inputs_func is not None:
            assert callable(inputs_func), "inputs_func必须为可调用对象"
            self.inputs_func = inputs_func
        if outputs_func is not None:
            assert callable(outputs_func), "outputs_func必须为可调用对象"
            self.outputs_func = outputs_func
        if labels_func is not None:
            assert callable(labels_func), "labels_func必须为可调用对象"
            self.labels_func = labels_func

        total = 0
        correct = 0
        outputs_list = []
        labels_list = []
        inference_time = []
        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                labels = self.labels_func(labels)
                inputs = self.inputs_func(inputs)
                start_time = time.time()
                outputs = model(inputs)
                end_time = time.time()
                outputs = self.outputs_func(outputs)

                outputs_list.append(outputs.cpu())
                labels_list.append(labels.cpu())

                inference_time.append(end_time - start_time)

                sample_total, sample_correct = self.total_and_correct_func(outputs, labels)
                total += sample_total
                correct += sample_correct

                self._spikingjelly_process()
        # 平均推理时间
        inference_time = sum(inference_time) / len(inference_time)
        # acc
        accuracy = correct / total
        # 参数量
        params = sum(p.numel() for p in model.parameters())

        info = f'[calc] accuracy: {accuracy:.3f}'
        self._print_and_toWriter(info)
        info = f'------ inference_time: {inference_time:.2e}s, params: {params / 1e3}K'
        self._print_and_toWriter(info)


        return accuracy, inference_time, params, outputs_list, labels_list

    def classify_unlabeled_data(self, dataloader) -> list: # todo
        '''
        返回 预测标签
        '''
        self.model.eval()
        labels = []
        with torch.no_grad():
            for elements in dataloader:
                if len(elements) == 2:
                    inputs, _ = elements
                else:
                    inputs = elements
                inputs = inputs.to(self.device)
                outputs = self.model(inputs)
                _, predicted = torch.max(outputs, 1)
                labels.extend(predicted.cpu())
                self._spikingjelly_process()
        return labels

    def classify_labeled_data(self, dataloader) -> (list, list, float): # todo
        '''
        返回 真实标签, 预测标签, acc
        '''
        self.model.eval()
        true_label = []
        pred_label = []
        with torch.no_grad():
            for inputs, labels in dataloader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                outputs = self.model(inputs)
                _, predicted = torch.max(outputs, 1)
                true_label.extend(labels.cpu())
                pred_label.extend(predicted.cpu())
                self._spikingjelly_process()
        # acc
        acc = (np.array(true_label) == np.array(pred_label)).sum() / len(true_label)
        return true_label, pred_label, acc

    def train_eval_s(
            self,
            epochs,
            test:bool=False,
            inputs_func=None,
            outputs_func=None,
            labels_func=None
    ):
        '''
        :param epochs:
        :param test: 在传递test_loader后, 若为True, 则同时在测试集测试
        :param inputs_func: 对inputs的处理函数
        :param outputs_func: 对outputs的处理函数
        :param labels_func: 对labels的处理函数
        :return:
        '''
        if inputs_func is not None:
            assert callable(inputs_func), "inputs_func必须为可调用对象"
            self.inputs_func = inputs_func
        if outputs_func is not None:
            assert callable(outputs_func), "outputs_func必须为可调用对象"
            self.outputs_func = outputs_func
        if labels_func is not None:
            assert callable(labels_func), "labels_func必须为可调用对象"
            self.labels_func = labels_func

        for epoch in range(epochs):
            self.epoch = epoch
            train_acc, train_loss, current_lr = self._train_once(epoch, epochs)
            val_acc = self._eval_once()
            if test:
                test_acc = self._test_once()
            print() # 换行
            # 日志
            if self.writer is not None:
                info = f'Epoch [{epoch}/{epochs}], lr: {current_lr:.2e} | ' \
                       f'train_loss: {train_loss:.3f} | train_acc: {train_acc:.3f}, val_acc: {val_acc:.3f}'
                if test:
                    info += f', test_acc: {test_acc:.3f}'
                self.writer.toFile(info)
            # 保存模型
            if self._save_best_during_train is not None:
                if self._save_best_during_train():
                    self.save_best_checkpoint(self._save_best_during_train.path)
            # 早停and重加载
            match self._stop_and_reload(train_loss, train_acc, val_acc):
                case "break":
                    break
                case "continue":
                    pass

    def _train_once(self, epoch, epochs):
        bar = B_Tqdm(range=len(self.train_loader))
        current_lr = self.optimizer.param_groups[0]['lr']

        self.model.train()
        correct = 0
        total = 0
        losses = 0
        for iter, (inputs, labels) in enumerate(self.train_loader):
            # 基本训练
            inputs, labels = inputs.to(self.device), labels.to(self.device)
            labels = self.labels_func(labels)
            inputs = self.inputs_func(inputs)
            outputs = self.model(inputs)
            outputs = self.outputs_func(outputs)

            loss = self.criterion(outputs, labels)
            self.optimizer.zero_grad()  # 清零梯度
            loss.backward()  # 计算梯度
            self.optimizer.step()  # 更新参数
            # SNN
            self._spikingjelly_process()
            # 进度条
            bar.update(
                1,
                color=B_Color.BLUE,
                appearance=B_Appearance.HIGHLIGHT,
                prefix=f"Epoch [{epoch:0{len(str(epochs))}}/{epochs}]",
                suffix=f"lr: {current_lr:.2e}, loss: {loss.item():.3f}"
            )
            # 数据记录
            self.train_loss_batches_lst.append(loss.item())

            losses += loss.item()

            sample_total, sample_correct = self.total_and_correct_func(outputs, labels)
            total += sample_total
            correct += sample_correct

        accuracy = correct / total
        train_loss = losses / len(self.train_loader)
        # 资源占用信息
        usage = ' '
        if self.device == torch.device('cuda'):
            gpu = b_get_gpu_nvidia()[0]
            usage = f' (GPU: {gpu[-2]}/{gpu[-1]}) '
        elif self.device == torch.device('cpu'):
            # 获取cpu的使用率
            usage = ' (CPU) '

        # 打印信息
        print(f'Epoch [{epoch:0{len(str(epochs))}}/{epochs}]{usage}(train_loss: {train_loss:.3f}) train_Acc: {accuracy:.3f}', end='')
        self.train_acc_lst.append(accuracy)
        self.train_loss_epoch_lst.append(train_loss)

        # 更新学习率
        if self.lrScheduler:
            self.lrScheduler.step()

        return accuracy, train_loss, current_lr

    def _eval_once(self):
        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in self.val_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                labels = self.labels_func(labels)
                inputs = self.inputs_func(inputs)
                outputs = self.model(inputs)
                outputs = self.outputs_func(outputs)

                self._spikingjelly_process()

                sample_total, sample_correct = self.total_and_correct_func(outputs, labels)
                total += sample_total
                correct += sample_correct

        # 记录accuracy
        accuracy = correct / total
        self.val_acc_lst.append(accuracy)
        # 打印信息
        print(f', val_Acc: {accuracy:.3f}', end='')

        # 保存最优模型
        if accuracy > self._best_acc:
            self._best_acc = accuracy
            self._best_model_state_dict = copy.deepcopy(self.model.state_dict())
            self._best_optimizer_state_dict = copy.deepcopy(self.optimizer.state_dict())
            self._best_lrScheduler_state_dict = copy.deepcopy(self.lrScheduler.state_dict()) if self.lrScheduler else None

        return accuracy

    def _test_once(self):
        assert self.test_loader is not None, "test_loader is None"

        self.model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for inputs, labels in self.test_loader:
                inputs, labels = inputs.to(self.device), labels.to(self.device)
                labels = self.labels_func(labels)
                inputs = self.inputs_func(inputs)
                outputs = self.model(inputs)
                outputs = self.outputs_func(outputs)
                _, predicted = torch.max(outputs, 1)

                self._spikingjelly_process()

                sample_total, sample_correct = self.total_and_correct_func(outputs, labels)
                total += sample_total
                correct += sample_correct

        # 记录accuracy
        accuracy = correct / total
        # 打印信息
        print(f', test_Acc: {accuracy:.3f}', end='')
        return accuracy


    ##### 杂项 #####

    def _spikingjelly_process(self):
        if self.isSpikingjelly14:
            from spikingjelly.activation_based import functional
            functional.reset_net(self.model)
        elif self.isSpikingjelly12:
            from spikingjelly.clock_driven import functional
            functional.reset_net(self.model)
    def _print_and_toWriter(self, info: str, if_print=True):
        if if_print:
            print(info)
        if self.writer is not None:
            self.writer.toFile(info)
    def _stop_and_reload(self, train_loss, train_acc, val_acc):
        ##### 早停
        if self._stop_by_acc(val_acc=val_acc):
            info = f'[stop] 模型在连续{self._stop_by_acc.func.rounds}个epoch内停滞, 触发stop_by_acc'
            self._print_and_toWriter(info)
            info = "[stop] " + str(self._stop_by_acc.func.cnt_list)
            self._print_and_toWriter(info, if_print=False)
            return "break"
        if self._stop_by_acc_delta(val_acc=val_acc):
            info = f'[stop] 模型在连续{self._stop_by_acc_delta.func.rounds}个epoch内过拟合, 触发stop_by_acc_delta'
            self._print_and_toWriter(info)
            info = "[stop] " + str(self._stop_by_acc_delta.func.cnt_list)
            self._print_and_toWriter(info, if_print=False)
            return "break"
        if self._stop_by_loss(train_loss=train_loss):
            info = f'[stop] 模型在连续{self._stop_by_loss.func.rounds}个epoch内停滞, 触发stop_by_loss'
            self._print_and_toWriter(info)
            info = "[stop] " + str(self._stop_by_loss.func.cnt_list)
            self._print_and_toWriter(info, if_print=False)
            return "break"
        if self._stop_by_loss_delta(train_loss=train_loss):
            info = f'[stop] 模型在连续{self._stop_by_loss_delta.func.rounds}个epoch内停滞, 触发stop_by_loss_delta'
            self._print_and_toWriter(info)
            info = "[stop] " + str(self._stop_by_loss_delta.func.cnt_list)
            self._print_and_toWriter(info, if_print=False)
            return "break"
        ##### 过拟合
        if self._stop_by_overfitting(train_acc=train_acc, val_acc=val_acc):
            info = f'[stop] 模型在连续{self._stop_by_overfitting.func.rounds}个epoch内过拟合, 触发stop_by_overfitting'
            self._print_and_toWriter(info)
            info = "[stop] " + str(self._stop_by_overfitting.func.cnt_list)
            self._print_and_toWriter(info, if_print=False)
            return "break"
        ##### 重加载
        match self._reload_by_loss(train_loss=train_loss):
            case 'normal':
                pass
            case 'reload':
                info = f'模型触发reload_by_loss(第{self._reload_by_loss.func.cnt_reload}次加载)'
                self._print_and_toWriter(info)
                # 加载
                self.model.load_state_dict(self._best_model_state_dict)
                self.optimizer.load_state_dict(self._best_optimizer_state_dict)
                if self.lrScheduler is not None:
                    self.lrScheduler.load_state_dict(self._best_lrScheduler_state_dict)
                self.calculate_model()
        return "continue"