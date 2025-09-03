import torch
import pickle
import websocket
from typing import Dict
from torch import nn
from torch.optim.optimizer import Optimizer
from abc import ABCMeta, abstractmethod
from ..pb import ConLParams, ConLMetrics


class ConLOptimizer(Optimizer, metaclass=ABCMeta):
    def __init__(self, args, org_optimizer, parameters):
        self._org_optimizer = org_optimizer
        self._server_url = args.server_url
        self._round = 0
        self._inner_loop = args.inner_loop
        self._inner_cnt = 0
        self._diff_latest = 0.
        self._criterion = nn.MSELoss(reduction="sum")

        ws_target_url = "ws://%s/ws" % args.server_url
        self._ws = websocket.create_connection(ws_target_url)

        defaults = dict(eta=args.eta)
        super().__init__(filter(lambda p: p.requires_grad, parameters), defaults)

    def __del__(self):
        self._ws.close()

    @torch.no_grad()
    def precondition(self):
        pass

    @abstractmethod
    def aggregate(self, rcv_p: Dict) -> Dict:
        pass

    @torch.no_grad()
    def step(self, closure=None):
        self.precondition()

        loss = self._org_optimizer.step(closure)

        self._inner_cnt += 1
        if self._inner_cnt >= self.inner_loop:
            # pull
            msg = ConLParams()
            msg.op = "pull"
            self._ws.send(msg.SerializeToString(), websocket.ABNF.OPCODE_BINARY)
            message = self._ws.recv()
            msg.ParseFromString(message)

            params = None
            if len(msg.params) > 0:
                params = pickle.loads(msg.params)
            merged = self.aggregate(params)

            # push
            msg.op = "push"
            msg.params = pickle.dumps(merged)
            self._ws.send(msg.SerializeToString(), websocket.ABNF.OPCODE_BINARY)
            self._inner_cnt = 0

        return loss

    def round_update(self, metrics: Dict):
        self._round += 1
        metrics_list = []
        for k, v in metrics.items():
            mt = ConLMetrics()
            mt.name = k
            mt.value = v
            metrics_list.append(mt)

        msg = ConLParams()
        msg.op = "update"
        msg.stats.round = self._round
        msg.stats.metrics.extend(metrics_list)

        self._ws.send(msg.SerializeToString(), websocket.ABNF.OPCODE_BINARY)
        self._ws.recv()

    @property
    def optimizer(self):
        return self._org_optimizer

    @property
    def lr(self):
        lr = 0.
        for group in self._org_optimizer.param_groups:
            lr = group['lr']
        return lr

    @property
    def inner_loop(self):
        return self._inner_loop

    @property
    def diff(self):
        return self._diff_latest

