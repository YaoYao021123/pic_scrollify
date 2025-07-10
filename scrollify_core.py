#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrollify - 长图转滚动GIF工具核心模块
将长图转换为可定制的滚动GIF或MP4动画
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ScrollifyConfig:
    """Scrollify配置类"""
    # 输入
    source_image: str
    
    # 输出窗口
    aspect_ratio: str = "16:9"  # "16:9", "4:3", "1:1", "source", "custom"
    output_width: int = 800
    output_height: Optional[int] = None  # 如果None，根据比例计算
    
    # 滚动动画
    scroll_speed: int = 8  # 像素/帧
    framerate: int = 24  # FPS
    scroll_mode: str = "down"  # "down", "down-up", "down-once"
    pause_duration: float = 2.0  # 秒
    
    # 输出
    output_format: str = "GIF"  # "GIF", "MP4"
    output_path: str = "output_scroll.gif"
    
    # 高级选项
    quality_factor: float = 0.8  # 质量因子 (0.1-1.0)
    add_watermark: bool = False
    watermark_text: str = "Created with Scrollify"


class ScrollifyGenerator:
    """Scrollify核心生成器"""
    
    def __init__(self, config: ScrollifyConfig):
        self.config = config
        self.source_image = None
        self.scaled_image = None
        self.window_height = None
        self.frames = []
        
    def run(self) -> bool:
        """运行完整的转换流程"""
        try:
            print(f"🎬 开始处理: {self.config.source_image}")
            
            self.load_image()
            self.calculate_dimensions()
            self.preprocess_image()
            self.generate_frames()
            self.save_output()
            
            print(f"✅ 转换完成: {self.config.output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 转换失败: {e}")
            return False
    
    def load_image(self):
        """加载源图片"""
        if not os.path.exists(self.config.source_image):
            raise FileNotFoundError(f"图片文件不存在: {self.config.source_image}")
        
        self.source_image = Image.open(self.config.source_image)
        if self.source_image.mode != 'RGB':
            self.source_image = self.source_image.convert('RGB')
        
        print(f"📷 源图片尺寸: {self.source_image.size}")
    
    def calculate_dimensions(self):
        """计算输出尺寸"""
        # 计算窗口高度
        if self.config.aspect_ratio == "source":
            # 使用源图片比例
            ratio = self.source_image.height / self.source_image.width
            self.window_height = int(self.config.output_width * ratio)
        elif self.config.aspect_ratio == "custom" and self.config.output_height:
            # 使用自定义高度
            self.window_height = self.config.output_height
        else:
            # 解析比例字符串如 "16:9"
            try:
                w_ratio, h_ratio = map(int, self.config.aspect_ratio.split(':'))
                self.window_height = int(self.config.output_width * h_ratio / w_ratio)
            except:
                # 默认使用16:9
                self.window_height = int(self.config.output_width * 9 / 16)
        
        print(f"📐 输出窗口尺寸: {self.config.output_width} x {self.window_height}")
    
    def preprocess_image(self):
        """预处理图片"""
        # 计算缩放比例
        scale_ratio = self.config.output_width / self.source_image.width
        
        # 应用质量因子
        final_scale = scale_ratio * self.config.quality_factor
        
        # 缩放图片
        new_width = int(self.source_image.width * final_scale)
        new_height = int(self.source_image.height * final_scale)
        
        self.scaled_image = self.source_image.resize(
            (new_width, new_height), 
            Image.Resampling.LANCZOS
        )
        
        # 调整窗口尺寸以匹配缩放后的宽度
        if new_width != self.config.output_width:
            scale_window = new_width / self.config.output_width
            self.window_height = int(self.window_height * scale_window)
            self.config.output_width = new_width
        
        print(f"🔧 缩放后尺寸: {self.scaled_image.size}")
        print(f"📐 最终窗口尺寸: {self.config.output_width} x {self.window_height}")
    
    def generate_frames(self):
        """生成动画帧"""
        print("🎞️  生成动画帧...")
        
        self.frames = []
        
        # 检查是否需要滚动
        if self.scaled_image.height <= self.window_height:
            print("⚠️  图片高度小于窗口高度，生成静态展示")
            frame = self._crop_safe(0, self.window_height)
            pause_frames = int(self.config.pause_duration * self.config.framerate)
            self.frames = [frame] * max(pause_frames, 30)
            return
        
        # 计算暂停帧数
        pause_frames = int(self.config.pause_duration * self.config.framerate)
        
        # 添加顶部暂停帧
        top_frame = self._crop_safe(0, self.window_height)
        self.frames.extend([top_frame] * pause_frames)
        
        # 生成向下滚动帧
        max_y = self.scaled_image.height - self.window_height
        y_position = 0
        
        while y_position < max_y:
            y_position = min(y_position + self.config.scroll_speed, max_y)
            frame = self._crop_safe(y_position, self.window_height)
            self.frames.append(frame)
        
        # 添加底部暂停帧
        bottom_frame = self._crop_safe(max_y, self.window_height)
        self.frames.extend([bottom_frame] * pause_frames)
        
        # 根据滚动模式添加返回帧
        if self.config.scroll_mode == "down-up":
            # 向上滚动回到顶部
            while y_position > 0:
                y_position = max(y_position - self.config.scroll_speed, 0)
                frame = self._crop_safe(y_position, self.window_height)
                self.frames.append(frame)
        elif self.config.scroll_mode == "down-once":
            # 不循环，移除最后的暂停帧
            self.frames = self.frames[:-pause_frames]
        
        # 添加水印
        if self.config.add_watermark:
            self._add_watermark_to_frames()
        
        print(f"🎬 生成了 {len(self.frames)} 帧")
    
    def _crop_safe(self, y_start: int, height: int) -> Image.Image:
        """安全裁剪图片，确保不超出边界"""
        y_end = min(y_start + height, self.scaled_image.height)
        actual_height = y_end - y_start
        
        # 裁剪图片
        cropped = self.scaled_image.crop((
            0, y_start, 
            self.config.output_width, y_end
        ))
        
        # 如果高度不足，用白色填充底部
        if actual_height < height:
            padded = Image.new('RGB', (self.config.output_width, height), (255, 255, 255))
            padded.paste(cropped, (0, 0))
            return padded
        
        return cropped
    
    def _add_watermark_to_frames(self):
        """为所有帧添加水印"""
        print("💧 添加水印...")
        
        for i, frame in enumerate(self.frames):
            # 创建半透明水印
            watermark = Image.new('RGBA', frame.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(watermark)
            
            # 尝试使用系统字体
            try:
                font_size = max(12, self.config.output_width // 50)
                # 这里可以扩展为从字体文件加载
                font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # 计算文字位置（右下角）
            text = self.config.watermark_text
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = frame.width - text_width - 10
            y = frame.height - text_height - 10
            
            # 绘制半透明背景
            padding = 5
            draw.rectangle([
                x - padding, y - padding,
                x + text_width + padding, y + text_height + padding
            ], fill=(0, 0, 0, 128))
            
            # 绘制文字
            draw.text((x, y), text, fill=(255, 255, 255, 200), font=font)
            
            # 合并水印到帧
            frame_rgba = frame.convert('RGBA')
            frame_with_watermark = Image.alpha_composite(frame_rgba, watermark)
            self.frames[i] = frame_with_watermark.convert('RGB')
    
    def save_output(self):
        """保存输出文件"""
        print(f"💾 保存为 {self.config.output_format} 格式...")
        
        if not self.frames:
            raise ValueError("没有生成任何帧")
        
        # 计算每帧持续时间（毫秒）
        duration_ms = int(1000 / self.config.framerate)
        
        if self.config.output_format.upper() == "GIF":
            self._save_as_gif(duration_ms)
        elif self.config.output_format.upper() == "MP4":
            self._save_as_mp4()
        else:
            raise ValueError(f"不支持的输出格式: {self.config.output_format}")
        
        # 显示文件大小
        file_size = os.path.getsize(self.config.output_path) / (1024 * 1024)
        print(f"📁 文件大小: {file_size:.2f} MB")
    
    def _save_as_gif(self, duration_ms: int):
        """保存为GIF格式"""
        loop_count = 0 if self.config.scroll_mode != "down-once" else 1
        
        self.frames[0].save(
            self.config.output_path,
            save_all=True,
            append_images=self.frames[1:],
            duration=duration_ms,
            loop=loop_count,
            optimize=True,
            disposal=2
        )
    
    def _save_as_mp4(self):
        """保存为MP4格式（需要安装moviepy）"""
        try:
            from moviepy.editor import ImageSequenceClip
            
            # 将PIL图片转换为numpy数组
            import numpy as np
            
            frames_array = []
            for frame in self.frames:
                frames_array.append(np.array(frame))
            
            # 创建视频剪辑
            clip = ImageSequenceClip(frames_array, fps=self.config.framerate)
            
            # 如果是循环模式，可以设置循环
            if self.config.scroll_mode != "down-once":
                clip = clip.loop()
            
            # 保存为MP4
            clip.write_videofile(
                self.config.output_path,
                codec='libx264',
                audio=False,
                verbose=False,
                logger=None
            )
            
        except ImportError:
            print("⚠️  MP4格式需要安装moviepy: pip install moviepy")
            print("🔄 自动切换为GIF格式...")
            
            # 修改输出路径为GIF
            base_name = os.path.splitext(self.config.output_path)[0]
            self.config.output_path = base_name + ".gif"
            
            duration_ms = int(1000 / self.config.framerate)
            self._save_as_gif(duration_ms)


def parse_aspect_ratio(ratio_str: str) -> Tuple[int, int]:
    """解析比例字符串"""
    if ratio_str == "source":
        return None, None
    
    try:
        w, h = map(int, ratio_str.split(':'))
        return w, h
    except:
        return 16, 9  # 默认16:9


# 便捷函数
def create_scrolling_gif(
    image_path: str,
    output_path: str = None,
    aspect_ratio: str = "16:9",
    width: int = 800,
    scroll_speed: int = 8,
    framerate: int = 24,
    scroll_mode: str = "down",
    pause_duration: float = 2.0
) -> bool:
    """
    便捷函数：快速创建滚动GIF
    
    Args:
        image_path: 源图片路径
        output_path: 输出路径（如果None，自动生成）
        aspect_ratio: 比例 ("16:9", "4:3", "1:1", "source")
        width: 输出宽度
        scroll_speed: 滚动速度（像素/帧）
        framerate: 帧率
        scroll_mode: 滚动模式 ("down", "down-up", "down-once")
        pause_duration: 暂停时间（秒）
    
    Returns:
        bool: 是否成功
    """
    if output_path is None:
        base_name = os.path.splitext(image_path)[0]
        output_path = f"{base_name}_scroll.gif"
    
    config = ScrollifyConfig(
        source_image=image_path,
        output_path=output_path,
        aspect_ratio=aspect_ratio,
        output_width=width,
        scroll_speed=scroll_speed,
        framerate=framerate,
        scroll_mode=scroll_mode,
        pause_duration=pause_duration
    )
    
    generator = ScrollifyGenerator(config)
    return generator.run()


if __name__ == "__main__":
    # 简单测试
    test_config = ScrollifyConfig(
        source_image="test_image.jpg",
        output_path="test_output.gif",
        aspect_ratio="16:9",
        output_width=600,
        scroll_speed=10,
        framerate=24
    )
    
    generator = ScrollifyGenerator(test_config)
    generator.run() 