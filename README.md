# Scrollify - 长图滚动GIF/MP4生成工具

Scrollify 是一个简单、强大、跨平台的长图转滚动动画工具，支持将任意长图片一键生成流畅的滚动GIF或MP4动画，适用于内容创作者、UI/UX设计师、产品经理等。

---

## ✨ 主要功能
- 支持 JPG、PNG、WebP 等主流图片格式
- 输出 GIF 或 MP4 动画（需安装 moviepy）
- 多种窗口比例：16:9、4:3、1:1、原图比例、自定义
- 滚动模式：向下、往返、单次滚动
- 可调节滚动速度、帧率、暂停时间、输出分辨率
- 支持添加自定义水印
- 命令行（CLI）与图形界面（GUI）双模式

---

## 🚀 安装方法

1. 克隆仓库
   ```bash
   git clone https://github.com/YaoYao021123/pic_scrollify.git
   cd pic_scrollify
   ```
2. 安装依赖
   ```bash
   pip install -r requirements.txt
   # 如需MP4支持
   pip install moviepy numpy
   ```

---

## 🖥️ 使用方法

### 命令行（CLI）

基础用法：
```bash
python scrollify_cli.py 图片路径 [参数...]
```

常用参数示例：
```bash
# 生成16:9滚动GIF，宽度800像素
python scrollify_cli.py mylong.png --width 800 --ratio 16:9

# 生成60帧高分辨率MP4
python scrollify_cli.py mylong.png --width 1920 --fps 60 --format MP4

# 添加水印，滚动模式为往返
python scrollify_cli.py mylong.png --watermark --watermark-text "演示水印" --mode down-up
```

所有参数说明请用 `-h` 查看：
```bash
python scrollify_cli.py -h
```

### 图形界面（GUI）

```bash
python scrollify_gui.py
```
弹出窗口，按提示选择图片、设置参数，一键生成动画。

---

## ⚙️ 常见参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--width` | 输出宽度 | 800 |
| `--ratio` | 窗口比例(16:9/4:3/1:1/source/custom) | 16:9 |
| `--height` | 自定义高度（ratio=custom时） | - |
| `--speed` | 滚动速度（像素/帧） | 8 |
| `--fps` | 帧率 | 24 |
| `--mode` | 滚动模式(down/down-up/down-once) | down |
| `--pause` | 滚动结束暂停时间(秒) | 2.0 |
| `--format` | 输出格式(GIF/MP4) | GIF |
| `--output` | 输出文件名 | 自动生成 |
| `--watermark` | 是否添加水印 | False |
| `--watermark-text` | 水印内容 | Created with Scrollify |
| `--quality` | 质量因子(0.1-1.0) | 0.8 |

---

## 💡 应用场景
- 展示长网页、聊天记录、文档、设计稿等
- 社交媒体内容创作
- 产品演示、交互动画

---

## ❓ 常见问题

- **Q: 如何生成高分辨率/高帧率动画？**
  - 设置 `--width` 为较大值，`--fps` 为60即可。
- **Q: MP4输出报错？**
  - 请确保已安装 `moviepy` 和 `numpy`。
- **Q: GIF太大怎么办？**
  - 降低分辨率、帧率或质量因子。
- **Q: 如何自定义窗口尺寸？**
  - 用 `--ratio custom --height 高度`。

---

## 📄 许可证
MIT

---

如有问题或建议，欢迎在 [GitHub Issues](https://github.com/YaoYao021123/pic_scrollify/issues) 反馈！
