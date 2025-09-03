from django.contrib.staticfiles.finders import AppDirectoriesFinder


class TemplateCSSFinder(AppDirectoriesFinder):
    """
    Finder for CSS files located within the templates directories.

    This finder allows CSS files located under the 'templates' directory to be collected
    as static files and served using Django’s {% static %} template tag. For example:
    <link rel="stylesheet" href="{% static 'website/pages/page.css' %}">

    To enable this finder, add it to the STATICFILES_FINDERS setting in your settings.py:

        STATICFILES_FINDERS = [
            "prune_lib.commons.static_finders.TemplateCSSFinder",
            ...
        ]
    """

    source_dir = "templates"

    def list(self, ignore_patterns):
        """Ne liste que les fichiers CSS"""
        for path, storage in super().list(ignore_patterns):
            if path.endswith(".css"):
                yield path, storage

    def find(self, path, find_all=False, **kwargs):
        """Ne cherche que les fichiers CSS"""
        if not path.endswith(".css"):
            return [] if find_all else None

        return super().find(path, find_all=find_all)
