def includeme(config):
    """
    Scanne les fichiers du répertoire courant pour inclure toutes les classes
    qui ont un decorateur "@dataquery_class()"
    """
    config.scan(package=".queries", categories=("dataqueries",))
