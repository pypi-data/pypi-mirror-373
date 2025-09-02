from django.db import models
from django.conf import settings

# Create your models here.


class TempFile(models.Model):
    """Model for managing temporary uploads"""

    userfk = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column="userfk",
    )
    file = models.BinaryField()
    filename = models.CharField(max_length=72)

    def __str__(self):
        """A concise & console friendly string output about Tempfile"""

        return self.filename

    class Meta:
        """Meta for TemporaryFile Model"""

        managed = True
        db_table = "tempfile"


class Term(models.Model):
    """Terminology used by a niche Group"""

    niche = models.CharField(max_length=255)
    phrase = models.CharField(max_length=255)
    rephrase = models.CharField(max_length=255)

    def __str__(self):
        """Return the Rephrased version of Phrase as per specified niche"""

        return self.rephrase

    class Meta:
        """Meta for Term"""

        managed = True
        db_table = "term"
        constraints = [
            models.UniqueConstraint(fields=["niche", "phrase"], name="unique_phrase"),
        ]
