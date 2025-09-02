from kws import extract_mfcc, extract_mel_spectrogram

# 2. Lấy MFCC
mfcc = extract_mfcc("D:/KWS/Audio/ffb86d3c_nohash_0.wav", n_mfcc=20)
print("MFCC shape:", mfcc.shape)

# 3. Lấy Mel spectrogram
mel = extract_mel_spectrogram("D:/KWS/Audio/ffb86d3c_nohash_0.wav", n_mels=128)
print("Mel spectrogram shape:", mel.shape)
