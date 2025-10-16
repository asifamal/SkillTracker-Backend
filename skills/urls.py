from django.urls import path
from .views import DashboardView, SkillGoalCreateView, SkillGoalDeleteView, SkillGoalDetailView, SkillGoalListView, SkillGoalUpdateProgressView, TimelineView

urlpatterns = [
    path('list_skills/', SkillGoalListView.as_view(), name='list_skills'),
    path('skill_create/', SkillGoalCreateView.as_view(), name='skill_create'),
    path('skill_detail/<int:pk>/', SkillGoalDetailView.as_view(), name='skill_detail'),
    path('update_skill/<int:pk>/', SkillGoalUpdateProgressView.as_view(), name='update_skill'),
    path('delete_skill/<int:pk>/', SkillGoalDeleteView.as_view(), name='skill_delete'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('timeline/', TimelineView.as_view(), name='timeline'),
]