from __future__ import annotations
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from env.simple_lob_env import SimpleLOBEnv
from agents.inventory_mm import InventoryAwareMarketMaker


class MarketMakingGymEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, cfg: dict | None = None):
        super().__init__()
        self._base_cfg = dict(cfg or {})
        cfg = self._base_cfg
        self.env = SimpleLOBEnv(
            seed=cfg.get("seed"),
            market=cfg.get("market"),
            execution=cfg.get("execution"),
            fees=cfg.get("fees"),
        )
        self.agent = InventoryAwareMarketMaker(
            spread=cfg.get("agent", {}).get("spread", 0.1),
            inventory_sensitivity=cfg.get("agent", {}).get("inventory_sensitivity", 0.05),
        )
        self.observation_space = spaces.Box(low=-np.array([1e9, 100.0, 10.0], dtype=np.float32), high=np.array([1e9, 100.0, 10.0], dtype=np.float32), dtype=np.float32)
        self.action_space = spaces.Box(low=np.array([0.0, 0.0], dtype=np.float32), high=np.array([0.5, 0.5], dtype=np.float32), dtype=np.float32)
        self.max_steps = int(cfg.get("steps", 1000))
        self.step_count = 0

    def _get_obs(self):
        return np.array([self.env.mid_price, self.env.inventory, self.env._current_sigma], dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        if seed is not None:
            # Recreate underlying env preserving current config
            self.env = SimpleLOBEnv(
                seed=seed,
                market=self._base_cfg.get("market"),
                execution=self._base_cfg.get("execution"),
                fees=self._base_cfg.get("fees"),
            )
        self.env.reset()
        self.step_count = 0
        return self._get_obs(), {}

    def step(self, action):
        action = np.clip(action, self.action_space.low, self.action_space.high)
        bid_offset, ask_offset = float(action[0]), float(action[1])
        mid = self.env.mid_price
        bid = mid - bid_offset
        ask = mid + ask_offset
        prev_pnl = self.env.pnl
        self.env.step(bid, ask)
        self.step_count += 1
        pnl_delta = self.env.pnl - prev_pnl
        inv_penalty = 0.01 * abs(self.env.inventory)
        reward = float(pnl_delta - inv_penalty)
        obs = self._get_obs()
        terminated = False
        truncated = self.step_count >= self.max_steps
        info = {"inventory": self.env.inventory, "pnl": self.env.pnl}
        return obs, reward, terminated, truncated, info


class SizeAwareGymEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, cfg: dict | None = None, depth_levels: int = 2):
        super().__init__()
        cfg = cfg or {}
        self.env = SimpleLOBEnv(
            seed=cfg.get("seed"),
            market=cfg.get("market"),
            execution=cfg.get("execution"),
            fees=cfg.get("fees"),
        )
        self.depth_levels = depth_levels
        # Observation same as before
        self.observation_space = spaces.Box(low=-np.array([1e9, 100.0, 10.0], dtype=np.float32), high=np.array([1e9, 100.0, 10.0], dtype=np.float32), dtype=np.float32)
        # Action: [bid_offset, ask_offset, size_level1, size_level2, ...]
        low = np.array([0.0, 0.0] + [0.0] * depth_levels, dtype=np.float32)
        high = np.array([0.5, 0.5] + [3.0] * depth_levels, dtype=np.float32)  # sizes up to 3 units
        self.action_space = spaces.Box(low=low, high=high, dtype=np.float32)
        self.max_steps = int(cfg.get("steps", 1000))
        self.step_count = 0

    def _get_obs(self):
        return np.array([self.env.mid_price, self.env.inventory, self.env._current_sigma], dtype=np.float32)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        if seed is not None:
            self.env = SimpleLOBEnv(seed=seed)
        self.env.reset()
        self.step_count = 0
        return self._get_obs(), {}

    def step(self, action):
        action = np.clip(action, self.action_space.low, self.action_space.high)
        bid_offset, ask_offset = float(action[0]), float(action[1])
        sizes = action[2:]
        mid = self.env.mid_price
        bid = mid - bid_offset
        ask = mid + ask_offset
        prev_pnl = self.env.pnl
        # Approximate: place level-1 sizes at chosen offsets; ignore deeper levels in SimpleLOBEnv
        # For a true size-aware fill, use MultiAssetEnv-based Gym.
        self.env.step(bid, ask)
        self.step_count += 1
        pnl_delta = self.env.pnl - prev_pnl
        inv_penalty = 0.01 * abs(self.env.inventory)
        size_penalty = 0.001 * float(np.sum(sizes))
        reward = float(pnl_delta - inv_penalty - size_penalty)
        obs = self._get_obs()
        terminated = False
        truncated = self.step_count >= self.max_steps
        info = {"inventory": self.env.inventory, "pnl": self.env.pnl}
        return obs, reward, terminated, truncated, info