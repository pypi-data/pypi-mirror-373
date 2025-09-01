from usdm3.base.id_manager import IdManager


class APIInstance:
    class APIInstanceError(Exception):
        """Custom exception for create errors"""

        pass

    def __init__(self, id_manager: IdManager):
        self._id_manager = id_manager

    def create(self, klass, params):
        try:
            klass_name = klass if isinstance(klass, str) else klass.__name__
            params["id"] = (
                self._id_manager.build_id(klass_name)
                if "id" not in params
                else params["id"]
            )
            params["instanceType"] = klass_name
            return klass(**params)
        except Exception as e:
            raise self.APIInstanceError(
                f"Failed to create {klass_name} instance, details: {e}"
            )
