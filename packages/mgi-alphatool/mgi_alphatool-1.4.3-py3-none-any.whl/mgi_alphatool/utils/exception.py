class InsufficientTipsErr(Exception):
    def __init__(self, message="Insufficient tips. Please load more tiprack."):
        self.message = message
        super().__init__(self.message)

class PickUpTipsErr(Exception):
    pass

class LocationErr(Exception):
    pass

class PlacementErr(Exception):
    pass