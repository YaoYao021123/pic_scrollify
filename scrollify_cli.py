#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrollify CLI - 命令行界面
使用示例: python scrollify_cli.py image.jpg --width 800 --ratio 16:9 --speed 10
"""

import argparse
import sys
import os
from pathlib import Path
from scrollify_core import ScrollifyConfig, ScrollifyGenerator, create_scrolling_gif


def main():
    parser = argparse.ArgumentParser(
        description="Scrollify - 将长图转换为滚动GIF/MP4动画",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基础用法
  python scrollify_cli.py image.jpg
  
  # 自定义参数
  python scrollify_cli.py image.jpg --width 1000 --ratio 16:9 --speed 12 --fps 30
  
  # 向下再向上滚动
  python scrollify_cli.py image.jpg --mode down-up --pause 3
  
  # 输出为MP4
  python scrollify_cli.py image.jpg --format MP4 --output video.mp4
  
  # 添加水印
  python scrollify_cli.py image.jpg --watermark --watermark-text "我的水印"
        """)
    
    # 必需参数
    parser.add_argument('image', help='输入图片路径')
    
    # 输出参数
    parser.add_argument('-o', '--output', 
                       help='输出文件路径（默认自动生成）')
    parser.add_argument('--format', choices=['GIF', 'MP4'], default='GIF',
                       help='输出格式 (默认: GIF)')
    
    # 尺寸参数
    parser.add_argument('-w', '--width', type=int, default=800,
                       help='输出宽度像素 (默认: 800)')
    parser.add_argument('-r', '--ratio', default='16:9',
                       help='宽高比 (16:9, 4:3, 1:1, source, 或 custom) (默认: 16:9)')
    parser.add_argument('--height', type=int,
                       help='自定义高度（仅当ratio=custom时使用）')
    
    # 动画参数
    parser.add_argument('-s', '--speed', type=int, default=8,
                       help='滚动速度 (像素/帧) (默认: 8)')
    parser.add_argument('--fps', type=int, default=24,
                       help='帧率 (默认: 24)')
    parser.add_argument('-m', '--mode', 
                       choices=['down', 'down-up', 'down-once'], 
                       default='down',
                       help='滚动模式 (默认: down)')
    parser.add_argument('-p', '--pause', type=float, default=2.0,
                       help='顶部/底部暂停时间(秒) (默认: 2.0)')
    
    # 质量参数
    parser.add_argument('-q', '--quality', type=float, default=0.8,
                       help='质量因子 (0.1-1.0) (默认: 0.8)')
    
    # 水印参数
    parser.add_argument('--watermark', action='store_true',
                       help='添加水印')
    parser.add_argument('--watermark-text', default='Created with Scrollify',
                       help='水印文字 (默认: "Created with Scrollify")')
    
    # 其他选项
    parser.add_argument('--preview', action='store_true',
                       help='只显示参数预览，不实际生成')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='详细输出')
    
    args = parser.parse_args()
    
    # 验证输入文件
    if not os.path.exists(args.image):
        print(f"❌ 错误: 文件不存在 '{args.image}'")
        sys.exit(1)
    
    # 生成输出路径
    if not args.output:
        input_path = Path(args.image)
        output_name = f"{input_path.stem}_scroll.{args.format.lower()}"
        args.output = str(input_path.parent / output_name)
    
    # 验证比例参数
    if args.ratio == 'custom' and not args.height:
        print("❌ 错误: 使用custom比例时必须指定--height参数")
        sys.exit(1)
    
    # 创建配置
    config = ScrollifyConfig(
        source_image=args.image,
        output_path=args.output,
        aspect_ratio=args.ratio,
        output_width=args.width,
        output_height=args.height,
        scroll_speed=args.speed,
        framerate=args.fps,
        scroll_mode=args.mode,
        pause_duration=args.pause,
        output_format=args.format,
        quality_factor=args.quality,
        add_watermark=args.watermark,
        watermark_text=args.watermark_text
    )
    
    # 预览模式
    if args.preview:
        print_preview(config)
        return
    
    # 执行转换
    print("🚀 Scrollify - 长图转滚动动画工具")
    print("=" * 50)
    
    generator = ScrollifyGenerator(config)
    success = generator.run()
    
    if success:
        print("=" * 50)
        print(f"✨ 完成！输出文件: {args.output}")
        
        # 显示文件信息
        file_size = os.path.getsize(args.output) / (1024 * 1024)
        print(f"📁 文件大小: {file_size:.2f} MB")
        
        # 如果是当前目录，提供相对路径
        if os.path.dirname(args.output) == os.getcwd():
            print(f"📂 当前目录: {os.path.basename(args.output)}")
    else:
        print("❌ 转换失败")
        sys.exit(1)


def print_preview(config: ScrollifyConfig):
    """打印参数预览"""
    print("📋 参数预览")
    print("=" * 50)
    print(f"输入文件: {config.source_image}")
    print(f"输出文件: {config.output_path}")
    print(f"输出格式: {config.output_format}")
    print()
    print(f"宽高比: {config.aspect_ratio}")
    print(f"输出宽度: {config.output_width}px")
    if config.output_height:
        print(f"输出高度: {config.output_height}px")
    print()
    print(f"滚动速度: {config.scroll_speed} 像素/帧")
    print(f"帧率: {config.framerate} FPS")
    print(f"滚动模式: {config.scroll_mode}")
    print(f"暂停时间: {config.pause_duration} 秒")
    print(f"质量因子: {config.quality_factor}")
    print()
    if config.add_watermark:
        print(f"水印: {config.watermark_text}")
    else:
        print("水印: 无")
    print("=" * 50)


def quick_convert():
    """快速转换函数，用于简单场景"""
    if len(sys.argv) < 2:
        print("用法: python scrollify_cli.py <图片文件>")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        return
    
    success = create_scrolling_gif(image_path)
    if success:
        output_path = os.path.splitext(image_path)[0] + "_scroll.gif"
        print(f"✅ 转换完成: {output_path}")
    else:
        print("❌ 转换失败")


if __name__ == "__main__":
    main() 