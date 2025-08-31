import pytest
import asyncio
from fletx.navigation import ModuleRouter, get_router, router_config
from fletx.decorators import register_router

### MOCKS ###
class MockPage:
    def __init__(self):
        self.navigation = []

class MockMiddleware:
    async def before_navigation(self, from_route, to_route):
        return True

class MockMiddlewareBlocker:
    async def before_navigation(self, from_route, to_route):
        return False

class DummyComponent:
    pass

### TESTS ###

def test_module_router_basic_patterns():
    class MyRouter(ModuleRouter):
        base_path = '/app'
        routes = [
            {'path': '/home', 'component': DummyComponent},
            {'path': '/settings', 'component': DummyComponent}
        ]
        sub_routers = []
        name = 'MyRouter'
        is_root = True

    router = MyRouter()
    patterns = router.get_route_patterns()
    assert any(p['pattern'] == '/app/home' for p in patterns)
    assert any(p['pattern'] == '/app/settings' for p in patterns)


def test_register_router_adds_to_config():
    router_config._module_routes.clear()  # reset config

    @register_router
    class MyRootRouter(ModuleRouter):
        base_path = '/'
        routes = [{'path': '/home', 'component': DummyComponent}]
        sub_routers = []
        name = 'MyRoot'
        is_root = True

    assert '' in router_config._module_routes
    module = router_config._module_routes['']
    assert isinstance(module, MyRootRouter)


@pytest.mark.asyncio
async def test_router_navigation_success():
    page = MockPage()
    router = Router(page=page)
    router._config.add_module_routes('/', ModuleRouter(
        base_path='/',
        routes=[
            {'path': '/test', 'component': DummyComponent}
        ],
        sub_routers=[]
    ))

    await router.navigate('/test')
    # Ici tu peux vérifier que ton router a bien matché et navigué
    # Exemple : assert page.navigation[-1] == '/test' (si tu as un tel mécanisme)

@pytest.mark.asyncio
async def test_router_navigation_with_middleware_allows():
    page = MockPage()
    router = RouteDe(page=page)
    router._middlewares.append(MockMiddleware())

    router._config.add_module_routes('/', ModuleRouter(
        base_path='/',
        routes=[
            {'path': '/test', 'component': DummyComponent}
        ],
        sub_routers=[]
    ))

    result = await router._run_before_middleware(None, '/test')
    assert result is True

@pytest.mark.asyncio
async def test_router_navigation_with_middleware_blocks():
    page = MockPage()
    router = FletX(page=page)
    router._middlewares.append(MockMiddlewareBlocker())

    result = await router._run_before_middleware(None, '/test')
    assert result is False

@pytest.mark.asyncio
async def test_router_navigation_404():
    page = MockPage()
    router = FletXRouter(page=page)
    # pas de routes ajoutées
    with pytest.raises(Exception):  # ou ton exception custom 404
        await router.navigate('/unknown')
