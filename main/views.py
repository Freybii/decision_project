from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from authentication.models import CustomUser
from authentication.serializers import UserRegistrationSerializer
from .models import Project, Alternative, Relation, RelationshipType, Criterion, Like
from .utils import analyze_project, get_dominance_graph, create_relations_from_ratings
import csv
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import models
from django.db.utils import IntegrityError
import json

def index(request):
    context = {
        'user': request.user
    }
    return render(request, 'main/index.html', context)

def about(request):
    return render(request, 'main/about.html')

def home(request):
    return render(request, 'main/home.html')

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Ви успішно увійшли в систему!')
            return redirect('home')
        else:
            messages.error(request, 'Невірний email або пароль.')
    
    return render(request, 'main/login.html')

@require_http_methods(["GET", "POST"])
def register_view(request):
    if request.method == "POST":
        serializer = UserRegistrationSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна!')
            return redirect('home')
        else:
            for field, errors in serializer.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    return render(request, 'main/register.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Ви успішно вийшли з системи.')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        user = request.user
        user.avatar = request.FILES['avatar']
        user.save()
        messages.success(request, 'Аватар успішно оновлено!')
        return redirect('profile')
    return render(request, 'main/profile.html')

@login_required
def create_project(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description", "")
        is_public = request.POST.get("is_public") == "on"
        image = request.FILES.get("image")
        
        project = Project.objects.create(
            user=request.user,
            title=title,
            description=description,
            is_public=is_public,
            image=image
        )
        messages.success(request, 'Проект успішно створено!')
        return redirect('project_detail', project_id=project.id)
    
    return render(request, 'main/create_project.html')

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    alternatives = project.alternatives.all()
    relationship_types = project.relationship_types.all()
    
    # Apply filters
    if request.GET:
        # Filter by rating
        rating_min = request.GET.get('rating_min')
        rating_max = request.GET.get('rating_max')
        if rating_min:
            alternatives = alternatives.filter(rating__gte=rating_min)
        if rating_max:
            alternatives = alternatives.filter(rating__lte=rating_max)
        
        # Filter by relationship
        relationship = request.GET.get('relationship')
        if relationship:
            alternatives = alternatives.filter(relationship_id=relationship)
        
        # Filter by criteria
        for criterion in project.criteria.all():
            criterion_min = request.GET.get(f'criterion_min_{criterion.id}')
            criterion_max = request.GET.get(f'criterion_max_{criterion.id}')
            criterion_value = request.GET.get(f'criterion_{criterion.id}')
            
            if criterion.type == 'numeric':
                if criterion_min or criterion_max:
                    filtered_alternatives = []
                    for alt in alternatives:
                        value = alt.criteria_values.get(criterion.name)
                        if value is not None:
                            value = float(value)
                            if (not criterion_min or value >= float(criterion_min)) and \
                               (not criterion_max or value <= float(criterion_max)):
                                filtered_alternatives.append(alt)
                    alternatives = filtered_alternatives
            elif criterion.type == 'text':
                if criterion_value:
                    filtered_alternatives = []
                    for alt in alternatives:
                        value = alt.criteria_values.get(criterion.name, '')
                        if criterion_value.lower() in value.lower():
                            filtered_alternatives.append(alt)
                    alternatives = filtered_alternatives
            elif criterion.type == 'color':
                if criterion_value:
                    filtered_alternatives = []
                    for alt in alternatives:
                        value = alt.criteria_values.get(criterion.name, '#000000')
                        if value.lower() == criterion_value.lower():
                            filtered_alternatives.append(alt)
                    alternatives = filtered_alternatives
    
    # Convert alternatives to list for graph data
    alternatives_list = list(alternatives)
    
    # Create graph data
    graph_data = {
        'nodes': [],
        'edges': []
    }
    
    # Add alternative nodes
    for alt in alternatives_list:
        graph_data['nodes'].append({
            'id': alt.name,
            'type': 'alternative',
            'rating': alt.rating
        })
    
    # Add relationship nodes and edges
    for rel_type in relationship_types:
        graph_data['nodes'].append({
            'id': rel_type.name,
            'type': 'relationship',
            'description': rel_type.description
        })
        
        # Add edges for alternatives with this relationship
        for alt in alternatives_list:
            if alt.relationship == rel_type:
                graph_data['edges'].append({
                    'source': alt.name,
                    'target': rel_type.name,
                    'type': 'has_relationship'
                })
    
    # Add edges for alternative relationships
    for alt1 in alternatives_list:
        for alt2 in alternatives_list:
            if alt1 != alt2:
                # Check if alt1 dominates alt2
                if alt1.rating > alt2.rating:
                    graph_data['edges'].append({
                        'source': alt1.name,
                        'target': alt2.name,
                        'type': 'domination'
                    })
                # Check if alternatives are indifferent
                elif alt1.rating == alt2.rating:
                    graph_data['edges'].append({
                        'source': alt1.name,
                        'target': alt2.name,
                        'type': 'indifference'
                    })
    
    # Calculate analysis scores
    analysis = {
        'all_scores': {}
    }
    
    # Calculate scores based on ratings and criteria
    for alt in alternatives_list:
        score = alt.rating  # Base score is the rating
        
        # Add criteria scores
        for criterion in project.criteria.all():
            value = alt.criteria_values.get(criterion.name)
            if value is not None:
                if criterion.type == 'numeric':
                    try:
                        score += float(value)
                    except (ValueError, TypeError):
                        pass
        
        analysis['all_scores'][alt.name] = score
    
    context = {
        'project': project,
        'alternatives': alternatives_list,
        'relationship_types': relationship_types,
        'graph_data': json.dumps(graph_data),
        'analysis': analysis
    }
    
    return render(request, 'main/project_detail.html', context)

def public_comparisons(request):
    public_projects = Project.objects.filter(is_public=True).order_by("-created_at")
    return render(request, 'main/public_comparisons.html', {'projects': public_projects})

@login_required
def add_alternative(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        Alternative.objects.create(
            project=project,
            name=name,
            description=description
        )
        messages.success(request, 'Альтернативу додано!')
        return redirect('project_detail', project_id=project_id)
    return render(request, 'main/add_alternative.html', {'project': project})

@api_view(['POST'])
@login_required
def create_relation(request):
    source_id = request.data.get('source')
    target_id = request.data.get('target')
    relation_type = request.data.get('type')
    
    source = get_object_or_404(Alternative, id=source_id)
    target = get_object_or_404(Alternative, id=target_id)
    
    # Verify that both alternatives belong to the same project
    if source.project != target.project:
        return Response({'error': 'Alternatives must belong to the same project'}, status=400)
    
    # Create or update the relation
    relation, created = Relation.objects.update_or_create(
        source=source,
        target=target,
        defaults={'relation_type': relation_type}
    )
    
    return Response({'status': 'success'})

@login_required
def export_csv(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="project_{project_id}.csv"'
    
    writer = csv.writer(response, delimiter=';')
    
    # Write project info
    writer.writerow(['Проект:', project.title])
    writer.writerow(['Опис:', project.description])
    writer.writerow(['Статус:', 'Публічний' if project.is_public else 'Приватний'])
    writer.writerow(['Створено:', project.created_at.strftime('%d.%m.%Y %H:%M')])
    writer.writerow([])  # Empty row for separation
    
    # Write alternatives with their ratings and criteria values
    writer.writerow(['Альтернативи'])
    headers = ['Назва', 'Опис', 'Рейтинг']
    
    # Add criteria headers
    criteria = project.criteria.all()
    for criterion in criteria:
        headers.append(f'Критерій: {criterion.name}')
    
    # Add relationship header
    headers.append('Відношення')
    writer.writerow(headers)
    
    # Write alternatives data
    alternatives = Alternative.objects.filter(project=project)
    for alt in alternatives:
        row = [alt.name, alt.description, alt.rating]
        
        # Add criteria values
        for criterion in criteria:
            value = alt.criteria_values.get(criterion.name, '')
            row.append(value)
        
        # Add relationship
        relationship = alt.relationship.name if alt.relationship else 'Без відношення'
        row.append(relationship)
        
        writer.writerow(row)
    
    writer.writerow([])  # Empty row for separation
    
    # Write relations between alternatives
    writer.writerow(['Відношення між альтернативами'])
    writer.writerow(['Альтернатива 1', 'Альтернатива 2', 'Тип відношення'])
    
    relations = Relation.objects.filter(source__project=project)
    for rel in relations:
        writer.writerow([rel.source.name, rel.target.name, rel.get_relation_type_display()])
    
    return response

@login_required
def alternatives_view(request):
    # Get only projects that belong to the current user
    projects = Project.objects.filter(user=request.user).prefetch_related('alternatives')
    liked_projects = set(Like.objects.filter(user=request.user).values_list('project_id', flat=True))
    
    context = {
        'projects': projects,
        'liked_projects': liked_projects
    }
    return render(request, 'main/alternatives.html', context)

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Перевіряємо, чи користувач є власником проекту
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для видалення цього проекту.')
        return redirect('alternatives')
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Проект успішно видалено.')
        return redirect('alternatives')
    
    return render(request, 'main/delete_project.html', {'project': project})

@login_required
def update_alternative_rating(request, project_id, alternative_id):
    if request.method == "POST":
        project = get_object_or_404(Project, id=project_id)
        alternative = get_object_or_404(Alternative, id=alternative_id, project=project)
        
        # Check if the user owns the project
        if project.user != request.user:
            messages.error(request, 'У вас немає прав для редагування цього проекту')
            return redirect('project_detail', project_id=project_id)
        
        try:
            rating = int(request.POST.get('rating', 0))
            alternative.rating = rating
            alternative.save()
            
            # Update relations based on new ratings
            create_relations_from_ratings(project_id)
            
            messages.success(request, 'Рейтинг успішно оновлено')
        except ValueError:
            messages.error(request, 'Невірне значення рейтингу')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def create_relationship_type(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для редагування цього проекту')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        
        try:
            RelationshipType.objects.create(
                project=project,
                name=name,
                description=description
            )
            messages.success(request, 'Тип відношення успішно створено')
        except IntegrityError:
            messages.error(request, 'Тип відношення з такою назвою вже існує')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def update_alternative_relationship(request, project_id, alternative_id):
    if request.method == "POST":
        project = get_object_or_404(Project, id=project_id)
        alternative = get_object_or_404(Alternative, id=alternative_id, project=project)
        
        # Check if the user owns the project
        if project.user != request.user:
            messages.error(request, 'У вас немає прав для редагування цього проекту')
            return redirect('project_detail', project_id=project_id)
        
        relationship_id = request.POST.get('relationship')
        if relationship_id:
            relationship = get_object_or_404(RelationshipType, id=relationship_id, project=project)
            alternative.relationship = relationship
        else:
            alternative.relationship = None
        
        alternative.save()
        messages.success(request, 'Відношення успішно оновлено')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def delete_alternative(request, project_id, alternative_id):
    project = get_object_or_404(Project, id=project_id)
    alternative = get_object_or_404(Alternative, id=alternative_id, project=project)
    
    # Check if the user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для видалення альтернативи')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == "POST":
        alternative.delete()
        messages.success(request, 'Альтернативу успішно видалено')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def delete_relation(request, project_id, relation_id):
    project = get_object_or_404(Project, id=project_id)
    relation = get_object_or_404(Relation, id=relation_id, source__project=project)
    
    # Check if the user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для видалення відношення')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == "POST":
        relation.delete()
        messages.success(request, 'Відношення успішно видалено')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def delete_relationship_type(request, project_id, type_id):
    project = get_object_or_404(Project, id=project_id)
    relationship_type = get_object_or_404(RelationshipType, id=type_id, project=project)
    
    # Check if the user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для видалення типу відношення')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == "POST":
        # Remove relationship from alternatives that use this type
        Alternative.objects.filter(relationship=relationship_type).update(relationship=None)
        # Delete the relationship type
        relationship_type.delete()
        messages.success(request, 'Тип відношення успішно видалено')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def public_projects_view(request):
    # Get all public projects with their alternatives and users
    public_projects = Project.objects.filter(is_public=True).select_related('user').prefetch_related('alternatives').order_by('-created_at')
    
    context = {
        'projects': public_projects
    }
    return render(request, 'main/public_projects.html', context)

@login_required
def copy_project(request, project_id):
    # Get the original project
    original_project = get_object_or_404(Project, id=project_id, is_public=True)
    
    # Prevent copying own projects
    if original_project.user == request.user:
        messages.error(request, 'Ви не можете скопіювати свій власний проект.')
        return redirect('public_projects')
    
    # Create a new project
    new_project = Project.objects.create(
        user=request.user,
        title=f"Копія: {original_project.title}",
        description=original_project.description,
        image=original_project.image,
        is_public=False  # New project is private by default
    )
    
    # Copy criteria first
    for criterion in original_project.criteria.all():
        Criterion.objects.create(
            project=new_project,
            name=criterion.name,
            type=criterion.type,
            description=criterion.description
        )
    
    # Copy relationship types
    relationship_type_map = {}  # Map to store original -> new relationship type mapping
    for rel_type in original_project.relationship_types.all():
        new_rel_type = RelationshipType.objects.create(
            project=new_project,
            name=rel_type.name,
            description=rel_type.description
        )
        relationship_type_map[rel_type.id] = new_rel_type
    
    # Copy alternatives with their relationships and criteria values
    for alt in original_project.alternatives.all():
        new_alt = Alternative.objects.create(
            project=new_project,
            name=alt.name,
            description=alt.description,
            rating=alt.rating,
            criteria_values=alt.criteria_values  # Copy criteria values
        )
        # Copy relationship if exists
        if alt.relationship:
            new_alt.relationship = relationship_type_map[alt.relationship.id]
            new_alt.save()
    
    messages.success(request, 'Проект успішно скопійовано!')
    return redirect('project_detail', project_id=new_project.id)

@login_required
def update_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для редагування цього проекту')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == "POST":
        title = request.POST.get('title')
        is_public = request.POST.get('is_public') == 'on'
        
        project.title = title
        project.is_public = is_public
        project.save()
        
        messages.success(request, 'Проект успішно оновлено')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def update_all_alternatives(request, project_id):
    if request.method == "POST":
        project = get_object_or_404(Project, id=project_id)
        
        # Check if the user owns the project
        if project.user != request.user:
            messages.error(request, 'У вас немає прав для редагування цього проекту')
            return redirect('project_detail', project_id=project_id)
        
        try:
            # Get all alternatives for this project
            alternatives = Alternative.objects.filter(project=project)
            
            # Update each alternative's rating, relationship and criteria values
            for alt in alternatives:
                rating_key = f'rating_{alt.id}'
                relationship_key = f'relationship_{alt.id}'
                
                if rating_key in request.POST:
                    try:
                        rating = int(request.POST.get(rating_key, 0))
                        alt.rating = rating
                    except ValueError:
                        messages.error(request, f'Невірне значення рейтингу для {alt.name}')
                        continue
                
                if relationship_key in request.POST:
                    relationship_id = request.POST.get(relationship_key)
                    if relationship_id:
                        try:
                            relationship = RelationshipType.objects.get(id=relationship_id, project=project)
                            alt.relationship = relationship
                        except RelationshipType.DoesNotExist:
                            messages.error(request, f'Невірний тип відношення для {alt.name}')
                            continue
                    else:
                        alt.relationship = None
                
                # Update criteria values
                criteria_values = {}
                for criterion in project.criteria.all():
                    value_key = f'criterion_{criterion.id}_{alt.id}'
                    if value_key in request.POST:
                        value = request.POST.get(value_key)
                        if criterion.type == 'numeric':
                            try:
                                value = float(value)
                            except ValueError:
                                messages.error(request, f'Невірне числове значення для {criterion.name} в {alt.name}')
                                continue
                        criteria_values[criterion.name] = value
                
                alt.criteria_values = criteria_values
                alt.save()
            
            # Update relations based on new ratings
            create_relations_from_ratings(project_id)
            
            messages.success(request, 'Всі зміни успішно збережено')
        except Exception as e:
            messages.error(request, f'Помилка при збереженні змін: {str(e)}')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def create_criterion(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if the user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для редагування цього проекту')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == "POST":
        name = request.POST.get("name")
        criterion_type = request.POST.get("type")
        description = request.POST.get("description", "")
        
        try:
            Criterion.objects.create(
                project=project,
                name=name,
                type=criterion_type,
                description=description
            )
            messages.success(request, 'Критерій успішно створено')
        except IntegrityError:
            messages.error(request, 'Критерій з такою назвою вже існує')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def delete_criterion(request, project_id, criterion_id):
    project = get_object_or_404(Project, id=project_id)
    criterion = get_object_or_404(Criterion, id=criterion_id, project=project)
    
    # Check if the user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для видалення критерію')
        return redirect('project_detail', project_id=project_id)
    
    if request.method == "POST":
        # Remove criterion values from all alternatives
        alternatives = Alternative.objects.filter(project=project)
        for alt in alternatives:
            if criterion.name in alt.criteria_values:
                del alt.criteria_values[criterion.name]
                alt.save()
        
        criterion.delete()
        messages.success(request, 'Критерій успішно видалено')
    
    return redirect('project_detail', project_id=project_id)

@login_required
def toggle_like(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    like, created = Like.objects.get_or_create(user=request.user, project=project)
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': project.likes.count()
    })

def public_projects(request):
    projects = Project.objects.filter(is_public=True).order_by('-created_at')
    if request.user.is_authenticated:
        liked_projects = set(Like.objects.filter(user=request.user).values_list('project_id', flat=True))
    else:
        liked_projects = set()
    
    context = {
        'projects': projects,
        'liked_projects': liked_projects
    }
    return render(request, 'main/public_projects.html', context)

@login_required
def my_projects(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    liked_projects = set(Like.objects.filter(user=request.user).values_list('project_id', flat=True))
    
    context = {
        'projects': projects,
        'liked_projects': liked_projects
    }
    return render(request, 'main/my_projects.html', context)

def profile(request, username):
    user = get_object_or_404(CustomUser, username=username)
    projects = Project.objects.filter(user=user).order_by('-created_at')
    if request.user.is_authenticated:
        liked_projects = set(Like.objects.filter(user=request.user).values_list('project_id', flat=True))
    else:
        liked_projects = set()
    
    context = {
        'profile_user': user,
        'projects': projects,
        'liked_projects': liked_projects
    }
    return render(request, 'main/profile.html', context)

@login_required
def update_project_image(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Check if user owns the project
    if project.user != request.user:
        messages.error(request, 'У вас немає прав для редагування цього проекту.')
        return redirect('project_detail', project_id=project.id)
    
    if request.method == 'POST' and request.FILES.get('image'):
        project.image = request.FILES['image']
        project.save()
        messages.success(request, 'Зображення проекту успішно оновлено!')
    else:
        messages.error(request, 'Помилка при оновленні зображення.')
    
    return redirect('project_detail', project_id=project.id)
