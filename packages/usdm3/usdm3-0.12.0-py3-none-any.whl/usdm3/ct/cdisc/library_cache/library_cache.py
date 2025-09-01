from usdm3.file_cache.file_cache import FileCache


class LibraryCache(FileCache):
    def __init__(self, filepath: str, filename: str):
        super().__init__(filepath, filename)
