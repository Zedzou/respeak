import pyaudio
import wave
import torchaudio
import io
from io import BytesIO

# 获取Respeaker的设备ID
def GetRespeake_id():

    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    Respeak_id = 0
    for i in range(0, numdevices):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print ( "Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name') )
            if p.get_device_info_by_host_api_device_index(0, i).get('name')[0:8] == "ReSpeake":
                Respeak_id = i

    return Respeak_id

# 从麦克风中获取音频数据并转成tensor
def GetMicArray_tensor():

    p = pyaudio.PyAudio()
    stream = p.open(
        rate = RESPEAKER_RATE,
        format = p.get_format_from_width(RESPEAKER_WIDTH),
        channels = RESPEAKER_CHANNELS,
        input = True,
        input_device_index = RESPEAKER_INDEX, )

    print("* recording")
    frames = []
    for i in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS) ):
        data = stream.read(CHUNK)
        frames.append(data)
    print("* done recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    container = io.BytesIO() # this is the virtual container for
    wf = wave.open( container, 'wb' )
    wf.setnchannels( RESPEAKER_CHANNELS )
    wf.setsampwidth( p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)) )
    wf.setframerate( RESPEAKER_RATE )
    # wf.writeframes( b''.join(frames) )
    wf.writeframes(data)

    container.seek(0)
    data_package = container.read()
    f = BytesIO( data_package )
    audio = torchaudio.load(f)
    wf.close()

if __name__ == "__main__":

    RESPEAKER_RATE = 16000
    RESPEAKER_CHANNELS = 6  # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
    RESPEAKER_WIDTH = 2
    RESPEAKER_INDEX = GetRespeake_id()  # refer to input device id
    CHUNK = 1024
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "./output.wav"
    GetMicArray_tensor()