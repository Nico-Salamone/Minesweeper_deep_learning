from enum import Enum

class Tile(Enum):
	"""
	Tile of a grid.
	"""

	EMPTY = 0 # Empty tile. It does not contain bomb (corresponds to the number of adjacent bombs).
	BOMB = -1 # Bomb tile.
	INVISIBLE = -2 # Invisible tile.

	def __str__(self):
		if self == Tile.BOMB:
			return '¤'
		elif self == Tile.INVISIBLE:
			return '▩'
		
		return None

	def __eq__(self, other):
		if (self is Tile.EMPTY) and (isinstance(other, int)):
			if 0 <= other <= 8:
				return True
			else:
				return False
		else:
			return super().__eq__(other)
