import torch
import torch.nn as nn

class DKTModel(nn.Module):
    def __init__(self, num_skills: int, hidden_dim: int = 64, num_layers: int = 1):
        super(DKTModel, self).__init__()
        self.num_skills = num_skills
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        # The input is the combination of skill_id and whether it was answered correctly (0 or 1).
        # We represent this as 2 * num_skills possible inputs.
        self.embedding = nn.Embedding(2 * num_skills, hidden_dim)
        
        # LSTM for temporal sequence processing
        self.lstm = nn.LSTM(hidden_dim, hidden_dim, num_layers, batch_first=True)
        
        # Output layer predicts the probability of answering each skill correctly next
        self.out = nn.Linear(hidden_dim, num_skills)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # x shape: (batch_size, sequence_length)
        embedded = self.embedding(x)
        
        # lstm_out shape: (batch_size, sequence_length, hidden_dim)
        lstm_out, _ = self.lstm(embedded)
        
        # We predict the probability for ALL skills at each time step.
        # preds shape: (batch_size, sequence_length, num_skills)
        logits = self.out(lstm_out)
        preds = self.sigmoid(logits)
        
        return preds
