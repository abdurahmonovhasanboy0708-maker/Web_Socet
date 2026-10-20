from django.db import models


class Message(models.Model):
    room = models.CharField(max_length=50, db_index=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]