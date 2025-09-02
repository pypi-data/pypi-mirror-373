from coderedcms.blocks.layout_blocks import BaseLayoutBlock
from wagtail import hooks
from wagtail.blocks.stream_block import StreamValue

from wagtail_crx_block_frontend_assets.blocks import BlockStaticAssetsRegistrationMixin


@hooks.register('before_serve_page')
def collect_block_assets(page, request, serve_args, serve_kwargs):
    static_files = get_blocks_static_assets(page.body)

    distinct_assets = list({asset.path: asset for asset in static_files}.values())

    request.block_assets = distinct_assets

def get_blocks_static_assets(body):
    static_files = []

    for block in body:
        if isinstance(block.block, BlockStaticAssetsRegistrationMixin): #hasattr(block.block, 'static_files'):
            static_files.extend(
                block.block.register_assets(block.value)
            )
        elif issubclass(block.block.__class__, BaseLayoutBlock) and block.value["content"] and isinstance(block.value["content"], StreamValue):
            static_files.extend(
                get_blocks_static_assets(block.value["content"])
            )

    return static_files

