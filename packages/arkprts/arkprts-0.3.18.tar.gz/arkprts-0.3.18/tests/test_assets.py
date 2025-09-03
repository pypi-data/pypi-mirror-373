"""Test game assets."""

import pytest

import arkprts


async def test_update(client: arkprts.Client) -> None:
    # we could force, but that takes up a lot of time
    await client.update_assets()


async def test_bundle_assets() -> None:
    try:
        assets = arkprts.BundleAssets()
    except ImportError:
        pytest.skip("Environment is not ready for bundle download.")
    else:
        await assets.update_assets(force=True)

        await assets.network.close()


async def test_git_assets() -> None:
    assets = arkprts.GitAssets()
    await assets.update_assets()


def test_access(client: arkprts.Client) -> None:
    operator = client.assets.full_character_table["char_1001_amiya2"]
    assert operator.name == "Amiya"


def calculate_trust(client: arkprts.Client) -> None:
    # 9915 - 10069
    assert client.assets.calculate_trust_level(10000) == 99
