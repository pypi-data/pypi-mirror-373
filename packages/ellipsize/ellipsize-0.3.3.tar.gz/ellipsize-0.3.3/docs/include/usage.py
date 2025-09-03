from pprint import pprint

from ellipsize.ellipsize import ellipsize

config = ...
pprint(ellipsize(config, max_items_to_show=3, max_item_length=99))
