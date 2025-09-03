class URLUtil:
    @staticmethod
    def compose(*args) -> str:
        args = list(args)
        if len(args) == 1 and isinstance(args[0], list):
            args = args[0]
        return "/".join(args)
