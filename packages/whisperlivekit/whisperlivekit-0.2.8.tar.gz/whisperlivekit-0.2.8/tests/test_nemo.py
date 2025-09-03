from nemo.collections.asr.models import SortformerEncLabelModel

# load model from Hugging Face model card directly (You need a Hugging Face token)
diar_model = SortformerEncLabelModel.from_pretrained("nvidia/diar_sortformer_4spk-v1")

# If you have a downloaded model in "/path/to/diar_sortformer_4spk-v1.nemo", load model from a downloaded file
# diar_model = SortformerEncLabelModel.restore_from(restore_path="/path/to/diar_sortformer_4spk-v1.nemo", map_location='cuda', strict=False)


# switch to inference mode
diar_model.eval()


audio_input="text-to-speech_synthesized_voices.wav"

# predicted_segments, predicted_probs = diar_model.diarize(audio=audio_input, batch_size=1, include_tensor_outputs=True)

# print("Predicted segments:", predicted_segments)
# print("Predicted probabilities:", predicted_probs)

from nemo.collections.asr.parts.mixins.diarization import DiarizeConfig, InternalDiarizeConfig

config = DiarizeConfig(session_len_sec=-1, batch_size=1, num_workers=0, postprocessing_yaml=None, verbose=True, include_tensor_outputs=True, postprocessing_params={'onset': 0.5, 'offset': 0.5, 'pad_onset': 0.0, 'pad_offset': 0.0, 'min_duration_on': 0.0, 'min_duration_off': 0.0}, _internal=InternalDiarizeConfig(device=None, dtype=None, training_mode=False, logging_level=20, dither_value=1e-05, pad_to_value=16, temp_dir='/var/folders/68/cmkt1gj90y91xlg9jntm2kjh0000gn/T/tmpf9n_gmge', manifest_filepath=None))
dataloader = diar_model._diarize_input_processing(audio=audio_input, diarcfg=config)
predicted_segments, predicted_probs = diar_model.diarize(audio=dataloader, batch_size=1, include_tensor_outputs=True)

