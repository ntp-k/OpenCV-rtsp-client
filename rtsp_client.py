import cv2
from threading import Thread
import time

from dummy_opencv_videocapture import DummyVideoCapture


class RTSPClient:
    def __init__(self, rtsp_url: str, verbose: bool = False) -> None:
        self.rtsp_url = rtsp_url
        self.verbose = verbose

        # running variable
        self.running = False
        self.frame = None

    def _print_v(self, text: str = ''):
        if self.verbose:
            print(f'[RTSPClient]\t {text}')

    def restart_rtsp_client(self):
        self.end_rtsp_client()
        self.start_rtsp_client()

    def end_rtsp_client(self):
        try:
            self._print_v(text=f'Disconnecting from {self.rtsp_url}')
            self.running = False
            self._bgt.join()
            self._print_v(text=f'Disconnected')
        except Exception as err:
            print(err)

    def start_rtsp_client(self):
        t = Thread(target=self._rtsp_client, args=())
        t.daemon = True
        t.start()
        self._bgt = t

        # wait until stream is initialized
        while not self.running:
            pass

    def _init_dummy_videocapture(self):
        self._print_v(text=f'Using dummy videocapture')
        self.stream = DummyVideoCapture()
        self.is_dummy = True

    def _rtsp_client(self):
        '''
        init VideoCapture from RTSP
        if network unreachable or error, init dummy RTSP
        '''

        if self.rtsp_url is not None and self.rtsp_url != '':
            try:
                self._print_v(text=f'Connecting to {self.rtsp_url}')
                self.stream = cv2.VideoCapture(self.rtsp_url)
                self.is_dummy = False
                time.sleep(1)  # wait for initialization

                self.is_connected = self.stream.isOpened()
                if self.is_connected:
                    self._print_v(text=f'Connected')
                else:
                    self._print_v(text=f'Can not connect to {self.rtsp_url}')
                    self._init_dummy_videocapture()

            except Exception as err:
                print(err)
                self._init_dummy_videocapture()
        else:
            self._init_dummy_videocapture()

        self.running = True
        self.stream_fps = self.stream.get(
            cv2.CAP_PROP_FPS) if not self.is_dummy else 999
        self._update()

    def _update(self):
        ''' continuously read and cache the latest frame from RTSP '''

        while self.running:
            # grabbed, frame = self.stream.read()
            grabbed = self.stream.grab()

            frame = None
            if grabbed:
                _, frame = self.stream.retrieve()

            self.frame = frame  # cache the latest frame

        self.stream.release()

    def get_frame(self):
        ''' 
        get the latest cached frame from rtsp

        parameter: 
            None
        return:
            - frame:
                - np.array cached frame from rtsp
                - None if error occur or network unreachable
        '''

        frame = None
        try:
            frame = self.frame
        except Exception as err:
            print(err)

        return frame

    def get_fps(self):
        return self.stream_fps


if __name__ == "__main__":
    rtsp_url = 'rtsp://localhost:8554/video_stream'
    rtsp_cli = RTSPClient(rtsp_url=rtsp_url, verbose=True)
    rtsp_cli.start_rtsp_client()
    run = True

    print('Press \'Enter\' to exit')
    while run:
        frame = rtsp_cli.get_frame()

        if frame is None:
            continue

        cv2.imshow("rtsp feed", frame)

        key = cv2.waitKey(1)
        if key == 13:  # wait for Enter Key
            run = False

    rtsp_cli.end_rtsp_client()

# EOF
