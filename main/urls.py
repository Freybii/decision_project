from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('home/', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('create-project/', views.create_project, name='create_project'),
    path(
        'projects/<int:project_id>/',
        views.project_detail,
        name='project_detail'
    ),
    path(
        'projects/<int:project_id>/update-image/',
        views.update_project_image,
        name='update_project_image'
    ),
    path(
        'public-comparisons/',
        views.public_comparisons,
        name='public_comparisons'
    ),
    path(
        'add-alternative/<int:project_id>/',
        views.add_alternative,
        name='add_alternative'
    ),
    path('create-relation/', views.create_relation, name='create_relation'),
    path(
        'export-csv/<int:project_id>/',
        views.export_csv,
        name='export_csv'
    ),
    path('alternatives/', views.alternatives_view, name='alternatives'),
    path(
        'delete-project/<int:project_id>/',
        views.delete_project,
        name='delete_project'
    ),
    path(
        'update-alternative-rating/<int:project_id>/<int:alternative_id>/',
        views.update_alternative_rating,
        name='update_alternative_rating'
    ),
    path(
        'create-relationship-type/<int:project_id>/',
        views.create_relationship_type,
        name='create_relationship_type'
    ),
    path(
        'update-alternative-relationship/<int:project_id>/<int:alternative_id>/',
        views.update_alternative_relationship,
        name='update_alternative_relationship'
    ),
    path(
        'delete-alternative/<int:project_id>/<int:alternative_id>/',
        views.delete_alternative,
        name='delete_alternative'
    ),
    path(
        'delete-relation/<int:project_id>/<int:relation_id>/',
        views.delete_relation,
        name='delete_relation'
    ),
    path(
        'delete-relationship-type/<int:project_id>/<int:type_id>/',
        views.delete_relationship_type,
        name='delete_relationship_type'
    ),
    path(
        'public-projects/',
        views.public_projects,
        name='public_projects'
    ),
    path(
        'copy-project/<int:project_id>/',
        views.copy_project,
        name='copy_project'
    ),
    path(
        'update-project/<int:project_id>/',
        views.update_project,
        name='update_project'
    ),
    path(
        'update-all-alternatives/<int:project_id>/',
        views.update_all_alternatives,
        name='update_all_alternatives'
    ),
    path(
        'create-criterion/<int:project_id>/',
        views.create_criterion,
        name='create_criterion'
    ),
    path(
        'delete-criterion/<int:project_id>/<int:criterion_id>/',
        views.delete_criterion,
        name='delete_criterion'
    ),
    path(
        'projects/<int:project_id>/like/',
        views.toggle_like,
        name='toggle_like'
    ),
]
