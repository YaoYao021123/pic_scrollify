#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrollify GUI - 桌面图形界面
基于tkinter的简洁GUI界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from pathlib import Path
from scrollify_core import ScrollifyConfig, ScrollifyGenerator


class ScrollifyGUI:
    """Scrollify图形界面主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Scrollify - 长图转滚动GIF工具")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # 变量
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
        self.aspect_ratio = tk.StringVar(value="16:9")
        self.output_width = tk.IntVar(value=800)
        self.output_height = tk.IntVar(value=450)
        self.scroll_speed = tk.IntVar(value=8)
        self.framerate = tk.IntVar(value=24)
        self.scroll_mode = tk.StringVar(value="down")
        self.pause_duration = tk.DoubleVar(value=2.0)
        self.quality_factor = tk.DoubleVar(value=0.8)
        self.output_format = tk.StringVar(value="GIF")
        self.add_watermark = tk.BooleanVar(value=False)
        self.watermark_text = tk.StringVar(value="Created with Scrollify")
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主容器
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # 标题
        title = ttk.Label(main_frame, text="Scrollify", font=("Arial", 16, "bold"))
        title.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        row += 1
        
        # 输入文件
        ttk.Label(main_frame, text="输入图片:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="浏览...", command=self.browse_input_file).grid(row=row, column=2, padx=5)
        row += 1
        
        # 输出文件
        ttk.Label(main_frame, text="输出文件:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(main_frame, text="选择...", command=self.browse_output_file).grid(row=row, column=2, padx=5)
        row += 1
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # 输出设置
        settings_label = ttk.Label(main_frame, text="输出设置", font=("Arial", 12, "bold"))
        settings_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        row += 1
        
        # 输出格式
        ttk.Label(main_frame, text="输出格式:").grid(row=row, column=0, sticky=tk.W, pady=2)
        format_combo = ttk.Combobox(main_frame, textvariable=self.output_format, values=["GIF", "MP4"], state="readonly", width=10)
        format_combo.grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1
        
        # 宽高比
        ttk.Label(main_frame, text="宽高比:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ratio_frame = ttk.Frame(main_frame)
        ratio_frame.grid(row=row, column=1, sticky=tk.W, padx=5)
        ratio_combo = ttk.Combobox(ratio_frame, textvariable=self.aspect_ratio, 
                                  values=["16:9", "4:3", "1:1", "source", "custom"], 
                                  state="readonly", width=10)
        ratio_combo.grid(row=0, column=0)
        ratio_combo.bind('<<ComboboxSelected>>', self.on_ratio_change)
        row += 1
        
        # 尺寸设置
        size_frame = ttk.Frame(main_frame)
        size_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        size_frame.columnconfigure(1, weight=1)
        size_frame.columnconfigure(3, weight=1)
        
        ttk.Label(size_frame, text="宽度:").grid(row=0, column=0, sticky=tk.W)
        width_spin = ttk.Spinbox(size_frame, from_=200, to=2000, textvariable=self.output_width, width=10)
        width_spin.grid(row=0, column=1, sticky=tk.W, padx=5)
        width_spin.bind('<KeyRelease>', self.on_width_change)
        
        ttk.Label(size_frame, text="高度:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.height_spin = ttk.Spinbox(size_frame, from_=100, to=2000, textvariable=self.output_height, width=10)
        self.height_spin.grid(row=0, column=3, sticky=tk.W, padx=5)
        row += 1
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # 动画设置
        anim_label = ttk.Label(main_frame, text="动画设置", font=("Arial", 12, "bold"))
        anim_label.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        row += 1
        
        # 滚动速度
        ttk.Label(main_frame, text="滚动速度:").grid(row=row, column=0, sticky=tk.W, pady=2)
        speed_frame = ttk.Frame(main_frame)
        speed_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        speed_scale = ttk.Scale(speed_frame, from_=1, to=20, variable=self.scroll_speed, orient=tk.HORIZONTAL, length=200)
        speed_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        speed_label = ttk.Label(speed_frame, textvariable=self.scroll_speed)
        speed_label.grid(row=0, column=1, padx=(10, 0))
        row += 1
        
        # 帧率
        ttk.Label(main_frame, text="帧率 (FPS):").grid(row=row, column=0, sticky=tk.W, pady=2)
        fps_combo = ttk.Combobox(main_frame, textvariable=self.framerate, 
                                values=[12, 15, 20, 24, 30, 60], state="readonly", width=10)
        fps_combo.grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1
        
        # 滚动模式
        ttk.Label(main_frame, text="滚动模式:").grid(row=row, column=0, sticky=tk.W, pady=2)
        mode_combo = ttk.Combobox(main_frame, textvariable=self.scroll_mode,
                                 values=[("down", "向下"), ("down-up", "往返"), ("down-once", "单次")],
                                 state="readonly", width=15)
        mode_combo.grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1
        
        # 暂停时间
        ttk.Label(main_frame, text="暂停时间 (秒):").grid(row=row, column=0, sticky=tk.W, pady=2)
        pause_spin = ttk.Spinbox(main_frame, from_=0.5, to=10.0, increment=0.5, 
                                textvariable=self.pause_duration, width=10)
        pause_spin.grid(row=row, column=1, sticky=tk.W, padx=5)
        row += 1
        
        # 质量因子
        ttk.Label(main_frame, text="质量:").grid(row=row, column=0, sticky=tk.W, pady=2)
        quality_frame = ttk.Frame(main_frame)
        quality_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), padx=5)
        quality_scale = ttk.Scale(quality_frame, from_=0.1, to=1.0, variable=self.quality_factor, 
                                 orient=tk.HORIZONTAL, length=200)
        quality_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        quality_label = ttk.Label(quality_frame, text="")
        quality_label.grid(row=0, column=1, padx=(10, 0))
        
        def update_quality_label(*args):
            quality_label.config(text=f"{self.quality_factor.get():.1f}")
        self.quality_factor.trace('w', update_quality_label)
        update_quality_label()
        row += 1
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # 水印设置
        watermark_frame = ttk.Frame(main_frame)
        watermark_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        watermark_check = ttk.Checkbutton(watermark_frame, text="添加水印:", variable=self.add_watermark)
        watermark_check.grid(row=0, column=0, sticky=tk.W)
        watermark_entry = ttk.Entry(watermark_frame, textvariable=self.watermark_text, width=30)
        watermark_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        watermark_frame.columnconfigure(1, weight=1)
        row += 1
        
        # 分隔线
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        row += 1
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="预览设置", command=self.preview_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="开始转换", command=self.start_conversion).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="打开输出目录", command=self.open_output_dir).pack(side=tk.LEFT, padx=5)
        row += 1
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        row += 1
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=2)
        
        # 初始化
        self.on_ratio_change()
        
    def browse_input_file(self):
        """浏览输入文件"""
        filename = filedialog.askopenfilename(
            title="选择长图文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.webp *.bmp"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.input_file.set(filename)
            # 自动生成输出文件名
            if not self.output_file.get():
                input_path = Path(filename)
                output_name = f"{input_path.stem}_scroll.gif"
                self.output_file.set(str(input_path.parent / output_name))
    
    def browse_output_file(self):
        """浏览输出文件"""
        format_ext = "gif" if self.output_format.get() == "GIF" else "mp4"
        filename = filedialog.asksaveasfilename(
            title="保存为",
            defaultextension=f".{format_ext}",
            filetypes=[
                (f"{self.output_format.get()}文件", f"*.{format_ext}"),
                ("所有文件", "*.*")
            ]
        )
        if filename:
            self.output_file.set(filename)
    
    def on_ratio_change(self, *args):
        """宽高比改变事件"""
        if self.aspect_ratio.get() == "custom":
            self.height_spin.config(state="normal")
        else:
            self.height_spin.config(state="disabled")
            self.on_width_change()
    
    def on_width_change(self, *args):
        """宽度改变事件"""
        ratio = self.aspect_ratio.get()
        if ratio == "custom":
            return
        
        width = self.output_width.get()
        
        if ratio == "16:9":
            height = int(width * 9 / 16)
        elif ratio == "4:3":
            height = int(width * 3 / 4)
        elif ratio == "1:1":
            height = width
        else:  # source
            height = width  # 实际会根据源图片计算
        
        self.output_height.set(height)
    
    def preview_settings(self):
        """预览设置"""
        if not self.input_file.get():
            messagebox.showwarning("警告", "请先选择输入图片文件")
            return
        
        config = self.create_config()
        
        preview_text = f"""
输入文件: {config.source_image}
输出文件: {config.output_path}
输出格式: {config.output_format}

宽高比: {config.aspect_ratio}
输出宽度: {config.output_width}px
输出高度: {config.output_height or '自动'}px

滚动速度: {config.scroll_speed} 像素/帧
帧率: {config.framerate} FPS
滚动模式: {config.scroll_mode}
暂停时间: {config.pause_duration} 秒
质量因子: {config.quality_factor}

水印: {'是' if config.add_watermark else '否'}
{f'水印文字: {config.watermark_text}' if config.add_watermark else ''}
        """
        
        messagebox.showinfo("设置预览", preview_text.strip())
    
    def create_config(self):
        """创建配置对象"""
        return ScrollifyConfig(
            source_image=self.input_file.get(),
            output_path=self.output_file.get() or "output_scroll.gif",
            aspect_ratio=self.aspect_ratio.get(),
            output_width=self.output_width.get(),
            output_height=self.output_height.get() if self.aspect_ratio.get() == "custom" else None,
            scroll_speed=self.scroll_speed.get(),
            framerate=self.framerate.get(),
            scroll_mode=self.scroll_mode.get(),
            pause_duration=self.pause_duration.get(),
            output_format=self.output_format.get(),
            quality_factor=self.quality_factor.get(),
            add_watermark=self.add_watermark.get(),
            watermark_text=self.watermark_text.get()
        )
    
    def start_conversion(self):
        """开始转换"""
        if not self.input_file.get():
            messagebox.showwarning("警告", "请先选择输入图片文件")
            return
        
        if not self.output_file.get():
            messagebox.showwarning("警告", "请指定输出文件路径")
            return
        
        # 在单独线程中运行转换
        self.progress.start()
        self.status_label.config(text="正在转换...")
        
        def conversion_thread():
            try:
                config = self.create_config()
                generator = ScrollifyGenerator(config)
                success = generator.run()
                
                # 在主线程中更新UI
                self.root.after(0, lambda: self.conversion_finished(success))
                
            except Exception as e:
                self.root.after(0, lambda: self.conversion_error(str(e)))
        
        threading.Thread(target=conversion_thread, daemon=True).start()
    
    def conversion_finished(self, success):
        """转换完成"""
        self.progress.stop()
        
        if success:
            self.status_label.config(text="转换完成！")
            file_size = os.path.getsize(self.output_file.get()) / (1024 * 1024)
            messagebox.showinfo("成功", f"转换完成！\n\n输出文件: {self.output_file.get()}\n文件大小: {file_size:.2f} MB")
        else:
            self.status_label.config(text="转换失败")
            messagebox.showerror("错误", "转换失败，请检查输入文件和设置")
    
    def conversion_error(self, error_msg):
        """转换出错"""
        self.progress.stop()
        self.status_label.config(text="转换出错")
        messagebox.showerror("错误", f"转换出错: {error_msg}")
    
    def open_output_dir(self):
        """打开输出目录"""
        if self.output_file.get():
            output_dir = os.path.dirname(self.output_file.get())
            if output_dir and os.path.exists(output_dir):
                os.system(f'open "{output_dir}"')  # macOS
                # os.system(f'explorer "{output_dir}"')  # Windows
                # os.system(f'xdg-open "{output_dir}"')  # Linux
    
    def run(self):
        """运行GUI"""
        self.root.mainloop()


def main():
    """主函数"""
    app = ScrollifyGUI()
    app.run()


if __name__ == "__main__":
    main() 