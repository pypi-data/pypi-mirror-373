A Python module for creating French-suited standard playing card.

Example usage:

```
from standard_playing_card import Card

card = Card("2", "c")

print(card.get_rank())
# prints "2"

print(card.get_suit())
# prints "clubs"
```

`Card(rank, suit)` expects a string rank of the following values `"2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"`, and a string suit of the following values `"clubs", "diamonds", "hearts", "spades"` or their shortened version `"c", "d", "h", "s"`