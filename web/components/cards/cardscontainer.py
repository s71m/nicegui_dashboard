from typing import Optional, Callable, Union, Awaitable
from nicegui import ui

from web.components.cards.cardtemplate import CardTemplate
from web.components.cards.cardtypes import CardType

# Global variables to track drag and drop state
dragged = None
drop_target = None

class CardContainer(ui.grid):
    def __init__(self, columns: int = 3,
                 card_type: Union[CardType, dict] = CardType.COMMON,
                 card_height: int = 300,
                 on_remove: Optional[Callable[[str], Awaitable[None]]] = None):
        super().__init__(columns=columns)
        self.ui_cards = {}
        self.card_type = card_type
        self.card_height = card_height
        self.on_remove = on_remove
        self.classes('w-full')
        ui.add_head_html('''
        <style>
            .left-zone .highlight {
                background-color: rgba(211, 211, 211, 0.3);
            }
            .right-zone .highlight {
                background-color: rgba(128, 255, 128, 0.2);
            }
        </style>
        ''')

    def add_card(self, card_name: str, card_dict: dict, **kwargs) -> None:
        if card_name not in self.ui_cards:
            with self:
                card_class = self.card_type.value
                self.ui_cards[card_name] = card_class(
                    card_name,
                    card_dict,
                    self,
                    self.on_remove,
                    **kwargs
                )

    def remove_card(self, card_name: str) -> None:
        if card_name in self.ui_cards:
            self.ui_cards[card_name].delete()
            del self.ui_cards[card_name]

    def clear_cards(self) -> None:
        for card in list(self.ui_cards.values()):
            card.delete()
        self.ui_cards.clear()

    def reorder_cards(self, dragged_card: CardTemplate, target_card: CardTemplate, position: str = 'left') -> None:
        """Reorder cards by moving their DOM elements instead of rebuilding"""
        dragged_name = dragged_card.name
        target_name = target_card.name

        if dragged_name not in self.ui_cards or target_name not in self.ui_cards:
            return

        if position == 'left':
            insert_code = 'parent.insertBefore(draggedCard, targetCard);'
        else:
            insert_code = 'parent.insertBefore(draggedCard, targetCard.nextSibling);'

        ui.run_javascript(f'''
            const draggedCard = document.querySelector(".q-card[id='c{dragged_card.id}']");
            const targetCard = document.querySelector(".q-card[id='c{target_card.id}']");
            if (draggedCard && targetCard) {{
                const parent = draggedCard.parentNode;
                {insert_code}
            }}
        ''')

        cards = list(self.ui_cards.items())
        dragged_idx = next(i for i, (name, _) in enumerate(cards) if name == dragged_name)
        target_idx = next(i for i, (name, _) in enumerate(cards) if name == target_name)

        cards.pop(dragged_idx)

        if position == 'left':
            insert_idx = target_idx if target_idx > dragged_idx else target_idx
        else:
            insert_idx = target_idx + 1 if target_idx >= dragged_idx else target_idx + 1

        cards.insert(insert_idx, (dragged_name, dragged_card))
        self.ui_cards = dict(cards)