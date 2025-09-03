import numpy as np
import gymnasium as gym

class DiscreteActionsWrapper(gym.Wrapper):
    """
    Wrapper to use discrete actions rather than continuous in TradingEnv.

    This wrapper effectively reverts to the original behaviour in gym-trading-env.
    """

    def __init__(self, env, positions=None):
        """
        Create a new instance of the Wrapper.

        :param env: The instance of TradingEnv to use.
        :type env: gym_trading_env.environments.TradingEnv

        :param positions: The list of positions to use; these will be the
            discrete actions that are accepted by the wrapped env. It defaults
            to [0, 1], exactly as in the original version of gym-trading-env.
        :type positions: list[int]
        """
        super().__init__(env)
        if positions is None:
            positions = [0, 1]
        self.positions = positions

        self.action_space = gym.spaces.Discrete(len(self.positions))

    def step(self, position_index):
        """
        Advance the simulation by one time step and take a new position.

        :param position_index: The index of the desired position, with
            respect to the ``positions`` list defined when creating the
            wrapper.
        :type position_index: int

        :return: The return values of the TradingEnv.step() method, that is,
            the new observations, reward, terminated, truncated, info.
            The info dict is modified to also include the position_index, as
            was done previously in gym-trading-env.
        """
        assert isinstance(position_index, (int, np.integer)), "position_index must be an int"
        assert 0 <= position_index <= len(self.positions), "position_index must be in [0, #positions]"

        position = self.positions[position_index]
        obs, reward, terminated, truncated, _ = self.env.step(position)
        self.unwrapped.historical_info['position_index', -1] = position_index  # FIXME
        info = self.unwrapped.historical_info[-1]

        return obs, reward, terminated, truncated, info
