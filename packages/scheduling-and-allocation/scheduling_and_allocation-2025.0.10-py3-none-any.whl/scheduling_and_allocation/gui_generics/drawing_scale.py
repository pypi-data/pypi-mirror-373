
DEFAULT_X_OFFSET: float = 1
DEFAULT_Y_OFFSET: float = 1
DEFAULT_X_ORIGIN: float = 0
DEFAULT_Y_ORIGIN: float = 0
DEFAULT_X_WIDTH_SCALE: float = 100
DEFAULT_Y_HEIGHT_SCALE: float = 60
CURRENT_SCALE: float = 1.0

# =============================================================================================================
# Get a drawing scale (for schedule views) based off a factor
# =============================================================================================================
class DrawingScale:
    def __init__(self, factor=CURRENT_SCALE):
        self.x_offset: float = DEFAULT_X_OFFSET
        self.y_offset: float = DEFAULT_Y_OFFSET
        self.x_origin: float = DEFAULT_X_ORIGIN
        self.y_origin: float = DEFAULT_Y_ORIGIN
        self.x_width_scale: float = DEFAULT_X_WIDTH_SCALE * factor
        self.y_height_scale: float = DEFAULT_Y_HEIGHT_SCALE * factor
        self.current_scale: float = factor

