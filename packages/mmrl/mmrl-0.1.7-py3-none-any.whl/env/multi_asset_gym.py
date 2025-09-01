from __future__ import annotations
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Dict, Any
from env.multi_asset_env import MultiAssetEnv


class MultiAssetGymEnv(gym.Env):
    metadata = {"render.modes": ["human"]}

    def __init__(self, cfg: Dict[str, Any] | None = None):
        super().__init__()
        self._base_cfg = dict(cfg or {})
        cfg = self._base_cfg
        ma = cfg.get("multi_asset", {})
        self.num_assets = int(ma.get("num_assets", 2))
        self.depth_levels = int(ma.get("depth_levels", 2))
        self.level_widen = float(ma.get("level_widen", 0.05))

        self.env = MultiAssetEnv(
            num_assets=self.num_assets,
            depth_levels=self.depth_levels,
            seed=cfg.get("seed"),
            market=cfg.get("market"),
            execution=cfg.get("execution"),
            fees=cfg.get("fees"),
        )
        # Observation: concat [mid, inventory, sigma_scale]
        obs_dim = self.num_assets * 3
        self.observation_space = spaces.Box(
            low=-np.full((obs_dim,), 1e9, dtype=np.float32),
            high=np.full((obs_dim,), 1e9, dtype=np.float32),
            dtype=np.float32,
        )
        # Action: for each asset → [bid_offset, ask_offset] + [sizes(k) for k in levels]
        per_asset = 2 + self.depth_levels
        low = np.concatenate([
            np.zeros((self.num_assets * 2,), dtype=np.float32),
            np.zeros((self.num_assets * self.depth_levels,), dtype=np.float32),
        ])
        high = np.concatenate([
            np.full((self.num_assets * 2,), 0.5, dtype=np.float32),
            np.full((self.num_assets * self.depth_levels,), 3.0, dtype=np.float32),
        ])
        self.action_space = spaces.Box(low=low, high=high, dtype=np.float32)
        self.max_steps = int(cfg.get("steps", 1000))
        self.step_count = 0

    def _get_obs(self) -> np.ndarray:
        return np.concatenate([
            self.env.mid.astype(np.float32),
            self.env.inventory.astype(np.float32),
            self.env._sigma_scale.astype(np.float32),
        ]).astype(np.float32)

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        if seed is not None:
            self.env = MultiAssetEnv(
                num_assets=self.num_assets,
                depth_levels=self.depth_levels,
                seed=seed,
                market=self._base_cfg.get("market"),
                execution=self._base_cfg.get("execution"),
                fees=self._base_cfg.get("fees"),
            )
        self.env.reset()
        self.step_count = 0
        return self._get_obs(), {}

    def step(self, action: np.ndarray):
        action = np.clip(action, self.action_space.low, self.action_space.high)
        bids = []
        asks = []
        per_asset = 2 + self.depth_levels
        for a in range(self.num_assets):
            start = a * per_asset
            bid_off = float(action[start + 0])
            ask_off = float(action[start + 1])
            sizes = action[start + 2 : start + 2 + self.depth_levels]
            # Construct price ladder per level around mid
            b_levels = []
            a_levels = []
            mid = float(self.env.mid[a])
            for k in range(self.depth_levels):
                spread_k = bid_off + ask_off + self.level_widen * k
                half = spread_k / 2.0
                b_px = mid - half
                a_px = mid + half
                size_k = float(sizes[k])
                b_levels.append((b_px, size_k))
                a_levels.append((a_px, size_k))
            bids.append(b_levels)
            asks.append(a_levels)
        prev_pnl = self.env.pnl
        self.env.step(bids, asks)
        self.step_count += 1
        pnl_delta = self.env.pnl - prev_pnl
        inv_penalty = 0.01 * float(np.linalg.norm(self.env.inventory, ord=1))
        size_penalty = 0.001 * float(np.sum(action[2:]))
        reward = float(pnl_delta - inv_penalty - size_penalty)
        obs = self._get_obs()
        terminated = False
        truncated = self.step_count >= self.max_steps
        info = {"inventory": self.env.inventory.copy(), "pnl": self.env.pnl}
        return obs, reward, terminated, truncated, info