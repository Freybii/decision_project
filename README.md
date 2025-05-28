# Decision Project

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/github/actions/workflow/status/Freybii/decision_project/django.yml?branch=main)](https://github.com/Freybii/decision_project/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A powerful Django-based decision-making application that helps users make informed decisions through structured analysis and comparison of alternatives. The application provides a comprehensive suite of tools for project management, alternative comparison, and decision analysis.

## 🌟 Features

### 🔐 Authentication System
- Custom user model with email-based authentication
- Google OAuth integration for seamless login
- Secure password handling and JWT tokens
- User profile management with avatar support

### 📊 Decision Analysis
- Create and manage decision projects
- Add and compare alternatives
- Rate alternatives based on criteria
- Visualize decision relationships
- Network analysis for complex decisions using NetworkX

### 🎯 Project Management
- Create and organize decision projects
- Add detailed descriptions and criteria
- Upload project images
- Track project progress
- Collaborative decision-making

### 💡 Alternative Management
- Add multiple alternatives to projects
- Define relationships between alternatives
- Rate alternatives based on criteria
- Compare alternatives visually
- Export analysis results

### 🔄 API Integration
- RESTful API endpoints
- JWT authentication
- Serialized data responses
- Comprehensive API documentation
- Swagger/OpenAPI support

## 🛠 Technology Stack

- **Backend Framework**: [Django 4.2](https://www.djangoproject.com/)
- **REST Framework**: [Django REST Framework 3.14](https://www.django-rest-framework.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Authentication**: JWT, Google OAuth
- **Frontend**: Django Templates, [Bootstrap 5](https://getbootstrap.com/)
- **Analysis**: [NetworkX](https://networkx.org/) for graph analysis
- **Testing**: Django Test Framework
- **CI/CD**: GitHub Actions

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL
- Virtual environment (recommended)
- Google OAuth credentials (for Google login)

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Freybii/decision_project.git
   cd decision_project
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## 📁 Project Structure

```
decision_project/
├── authentication/     # User authentication and management
├── main/              # Core decision-making functionality
├── decisionproject/   # Project configuration
├── media/            # User-uploaded files
├── .github/          # GitHub Actions workflows
└── requirements.txt  # Project dependencies
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/google-login/` - Google OAuth login
- `GET /api/auth/profile/` - User profile
- `PUT /api/auth/profile/` - Update profile

### Projects
- `GET /api/projects/` - List projects
- `POST /api/projects/` - Create project
- `GET /api/projects/{id}/` - Project details
- `PUT /api/projects/{id}/` - Update project
- `DELETE /api/projects/{id}/` - Delete project

### Alternatives
- `GET /api/projects/{id}/alternatives/` - List alternatives
- `POST /api/projects/{id}/alternatives/` - Add alternative
- `GET /api/alternatives/{id}/` - Alternative details
- `PUT /api/alternatives/{id}/` - Update alternative
- `DELETE /api/alternatives/{id}/` - Delete alternative

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -am 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 Code Style

This project follows PEP 8 style guidelines. Run the linter:
```bash
flake8 .
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

For support, please:
- Open an issue in the GitHub repository
- Contact the maintainers
- Join our community discussions

## 🙏 Acknowledgments

- [Django](https://www.djangoproject.com/) and [Django REST Framework](https://www.django-rest-framework.org/) communities
- [NetworkX](https://networkx.org/) for graph analysis capabilities
- All contributors who have helped shape this project

## 📞 Contact

- GitHub: [@Freybii](https://github.com/Freybii)
- Project Link: [https://github.com/Freybii/decision_project](https://github.com/Freybii/decision_project) 