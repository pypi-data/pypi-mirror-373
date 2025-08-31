import pytest

try:
    from env.gym_env import MarketMakingGymEnv
    HAS_GYM = True
except Exception:
    HAS_GYM = False

pytestmark = pytest.mark.skipif(not HAS_GYM, reason="gymnasium not available")


def test_gym_env_step_contract():
    env = MarketMakingGymEnv({"steps": 10})
    obs, info = env.reset()
    assert obs.shape == (3,)
    action = env.action_space.sample()
    obs2, reward, terminated, truncated, info = env.step(action)
    assert obs2.shape == (3,)
    assert isinstance(reward, float)
    assert isinstance(terminated, bool)
    assert isinstance(truncated, bool)