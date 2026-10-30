# VSQ-Studio Organization Profile

独立原创的 VSQ-Studio GitHub Organization Profile 模板，采用像素艺术视觉风格，提供中英双语主页、社区贡献说明，以及由 GitHub Actions 自动更新的组织公开活动图。

## 部署目录

将本目录内容合并到 `VSQ-Studio/.github` 仓库根目录：

```text
.github/
├── workflows/
│   └── update-activity.yml
assets/
├── activity.svg
├── vsq-banner.png
├── vsq-divider.svg
└── vsq-logo-pixel.png
profile/
├── README.md
└── README.en.md
scripts/
└── update_activity.py
```

GitHub Organization 默认显示 `profile/README.md`；英文版本通过主页顶部的 `README.en.md` 链接切换。

## GitHub 活动图

- 使用 GitHub REST API 的公开 Organization Events 接口。
- 工作流每 6 小时运行一次，也支持手动触发。
- 工作流需要 `contents: write` 权限，以便更新 `assets/activity.svg`。
- 活动图统计最近 14 天公开事件；不包含私有仓库活动，也不是实时在线状态。
- 首次部署后可在 Actions 中手动运行 **Update organization activity**。

## 自定义

- 组织名称：`VSQ-Studio`
- 横幅：`assets/vsq-banner.png`
- 像素 Logo：`assets/vsq-logo-pixel.png`
- 颜色：`#061326` / `#087EB7` / `#16BBD8` / `#2CE3F3`
- 中英文内容分别维护在 `profile/README.md` 与 `profile/README.en.md`。

本模板为 VSQ-Studio 独立制作，不复制引用模板仓库的 README、脚本或图片素材。
