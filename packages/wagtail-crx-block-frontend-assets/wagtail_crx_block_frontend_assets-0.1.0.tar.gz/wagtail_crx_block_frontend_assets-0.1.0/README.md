# Wagtail CRX block frontend assets rendering

Define and organize frontend assets (like js or css files) for your Wagtail CRX blocks.

## Getting started

1. Add the app to INSTALLED_APPS:
   ```
   INSTALLED_APPS = [
    ...
    "wagtail_crx_block_frontend_assets",
    ...
    ]
   ```

2. Integrate your blocks with this app.
   ```
    from wagtail.blocks import CharBlock, StructBlock
    from wagtail_crx_block_frontend_assets.blocks import BlockStaticAssetsRegistrationMixin

    class FrontendAssetsBlock(BlockStaticAssetsRegistrationMixin, StructBlock):

        title = CharBlock(
            required=False,
            label="Title",
        )

        def register_assets(self, block_value):
            static_assets = []

            static_assets += [
                self.StaticAsset("path/to/asset.js", target="_blank"),
                self.StaticAsset("path/to/style.css", media="print"),

            ]

            return static_assets
   ```
   Your block class has to inherit from `BlockStaticAssetsRegistrationMixin` and you have to implement `register_assets` function.
   This function returns array of `BlockStaticAssetsRegistrationMixin.StaticAsset` instances.
   You can use `block_value` parameter to conditionally render assets based on current block values.

3. Then you can define place in your templates where you want your block assets to be rendered like this:
    ```
    {% extends "coderedcms/pages/base.html" %}

    {% block custom_assets %}
    {{ block.super }}
    {% include "wagtail_crx_block_frontend_assets/includes/block_assets.html" with required_file_extension=".css" %}
    {% endblock custom_assets %}

    {% block custom_scripts %}
    {{ block.super }}
    {% include "wagtail_crx_block_frontend_assets/includes/block_assets.html" with required_file_extension=".js" %}
    {% endblock custom_scripts %}
    ```

## Development

1. Make sure you have Python virtual env installed
    ```
    $ python -m venv .venv
    ```
2. Install this app in editable mode
    ```
    $ pip install -e .
    ```
3. Migrate testapp DB
    ```
    $ python manage.py migrate
    ```
3. Run the testapp
    ```
    $ python manage.py runserver
    ```
    Or hit F5 if you use Visual Studio Code
