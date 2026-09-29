import torch
import os
from typing import List
from app.models.dkt import DKTModel
from app.common.schemas import Interaction, DKTPrediction

class KnowledgeTracingService:
    def __init__(self, num_skills: int = 100):
        self.num_skills = num_skills
        self.model = DKTModel(num_skills=self.num_skills)
        self.is_loaded = False
        
        # Load weights if available
        weight_path = os.getenv("DKT_WEIGHTS_PATH", "weights.pth")
        if os.path.exists(weight_path):
            self.model.load_state_dict(torch.load(weight_path))
            self.is_loaded = True
        
        self.model.eval()

    def estimate_mastery(self, sequence: List[Interaction]) -> List[DKTPrediction]:
        """
        Estimate the mastery of all skills based on the interaction sequence.
        If no weights are loaded, return a default estimation and high uncertainty.
        """
        if not self.is_loaded:
            # Fallback when no trained model is available
            return [
                DKTPrediction(
                    skill_id=str(i),
                    mastery_estimation=0.5,
                    uncertainty=1.0
                ) for i in range(self.num_skills)
            ]
            
        if not sequence:
             return [
                DKTPrediction(
                    skill_id=str(i),
                    mastery_estimation=0.5,
                    uncertainty=0.8 # Cold start
                ) for i in range(self.num_skills)
            ]

        # Convert sequence to tensor
        x = []
        for interact in sequence:
            # Simple hash/mapping for skill_id to int for this example
            try:
                skill_idx = int(interact.skill_id) % self.num_skills
            except ValueError:
                skill_idx = hash(interact.skill_id) % self.num_skills
                
            val = skill_idx + (self.num_skills if interact.is_correct else 0)
            x.append(val)
            
        x_tensor = torch.tensor([x], dtype=torch.long)
        
        with torch.no_grad():
            preds = self.model(x_tensor)
            
        # Get the predictions at the last time step
        last_step_preds = preds[0, -1, :].tolist()
        
        predictions = []
        for i, pred in enumerate(last_step_preds):
            predictions.append(
                DKTPrediction(
                    skill_id=str(i),
                    mastery_estimation=pred,
                    uncertainty=0.2 # Lower uncertainty if we have sequence
                )
            )
            
        return predictions
