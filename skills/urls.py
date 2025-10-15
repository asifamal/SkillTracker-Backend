from django.urls import path
from .views import SkillGoalCreateView, SkillGoalDetailView, SkillGoalListView

urlpatterns = [
    path('list_skills/', SkillGoalListView.as_view(), name='list_skills'),
    path('skill_create/', SkillGoalCreateView.as_view(), name='skill_create'),
    path('skill_detail/<int:pk>/', SkillGoalDetailView.as_view(), name='skill_detail'),
]