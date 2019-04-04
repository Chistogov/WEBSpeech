import pydub

def remove(sound):
    silence = pydub.silence.detect_silence(sound, silence_thresh=-60.0)
    out_silence = sound[0:0]
    n = 0
    for start, end in silence:
        segment = sound[n: start]
        n = end
        out_silence += segment
    out_silence += sound[n: len(sound)]
    return out_silence