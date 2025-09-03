from .mixin import ConLOptimizer


class DSgd(ConLOptimizer):
    STATE_P = "state_p"

    def __init__(self, args, org_optimizer, parameters):
        super(DSgd, self).__init__(args, org_optimizer, parameters)

    def __setstate__(self, state):
        super(DSgd, self).__setstate__(state)
        for group in self.param_groups:
            group.setdefault('nesterov', False)

    def aggregate(self, rcv_p):
        i = 0
        diff_sum = 0.
        snd_p = []
        state = None
        if rcv_p is not None:
            state = rcv_p[self.STATE_P]

        for group in self.param_groups:
            for p in group['params']:
                if p.grad is None:
                    continue

                if state is not None:
                    p_d = state[i].to(p.get_device())
                    diff_sum += self._criterion(p_d, p.data)
                    p.data = (p_d + p.data) / 2
                    i += 1
                snd_p.append(p.data.clone().to("cpu"))

        self._diff_latest = diff_sum
        return {self.STATE_P: snd_p}
