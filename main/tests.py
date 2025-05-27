from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Project, Alternative, Criterion, RelationshipType, Like
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class ProjectTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        # Create test project
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project',
            description='Test Description',
            is_public=True
        )
        
        # Create test image
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',
            content_type='image/jpeg'
        )

    def test_create_project(self):
        """Test project creation"""
        response = self.client.post(reverse('create_project'), {
            'title': 'New Project',
            'description': 'New Description',
            'is_public': 'on'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Project.objects.filter(title='New Project').exists())

    def test_project_detail_view(self):
        """Test project detail view"""
        response = self.client.get(reverse('project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')
        self.assertContains(response, 'Test Description')

    def test_update_project(self):
        """Test project update"""
        response = self.client.post(reverse('update_project', args=[self.project.id]), {
            'title': 'Updated Project',
            'is_public': 'on'
        })
        self.assertEqual(response.status_code, 302)
        updated_project = Project.objects.get(id=self.project.id)
        self.assertEqual(updated_project.title, 'Updated Project')

    def test_delete_project(self):
        """Test project deletion"""
        response = self.client.post(reverse('delete_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_update_project_image(self):
        """Test project image update"""
        response = self.client.post(
            reverse('update_project_image', args=[self.project.id]),
            {'image': self.test_image}
        )
        self.assertEqual(response.status_code, 302)
        updated_project = Project.objects.get(id=self.project.id)
        self.assertTrue(updated_project.image)

class AlternativeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project',
            description='Test Description'
        )

    def test_create_alternative(self):
        """Test alternative creation"""
        response = self.client.post(reverse('add_alternative', args=[self.project.id]), {
            'name': 'Test Alternative',
            'description': 'Test Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Alternative.objects.filter(name='Test Alternative').exists())

    def test_update_alternative_rating(self):
        """Test alternative rating update"""
        alternative = Alternative.objects.create(
            project=self.project,
            name='Test Alternative',
            rating=5
        )
        response = self.client.post(
            reverse('update_alternative_rating', args=[self.project.id, alternative.id]),
            {'rating': 8}
        )
        self.assertEqual(response.status_code, 302)
        updated_alternative = Alternative.objects.get(id=alternative.id)
        self.assertEqual(updated_alternative.rating, 8)

    def test_delete_alternative(self):
        """Test alternative deletion"""
        alternative = Alternative.objects.create(
            project=self.project,
            name='Test Alternative'
        )
        response = self.client.post(
            reverse('delete_alternative', args=[self.project.id, alternative.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Alternative.objects.filter(id=alternative.id).exists())

class CriterionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project'
        )

    def test_create_criterion(self):
        """Test criterion creation"""
        response = self.client.post(reverse('create_criterion', args=[self.project.id]), {
            'name': 'Test Criterion',
            'type': 'numeric',
            'description': 'Test Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Criterion.objects.filter(name='Test Criterion').exists())

    def test_delete_criterion(self):
        """Test criterion deletion"""
        criterion = Criterion.objects.create(
            project=self.project,
            name='Test Criterion',
            type='numeric'
        )
        response = self.client.post(
            reverse('delete_criterion', args=[self.project.id, criterion.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Criterion.objects.filter(id=criterion.id).exists())

class RelationshipTypeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project'
        )

    def test_create_relationship_type(self):
        """Test relationship type creation"""
        response = self.client.post(reverse('create_relationship_type', args=[self.project.id]), {
            'name': 'Test Relationship',
            'description': 'Test Description'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RelationshipType.objects.filter(name='Test Relationship').exists())

    def test_delete_relationship_type(self):
        """Test relationship type deletion"""
        relationship_type = RelationshipType.objects.create(
            project=self.project,
            name='Test Relationship'
        )
        response = self.client.post(
            reverse('delete_relationship_type', args=[self.project.id, relationship_type.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RelationshipType.objects.filter(id=relationship_type.id).exists())

class LikeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project',
            is_public=True
        )

    def test_toggle_like(self):
        """Test like toggling"""
        # Test adding like
        response = self.client.post(reverse('toggle_like', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['liked'])
        self.assertEqual(data['likes_count'], 1)
        
        # Test removing like
        response = self.client.post(reverse('toggle_like', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['liked'])
        self.assertEqual(data['likes_count'], 0)

class ProjectAnalysisTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project'
        )
        
        # Create alternatives with different ratings
        self.alternative1 = Alternative.objects.create(
            project=self.project,
            name='Alternative 1',
            rating=8
        )
        self.alternative2 = Alternative.objects.create(
            project=self.project,
            name='Alternative 2',
            rating=6
        )
        
        # Create criteria
        self.criterion = Criterion.objects.create(
            project=self.project,
            name='Test Criterion',
            type='numeric'
        )
        
        # Set criteria values
        self.alternative1.criteria_values = {'Test Criterion': 5}
        self.alternative1.save()
        self.alternative2.criteria_values = {'Test Criterion': 3}
        self.alternative2.save()

    def test_project_analysis(self):
        """Test project analysis functionality"""
        response = self.client.get(reverse('project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        
        # Check if analysis data is present in response
        self.assertContains(response, 'Аналіз')
        self.assertContains(response, 'Alternative 1')
        self.assertContains(response, 'Alternative 2')

class ProjectExportTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        self.project = Project.objects.create(
            user=self.user,
            title='Test Project',
            description='Test Description'
        )
        
        # Create test data
        self.alternative = Alternative.objects.create(
            project=self.project,
            name='Test Alternative',
            rating=7
        )
        
        self.criterion = Criterion.objects.create(
            project=self.project,
            name='Test Criterion',
            type='numeric'
        )
        
        self.alternative.criteria_values = {'Test Criterion': 5}
        self.alternative.save()

    def test_export_csv(self):
        """Test CSV export functionality"""
        response = self.client.get(reverse('export_csv', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8-sig')
        
        # Check if CSV contains project data
        content = response.content.decode('utf-8-sig')
        self.assertIn('Test Project', content)
        self.assertIn('Test Alternative', content)
        self.assertIn('Test Criterion', content)

class ProjectCopyTests(TestCase):
    def setUp(self):
        self.user1 = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = get_user_model().objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(email='user2@example.com', password='testpass123')
        
        # Create public project
        self.project = Project.objects.create(
            user=self.user1,
            title='Test Project',
            description='Test Description',
            is_public=True
        )
        
        # Add some data to the project
        self.alternative = Alternative.objects.create(
            project=self.project,
            name='Test Alternative',
            rating=7
        )
        
        self.criterion = Criterion.objects.create(
            project=self.project,
            name='Test Criterion',
            type='numeric'
        )
        
        self.relationship_type = RelationshipType.objects.create(
            project=self.project,
            name='Test Relationship'
        )

    def test_copy_project(self):
        """Test project copying functionality"""
        response = self.client.post(reverse('copy_project', args=[self.project.id]))
        self.assertEqual(response.status_code, 302)
        
        # Check if project was copied
        copied_project = Project.objects.filter(
            user=self.user2,
            title__startswith='Копія:'
        ).first()
        self.assertIsNotNone(copied_project)
        
        # Check if alternatives were copied
        self.assertTrue(copied_project.alternatives.filter(name='Test Alternative').exists())
        
        # Check if criteria were copied
        self.assertTrue(copied_project.criteria.filter(name='Test Criterion').exists())
        
        # Check if relationship types were copied
        self.assertTrue(copied_project.relationship_types.filter(name='Test Relationship').exists())
