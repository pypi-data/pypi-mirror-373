__version__ = "0.1.2"

import os
import logging
# import importlib.util
import importlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from raystack.conf import settings
from raystack import shortcuts


def setup():
    """
    Configure the settings module if not already configured.
    """
    if not settings.configured:
        settings.configure()


logger = logging.getLogger("uvicorn")


class Raystack(FastAPI):

    def __init__(self):
        super().__init__()

        self.settings = settings
        self.shortcuts = shortcuts

        # Get absolute path to current directory
        self.raystack_directory = os.path.dirname(os.path.abspath(__file__))
        
        # Include routers
        self.include_routers()
        self.include_templates()
        self.include_static()
        self.include_middleware()

    def include_routers(self):
        # Check and import installed applications
        logger.info(f"Loading apps and routers:")
        for app_path in self.settings.INSTALLED_APPS:
            # Dynamically import module
            module = importlib.import_module(app_path)
            logger.info(f"✅'{app_path}'")

            # If module contains routers, include them
            if hasattr(module, "router"):
                self.include_router(module.router)
                logger.info(f"✅'{app_path}.router'")
            else:
                logger.warning(f"⚠️ '{app_path}.router'")

    def include_templates(self):
        # Connect internal Raystack templates (e.g., admin templates)
        internal_template_dirs = [
            os.path.join(self.raystack_directory, "contrib", "templates")
        ]
        for template in self.settings.TEMPLATES:
            # Add internal templates to user template directories
            template_dirs = template.get("DIRS", [])
            # Convert relative paths to absolute
            template_dirs = [os.path.join(self.settings.BASE_DIR, path) for path in template_dirs]
            # Add internal templates if not already present
            for internal_dir in internal_template_dirs:
                if internal_dir not in template_dirs:
                    template_dirs.append(internal_dir)
            template["DIRS"] = template_dirs

    def include_static(self):
        # Include framework static files
        internal_static_dir = os.path.join(self.raystack_directory, "contrib", "static")
        self.mount("/admin_static", StaticFiles(directory=internal_static_dir), name="admin_static")

        # Include static files from STATICFILES_DIRS
        if hasattr(self.settings, 'STATICFILES_DIRS') and self.settings.STATICFILES_DIRS:
            for static_dir in self.settings.STATICFILES_DIRS:
                if os.path.exists(static_dir):
                    self.mount("/static", StaticFiles(directory=static_dir), name="static")
                    break  # Mount only the first existing directory
        # Fallback to default static directory
        elif self.settings.STATIC_URL:
            static_dir = os.path.join(self.settings.BASE_DIR, self.settings.STATIC_URL)
            if os.path.exists(static_dir):
                self.mount("/static", StaticFiles(directory=static_dir), name="static")

    def include_middleware(self):
        # Include middleware from settings
        if hasattr(self.settings, 'MIDDLEWARE') and self.settings.MIDDLEWARE:
            logger.info(f"Loading middleware:")
            for middleware_path in self.settings.MIDDLEWARE:
                try:
                    # Import middleware class
                    module_path, class_name = middleware_path.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    middleware_class = getattr(module, class_name)
                    
                    # Add middleware
                    self.add_middleware(middleware_class)
                    logger.info(f"✅'{middleware_path}'")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load middleware '{middleware_path}': {e}")