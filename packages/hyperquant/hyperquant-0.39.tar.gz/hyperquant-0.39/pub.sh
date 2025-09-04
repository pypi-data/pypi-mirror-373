#!/bin/bash
echo "清理旧的构建文件..."
rm -rf dist/* build/*

echo "重新构建包..."
uv build

echo "发布到 PyPI..."
# 从 .pypirc 文件读取 token
TOKEN=$(grep "password" .pypirc | cut -d "=" -f2 | tr -d ' ')

# 使用 token 发布
TWINE_USERNAME=__token__ TWINE_PASSWORD=$TOKEN uv run twine upload dist/*