from card import Card, Param
SECONDS_IN_DAY = 86400
SECONDS_IN_HOUR = 3600


class ShittyFarmer(Card):
    """
    Params:
        crop: Increases by 10 per day, max 100
        last_time: previous passive check
    """
    def passive(self, t):
        passive_increase_param(self.get_param('crop'), self.get_param)


def passive_increase_param(param: Param, t, last_t,  rate):
    val = param.get_val()
    max_val = param.get_max()
    dt = int(t - last_t)
    new_val = max(val+rate*dt, max_val)
    param.set_val(new_val)
