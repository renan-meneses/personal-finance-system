class MongoRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == "transactions":
            return "default"
        return "default"

    def db_for_write(self, model, **hints):
        if model._meta.app_label == "transactions":
            return "default"
        return "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == "transactions":
            return False
        return db == "default"
