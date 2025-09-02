class BaseCommand:
    def add_arguments(self, parser):
        raise NotImplementedError

    def run(self, args, dubhub):
        raise NotImplementedError
