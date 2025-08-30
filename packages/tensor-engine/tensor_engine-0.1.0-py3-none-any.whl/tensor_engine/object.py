



class Object:
    def __init__(self, size: tuple[int, int], coords: tuple[int, int], ch: chr=None, shape: list[chr]=None):
        self.x: int = coords[0]
        self.y: int = coords[1]
        self.size: tuple[int, int] = size
        self.ch: str = ch
        self.tag: str = None
        self.shape: list = [[self.ch]*self.size[0] for _ in range(self.size[1])] if shape is None else shape
    
    def render(self) -> list:
        return self.shape

    def check_collision(self, other: "Object") -> bool:
        coords = set(
            (self.x + dx, self.y + dy)
            for dy in range(self.size[1])
            for dx in range(self.size[0])
            if self.shape[dy][dx] != ' '
        )
        other_coords = set(
            (other.x + dx, other.y + dy)
            for dy in range(other.size[1])
            for dx in range(other.size[0])
            if other.shape[dy][dx] != ' '
        )

        return not coords.isdisjoint(other_coords)