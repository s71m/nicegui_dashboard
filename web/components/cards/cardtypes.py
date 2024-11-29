from enum import Enum


from web.components.cards.commoncard import CommonCard, ChartCard


class CardType(Enum):
    COMMON = CommonCard
    CHART = ChartCard