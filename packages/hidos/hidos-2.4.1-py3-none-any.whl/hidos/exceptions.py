class HidosError(Exception):
    """Base class for all hidos exceptions"""


class SuccessionCheckedOut(HidosError):
    """Succession is checked-out"""


class SignedCommitVerifyFailedError(HidosError):
    """Git verify of signed commit failed"""


class HidosWarning(Warning):
    """Base class for all hidos exceptions"""


class SuccessionSplitWarning(HidosWarning):
    """Succession revision chain split"""


class EditionRevisionWarning(HidosWarning):
    """Ignored revision to edition"""


class SignedCommitVerifyFailedWarning(HidosWarning):
    """Git verify of signed commit failed"""
