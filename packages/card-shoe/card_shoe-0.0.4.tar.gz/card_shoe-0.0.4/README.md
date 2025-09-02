A Python card shoe library for creating card shoes with multiple decks for blackjack and casino usage.

Example usage:

```
from card_shoe import CardShoe

shoe = CardShoe()  # 1 deck
print(shoe.draw_card())
# will print a random card drawn
print(shoe.draw_card())
# will print a different card drawn

shoe = CardShoe(7)  # 7 decks for blackjack
shoe.shuffle()
print(shoe.draw_card())
# will print a random card
print(shoe.draw_card())
# can print the same card due to multiple decks
```