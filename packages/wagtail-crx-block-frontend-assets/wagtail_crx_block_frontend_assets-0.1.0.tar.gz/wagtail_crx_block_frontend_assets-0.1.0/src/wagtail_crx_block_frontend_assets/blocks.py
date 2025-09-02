
import os

from django.utils.translation import gettext_lazy as _


class BlockStaticAssetsRegistrationMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Register the block's assets
        self.static_files = []
        # self.register_assets()

    class StaticAsset:
        def __init__(self, path, **kwargs) -> None:
            self.kwargs = kwargs
            self.path = path

        @property
        def file_extension(self):
            return os.path.splitext(self.path)[1]

        @property
        def render_kwargs(self):
            kwargs_string = ""
            for key, value in self.kwargs.items():
                kwargs_string += '{}={} '.format(key, value)
            return kwargs_string

    def register_assets(self, block_value) -> list[StaticAsset]:
        """
        This method can be overridden in child blocks to specify which assets are needed.
        """
        return []


