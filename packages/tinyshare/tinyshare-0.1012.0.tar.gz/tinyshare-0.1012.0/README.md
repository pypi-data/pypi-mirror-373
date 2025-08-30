# TinyShare SDK

## 构建说明

### 标准构建（源码可见）
```bash
python3 -m build
```

### 安全构建（移除注释+代码混淆）
```bash
# 使用shell脚本（推荐）
./build_secure.sh

# 或直接使用Python脚本
python3 build_obfuscated.py
```

## 发布
```bash
python3 -m twine upload dist/*
```