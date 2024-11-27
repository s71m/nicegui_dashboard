## CardTemplate (Base Class)
- Base UI card with drag-drop functionality
- Extend this to create new card types
- Key method to override: `content()`

## CardContainer
- Manages grid with collection of cards
- Handles cards drag-n-drops

## CardsModulePage
- Manages sync between grid and cards
- Handles selection and filtering
- Contains CardContainer instance
- Key methods to override: `sidebar()` `main()`

# Creating New Card Type

1. Create new class extending CardTemplate:
```python
class NewCard(CardTemplate):
    def content(self):
        with ui.card_section():
            # Add your custom content here
            self.update_header("info text") # will update placeholder self.ui_info_label
```

2. Add to CardType enum:
```python
class CardType(Enum):
    COMMON = CommonCard
    CHART = ChartCard
    NEW = NewCard
```

3. Use in CardContainer:
```python
container = CardContainer(
    columns=3,
    card_type=CardType.NEW,
    card_height=300
)
```
### Card Removal Flow
Have to create multiple callbacks to removing card from grid between classes
1. User press X -> CardTemplate.handle_remove() 
2. CardTemplate -> CardsModulePage.handle_card_remove(card_name)
3. CardsModulePage -> AgGrid.run_row_method(deselect row)
4. CardsModulePage -> CardContainer.remove_card(card_name)
5. CardContainer: removes UI element and cleans dictionary

```mermaid
sequenceDiagram
    participant User
    participant CardTemplate
    participant CardContainer
    participant CardsModulePage
    participant AgGrid
    
    User->>CardTemplate: Click X icon
    activate CardTemplate
    Note over CardTemplate: handle_remove() async
    CardTemplate->>CardsModulePage: on_close(card_name)
    activate CardsModulePage
    
    CardsModulePage->>CardsModulePage: handle_card_remove(card_name)
    
    alt card in selected_card_names
        CardsModulePage->>AgGrid: run_row_method(card_name, 'setSelected', False)
        CardsModulePage->>CardsModulePage: Remove from selected_card_names
    end
    
    CardsModulePage->>CardContainer: remove_card(card_name)
    activate CardContainer
    CardContainer->>CardContainer: Delete UI card
    CardContainer->>CardContainer: Remove from ui_cards dict
    deactivate CardContainer
    
    deactivate CardsModulePage
    deactivate CardTemplate