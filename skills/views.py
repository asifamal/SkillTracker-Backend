import json
from django.http import HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SkillGoal, LearningActivity
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date
from django.utils import timezone

# --- Heuristic auto-categorization utilities ---
CATEGORY_KEYWORDS = [
    ("Frontend", ["react", "vue", "angular", "html", "css", "tailwind", "typescript", "javascript", "next.js", "vite"]),
    ("Backend", ["django", "rest api", "node", "express", "fastapi", "spring", "laravel", "flask", "api"]),
    ("Data", ["pandas", "numpy", "data analysis", "etl", "excel", "power bi"]),
    ("AI/ML", ["machine learning", "deep learning", "pytorch", "tensorflow", "sklearn", "nlp", "llm"]),
    ("Databases", ["sql", "postgres", "mysql", "sqlite", "mongodb", "redis"]),
    ("DevOps", ["docker", "kubernetes", "ci/cd", "terraform", "aws", "gcp", "azure", "ansible"]),
    ("Mobile", ["react native", "flutter", "android", "ios", "kotlin", "swift"]),
    ("Testing", ["jest", "pytest", "cypress", "playwright", "unit test", "integration test"]),
    ("Languages", ["python", "java", "c#", "go", "rust", "typescript", "javascript"]),
]

PLATFORM_HINTS = {
    'YouTube': 'Frontend',
    'Udemy': 'Languages',
    'Coursera': 'AI/ML',
    'edX': 'AI/ML',
}

def normalize_text(*parts):
    return " ".join([str(p or "").lower() for p in parts])

def categorize_skill_content(skill_name: str = None, platform: str = None, notes: str = None):
    text = normalize_text(skill_name, platform, notes)
    # Platform hint first
    if platform and platform in PLATFORM_HINTS:
        return PLATFORM_HINTS[platform]
    # Keyword matching
    for cat, keywords in CATEGORY_KEYWORDS:
        for kw in keywords:
            if kw in text:
                return cat
    # Fallbacks
    if 'course' in text or 'video' in text:
        return 'Languages'
    return 'General'

# Create your views here.
class SkillGoalListView(APIView):
    def get(self, request):
        try:
            skills_qs = SkillGoal.objects.all()
            skills = []
            for s in skills_qs:
                skills.append({
                    'id': s.id,
                    'skill_name': s.skill_name,
                    'resource_type': s.resource_type,
                    'platform': s.platform,
                    'status': s.status,
                    'hours_spent': s.hours_spent,
                    'notes': s.notes,
                    'difficulty_rating': s.difficulty_rating,
                    'category': categorize_skill_content(s.skill_name, s.platform, s.notes),
                })
            if skills:
                return Response({'status': 1, 'data': skills})
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
            # Log an initial learning activity for timeline/calendar
            try:
                LearningActivity.objects.create(
                    skill=skill,
                    date=timezone.now().date(),
                    title='Created Skill',
                    hours=float(data.get('hours_spent', 0) or 0),
                    notes=data.get('notes', '') or '',
                )
            except Exception:
                # Don't block creation if activity log fails
                pass
            return Response({'status': 1, 'id': skill.id, 'category': categorize_skill_content(skill.skill_name, skill.platform, skill.notes)})
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
                'category': categorize_skill_content(skill.skill_name, skill.platform, skill.notes),
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

            # Capture previous values for logging
            before_hours = float(skill.hours_spent or 0)
            before_status = int(skill.status)

            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(skill, field, data[field])
                    updated = True
            
            if updated:
                skill.save()
                # Create timeline activities for meaningful changes
                try:
                    today = timezone.now().date()
                    # Log hours change if increased
                    after_hours = float(skill.hours_spent or 0)
                    delta = after_hours - before_hours
                    if 'hours_spent' in data and abs(delta) > 0:
                        LearningActivity.objects.create(
                            skill=skill,
                            date=today,
                            title='Updated Hours',
                            hours=max(delta, 0),
                            notes=f"Total: {after_hours}h" + (f" | {data.get('notes') if data.get('notes') else ''}"),
                        )
                    # Log status change
                    if 'status' in data and int(skill.status) != before_status:
                        status_label = dict(SkillGoal.SKILL_STATUS).get(int(skill.status), str(skill.status))
                        LearningActivity.objects.create(
                            skill=skill,
                            date=today,
                            title=f"Status: {status_label}",
                            hours=0,
                            notes=data.get('notes', ''),
                        )
                    # Log notes-only update if provided without hours/status
                    if 'notes' in data and not ('hours_spent' in data or 'status' in data):
                        LearningActivity.objects.create(
                            skill=skill,
                            date=today,
                            title='Notes Updated',
                            hours=0,
                            notes=data.get('notes', ''),
                        )
                except Exception:
                    # Avoid breaking update on activity log issues
                    pass
                return Response({'status': 1, 'message': 'Skill progress updated successfully', 'category': categorize_skill_content(skill.skill_name, skill.platform, skill.notes)})
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


class TimelineView(APIView):
    def get(self, request):
        # Optional filters: ?skill=<id>&from=YYYY-MM-DD&to=YYYY-MM-DD
        skill_id = request.query_params.get('skill')
        from_str = request.query_params.get('from')
        to_str = request.query_params.get('to')

        qs = LearningActivity.objects.select_related('skill').all()
        if skill_id:
            qs = qs.filter(skill_id=skill_id)
        if from_str:
            d = parse_date(from_str)
            if d:
                qs = qs.filter(date__gte=d)
        if to_str:
            d = parse_date(to_str)
            if d:
                qs = qs.filter(date__lte=d)

        activities = [
            {
                'id': a.id,
                'skill_id': a.skill_id,
                'skill_name': a.skill.skill_name,
                'date': a.date.isoformat(),
                'title': a.title,
                'hours': a.hours,
                'notes': a.notes,
            }
            for a in qs.order_by('-date', '-id')[:500]
        ]
        return Response({'status': 1, 'data': activities})

    def post(self, request):
        try:
            data = request.data
            activity = LearningActivity.objects.create(
                skill_id=data.get('skill_id'),
                date=data.get('date'),
                title=data.get('title'),
                hours=data.get('hours', 0),
                notes=data.get('notes', ''),
            )
            return Response({'status': 1, 'id': activity.id})
        except Exception:
            return Response({'status': 0, 'message': 'Error occurred in server'})


class CategorizeView(APIView):
    def post(self, request):
        data = request.data or {}
        name = data.get('skill_name') or data.get('name')
        platform = data.get('platform')
        notes = data.get('notes')
        category = categorize_skill_content(name, platform, notes)
        return Response({'status': 1, 'category': category})