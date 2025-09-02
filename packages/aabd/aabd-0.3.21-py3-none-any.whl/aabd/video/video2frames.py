import json
import math
import time
from abc import abstractmethod
import logging
from threading import Thread

import cv2
import os
import numpy

def_logger = logging.getLogger(__name__)
video_keywords = ('.mp4', '.avi', '.mkv', '.mov')

try:
    import torch
    import torch.nn.functional as F

except ImportError:
    print('PyTorch not found.')


def tensor2numpy_bgr(img_tensor):
    img = (img_tensor * 255.0).cpu().numpy()
    img = img.astype(numpy.uint8)
    if len(img.shape) == 3 and img.shape[0] == 3:  # 对于RGB图像
        img = numpy.transpose(img, (1, 2, 0))  # 更改维度顺序
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # OpenCV使用BGR格式
        return img


def video_info(video_path, timeout=5000):
    data = []

    def func():
        cap = cv2.VideoCapture(video_path)
        w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        cap.release()
        data.append((int(w), int(h), fps, int(frame_count)))

    Thread(target=func).start()
    start_time = time.time()
    while time.time() - start_time < timeout / 1000:
        if len(data) > 0:
            return data[0]
        else:
            time.sleep(0.01)
    raise Exception("read video timeout")


class StreamDecoder:
    def __init__(self, video_path, start=0, end=None, max_fps=500, out_path=None, logger=def_logger,
                 tqdm_enable=True, control_type='frame', is_live=None, frame_type='numpy_rgb', **kwargs):
        # numpy_rgb,numpy_bgr,pillow,tensor
        self.frame_type = frame_type or 'numpy_rgb'

        if logger is None:
            self.logger = def_logger
        else:
            self.logger = logger
        self.video_path = video_path

        if is_live is None:
            if video_path.startswith('rtmp') or video_path.startswith('rtsp'):
                self.is_live = True
            elif video_path.endswith(video_keywords):
                self.is_live = False
            else:
                raise ValueError('live is null')
        else:
            self.is_live = is_live
        if self.is_live and start > 0:
            raise Exception('start must be 0 for live stream')
        self.width, self.height, self.fps, frame_count = video_info(video_path, timeout=kwargs.get('open_video_timeout', 5000))
        if abs(self.fps - 25) < 0.2:
            self.fps = 25.
        elif abs(self.fps - 30) < 0.2:
            self.fps = 30.

        # self.ori_start = start
        # self.ori_end = end
        self.ori_max_fps = max_fps or self.fps
        self.target_fps = min(self.ori_max_fps, self.fps)
        self.total_frame = None
        if not self.is_live and control_type == 'frame':
            self.start_frame = start
            self.start_time = start / self.fps * 1000
            self.end_frame = end if end is not None and end <= frame_count else frame_count
            self.end_time = self.end_frame / self.fps * 1000
            self.total_frame = self.end_frame - self.start_frame
        elif not self.is_live and control_type == 'time':
            self.start_frame = int(start / 1000 * self.fps)
            self.start_time = start
            self.end_frame = int(end / 1000 * self.fps) if end is not None else frame_count
            self.end_frame = min(self.end_frame, frame_count)
            self.end_time = self.end_frame / self.fps * 1000
            self.total_frame = self.end_frame - self.start_frame
        elif self.is_live and control_type == 'frame':
            # self.start_frame = start
            self.start_frame = 0
            self.start_time = 0
            self.end_frame = end
            if end is not None:
                self.end_time = end / self.fps * 1000
                self.total_frame = self.end_frame - self.start_frame
        elif self.is_live and control_type == 'time':
            self.start_frame = int(start / 1000 * self.fps)
            self.start_time = start
            self.start_frame = 0
            self.end_frame = None if end is None else int(end / 1000 * self.fps)
            if end is not None:
                self.end_time = end
                self.total_frame = self.end_frame - self.start_frame

        if tqdm_enable and self.total_frame is not None:
            from tqdm import tqdm
            self.tqdm_c = tqdm(total=self.__len__(), unit='frame', desc=f'{os.path.basename(video_path)}')
        else:
            self.tqdm_c = None

        self.out_writer = self.__make_video_writer__(out_path) if out_path is not None else None

        self.kwargs = kwargs

        self.stop_flag = False

        self.fram_iter = self.decode_iter()

        self.tqdm_count = 0

    @abstractmethod
    def decode_iter(self):
        pass

    def __make_video_writer__(self, output_video_path):
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        return cv2.VideoWriter(output_video_path, fourcc, self.fps, (self.width, self.height))

    def __enter__(self):
        if self.out_writer is not None:
            return self, self.out_writer
        else:
            return self, None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def stop(self):
        try:
            # 尝试发送停止信号，适用于协程或生成器
            self.stop_flag = True
            if self.out_writer is not None:
                self.out_writer.release()
        except Exception:
            pass

    def __next__(self):
        data = next(self.fram_iter)
        if self.tqdm_c is not None:
            # update_data = data['src_frame_idx'] - self.tqdm_count
            self.tqdm_c.update(1)
            # self.tqdm_count = data['src_frame_idx']
        return data

    def __iter__(self):
        return self

    def __len__(self):
        if self.total_frame:
            return math.ceil(self.total_frame / self.fps * self.target_fps)
        else:
            return 0


class SDKAStreamDecoder(StreamDecoder):
    def __init__(self, video_path, start=0, end=None, max_fps=500, out_path=None, logger=def_logger, tqdm_enable=True,
                 control_type='frame', is_live=None, frame_type='numpy_rgb', **kwargs):
        if kwargs.get('time_log_enable', False):
            self.time_log_delay_threshold = kwargs.get('time_log_delay_threshold', -1000)
            from aabd.base.log_setting import get_set_once_logger
            lm = kwargs.get('task_id', None) or f'dm{str(int(time.time()))}'
            self.tmp_logger = get_set_once_logger(f"dtl_{lm}", log_type="single_file", sub_dir='decoder_time_log',
                                                  propagate=True)
        else:
            self.tmp_logger = None
        super().__init__(video_path, start, end, max_fps, out_path, logger, tqdm_enable, control_type, is_live,
                         frame_type, **kwargs)

    def decode_iter(self):
        if self.stop_flag:
            return
        import xvdecoder
        sei_key = self.kwargs.get('sei_key', None)
        ret = xvdecoder.start_decoder(self.video_path, sei_key or '', 10, "xvdecoder.log")

        ori_frame_count = 0
        target_frame_count = 0
        seek_idx = 0
        try:
            while True:
                time_log1 = int(time.time() * 1000)
                if self.stop_flag:
                    break

                # 如果帧数够了停止
                if self.total_frame is not None and ori_frame_count >= self.total_frame:
                    break
                tensor = xvdecoder.decode_frame_to_tensor()
                if tensor is None or tensor.numel() == 0:
                    # 检查内部c++任务是否已经结束
                    is_finished = xvdecoder.check_finished()

                    if is_finished > 0:
                        print("is_finished ", is_finished)
                        break
                    else:
                        time.sleep(0.1)
                        continue
                if seek_idx < self.start_frame:
                    seek_idx += 1
                    continue
                sei_msg = xvdecoder.get_curr_sei_msg()
                try:
                    utc = 0 if len(sei_msg) <= 1 else int(json.loads(sei_msg)['utc'])
                except:
                    utc = 0
                next_time_point = target_frame_count / self.target_fps * 1000
                current_time_point = int(ori_frame_count / self.fps * 1000)
                if current_time_point >= next_time_point:
                    if self.frame_type == 'numpy_bgr':
                        image_data = tensor.cpu().numpy()[:, :, ::-1]
                    elif self.frame_type == 'numpy_rgb':
                        image_data = tensor.cpu().numpy()
                    elif self.frame_type == 'tensor':
                        image_data = tensor.float() / 255.0
                        image_data = image_data.permute(2, 0, 1)
                        # image_data = image_data[[2, 1, 0], :, :]
                    else:
                        image_data = None

                    data = {
                        'src_fps': self.fps,
                        'fps': self.target_fps,
                        'offset_idx': self.start_frame,
                        'offset_time': self.start_time,
                        'src_frame_idx': ori_frame_count,
                        'src_frame_time': round(current_time_point),
                        'target_frame_idx': target_frame_count,
                        'frame': image_data,
                        # 'target_frame_time': target_frame_count * 1000 / target_fps,
                        'sei': sei_msg,
                        'decoder_timestamp': int(time.time() * 1000),
                    }
                    time_log2 = int(time.time() * 1000)
                    yield data
                    time_log3 = int(time.time() * 1000)
                    if self.tmp_logger:
                        log_mark = "OKK" if time_log3 - utc < self.time_log_delay_threshold else "BAD"
                        self.tmp_logger.info(
                            f'SDTLOG|{log_mark}|sei:{sei_msg}|time1:{time_log1}|time2:{time_log2}|time3:{time_log3}|decoder:{time_log2 - time_log1}|model:{time_log3 - time_log2}|delay:{time_log3 - utc}')
                    target_frame_count += 1
                ori_frame_count += 1

        except:
            self.logger.exception("xvdecoder error")
        finally:
            xvdecoder.stop_decoder()


class SDKBStreamDecoder(StreamDecoder):
    def __init__(self, video_path, start=0, end=None, max_fps=500, out_path=None, logger=def_logger, tqdm_enable=True,
                 control_type='frame', is_live=None, frame_type='numpy_rgb', **kwargs):
        if kwargs.get('time_log_enable', False):
            self.time_log_delay_threshold = kwargs.get('time_log_delay_threshold', -1000)
            from aabd.base.log_setting import get_set_once_logger
            lm = kwargs.get('task_id', None) or f'dm{str(int(time.time()))}'
            self.tmp_logger = get_set_once_logger(f"dtl_{lm}", log_type="single_file", sub_dir='decoder_time_log',
                                                  propagate=True)
        else:
            self.tmp_logger = None
        super().__init__(video_path, start, end, max_fps, out_path, logger, tqdm_enable, control_type, is_live,
                         frame_type, **kwargs)

    def decode_iter(self):
        if self.stop_flag:
            return
        import xvdecoder
        sei_key = self.kwargs.get('sei_key', None)
        ret = xvdecoder.start_decoder(self.video_path, sei_key or '', 10, "xvdecoder.log")

        ori_frame_count = 0
        target_frame_count = 0
        seek_idx = 0
        change_frame_pointer_time = 0
        try:
            while True:
                time_log1 = int(time.time() * 1000)
                if self.stop_flag:
                    break

                # 如果帧数够了停止
                if self.total_frame is not None and ori_frame_count >= self.total_frame:
                    break
                tensor = xvdecoder.decode_frame_to_tensor()
                if tensor is None or tensor.numel() == 0:
                    # 检查内部c++任务是否已经结束
                    is_finished = xvdecoder.check_finished()

                    if is_finished > 0:
                        print("is_finished ", is_finished)
                        break
                    else:
                        time.sleep(0.1)
                        continue
                if seek_idx < self.start_frame:
                    seek_idx += 1
                    continue
                sei_msg = xvdecoder.get_curr_sei_msg()
                try:
                    utc = 0 if len(sei_msg) <= 1 else int(json.loads(sei_msg)['utc'])
                except:
                    utc = 0
                if utc > 0:
                    if ori_frame_count == 0:
                        change_frame_pointer_time = utc
                    current_time_point = utc
                    next_time_point = change_frame_pointer_time
                else:
                    next_time_point = target_frame_count / self.target_fps * 1000
                    current_time_point = int(ori_frame_count / self.fps * 1000)
                if current_time_point >= next_time_point:
                    if self.frame_type == 'numpy_bgr':
                        image_data = tensor.cpu().numpy()[:, :, ::-1]
                    elif self.frame_type == 'numpy_rgb':
                        image_data = tensor.cpu().numpy()
                    elif self.frame_type == 'tensor':
                        image_data = tensor.float() / 255.0
                        image_data = image_data.permute(2, 0, 1)
                        # image_data = image_data[[2, 1, 0], :, :]
                    else:
                        image_data = None

                    data = {
                        'src_fps': self.fps,
                        'fps': self.target_fps,
                        'offset_idx': self.start_frame,
                        'offset_time': self.start_time,
                        'src_frame_idx': ori_frame_count,
                        'src_frame_time': round(current_time_point),
                        'target_frame_idx': target_frame_count,
                        'frame': image_data,
                        # 'target_frame_time': target_frame_count * 1000 / target_fps,
                        'sei': sei_msg,
                        'decoder_timestamp': int(time.time() * 1000),
                    }
                    time_log2 = int(time.time() * 1000)
                    yield data
                    time_log3 = int(time.time() * 1000)
                    if self.tmp_logger:
                        log_mark = "OKK" if time_log3 - utc < self.time_log_delay_threshold else "BAD"
                        self.tmp_logger.info(
                            f'SDTLOG|{log_mark}|sei:{sei_msg}|time1:{time_log1}|time2:{time_log2}|time3:{time_log3}|decoder:{time_log2 - time_log1}|model:{time_log3 - time_log2}|delay:{time_log3 - utc}')

                    # 使用utc时间时,如果出现丢帧则将节拍追上
                    while True:
                        change_frame_pointer_time += 1000 / self.target_fps
                        if change_frame_pointer_time > current_time_point:
                            break
                    target_frame_count += 1
                ori_frame_count += 1

        except:
            self.logger.exception("xvdecoder error")
        finally:
            xvdecoder.stop_decoder()


class AVStreamDecoder(StreamDecoder):
    def __init__(self, video_path, start=0, end=None, max_fps=500, out_path=None, logger=def_logger, tqdm_enable=True,
                 control_type='frame', is_live=None, to_device='cpu', frame_type='numpy_rgb', gpu_decoder=False,
                 **kwargs):
        self.to_device = to_device
        self.gpu_decoder = gpu_decoder
        if kwargs.get('time_log_enable', False):
            self.time_log_delay_threshold = kwargs.get('time_log_delay_threshold', -1000)
            from aabd.base.log_setting import get_set_once_logger
            lm = kwargs.get('task_id', None) or f'dm{str(int(time.time()))}'
            self.tmp_logger = get_set_once_logger(f"dtl_{lm}", log_type="single_file", sub_dir='decoder_time_log',
                                                  propagate=True)
        else:
            self.tmp_logger = None
        super().__init__(video_path, start, end, max_fps, out_path, logger, tqdm_enable, control_type, is_live,
                         frame_type, **kwargs)

    def yuv420p_to_rgb_gpu(self, y, u, v):
        y = torch.tensor(y, dtype=torch.float32, device=self.to_device)
        u = torch.tensor(u, dtype=torch.float32, device=self.to_device)
        v = torch.tensor(v, dtype=torch.float32, device=self.to_device)

        # 上采样 U 和 V 到 Y 的分辨率
        u_upsampled = u.repeat_interleave(2, dim=0).repeat_interleave(2, dim=1)
        v_upsampled = v.repeat_interleave(2, dim=0).repeat_interleave(2, dim=1)

        # YUV 转 RGB 公式（BT.601）
        r = y + 1.402 * (v_upsampled - 128)
        g = y - 0.34414 * (u_upsampled - 128) - 0.71414 * (v_upsampled - 128)
        b = y + 1.772 * (u_upsampled - 128)

        # 合并通道并裁剪到 [0, 255]
        rgb = torch.stack([r, g, b], dim=0).clamp(0, 255)

        # 归一化到 [0, 1]
        rgb_normalized = rgb / 255.0

        return rgb_normalized  # 返回 float32 类型，范围 [0, 1]

    def decode_iter(self):
        if self.stop_flag:
            return
        import av

        if self.kwargs.get('ffmpeg_path', None):
            ffmpeg_path = self.kwargs.get('ffmpeg_path', None)

            # if 'LD_LIBRARY_PATH' in os.environ:
            #     os.environ['LD_LIBRARY_PATH'] = f"{ffmpeg_path}/lib:" + os.environ['LD_LIBRARY_PATH']
            # else:
            #     os.environ['LD_LIBRARY_PATH'] = f"{ffmpeg_path}/lib"
            # if 'PATH' in os.environ:
            #     os.environ['PATH'] = f"{ffmpeg_path}/bin:" + os.environ['PATH']
            # else:
            #     os.environ['PATH'] = f"{ffmpeg_path}/bin"
            try:
                av.utils.ffmpeg_path = ffmpeg_path
            except:
                self.logger.exception('ffmpeg path set error')

        sei_key = self.kwargs.get('sei_key', None)

        container = None
        if self.gpu_decoder:
            try:
                from av.codec.hwaccel import HWAccel, hwdevices_available
                if 'cuda' in hwdevices_available():
                    hwaccel = HWAccel(device_type='cuda', allow_software_fallback=False)
                    container = av.open(self.video_path, hwaccel=hwaccel, timeout=5)
            except:
                self.logger.exception('gpu ffmpeg error')

        if container is None:
            container = av.open(self.video_path, timeout=5)
        if self.stop_flag:
            return
        with container:
            try:
                is_hwaccel = container.streams.video[0].codec_context.is_hwaccel
            except:
                is_hwaccel = False
            stream = next(s for s in container.streams if s.type == 'video')
            total_frames = int(stream.frames)
            # fps = float(stream.average_rate)
            time_base = stream.time_base
            color_format = stream.format.name
            self.logger.info(
                f'video info --> video:{self.video_path}, color_format:{color_format}, '
                f'total_frames:{total_frames}, fps:{self.fps}, is_hwaccel:{is_hwaccel}')

            if self.start_time is not None and self.start_time > 0:
                container.seek(
                    int(self.start_time / 1000 / time_base),
                    # any_frame=True,
                    # backward=False,
                    stream=stream
                )

            target_fps = min(self.ori_max_fps, self.fps)

            if self.frame_type == "tensor":
                from torchvision import transforms
                to_tensor = transforms.ToTensor()

            # 需要seek
            seek_tag = self.start_time is not None and self.start_time > 0

            ori_frame_count = 0
            target_frame_count = 0
            for frame in container.decode(stream):
                time_log1 = int(time.time() * 1000)
                # 遇到停止标识停止
                if self.stop_flag:
                    break

                # 由于seek只是到关键帧需要继续到指定位置
                if seek_tag and float(frame.time * 1000) < self.start_time:
                    continue
                seek_tag = False

                # 如果帧数够了停止
                if self.total_frame is not None and ori_frame_count >= self.total_frame:
                    break
                next_time_point = round(target_frame_count / self.target_fps * 1000)
                current_time_point = round(ori_frame_count / self.fps * 1000)

                if current_time_point >= next_time_point:
                    sei_message_str = None
                    if sei_key is not None:
                        try:
                            for sd in frame.side_data:
                                sd_str = bytes(sd).decode('utf-8')
                                if sd_str.startswith(sei_key):
                                    sei_message_str = sd_str[len(sei_key):]
                                    break
                        except:
                            self.logger.exception('解析sei信息错误')
                    try:
                        utc = 0 if len(sei_message_str) <= 1 else int(json.loads(sei_message_str)['utc'])
                    except:
                        utc = 0
                    if frame.format.name == 'nv12' and self.gpu_decoder and self.frame_type == 'tensor':
                        yuv_data = frame.reformat(format='yuv420p')
                        y_plane = yuv_data.planes[0]
                        y_plane_n = numpy.frombuffer(y_plane, dtype=numpy.uint8).reshape(
                            (y_plane.height, y_plane.width))
                        u_plane = yuv_data.planes[1]
                        u_plane_n = numpy.frombuffer(u_plane, dtype=numpy.uint8).reshape(
                            (u_plane.height, u_plane.width))
                        v_plane = yuv_data.planes[2]
                        v_plane_n = numpy.frombuffer(v_plane, dtype=numpy.uint8).reshape(
                            (v_plane.height, v_plane.width))

                        final_frame = self.yuv420p_to_rgb_gpu(y_plane_n, u_plane_n, v_plane_n)
                    else:
                        if self.frame_type == 'pillow':
                            final_frame = frame.to_image()
                        elif self.frame_type == 'numpy_rgb':
                            final_frame = frame.to_ndarray(format='rgb24')
                        elif self.frame_type == 'numpy_bgr':
                            final_frame = frame.to_ndarray(format='bgr24')
                        elif self.frame_type == 'tensor':
                            if self.to_device.startswith('cuda') and frame.format.name == 'yuv420p':
                                yuv_data = frame.reformat(format='yuv420p')
                                y_plane = yuv_data.planes[0]
                                y_plane_n = numpy.frombuffer(y_plane, dtype=numpy.uint8).reshape(
                                    (y_plane.height, y_plane.width))
                                u_plane = yuv_data.planes[1]
                                u_plane_n = numpy.frombuffer(u_plane, dtype=numpy.uint8).reshape(
                                    (u_plane.height, u_plane.width))
                                v_plane = yuv_data.planes[2]
                                v_plane_n = numpy.frombuffer(v_plane, dtype=numpy.uint8).reshape(
                                    (v_plane.height, v_plane.width))

                                final_frame = self.yuv420p_to_rgb_gpu(y_plane_n, u_plane_n, v_plane_n)
                            else:
                                final_frame = to_tensor(frame.to_ndarray(format='rgb24'))
                    data = {
                        'src_fps': self.fps,
                        'fps': target_fps,
                        'offset_idx': self.start_frame,
                        'offset_time': self.start_time,
                        'src_frame_idx': ori_frame_count,
                        'src_frame_time': round(current_time_point),
                        'target_frame_idx': target_frame_count,
                        'frame': final_frame,
                        # 'target_frame_time': target_frame_count * 1000 / target_fps,
                        'sei': sei_message_str,
                        'decoder_timestamp': int(time.time() * 1000),
                        'pts': frame.time,
                    }
                    time_log2 = int(time.time() * 1000)
                    yield data
                    time_log3 = int(time.time() * 1000)
                    if self.tmp_logger:
                        log_mark = "OKK" if time_log3 - utc < self.time_log_delay_threshold else "BAD"
                        self.tmp_logger.info(
                            f'SDTLOG|{log_mark}|sei:{sei_message_str}|time1:{time_log1}|time2:{time_log2}|time3:{time_log3}|decoder:{time_log2 - time_log1}|model:{time_log3 - time_log2}|delay:{time_log3 - utc}')
                    target_frame_count += 1
                ori_frame_count += 1


class CVStreamDecoder(StreamDecoder):
    def __init__(self, video_path, start=0, end=None, max_fps=500, out_path=None, logger=def_logger, tqdm_enable=True,
                 control_type='frame', is_live=None, to_device='cpu', frame_type='numpy_rgb', **kwargs):
        self.to_device = to_device
        super().__init__(video_path, start, end, max_fps, out_path, logger, tqdm_enable, control_type, is_live,
                         frame_type, **kwargs)

    def decode_iter(self):
        from PIL import Image
        if self.stop_flag:
            return

        # 使用 OpenCV 的 VideoCapture
        cap = cv2.VideoCapture(self.video_path)
        try:
            if not cap.isOpened():
                self.logger.error("无法打开视频文件")
                return

            self.logger.info(
                f'video info --> video:{self.video_path}, total_frames:{self.total_frame}, fps:{self.fps}, is_hwaccel:False'
            )

            # 设置起始时间跳转
            if self.start_time is not None and self.start_time > 0:
                cap.set(cv2.CAP_PROP_POS_MSEC, self.start_time)

            ori_frame_count = 0
            target_frame_count = 0

            # 转换为 tensor 的 transform
            if self.frame_type == "tensor":
                from torchvision import transforms
                to_tensor = transforms.ToTensor()
            else:
                pass  # 其他格式处理

            # 逐帧读取
            while True:
                # 遇到停止标识停止
                if self.stop_flag:
                    break

                # 如果帧数够了停止
                if self.total_frame is not None and ori_frame_count >= self.total_frame:
                    break

                ret, frame_bgr = cap.read()
                if not ret:
                    break

                next_time_point = round(target_frame_count / self.target_fps * 1000)
                current_time_point = round(ori_frame_count / self.fps * 1000)

                if current_time_point >= next_time_point:
                    sei_message_str = None  # OpenCV 不支持提取 SEI 消息

                    # 处理帧格式转换
                    if self.frame_type == 'pillow':
                        final_frame = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
                    elif self.frame_type == 'numpy_rgb':
                        final_frame = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                    elif self.frame_type == 'numpy_bgr':
                        final_frame = frame_bgr
                    elif self.frame_type == 'tensor':
                        # OpenCV 帧为 BGR HWC，转换为 RGB CHW
                        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
                        final_frame = to_tensor(frame_rgb).to(self.to_device)
                    else:
                        final_frame = None  # 默认返回 numpy_bgr

                    # 构造返回数据字典
                    data = {
                        'src_fps': self.fps,
                        'fps': self.target_fps,
                        'offset_idx': self.start_frame,
                        'offset_time': self.start_time,
                        'src_frame_idx': ori_frame_count,
                        'src_frame_time': round(current_time_point),
                        'target_frame_idx': target_frame_count,
                        'frame': final_frame,
                        'sei': sei_message_str,
                        'decoder_timestamp': int(time.time() * 1000),
                    }
                    yield data

                    target_frame_count += 1
                ori_frame_count += 1
        finally:
            cap.release()  # 清理资源


class MockStreamDecoder(StreamDecoder):
    def __init__(self, video_path, start=0, end=None, max_fps=500, out_path=None, logger=def_logger, tqdm_enable=True,
                 control_type='frame', is_live=None, to_device='cpu', frame_type='numpy_rgb', **kwargs):
        self.to_device = to_device
        super().__init__(video_path, start, end, max_fps, out_path, logger, tqdm_enable, control_type, is_live,
                         frame_type, **kwargs)

    def decode_iter(self):
        # ori_frame_count = 0
        target_frame_count = 0
        for ori_frame_count in range(self.total_frame):
            # 遇到停止标识停止
            if self.stop_flag:
                break
            # 如果帧数够了停止
            if self.total_frame is not None and ori_frame_count >= self.total_frame:
                break
            next_time_point = round(target_frame_count / self.target_fps * 1000)
            current_time_point = round(ori_frame_count / self.fps * 1000)
            if current_time_point >= next_time_point:
                data = {
                    'weight': self.width,
                    'height': self.height,
                    'src_fps': self.fps,
                    'fps': self.target_fps,
                    'offset_idx': self.start_frame,
                    'offset_time': self.start_time,
                    'src_frame_idx': ori_frame_count,
                    'src_frame_time': round(ori_frame_count / self.target_fps * 1000),
                    'target_frame_idx': target_frame_count,
                    'frame': None,
                    'sei': json.dumps({'utc': round(ori_frame_count / self.target_fps * 1000)}),
                }
                yield data
                target_frame_count += 1


if __name__ == '__main__':
    from aabd.base.log_setting import get_set_once_logger
    from aabd.base.path_util import to_absolute_path_str
    import os

    os.environ['PROJECT_ROOT'] = os.path.abspath("../")
    logger = get_set_once_logger(log_type=['console'])
    with CVStreamDecoder(to_absolute_path_str('files/111.mp4'), start=1000, end=3000, max_fps=30, logger=logger,
                         frame_type="numpy_bgr", control_type='time') as (
            decoder,
            _):
        for frame in decoder:
            cv2.imwrite(f'images/{frame["src_frame_idx"]}.png', frame['frame'])
            frame['frame'] = None
            logger.info(frame)
