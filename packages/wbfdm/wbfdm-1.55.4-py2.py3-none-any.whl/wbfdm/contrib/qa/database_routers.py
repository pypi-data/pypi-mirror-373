class QARouter:
    """
    QA from Refinitiv is usually served through an external mssql, oracle or snowflake database.
    We are going to use it in a mostly read-only way, therefore we need a DBRouter that routes
    all database connections for models from QA to the correct database. The database needs to be
    registered in the settings of the project like this:

    ```
    DATABASES = {
        "default": {}, # This is the default django database
        "qa": {},  # This is the important database. The name qa is really important here.
    }
    ```
    Afterwards the settings needs to declare this router explicately as one of the `DATABASE_ROUTERS`
    """

    def db_for_read(self, model, **hints):
        if model._meta.app_label == "qa":
            return "qa"
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "qa":
            return False
        return None
