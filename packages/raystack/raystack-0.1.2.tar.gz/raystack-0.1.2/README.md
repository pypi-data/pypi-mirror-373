# 🚀 Raystack: Where FastAPI Speed Meets Django Elegance

![PyPI Version](https://img.shields.io/pypi/v/raystack)
![Python Versions](https://img.shields.io/pypi/pyversions/raystack) ![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue)
![License](https://img.shields.io/pypi/l/raystack)
![Downloads](https://img.shields.io/pypi/dm/raystack)

**Raystack** is a modern, high-performance Python web framework that merges the asynchronous power of FastAPI with the battle-tested structure and development convenience inspired by Django. Forget the compromises between speed and ease of development — with Raystack, you get the best of both worlds!

## ✨ Why Choose Raystack?

Do you love FastAPI's speed but miss Django's organized project structure? Do you want a powerful ORM with built-in async support and a familiar admin panel? Raystack is built for you! It's ideal for:

*   **High-Performance APIs and Microservices**: Leverage FastAPI's capabilities for blazing-fast and concurrent request handling.
*   **Rapid Development of Full-Featured Web Applications**: Benefit from a ready-to-use project structure, templating, admin panel, and CLI tools.
*   **Developers Transitioning from Django**: Get up to speed instantly with familiar "app" concepts, ORM, and management commands.
*   **Projects Requiring a Flexible and Robust ORM**: SQLAlchemy under the hood gives you full control over your database.

## 🌟 Key Features

*   **FastAPI at its Core**: Experience incredible speed and asynchronous performance for your web applications.
*   **Django-Inspired Project Structure**: Organize your project with "apps" for clean, modular, and maintainable code.
*   **Universal SQLAlchemy ORM**: A powerful and flexible ORM with a unified API for both synchronous and asynchronous operations.
*   **Smart Database Management (Alembic)**: Seamless database migrations for effortless schema evolution.
*   **Jinja2 Templating**: A robust and flexible templating engine for dynamic HTML rendering.
*   **Built-in Admin Panel**: A ready-to-use, customizable administrative interface for easy data management.
*   **Convenient CLI Commands**: Create projects and apps, run the server, manage migrations, and more—all from your command line.
*   **Async-First Design**: Full support for asynchronous views and database operations with minimal effort.
*   **Multi-Database Support**: Connect to SQLite, PostgreSQL, MySQL, and other databases with easy switching between sync and async drivers.
*   **Extensible Architecture**: Easily integrate your own apps, middleware, and commands to tailor the framework to your needs.

## ⚡ Quick Start

Get your project up and running in minutes!

### 1. Install Raystack

```bash
pip install raystack
```

### 2. Create a New Project

```bash
raystack startproject myproject
cd myproject
```

### 3. Run the Development Server

```bash
raystack runserver
```

Open your browser and navigate to: [http://127.0.0.1:8000](http://127.0.0.1:8000/)

## 🏗️ Project Structure

Raystack offers a clear and modular project structure, inspired by Django:

```mermaid
graph TD
    A[Raystack Project] --> B[myproject/];
    B --> C[apps/];
    C --> D[home/];
    D --> D1[models.py];
    D --> D2[views.py];
    D --> D3[urls.py];
    D --> D4[admin.py];
    B --> E[config/];
    E --> E1[settings.py];
    E --> E2[urls.py];
    B --> F[core/];
    F --> F1[__init__.py];
    B --> G[templates/];
    G --> G1[base.html];
    G --> G2[home/];
    B --> H[requirements.txt];
    B --> I[README.md];
```

## 🌐 URL-Based Async/Sync Mode Detection

Raystack introduces a unique approach to database interaction, allowing you to explicitly control whether to use synchronous or asynchronous operations by simply specifying the appropriate driver in your database URL.

### How It Works:

The mode is determined by the presence of async drivers in your database URL within your `config/settings.py` file.

```python
# Synchronous mode (default)
DATABASES = {
    'default': {
        'ENGINE': 'raystack.core.database.sqlalchemy',
        'URL': 'sqlite:///db.sqlite3',  # Sync mode
    }
}

# Asynchronous mode
DATABASES = {
    'default': {
        'ENGINE': 'raystack.core.database.sqlalchemy',
        'URL': 'sqlite+aiosqlite:///' + str(BASE_DIR / 'db.sqlite3'),  # Async mode
    }
}
```

### Supported Drivers:

**Synchronous:**
*   **SQLite**: `sqlite:///db.sqlite3`
*   **PostgreSQL**: `postgresql://user:pass@localhost/dbname`
*   **MySQL**: `mysql://user:pass@localhost/dbname`

**Asynchronous:**
*   **SQLite**: `sqlite+aiosqlite:///db.sqlite3` (requires `aiosqlite`)
*   **PostgreSQL**: `postgresql+asyncpg://user:pass@localhost/dbname` (requires `asyncpg`)
*   **MySQL**: `mysql+aiomysql://user:pass@localhost/dbname` (requires `aiomysql`)

### Benefits:

*   ✅ **Explicit Control**: You explicitly choose the mode in settings, not based on execution context.
*   ✅ **Predictable Behavior**: Database operations are always clear and predictable.
*   ✅ **Framework Agnostic**: Works consistently with FastAPI, Django, Flask, or any other framework.
*   ✅ **Easy Switching**: Simply change the URL to switch between sync and async modes.
*   ✅ **Clear Intent**: The URL clearly indicates whether you're using sync or async database drivers.

## 🛠️ ORM Usage Examples

Raystack's ORM automatically detects the mode based on your database configuration and adapts accordingly. No need for separate sync/async methods!

### Basic CRUD Operations

```python
# Create
article = await Article.objects.create(title="Hello", content="World", author_id=1)

# Get a single object
user = await UserModel.objects.get(id=1)

# Filter
users = await UserModel.objects.filter(age__gte=25).execute()

# Update
user.name = "Jane Doe"
await user.save()

# Delete
await user.delete()

# Count
count = await UserModel.objects.count()

# Check existence
exists = await UserModel.objects.filter(email="john@example.com").exists()
```

## 🖼️ Screenshots

**Home Page:**
![Home Page](.docs/img/first_page.jpg)

**Login Page:**
![Login Page](.docs/img/login_page.jpg)

**Admin Panel:**
![Admin Page](.docs/img/admin_page.jpg)

## 📚 Documentation

*   [Technical Documentation](.docs/index.md)
*   [ORM Reference](.docs/orm.md)
*   [Template Reference](.docs/templates.md)
*   [Command Reference](.docs/commands.md)
*   [Middleware Reference](.docs/middleware.md)
*   [Extending Raystack](.docs/extending.md)
*   [FAQ](.docs/faq.md)

## 🤝 Contributing

Pull requests and issues are welcome! See [GitHub](https://github.com/ForceFledgling/raystack).

## 📜 License

MIT License. See [LICENSE](LICENSE) for details.
