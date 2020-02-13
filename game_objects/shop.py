from typing import List
from player import Player
import shop_listings


class Shop:
    def __init__(self, sql_connection, sql_id: int):
        self.id = sql_id
        self.conn = sql_connection
        self.cursor = self.conn.cursor()

    def get_name(self) -> str:
        sqlstr = """SELECT name FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_greeting_quip(self) -> str:
        sqlstr = """SELECT greeting_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def has_player_unlocked(self, player: Player) -> bool:
        sqlstr = """SELECT EXISTS(
                        SELECT 1
                        FROM ShopUnlocked
                        WHERE player_id = :p_id
                        AND shop_id = :s_id
                    );"""
        self.cursor.execute(sqlstr, {'p_id': player.id, 's_id': self.id})
        return self.cursor.fetchone()[0]

    def get_exit_quip(self) -> str:
        sqlstr = """SELECT exit_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_examine_quip(self) -> str:
        sqlstr = """SELECT examine_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_cancel_quip(self) -> str:
        sqlstr = """SELECT cancel_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_buy_quip(self) -> str:
        sqlstr = """SELECT buy_quip FROM Shop
                    WHERE id=:id;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return self.cursor.fetchone()[0]

    def get_card_listings(self) -> List[shop_listings.ShopListing]:
        """Returns set of ShopListings"""
        sqlstr = """SELECT id FROM ShopListing
                    WHERE shop_id=:id
                    ORDER BY shop_index;"""
        self.cursor.execute(sqlstr, {'id': self.id})
        return [shop_listings.ShopListing(self.conn, i[0]) for i in self.cursor.fetchall()]

    def get_listing_from_index(self, index) -> shop_listings.ShopListing:
        sqlstr = """SELECT id FROM ShopListing
                    WHERE shop_id=:id
                    AND ShopListing.shop_index=:index;"""
        self.cursor.execute(sqlstr, {'id': self.id, 'index': index})
        return shop_listings.ShopListing(self.conn, self.cursor.fetchone()[0])

    def render(self) -> str:
        """Returns a string representation of the shop
         Lines:
            |------------------------------|  topline, # dashes equal to the max width -2
            |         | shop name |        |  name_line, middle section centered
            |------------------------------|  divline,
            |" Greeting quip "             |  quipline
            | 1 - card 1       price, type |  listing_lines, price right justified
            | n - card n       price, type |
            |------------------------------|  bottomline

        """
        minimum_internal_width = 1

        # First pass: get size of each internal line
        nameline_internal = f'  | {self.get_name()} |  '  # minimum size of name line
        quipline_internal = f'" {self.get_greeting_quip()} " '  # minimum size of greeting line
        # Listings
        listing_lines_left = []
        listing_lines_right = []
        for i, listing in enumerate(self.get_card_listings()):
            listing_lines_left.append(f'| {i + 1} - {listing.get_card_name()} ')
            listing_lines_right.append(f' {listing.get_price()} {listing.get_price_name()} |')

        # Calculate longest line now that we have all the minimum lengths
        # Even if everything is short, shop will still have a minimum length so its not too narrow
        max_internal_len = max([len(l) + len(r) for l, r in zip(listing_lines_left, listing_lines_right)])
        max_internal_len = max(len(nameline_internal),
                               len(quipline_internal),
                               max_internal_len,
                               minimum_internal_width)

        # second pass: fill in blank spaces to line everything up
        topline = f'|{"-" * max_internal_len}|'

        # name spacing
        name_space_len = max_internal_len - len(nameline_internal)
        left_namespaces = ' ' * (name_space_len // 2)
        if name_space_len % 2 == 0:
            right_namespaces = left_namespaces
        else:
            right_namespaces = left_namespaces + ' '
        nameline = '|' + left_namespaces + nameline_internal + right_namespaces + '|'

        divline = f'|{"-" * max_internal_len}|'
        quipline = f'|{quipline_internal}{" " * (max_internal_len - len(quipline_internal))}|'
        listing_lines = []
        for l, r in zip(listing_lines_left, listing_lines_right):
            listing_lines.append(f'|{l}{" " * (max_internal_len - len(l) - len(r))}{r}|')
        bottomline = f'|{"-" * max_internal_len}|'

        # bring it together and return
        output = topline + '\n' + nameline + '\n' + divline + '\n' + quipline + '\n'
        for l in listing_lines:
            output += l + '\n'
        output += bottomline
        return output


def render_shop_menu(player):
    """Renders all shops a given player has unlocked."""
    shops = player.get_unlocked_shops()
    if len(shops) == 0:
        return 'No shops to display.'
    lines = [f'{i+1} ' for i in range(len(shops))]
    max_len = max([len(l) for l in lines])
    for i in range(len(shops)):
        lines[i] += ' '*(max_len-len(lines[i])) + '| ' + shops[i].get_name() + '\n'
    render = '---------------Shops---------------\n'
    for line in lines:
        render += line
    render += '-----------------------------------'
    print(render)
    return '```' + render + '```'


def get_shop_by_name(name, sql_conn):
    curr = sql_conn.cursor()
    sqlstr = '''SELECT id FROM Shop
                WHERE name=:name;'''
    curr.execute(sqlstr, {'name', name})
    return Shop(sql_conn, curr.fetchone()[0])
