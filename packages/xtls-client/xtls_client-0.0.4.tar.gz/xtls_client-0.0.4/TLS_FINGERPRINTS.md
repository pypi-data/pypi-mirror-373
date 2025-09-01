# TLS指纹数据集成

本库已经集成了来自 `tls_datas/` 目录的真实浏览器TLS指纹数据，提供了更加准确和难以检测的浏览器模拟能力。

## 新功能

### 自动指纹加载
- 自动加载 `tls_datas/` 中的所有JSON指纹文件
- 支持Chrome、Firefox、Safari等多种浏览器指纹
- 包含真实的TLS和HTTP/2特征数据

### 新的预设客户端标识符
除了原有的预设（如 `chrome_124`、`firefox_142` 等），现在还支持基于真实指纹数据的标识符：

#### Chrome指纹
- `chrome_macos_chrome_139_macos_10_15_7`
- `chrome_windows_chrome_138_windows_10_x64`
- `chrome_windows_chrome_135_windows_10_x64`
- 等等...

#### Firefox指纹
- `firefox_macos_firefox_142_macos_10_15`
- `firefox_windows_firefox_142_windows_10_x64`
- 等等...

#### Safari指纹
- `safari_ios_safari_ios_18_6_2_iphone`
- `safari_macos_safari_macos_10_15_7_version_18_6`
- 等等...

## 使用方法

### 基本使用
```python
import xtls_client

# 使用Chrome macOS指纹
session = xtls_client.Session(
    client_identifier="chrome_macos_chrome_139_macos_10_15_7"
)

# 使用Firefox指纹
session = xtls_client.Session(
    client_identifier="firefox_macos_firefox_142_macos_10_15"
)

# 使用Safari iOS指纹
session = xtls_client.Session(
    client_identifier="safari_ios_safari_ios_18_6_2_iphone"
)
```

### 列出可用指纹
```python
import xtls_client

# 列出所有可用指纹
all_fingerprints = xtls_client.list_available_fingerprints()
print(f"共有 {len(all_fingerprints)} 个可用指纹")

# 按浏览器类型筛选
chrome_fingerprints = xtls_client.get_fingerprints_by_browser("chrome")
firefox_fingerprints = xtls_client.get_fingerprints_by_browser("firefox")
safari_fingerprints = xtls_client.get_fingerprints_by_browser("safari")
```

### 自定义参数覆盖
```python
import xtls_client

# 使用指纹数据，但覆盖特定参数
session = xtls_client.Session(
    client_identifier="chrome_macos_chrome_139_macos_10_15_7",
    ja3_string="自定义JA3字符串",  # 覆盖指纹中的JA3
    connection_flow=999999,  # 覆盖指纹中的连接流
    # User-Agent等其他参数仍使用指纹数据
)
```

### 兼容性
原有的预设标识符仍然保持完全兼容：
```python
import xtls_client

# 原有预设仍然可用
session = xtls_client.Session(client_identifier="chrome_124")
session = xtls_client.Session(client_identifier="firefox_142")
```

## 指纹数据来源

指纹数据基于真实浏览器的TLS握手和HTTP/2连接特征，包含：
- **JA3指纹**: TLS握手特征
- **HTTP/2设置**: 窗口大小、头部表大小等
- **头部顺序**: 真实浏览器的头部发送顺序
- **User-Agent**: 对应浏览器版本的UA字符串
- **签名算法**: 支持的TLS签名算法列表
- **密钥交换曲线**: 支持的椭圆曲线列表

## 优势

1. **更好的反检测能力**: 基于真实浏览器数据，难以被检测
2. **完整的特征模拟**: 不仅仅是User-Agent，包含完整的TLS和HTTP/2特征
3. **多平台支持**: 覆盖Windows、macOS、iOS等多个平台
4. **向后兼容**: 不影响现有代码的使用
5. **灵活配置**: 可以部分覆盖指纹数据中的参数

## 示例

完整的使用示例请参考：
- `examples/example_fingerprint_usage.py` - 完整功能演示
- `examples/example_fingerprint_preset.py` - 基本使用示例
- `examples/example1 - preset.py` - 原有预设使用方法
- `examples/example2 - custom.py` - 自定义参数使用方法

## 注意事项

1. 指纹数据文件必须是有效的JSON格式
2. 用户提供的参数优先级高于指纹数据
3. 如果指纹文件损坏，会显示警告但不影响程序运行
4. 指纹名称基于文件路径自动生成
