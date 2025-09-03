from mcp.server.fastmcp import FastMCP, Context
import ffmpeg
import os  # For checking file existence if needed, though ffmpeg handles it
import re  # For parsing silencedetect output
import tempfile  # For add_b_roll
import shutil  # For cleaning up temporary directories
import subprocess  # For running external commands
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# 配置日志输出到stderr，避免干扰MCP通信
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 防止 basicConfig 被早期初始化抵消

# 使用用户临时目录存放日志文件
log_dir = Path(tempfile.gettempdir()) / "video-format-converter-mcp"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "debug.log"

file_handler = RotatingFileHandler(str(log_file), maxBytes=5_000_000, backupCount=3, encoding="utf-8")
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.propagate = False

FFMPEG_PATH_DIR = os.environ.get('FFMPEG_PATH')


def _resolve_binary(explicit_bin: str | None, path_dir: str | None, base_name: str) -> str:
    if explicit_bin:
        return explicit_bin
    if path_dir:
        candidate_names = [base_name]
        if os.name == 'nt':  # Windows prefers .exe
            candidate_names = [f"{base_name}.exe", base_name]
        for name in candidate_names:
            candidate_path = os.path.join(path_dir, name)
            if os.path.exists(candidate_path):
                return candidate_path
    which_path = shutil.which(base_name)
    if which_path:
        return which_path
    # Fallback to base name; may still work if OS can resolve via PATHEXT
    return base_name


FFMPEG_BIN = _resolve_binary(os.environ.get('FFMPEG_BIN'), FFMPEG_PATH_DIR, 'ffmpeg')
FFPROBE_BIN = _resolve_binary(os.environ.get('FFPROBE_BIN'), FFMPEG_PATH_DIR, 'ffprobe')
# Configure ffmpeg-python to use the resolved binaries
os.environ['FFMPEG_BINARY'] = FFMPEG_BIN
os.environ['FFPROBE_BINARY'] = FFPROBE_BIN


# --- ffmpeg/ffprobe helpers that always use resolved binaries ---
def _ffmpeg_run(stream_spec, **kwargs):
    """Run ffmpeg with an explicit binary path to avoid env propagation issues."""
    return ffmpeg.run(stream_spec, cmd=FFMPEG_BIN, **kwargs)


def _ffmpeg_run_async(stream_spec, **kwargs):
    """Run ffmpeg asynchronously with explicit binary path."""
    return ffmpeg.run_async(stream_spec, cmd=FFMPEG_BIN, **kwargs)


def _ffprobe_probe(path: str, **kwargs):
    """Probe media with explicit ffprobe binary."""
    return ffmpeg.probe(path, cmd=FFPROBE_BIN, **kwargs)


def _parse_time_to_seconds(time_input) -> float:
    """Parse time input to seconds (float)."""
    if isinstance(time_input, (int, float)):
        return float(time_input)
    if isinstance(time_input, str):
        # HH:MM:SS[.mmm] format
        if ':' in time_input:
            parts = time_input.split(':')
            if len(parts) == 3:
                h, m, s = parts
                return float(h) * 3600 + float(m) * 60 + float(s)
            elif len(parts) == 2:
                m, s = parts
                return float(m) * 60 + float(s)
        else:
            return float(time_input)
    raise ValueError(f"Invalid time format: {time_input}")


def _prepare_path(input_path: str, output_path: str) -> None:
    if not os.path.exists(input_path):
        raise RuntimeError(f"Error: Input file not found at {input_path}")
    try:
        parent_dir = os.path.dirname(output_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
    except Exception as e:
        raise RuntimeError(f"Error creating output directory for {output_path}: {str(e)}")
    if os.path.exists(output_path):
        raise RuntimeError(
            f"Error: Output file already exists at {output_path}. Please choose a different path or delete the existing file.")


# Create an MCP server instance
mcp = FastMCP("VideoAudioServer")


@mcp.tool()
def convert_video_properties(input_video_path: str, output_video_path: str, target_format: str,
                             resolution: str = None, video_codec: str = None, video_bitrate: str = None,
                             frame_rate: int = None, audio_codec: str = None, audio_bitrate: str = None,
                             audio_sample_rate: int = None, audio_channels: int = None) -> str:
    """视频容器转换与属性重设（分辨率/帧率/视频编码/视频码率/音频编码/音频码率/采样率/声道）。

    Args:
        input_video_path: 输入视频文件路径。
        output_video_path: 输出视频文件路径（包含文件名和目标后缀）。
        target_format: 目标封装格式（如 'mp4'|'mov'|'mkv'|'webm'|'m4v'|'avi' 等）。
        resolution: 目标分辨率；支持 '宽x高'（如 '1920x1080'），或仅传高度（如 '720'，宽度按比例自动为 -2）。传 'preserve' 或 None 时保持原分辨率。
        video_codec: 视频编码器（如 'libx264'|'libx265'|'vp9'|'libvpx-vp9'|'wmv2' 等）。不传时由 ffmpeg 根据容器默认或继承原视频决定。
        video_bitrate: 视频码率（如 '2500k'、'1M'）。不传则由编码器/预设决定。
        frame_rate: 目标帧率（整数，如 24/30/60）。不传保持原始帧率。
        audio_codec: 音频编码器（如 'aac'|'libopus'|'libvorbis'|'mp3'|'wmav2'）。不传则由容器默认或继承原音频决定。
        audio_bitrate: 音频码率（如 '128k'、'192k'）。不传由编码器/预设决定。
        audio_sample_rate: 音频采样率（Hz，如 44100/48000）。不传保持原始采样率。
        audio_channels: 音频声道数（1=单声道，2=立体声）。不传保持原始声道数。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(input_video_path, output_video_path)
    try:
        # 后缀与目标容器不一致时给出提示（不强制修改）
        out_ext = os.path.splitext(output_video_path)[1].lstrip('.').lower() if os.path.splitext(output_video_path)[
            1] else ''
        if out_ext and out_ext != target_format.lower():
            logger.warning(
                f"Output file extension '.{out_ext}' does not match target_format '{target_format}'. This may be confusing.")

        # 分辨率参数校验
        if resolution and resolution.lower() != 'preserve':
            if 'x' in resolution:
                if not re.match(r'^\d{2,5}x\d{2,5}$', resolution):
                    raise RuntimeError(f"Error: Invalid resolution '{resolution}'. Expected like '1920x1080'.")
            else:
                if not re.match(r'^\d{2,5}$', str(resolution)):
                    raise RuntimeError(f"Error: Invalid resolution '{resolution}'. Expected height like '720'.")

        # 纯换容器（remux）快速路径：未指定任何转码相关参数且未改分辨率/帧率
        pure_remux = (
                (not resolution or str(resolution).lower() == 'preserve') and
                video_codec is None and video_bitrate is None and frame_rate is None and
                audio_codec is None and audio_bitrate is None and audio_sample_rate is None and audio_channels is None
        )

        stream = ffmpeg.input(input_video_path)

        if pure_remux:
            try:
                output_stream = stream.output(output_video_path, format=target_format, c='copy')
                _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)
                return f"Remux completed: copied streams into container '{target_format}' → {output_video_path}"
            except ffmpeg.Error as e_copy:
                # 回退：尝试按容器默认策略重编码
                logger.info(
                    f"Remux failed, falling back to re-encode: {e_copy.stderr.decode('utf8') if e_copy.stderr else str(e_copy)}")

        # 构建输出参数（带容器缺省编解码策略）
        def _defaults_for_container(fmt: str) -> tuple[str | None, str | None, dict]:
            fmt_l = (fmt or '').lower()
            extra: dict = {}
            v, a = None, None
            if fmt_l in {'mp4', 'm4v'}:
                v, a = 'libx264', 'aac'
                extra.update({'pix_fmt': 'yuv420p', 'movflags': '+faststart'})
            elif fmt_l in {'mov'}:
                v, a = 'libx264', 'aac'
                extra.update({'pix_fmt': 'yuv420p'})
            elif fmt_l in {'webm'}:
                v, a = 'libvpx-vp9', 'libopus'
                extra.update({'pix_fmt': 'yuv420p'})
            elif fmt_l in {'mkv'}:
                # MKV 兼容面广，给出通用默认
                v, a = 'libx264', 'aac'
                extra.update({'pix_fmt': 'yuv420p'})
            elif fmt_l in {'avi'}:
                v, a = 'mpeg4', 'mp3'
            elif fmt_l in {'wmv'}:
                v, a = 'wmv2', 'wmav2'
            else:
                v, a = None, None
            return v, a, extra

        def_v, def_a, def_extra = _defaults_for_container(target_format)

        kwargs: dict = {}
        vf_filters = []

        # 分辨率处理
        if resolution and str(resolution).lower() != 'preserve':
            if 'x' in resolution:
                vf_filters.append(f"scale={resolution}")
            else:
                vf_filters.append(f"scale=-2:{resolution}")
        if vf_filters:
            kwargs['vf'] = ",".join(vf_filters)

        # 选择编码器：显式优先生效，否则按容器默认
        vcodec_to_use = video_codec or def_v
        acodec_to_use = audio_codec or def_a
        if vcodec_to_use:
            kwargs['vcodec'] = vcodec_to_use
        if acodec_to_use:
            kwargs['acodec'] = acodec_to_use

        # 常见播放兼容：H.264/H.265默认 yuv420p
        if vcodec_to_use and any(x in vcodec_to_use for x in ['libx264', 'libx265', 'h264', 'hevc']):
            kwargs.setdefault('pix_fmt', 'yuv420p')

        # 按容器附加参数（如 mp4 faststart）
        for k, v in def_extra.items():
            kwargs.setdefault(k, v)

        # 码率/帧率/音频参数
        if video_bitrate:
            kwargs['video_bitrate'] = video_bitrate
        if frame_rate:
            kwargs['r'] = frame_rate
        if audio_bitrate:
            kwargs['audio_bitrate'] = audio_bitrate
        if audio_sample_rate:
            kwargs['ar'] = audio_sample_rate
        if audio_channels:
            kwargs['ac'] = audio_channels

        kwargs['format'] = target_format

        output_stream = stream.output(output_video_path, **kwargs)
        _ffmpeg_run(output_stream, capture_stdout=True, capture_stderr=True)
        return f"Video converted successfully to {output_video_path} with format {target_format} and specified properties."
    except ffmpeg.Error as e:
        error_message = e.stderr.decode('utf8') if e.stderr else str(e)
        raise RuntimeError(f"Error converting video properties: {error_message}")
    except FileNotFoundError:
        raise RuntimeError(f"Error: Input video file not found at {input_video_path}")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")


# --- GIF Export ---
@mcp.tool()
def video_to_gif(
        video_path: str,
        output_gif_path: str,
        fps: int = 8,
        width: int | None = 480,
        height: int | None = None,
        keep_aspect: bool = True,
        start_time: str | float | None = None,
        duration: float | None = None,
        dither: str = "bayer",
        max_colors: int = 128,
        loop: int = 0,
        crop: dict | None = None,
        scale_flags: str = "lanczos",
        bayer_scale: int | None = 3
) -> str:
    """将视频片段高质量导出为 GIF（palettegen/paletteuse 两遍法）。

    Args:
        video_path: 输入视频路径。
        output_gif_path: 输出 GIF 路径（应以 .gif 结尾）。
        fps: GIF 帧率，建议 8~20 之间。
        width: 目标宽度（keep_aspect 为 True 时，height 需为空）。
        height: 目标高度（keep_aspect 为 True 时，width 需为空）。
        keep_aspect: 是否保持纵横比。
        start_time: 起始时间（秒或 'HH:MM:SS(.ms)'）。
        duration: 时长（秒）。
        dither: 调色算法，支持 'none'|'bayer'|'floyd_steinberg'|'sierra2_4a'|'burkes'。
        max_colors: 调色板颜色数，2~256。
        loop: 循环次数（0 为无限循环）。
        crop: 裁剪参数，如 {"x":0, "y":0, "w":320, "h":240}。
        scale_flags: 缩放插值算法，如 'lanczos'|'bicubic' 等。
        bayer_scale: bayer 调色算法的缩放因子（0~5）。

    Returns:
        A status message indicating success or failure.
    """
    _prepare_path(video_path, output_gif_path)
    try:
        if not output_gif_path.lower().endswith(".gif"):
            raise RuntimeError("Error: output_gif_path must end with .gif")
        if fps <= 0:
            raise RuntimeError("Error: fps must be positive")
        if not (2 <= int(max_colors) <= 256):
            raise RuntimeError("Error: max_colors must be in [2, 256]")
        if loop < 0:
            raise RuntimeError("Error: loop must be >= 0")

        valid_dither = {"none", "bayer", "floyd_steinberg", "sierra2_4a", "burkes"}
        if dither not in valid_dither:
            raise RuntimeError(f"Error: Unsupported dither '{dither}'. Supported: {', '.join(sorted(valid_dither))}")
        if dither == "bayer" and bayer_scale is not None and not (0 <= int(bayer_scale) <= 5):
            raise RuntimeError("Error: bayer_scale must be in [0, 5]")

        if keep_aspect and (width and height):
            raise RuntimeError("Error: When keep_aspect=True, provide only width or height, not both")

        # 输入裁剪参数校验
        crop_params = None
        if crop is not None:
            required_keys = {"x", "y", "w", "h"}
            if not isinstance(crop, dict) or not required_keys.issubset(crop.keys()):
                raise RuntimeError("Error: crop must be a dict with keys {'x','y','w','h'}")
            crop_params = {
                "x": int(crop["x"]),
                "y": int(crop["y"]),
                "w": int(crop["w"]),
                "h": int(crop["h"]),
            }

        # 解析时间
        ss_arg = None
        t_arg = None
        if start_time is not None:
            ss_arg = _parse_time_to_seconds(start_time)
        if duration is not None:
            if duration <= 0:
                raise RuntimeError("Error: duration must be positive")
            t_arg = float(duration)

        # 构建公共滤镜链（两遍都要）
        def apply_common_filters(stream):
            filtered = stream
            filtered = filtered.filter("fps", fps)
            if crop_params:
                filtered = filtered.filter("crop", w=crop_params["w"], h=crop_params["h"], x=crop_params["x"],
                                           y=crop_params["y"])
            if width and height and not keep_aspect:
                filtered = filtered.filter("scale", width, height, flags=scale_flags)
            elif width:
                filtered = filtered.filter("scale", width, -1, flags=scale_flags)
            elif height:
                filtered = filtered.filter("scale", -1, height, flags=scale_flags)
            # GIF 建议 RGB24
            filtered = filtered.filter("format", "rgb24")
            return filtered

        # 临时调色板文件
        temp_dir = tempfile.mkdtemp()
        palette_path = os.path.join(temp_dir, "palette.png")

        try:
            # 第一遍：生成调色板
            in1 = ffmpeg.input(video_path, ss=ss_arg, t=t_arg) if (
                        ss_arg is not None or t_arg is not None) else ffmpeg.input(video_path)
            v1 = apply_common_filters(in1.video).filter("palettegen", stats_mode="single", max_colors=max_colors)
            # 在部分 ffmpeg 版本中，image2 复用器会因多次写入同名文件报错；加 update=1 允许覆盖同名单文件
            _ffmpeg_run(ffmpeg.output(v1, palette_path, update=1), capture_stdout=True, capture_stderr=True)

            # 第二遍：应用调色板生成 GIF
            in2 = ffmpeg.input(video_path, ss=ss_arg, t=t_arg) if (
                        ss_arg is not None or t_arg is not None) else ffmpeg.input(video_path)
            v2 = apply_common_filters(in2.video)
            pal = ffmpeg.input(palette_path)
            if dither == "bayer" and bayer_scale is not None:
                gif_v = ffmpeg.filter([v2, pal], "paletteuse", dither=dither, bayer_scale=bayer_scale)
            else:
                gif_v = ffmpeg.filter([v2, pal], "paletteuse", dither=dither)
            _ffmpeg_run(
                ffmpeg.output(gif_v, output_gif_path, format="gif", loop=loop),
                capture_stdout=True,
                capture_stderr=True,
            )

            return f"GIF created successfully at {output_gif_path}"
        finally:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
    except ffmpeg.Error as e:
        error_message = e.stderr.decode("utf8") if e.stderr else str(e)
        raise RuntimeError(f"Error converting video to GIF: {error_message}")
    except FileNotFoundError:
        raise RuntimeError("Error: Required file not found (input video or palette)")
    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred in video_to_gif: {str(e)}")


def main():
    """Main entry point for the MCP server."""
    mcp.run()


# Main execution block to run the server
if __name__ == "__main__":
    main() 