太好了！完善的文档是开源项目成功的关键。我来为你提供中英文双语的README.md：

# 双语 README.md

```markdown
# RandGen - Smart Random Data Generator

[中文](#randgen---智能随机数据生成器)

## 🚀 Overview

RandGen is a powerful command-line tool for generating realistic random test data. Perfect for developers, testers, and anyone who needs mock data for testing, demonstrations, or database seeding.

## ✨ Features

- **Multiple Data Types**: Names, emails, dates, integers, floats, strings, phone numbers, addresses
- **Localized Data**: Support for different locales (en_US, zh_CN, etc.)
- **Flexible Output**: CSV and JSON formats
- **Batch Generation**: Generate multiple records at once
- **File Export**: Save results to files or output to stdout

## 📦 Installation

```bash
# Install from PyPI
pip install randgen

# Or install from source
git clone https://github.com/fengjikui/randgen.git
cd randgen
pip install -e .
```

## 🛠️ Usage

### Basic Examples

```bash
# Generate 5 random names
randgen --name -n 5

# Generate names and emails
randgen --name --email -n 3

# Generate Chinese data
randgen --name --phone --locale zh_CN -n 5

# Save to JSON file
randgen --name --email --date -n 10 -f json -o data.json

# Generate all data types
randgen --name --email --date --int --float --string --phone --address -n 2
```

### Full Options

```bash
usage: randgen [-h] [--name] [--email] [--date] [--int] [--float] [--string]
               [--phone] [--address] [-n NUMBER] [-f {csv,json}] [-o OUTPUT]
               [--locale LOCALE]

Generate random test data for testing and development.

options:
  -h, --help            show this help message and exit
  --name                Generate random names
  --email               Generate random email addresses
  --date                Generate random dates
  --int                 Generate random integers
  --float               Generate random floating-point numbers
  --string              Generate random strings
  --phone               Generate random phone numbers
  --address             Generate random addresses
  -n NUMBER, --number NUMBER
                        Number of records to generate (default: 1)
  -f {csv,json}, --format {csv,json}
                        Output format (default: csv)
  -o OUTPUT, --output OUTPUT
                        Output file name (default: print to stdout)
  --locale LOCALE       Locale for localized data (e.g., zh_CN, en_US, ja_JP)
```

## 🔧 Advanced Usage

### Custom Ranges

While the CLI doesn't directly support custom ranges, you can use RandGen as a library:

```python
from randgen.generator import DataGenerator

gen = DataGenerator()
# Custom integer range
custom_int = gen.generate_int(100, 200)
# Custom string length
custom_str = gen.generate_string(20)
```

### Integration with Other Tools

```bash
# Pipe to other commands
randgen --name --email -n 100 | head -n 5

# Use in scripts
for i in {1..3}; do
    randgen --name --email -n 1 >> users.csv
done
```

## 📊 Output Examples

### CSV Output
```csv
Name,Email,Date
John Doe,john.doe@example.com,2023-10-15
Jane Smith,jane.smith@example.com,2023-09-20
```

### JSON Output
```json
[
  {
    "Name": "John Doe",
    "Email": "john.doe@example.com",
    "Date": "2023-10-15"
  }
]
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=randgen --cov-report=html

# Run specific test category
pytest tests/unit/
pytest tests/integration/
```

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Faker](https://faker.readthedocs.io/) library
- Inspired by the need for simple test data generation tools

---

# RandGen - 智能随机数据生成器

## 🚀 概述

RandGen 是一个强大的命令行工具，用于生成逼真的随机测试数据。非常适合开发人员、测试人员以及任何需要模拟数据进行测试、演示或数据库填充的用户。

## ✨ 功能特点

- **多种数据类型**: 姓名、邮箱、日期、整数、浮点数、字符串、电话号码、地址
- **本地化数据**: 支持不同区域设置（en_US、zh_CN等）
- **灵活输出**: CSV 和 JSON 格式
- **批量生成**: 一次生成多条记录
- **文件导出**: 保存结果到文件或输出到标准输出

## 📦 安装

```bash
# 从PyPI安装
pip install randgen

# 或从源码安装
git clone https://github.com/fengjikui/randgen.git
cd randgen
pip install -e .
```

## 🛠️ 使用方法

### 基础示例

```bash
# 生成5个随机姓名
randgen --name -n 5

# 生成姓名和邮箱
randgen --name --email -n 3

# 生成中文数据
randgen --name --phone --locale zh_CN -n 5

# 保存到JSON文件
randgen --name --email --date -n 10 -f json -o data.json

# 生成所有数据类型
randgen --name --email --date --int --float --string --phone --address -n 2
```

### 完整选项

```bash
用法: randgen [-h] [--name] [--email] [--date] [--int] [--float] [--string]
               [--phone] [--address] [-n NUMBER] [-f {csv,json}] [-o OUTPUT]
               [--locale LOCALE]

生成用于测试和开发的随机数据。

选项:
  -h, --help            显示帮助信息
  --name                生成随机姓名
  --email               生成随机邮箱地址
  --date                生成随机日期
  --int                 生成随机整数
  --float               生成随机浮点数
  --string              生成随机字符串
  --phone               生成随机电话号码
  --address             生成随机地址
  -n NUMBER, --number NUMBER
                        要生成的记录数量（默认: 1）
  -f {csv,json}, --format {csv,json}
                        输出格式（默认: csv）
  -o OUTPUT, --output OUTPUT
                        输出文件名（默认: 输出到标准输出）
  --locale LOCALE       本地化数据区域设置（例如: zh_CN, en_US, ja_JP）
```

## 🔧 高级用法

### 自定义范围

虽然CLI不直接支持自定义范围，但你可以将RandGen作为库使用：

```python
from randgen.generator import DataGenerator

gen = DataGenerator()
# 自定义整数范围
custom_int = gen.generate_int(100, 200)
# 自定义字符串长度
custom_str = gen.generate_string(20)
```

### 与其他工具集成

```bash
# 管道传输到其他命令
randgen --name --email -n 100 | head -n 5

# 在脚本中使用
for i in {1..3}; do
    randgen --name --email -n 1 >> users.csv
done
```

## 📊 输出示例

### CSV 输出
```csv
姓名,邮箱,日期
张三,zhangsan@example.com,2023-10-15
李四,lisi@example.com,2023-09-20
```

### JSON 输出
```json
[
  {
    "姓名": "张三",
    "邮箱": "zhangsan@example.com",
    "日期": "2023-10-15"
  }
]
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行带覆盖率报告
pytest --cov=randgen --cov-report=html

# 运行特定测试类别
pytest tests/unit/
pytest tests/integration/
```

## 🤝 贡献

我们欢迎贡献！请随时提交问题、功能请求或拉取请求。

1.  Fork 仓库
2.  创建特性分支 (`git checkout -b feature/amazing-feature`)
3.  提交更改 (`git commit -m '添加 amazing feature'`)
4.  推送到分支 (`git push origin feature/amazing-feature`)
5.  打开拉取请求

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- 基于 [Faker](https://faker.readthedocs.io/) 库构建
- 灵感来源于对简单测试数据生成工具的需求
```

## 使用说明

1. 将上述内容保存为 `README.md`
2. 替换 `fengjikui` 为你的GitHub用户名
3. 确保项目根目录有 `LICENSE` 文件（MIT许可证）
4. 你可以根据需要调整示例和描述

## 额外的文档文件（可选）

你还可以创建：
- `CONTRIBUTING.md` - 贡献指南
- `CHANGELOG.md` - 版本更新日志
- `EXAMPLES.md` - 更多使用示例

现在你的项目就有了专业的中英文文档，非常适合发布到PyPI和GitHub！