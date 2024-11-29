from typing import Set, Optional
from datetime import date
import polars as pl

from nicegui import ui

from web.pagetemplate import PageTemplate
from web.components.aggrid_polars import AgGridPolars
from web.components.cards.cardscontainer import CardContainer
from web.components.cards.cardtypes import CardType



class CardsModulPage(PageTemplate):
    def __init__(self, **kwargs):
        # Initialize data
        self.df = pl.DataFrame({
            'name': pl.Series(['Card ' + str(i) for i in range(1, 15)], dtype=pl.String),
            'description': pl.Series(['Description ' + str(i+5) for i in range(1, 15)], dtype=pl.String),
            'value': pl.Series([i * 1.5 for i in range(1, 15)], dtype=pl.Float32),
            'active': pl.Series([i % 2 == 0 for i in range(1, 15)], dtype=pl.Boolean),
            'created_date': pl.Series([date(2024, 1, i) for i in range(1, 15)], dtype=pl.Date)
        })
        self.cls_card_container: Optional[CardContainer] = None
        self.cls_aggrid_polars: Optional[AgGridPolars] = None
        super().__init__(**kwargs)

    def sidebar(self):
        """Create sidebar with search and data grid"""
        with ui.row().classes('w-full'):
            ui.input(placeholder='Quick search by name...', on_change=self.handle_search) \
                .props('dense clearable').classes('w-full')

        self.cls_aggrid_polars = AgGridPolars(
            df=self.df,
            checkbox_field='name',
            grid_height=self.pageconf.get("sidebar_cards_grid_height"),
            on_selection_change=self.handle_selection_change
        )
        self.cls_aggrid_polars.create_grid()

    def main(self):
        """Initialize main content area with cards grid"""
        self.cls_card_container = CardContainer(
            columns=self.pageconf.get("cards_per_row"),
            card_type=CardType.CHART,
            card_height=self.pageconf.get("card_height"),
            on_remove=self.handle_card_remove
        )

    async def handle_search(self, event):
        """Filter grid data based on name field"""
        search_text = event.value if event.value is not None else ''
        await self.cls_aggrid_polars.search(search_text)

    async def handle_card_remove(self, card_name: str):
        """Handle card removal triggered by X button click"""
        await self.cls_aggrid_polars.deselect_row(card_name)

    async def handle_selection_change(self, removed: Set[str], added: Set[str]):
        """Update displayed cards based on grid selection changes"""
        # Remove deselected cards
        for card_name in removed:
            self.cls_card_container.remove_card(card_name)

        # Add newly selected cards
        for card_name in added:
            card_dict = self.df.filter(pl.col('name') == card_name).to_dicts()[0]
            self.cls_card_container.add_card(card_name, card_dict)
