
import torch
import time
import json
#from bournemouth_aligner import PhonemeTimestampAligner
import sys
sys.path.append('.')
from bournemouth_aligner.core import PhonemeTimestampAligner




def plot_mel_phonemes(mel, compress_framesed, save_path="mel_phonemes.png"):
    """
    Plot mel spectrogram with phoneme IDs overlaid directly on the spectrogram
    
    Args:
        mel: Mel spectrogram tensor [frames, mel_bins]
        phn_frame_ids: List of phoneme IDs aligned to frames
        phn_frame_counts: List of counts for each phoneme ID
        save_path: Path to save the plot
    """
    import matplotlib.pyplot as plt
    
    assert mel.dim() == 2, f"Expected 2D mel tensor, got {mel.dim()}D"
    phn_frame_ids = [phoneme_id for phoneme_id, _ in compress_framesed]
    phn_frame_counts = [count for _, count in compress_framesed]

    # Create single plot - make it twice as wide
    fig, ax = plt.subplots(1, 1, figsize=(30, 8))
    
    # Convert mel to numpy for plotting
    mel_np = mel.cpu().numpy() if isinstance(mel, torch.Tensor) else mel
    
    # Add statistics to title instead of overlaying on spectrum
    unique_phonemes = len(set(phn_frame_ids))
    stats_text = f"Frames: {sum(phn_frame_counts)} | Unique Phonemes: {unique_phonemes} | Mel Bins: {mel.shape[1]}"
    title_text = f'Mel Spectrogram with Phoneme Alignment\n{stats_text}'
    
    # Plot mel spectrogram
    im = ax.imshow(mel_np.T, aspect='auto', origin='lower', 
                    cmap='viridis', interpolation='nearest')
    ax.set_ylabel('Mel Bins')
    ax.set_xlabel('Frame Index')
    ax.set_title(title_text)
    plt.colorbar(im, ax=ax, label='Magnitude')
    
    # Overlay phoneme information
    frame_pos = 0
    for phn_id, count in zip(phn_frame_ids, phn_frame_counts):
        # Draw vertical boundary lines (except for first segment)
        if frame_pos > 0:
            ax.axvline(x=frame_pos-0.5, color='red', linestyle='-', alpha=0.8, linewidth=2)
        
        # Add phoneme ID text at the top of the spectrogram
        if count > 1:  # Only add text if segment is wide enough
            text_x = frame_pos + count/2
            text_y = mel.shape[1] - 2  # Near the top of the mel bins
            
            # Add text with background for visibility
            ax.text(text_x, text_y, str(phn_id), 
                    ha='center', va='center', fontsize=12, fontweight='bold',
                    color='white', 
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.8))
        
        frame_pos += count
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"Mel-phoneme alignment plot saved to: {save_path}")
    
    return save_path


def example_audio_timestamps():

    text_sentences = "butterfly."
    audio_path = "examples/samples/audio/109867__timkahn__butterfly.wav"
    
    model_name = "en_libri1000_uj01d_e199_val_GER=0.2307.ckpt" 
    extractor = PhonemeTimestampAligner(model_name=model_name, lang='en-us', duration_max=10, device='cpu', enforce_all_targets=False)

    full_clip_wav = extractor.load_audio(audio_path) # can replace it with custom audio source

    t0 = time.time()

    timestamps = extractor.process_sentence(text_sentences, full_clip_wav, ts_out_path=None, extract_embeddings=False, vspt_path=None, do_groups=False, debug=False)

    t1 = time.time()
    print(f"Processing time: {t1 - t0:.2f} seconds")

    print("Timestamps:")
    print(json.dumps(timestamps, indent=4))
    
    # Extract Mel-Spectrum
    # Use the same config to generate mel-spectrum as bigvan vocoder model, so that the mel-spectrum can be converted back to audio easily.
    bigvgan_config = {'num_mels': 80, 'num_freq': 1025, 'n_fft': 1024, 'hop_size': 256, 'win_size': 1024, 'sampling_rate': 22050, 'fmin': 0, 'fmax': 8000, 'model': 'nvidia/bigvgan_v2_22khz_80band_fmax8k_256x'}

    # we just need to extract the mel-spectrogram for the segment 0
    segment_start_frame = int(timestamps['segments'][0]['start'] * extractor.resampler_sample_rate)
    segment_end_frame = int(timestamps['segments'][0]['end'] * extractor.resampler_sample_rate)
    segment_wav = full_clip_wav[segment_start_frame:segment_end_frame]
    mel_spec = extractor.extract_mel_spectrum(segment_wav, wav_sample_rate=extractor.resampler_sample_rate, bigvgan_config=bigvgan_config)


    # Assort phonemes into frame steps to match the mel-spectrogram hop-size
    segment_duration = timestamps['segments'][0]['end'] - timestamps['segments'][0]['start']

    
    
    total_frames = mel_spec.shape[0]
    frames_per_second = total_frames / segment_duration
    frames_assorted = extractor.framewise_assortment(aligned_ts=timestamps['segments'][0]['phoneme_ts'], total_frames=total_frames, frames_per_second=frames_per_second, gap_contraction=5, select_key="phoneme_idx")
    # convert phoneme IDs to labels
    frames_assorted = [extractor.phoneme_id_to_label[phoneme_id] for phoneme_id in frames_assorted]

    compress_framesed = extractor.compress_frames(frames_assorted)


    plot_mel_phonemes(mel_spec, compress_framesed, save_path="mel_phonemes.png")

if __name__ == "__main__":
    torch.random.manual_seed(42)
    example_audio_timestamps()















'''output
Model available at: /root/.cache/huggingface/hub/models--Tabahi--CUPE-2i/snapshots/5bb0124be864e01d12c90145863f727e490ab3fb/ckpt/en_libri1000_uj01d_e199_val_GER=0.2307.ckpt
Setting backend for language: en-us
Expected phonemes: ['b', 'ʌ', 'ɾ', 'ɚ', 'f', 'l', 'aɪ']
Target phonemes: 7, Expected: ['b', 'ʌ', 'ɾ', 'ɚ', 'f', 'l', 'aɪ']
Spectral length: 75
Forced alignment took 18.673 ms
Aligned phonemes: 7
Target phonemes: 7
SUCCESS: All target phonemes were aligned!
Predicted phonemes 7
Predicted groups 7
start_offset_time 0.0
 1:   b, voiced_stops  -> (33.568 - 50.352), Confidence: 0.991
 2:   ʌ, central_vowels  -> (100.705 - 117.489), Confidence: 0.845
 3:   ɾ, rhotics  -> (134.273 - 151.057), Confidence: 0.285
 4:   ɚ, central_vowels  -> (285.331 - 302.115), Confidence: 0.738
 5:   f, voiceless_fricatives  -> (352.467 - 402.820), Confidence: 0.988
 6:   l, laterals  -> (520.309 - 553.878), Confidence: 0.916
 7:  aɪ, diphthongs  -> (604.230 - 621.014), Confidence: 0.412
Alignment Coverage Analysis:
  Target phonemes: 7
  Aligned phonemes: 7
  Coverage ratio: 100.00%

============================================================
PROCESSING SUMMARY
============================================================
Total segments processed: 1
Perfect sequence matches: 1/1 (100.0%)
Total phonemes aligned: 7
Overall average confidence: 0.655
============================================================
Timestamps:
{
    "segments": [
        {
            "start": 0.0,
            "end": 1.2588125,
            "text": "butterfly",
            "ph66": [
                29,
                10,
                58,
                9,
                43,
                56,
                23
            ],
            "pg16": [
                7,
                2,
                14,
                2,
                8,
                13,
                5
            ],
            "coverage_analysis": {
                "target_count": 7,
                "aligned_count": 7,
                "missing_count": 0,
                "extra_count": 0,
                "coverage_ratio": 1.0,
                "missing_phonemes": [],
                "extra_phonemes": []
            },
            "ipa": [
                "b",
                "ʌ",
                "ɾ",
                "ɚ",
                "f",
                "l",
                "aɪ"
            ],
            "word_num": [
                0,
                0,
                0,
                0,
                0,
                0,
                0
            ],
            "words": [
                "butterfly"
            ],
            "phoneme_ts": [
                {
                    "phoneme_idx": 29,
                    "phoneme_label": "b",
                    "start_ms": 33.56833267211914,
                    "end_ms": 50.35249710083008,
                    "confidence": 0.9849503040313721
                },
                {
                    "phoneme_idx": 10,
                    "phoneme_label": "ʌ",
                    "start_ms": 100.70499420166016,
                    "end_ms": 117.48916625976562,
                    "confidence": 0.8435571193695068
                },
                {
                    "phoneme_idx": 58,
                    "phoneme_label": "ɾ",
                    "start_ms": 134.27333068847656,
                    "end_ms": 151.0574951171875,
                    "confidence": 0.3894280791282654
                },
                {
                    "phoneme_idx": 9,
                    "phoneme_label": "ɚ",
                    "start_ms": 285.3308410644531,
                    "end_ms": 302.114990234375,
                    "confidence": 0.3299962282180786
                },
                {
                    "phoneme_idx": 43,
                    "phoneme_label": "f",
                    "start_ms": 369.2516784667969,
                    "end_ms": 386.03582763671875,
                    "confidence": 0.9150863289833069
                },
                {
                    "phoneme_idx": 56,
                    "phoneme_label": "l",
                    "start_ms": 520.3091430664062,
                    "end_ms": 553.8775024414062,
                    "confidence": 0.9060741662979126
                },
                {
                    "phoneme_idx": 23,
                    "phoneme_label": "aɪ",
                    "start_ms": 604.22998046875,
                    "end_ms": 621.01416015625,
                    "confidence": 0.21650740504264832
                }
            ],
            "group_ts": [
                {
                    "group_idx": 7,
                    "group_label": "voiced_stops",
                    "start_ms": 33.56833267211914,
                    "end_ms": 50.35249710083008,
                    "confidence": 0.9911064505577087
                },
                {
                    "group_idx": 2,
                    "group_label": "central_vowels",
                    "start_ms": 100.70499420166016,
                    "end_ms": 117.48916625976562,
                    "confidence": 0.8446590304374695
                },
                {
                    "group_idx": 14,
                    "group_label": "rhotics",
                    "start_ms": 134.27333068847656,
                    "end_ms": 151.0574951171875,
                    "confidence": 0.28526052832603455
                },
                {
                    "group_idx": 2,
                    "group_label": "central_vowels",
                    "start_ms": 285.3308410644531,
                    "end_ms": 302.114990234375,
                    "confidence": 0.7377423048019409
                },
                {
                    "group_idx": 8,
                    "group_label": "voiceless_fricatives",
                    "start_ms": 352.4674987792969,
                    "end_ms": 402.8199768066406,
                    "confidence": 0.9877637028694153
                },
                {
                    "group_idx": 13,
                    "group_label": "laterals",
                    "start_ms": 520.3091430664062,
                    "end_ms": 553.8775024414062,
                    "confidence": 0.9163824915885925
                },
                {
                    "group_idx": 5,
                    "group_label": "diphthongs",
                    "start_ms": 604.22998046875,
                    "end_ms": 621.01416015625,
                    "confidence": 0.4117060899734497
                }
            ],
            "words_ts": [
                {
                    "word": "butterfly",
                    "start_ms": 33.56833267211914,
                    "end_ms": 621.01416015625,
                    "confidence": 0.6550856615815844,
                    "ph66": [
                        29,
                        10,
                        58,
                        9,
                        43,
                        56,
                        23
                    ],
                    "ipa": [
                        "b",
                        "ʌ",
                        "ɾ",
                        "ɚ",
                        "f",
                        "l",
                        "aɪ"
                    ]
                }
            ]
        }
    ]
}
Processing time: 0.19 seconds
'''