"""
Managers for our models
"""

# Django
from django.db import models
from django.db.models import Count, F


class FatLinkQuerySet(models.QuerySet):
    """
    FAT link queryset
    """

    def annotate_fats_count(self):
        """
        Annotate the amount fats per fat link

        :return:
        :rtype:
        """

        return self.annotate(fats_count=Count(expression=F("afat_fats")))


class FatLinkManager(models.Manager):
    """
    FAT link manager
    """

    def get_queryset(self) -> models.QuerySet:
        """
        Integrate custom QuerySet methods.
        """

        return FatLinkQuerySet(self.model, using=self._db)

    def select_related_default(self):
        """
        Apply select_related for default query optimizations.
        """

        return self.select_related(
            "creator", "character", "creator__profile__main_character"
        )


class FatManager(models.Manager):
    """
    FAT manager
    """

    def select_related_default(self):
        """
        Apply select_related for default query optimizations.
        """

        return self.select_related("fatlink", "character")
