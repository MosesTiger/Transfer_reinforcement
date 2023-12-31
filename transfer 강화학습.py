import gym
import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np

# DQN 네트워크 정의
class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, output_dim)
        )

    def forward(self, x):
        return self.fc(x)

# 환경 초기화
env = gym.make('CartPole-v1')
input_dim = env.observation_space.shape[0]
output_dim = env.action_space.n

# 모델 및 최적화 초기화
model = DQN(input_dim, output_dim)
optimizer = optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

# 학습 파라미터
num_episodes = 500
gamma = 0.99  # 할인 계수

for episode in range(num_episodes):
    state = env.reset()
    done = False
    while not done:
        # 행동 선택 (랜덤 또는 모델 예측)
        if random.random() < 0.1:
            action = env.action_space.sample()
        else:
            q_values = model(torch.tensor(state, dtype=torch.float32))
            action = torch.argmax(q_values).item()

        # 행동 수행 및 다음 상태 관찰
        next_state, reward, done, _ = env.step(action)

        # 목표 Q-값 계산
        target_q = reward
        if not done:
            next_q_values = model(torch.tensor(next_state, dtype=torch.float32))
            target_q += gamma * torch.max(next_q_values).item()

        # 현재 Q-값 계산
        current_q = model(torch.tensor(state, dtype=torch.float32))[action]

        # 손실 계산 및 업데이트
        loss = criterion(current_q, torch.tensor([target_q], dtype=torch.float32))
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        state = next_state

# 모델 저장
torch.save(model.state_dict(), 'dqn_model.pth')