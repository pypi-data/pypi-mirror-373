from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import IntegerPreference

general = Section("wbwriter")


@global_preferences_registry.register
class ReviewerRollDaysRangePreference(IntegerPreference):
    section = general
    name = "reviewer_roll_days_range"
    default = 31

    verbose_name = "Reviewer roll days range"
    help_text = "The number of days that the reviewer-picking-algorithm looks into the past to count the reviews a member of the reviewer groups has been given."
