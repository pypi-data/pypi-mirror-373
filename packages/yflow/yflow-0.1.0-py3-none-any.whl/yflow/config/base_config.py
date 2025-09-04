class BaseConfig:
    def __init__(self):
        # registry lưu mapping tên func → string path "module:func"
        self._registry = {}

    def add_func(self, name: str, path: str):
        """
        Đăng ký một func mới
        Ví dụ:
            name = "minio"
            path = "yflow.core.extract.minio_extractors:extractor"
        """
        self._registry[name] = path

    def get_func_path(self, name: str) -> str:
        if name not in self._registry:
            raise KeyError(f"Func '{name}' chưa được đăng ký")
        return self._registry[name]

    def list_funcs(self):
        return list(self._registry.keys())
