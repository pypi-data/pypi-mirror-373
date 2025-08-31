import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from env.multi_asset_gym import MultiAssetGymEnv
from agents.depth_mm import DepthAwareMarketMaker
import numpy as np


def train(cfg):
    def make_env():
        return MultiAssetGymEnv(cfg)
    env = DummyVecEnv([make_env])
    model = PPO("MlpPolicy", env, verbose=1)
    timesteps = int(cfg.get('train_timesteps', 20000))
    model.learn(total_timesteps=timesteps)
    out = os.path.join(cfg.get('output_dir', 'results'), 'ppo_multi')
    model.save(out)
    print('Saved', out + '.zip')


def evaluate(cfg):
    # Simple eval loop comparing PPO vs depth-aware rule-based by total reward proxy
    env = MultiAssetGymEnv(cfg)
    from stable_baselines3 import PPO
    model = PPO.load(os.path.join(cfg.get('output_dir', 'results'), 'ppo_multi'))
    obs, _ = env.reset()
    total_r = 0.0
    for _ in range(int(cfg.get('steps', 1000))):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        total_r += float(reward)
        if terminated or truncated:
            break
    print('PPO total reward:', total_r)
    # Depth-aware baseline
    from env.multi_asset_env import MultiAssetEnv
    env2 = MultiAssetEnv(num_assets=cfg.get('multi_asset', {}).get('num_assets', 2), depth_levels=cfg.get('multi_asset', {}).get('depth_levels', 2), seed=cfg.get('seed'), market=cfg.get('market'), execution=cfg.get('execution'), fees=cfg.get('fees'))
    agent = DepthAwareMarketMaker(depth_levels=cfg.get('multi_asset', {}).get('depth_levels', 2))
    prev_pnl = env2.pnl
    for _ in range(int(cfg.get('steps', 1000))):
        bids, asks = agent.quote(env2.mid, env2.inventory, env2._sigma_scale)
        env2.step(bids, asks)
    print('Depth-aware pnl:', env2.pnl)


def main():
    cfg_path = os.environ.get('MMRL_CONFIG', 'configs/inventory.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)
    train(cfg)
    evaluate(cfg)


if __name__ == '__main__':
    main()