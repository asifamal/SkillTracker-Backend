import json
from django.http import HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SkillGoal
from django.db.models import Sum, Count

# Create your views here.
class SkillGoalListView(APIView):
    def get(self, request):
        try:
            skills = SkillGoal.objects.all().values(
                'id', 'skill_name', 'resource_type', 'platform', 'status', 'hours_spent', 'notes', 'difficulty_rating'
            )
            skills_list = list(skills)
            if skills_list:
                return Response({'status': 1, 'data': skills_list})
            return Response({'status': 0, 'message': 'No skills found'})
        except Exception as e:
            return Response({'status': 0, 'message': 'Error occurred in server'})


class SkillGoalCreateView(APIView):
    def post(self, request):
        try:
            data = request.data
            skill = SkillGoal.objects.create(
                skill_name=data.get('skill_name'),
                resource_type=data.get('resource_type'),
                platform=data.get('platform'),
                status=data.get('status', 1),
                hours_spent=data.get('hours_spent', 0),
                notes=data.get('notes', ''),
                difficulty_rating=data.get('difficulty_rating', 1),
            )
            return Response({'status': 1, 'id': skill.id})
        except Exception as e:
            return Response({'status': 0, 'message': 'Error occurred in server'})


class SkillGoalDetailView(APIView):
    def get(self, request, pk=None):
        skill_id = pk or request.query_params.get('id')
        if not skill_id:
            return Response({'status': 0, 'message': 'ID parameter is required'})

        try:
            skill = SkillGoal.objects.get(pk=skill_id)
            data = {
                'id': skill.id,
                'skill_name': skill.skill_name,
                'resource_type': skill.resource_type,
                'platform': skill.platform,
                'status': skill.status,
                'hours_spent': skill.hours_spent,
                'notes': skill.notes,
                'difficulty_rating': skill.difficulty_rating,
            }
            return Response({'status': 1, 'data': data})
        except SkillGoal.DoesNotExist:
            return Response({'status': 0, 'message': 'Skill not found'})
        except Exception as e:
            return Response({'status': 0, 'message': 'Error occurred in server'})

class SkillGoalUpdateProgressView(APIView):
    def patch(self, request, pk):
        try:
            skill = SkillGoal.objects.get(pk=pk)
            data = json.loads(request.body)

            allowed_fields = ['status', 'hours_spent', 'notes', 'difficulty_rating']

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(skill, field, data[field])
                    updated = True
            
            if updated:
                skill.save()
                return Response({'status': 1, 'message': 'Skill progress updated successfully'})
            else:
                return HttpResponseBadRequest('No valid fields provided for update')

        except SkillGoal.DoesNotExist:
            return Response({'status': 0, 'message': 'Skill not found'}, status=404)
        except Exception as e:
            return HttpResponseBadRequest(f"Error updating skill: {str(e)}")

class SkillGoalDeleteView(APIView):
    def delete(self, request, pk):
        try:
            skill = SkillGoal.objects.get(pk=pk)
            skill.delete()
            return Response({'status': 1, 'message': 'Skill deleted successfully'})
        except SkillGoal.DoesNotExist:
            return Response({'status': 0, 'message': 'Skill not found'}, status=404)


class DashboardView(APIView):
    def get(self, request):
        total_hours = SkillGoal.objects.aggregate(hours=Sum('hours_spent'))['hours'] or 0

        status_breakdown = (
            SkillGoal.objects
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        top_skills = (
            SkillGoal.objects
            .values('skill_name')
            .annotate(times=Count('id'))
            .order_by('-times')[:5]
        )

        platform_breakdown = (
            SkillGoal.objects
            .values('platform')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'status': 1,
            'total_hours': total_hours,
            'progress_breakdown': list(status_breakdown),
            'top_skills': list(top_skills),
            'platform_breakdown': list(platform_breakdown),
        })