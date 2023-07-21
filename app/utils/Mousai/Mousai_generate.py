from audio_diffusion_pytorch import DiffusionModel, UNetV0, VDiffusion, VSampler
import torch

'''
Reference:
https://github.com/archinetai/audio-diffusion-pytorch
'''

model = DiffusionModel(
    # ... same as unconditional model
    use_text_conditioning=True, # U-Net: enables text conditioning (default T5-base)
    use_embedding_cfg=True, # U-Net: enables classifier free guidance
    embedding_max_length=64, # U-Net: text embedding maximum length (default for T5-base)
    embedding_features=768, # U-Net: text mbedding features (default for T5-base)
    cross_attentions=[0, 0, 0, 1, 1, 1, 1, 1, 1], # U-Net: cross-attention enabled/disabled at each layer
)

# # Train model with audio waveforms
# audio_wave = torch.randn(1, 2, 2**18) # [batch, in_channels, length]
# loss = model(
#     audio_wave,
#     text=['The audio description'], # Text conditioning, one element per batch
#     embedding_mask_proba=0.1 # Probability of masking text with learned embedding (Classifier-Free Guidance Mask)
# )
# loss.backward()

# Turn noise into new audio sample with diffusion
noise = torch.randn(1, 2, 2**18)
sample = model.sample(
    noise,
    text=['The audio description'],
    embedding_scale=5.0, # Higher for more text importance, suggested range: 1-15 (Classifier-Free Guidance Scale)
    num_steps=20 # Higher for better quality, suggested num_steps: 10-100
)