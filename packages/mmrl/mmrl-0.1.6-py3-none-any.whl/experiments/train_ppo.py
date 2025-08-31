import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yaml
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from env.gym_env import MarketMakingGymEnv


def main():
    cfg_path = os.environ.get('MMRL_CONFIG', 'configs/inventory.yaml')
    with open(cfg_path, 'r') as f:
        cfg = yaml.safe_load(f)

    def make_env():
        return MarketMakingGymEnv(cfg)

    env = DummyVecEnv([make_env])
    model = PPO("MlpPolicy", env, verbose=1)
    timesteps = int(cfg.get('train_timesteps', 10000))
    model.learn(total_timesteps=timesteps)
    out_dir = cfg.get('output_dir', 'results')
    os.makedirs(out_dir, exist_ok=True)
    model.save(os.path.join(out_dir, 'ppo_market_making'))
    print("Saved PPO model to", os.path.join(out_dir, 'ppo_market_making.zip'))


if __name__ == "__main__":
    main()