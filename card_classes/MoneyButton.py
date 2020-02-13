from game_objects import card
import time
TIME_COOLDOWN = 60*60*24


class MoneyButton(card.Card):
    async def use(self, message):
        """Gains 1 money, if enough time has passed"""
        last = self.get_param('last_use')
        diff = time.time() - float(last.get_val())
        if diff > TIME_COOLDOWN:
            money = self.get_param('money')
            m_val = int(money.get_val())
            if m_val >= int(money.get_max()):
                await message.channel.send('Error: money maxed out.')
            else:
                await message.channel.send('Gained 1 money.')
                last.set_val(time.time())
                money.set_val(m_val+1)
        else:
            await message.channel.send(f'Card on cooldown. {int(TIME_COOLDOWN-diff)} seconds remaining.')

    def passive(self, t=None):
        pass
