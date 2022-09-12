from django.apps import AppConfig
from model.class_engine import generator


class ModelConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'model'

    generator = {
        "lofi": None,
        "anime": None,
        "mozart": None,
        "beethoven": None,
        "maestro_2017": None,
        "maestro_2018": None,
    }

    def ready(self) -> None:
        print("in ready")

        for generator_name in self.generator:
            print(f"start {generator_name}")

            if self.generator[generator_name] is None:
                print("generated class")
                self.generator[generator_name] = generator.AlphaGenerate(model_name=generator_name)

            print(f"done {generator_name}")

        return super().ready()
