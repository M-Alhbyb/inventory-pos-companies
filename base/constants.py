"""Application constants and configuration."""


class FirstDayOfMonth:
    """Configurable first day of the month for reports."""
    
    _first_day = 1

    @classmethod
    def set(cls, value):
        """Set the first day of the month."""
        cls._first_day = value

    @classmethod
    def get(cls):
        """Get the first day of the month."""
        return cls._first_day