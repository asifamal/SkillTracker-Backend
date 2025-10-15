from django.db import models

# Create your models here.
class SkillGoal(models.Model):
    SKILL_STATUS = (
        (1, 'Started'),
        (2, 'In Progress'),
        (3, 'Completed'),
    )
    RESOURCE_TYPE = (
        (1, 'Video'),
        (2, 'Course'),
        (3, 'Article'),
    )

    skill_name = models.CharField(max_length=100)
    resource_type = models.PositiveSmallIntegerField(choices=RESOURCE_TYPE)
    platform = models.CharField(max_length=50)
    status = models.PositiveSmallIntegerField(choices=SKILL_STATUS, default=1)
    hours_spent = models.FloatField(default=0)
    notes = models.TextField(blank=True)
    difficulty_rating = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return f"{self.skill_name} [{self.get_resource_type_display()}]"