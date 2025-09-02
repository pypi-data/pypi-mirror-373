#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import random
import threading
from typing import Dict, List, Optional, Any
from pathlib import Path

class FingerprintLoader:
    """TLS指纹数据加载器，将JSON格式的指纹数据转换为xtls_client可用的参数（线程安全版本）"""
    
    def __init__(self):
        # 线程锁，用于保护缓存操作
        self._lock = threading.RLock()
        self._initialized = False
        
        # 获取tls_datas目录的路径
        # 优先从当前工作目录查找，然后从包安装目录查找
        current_dir = Path.cwd() / "tls_datas"
        package_dir = Path(__file__).parent.parent / "tls_datas"
        
        if current_dir.exists():
            self.data_dir = current_dir
        elif package_dir.exists():
            self.data_dir = package_dir
        else:
            # 如果都不存在，尝试从sys.prefix查找（适用于pip安装）
            import sys
            install_dir = Path(sys.prefix) / "tls_datas"
            if install_dir.exists():
                self.data_dir = install_dir
            else:
                self.data_dir = package_dir  # 使用默认路径，即使不存在
        # print(f"指纹数据目录: {self.data_dir}")
        self._fingerprint_cache = {}
        self._load_all_fingerprints()
    
    def _load_all_fingerprints(self):
        """加载所有指纹文件（线程安全）"""
        with self._lock:
            if self._initialized:
                return
                
            if not self.data_dir.exists():
                self._initialized = True
                return
            
            # 遍历所有JSON文件
            for json_file in self.data_dir.rglob("*.json"):
                fingerprint_name = self._generate_fingerprint_name(json_file)
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        fingerprint_config = self._parse_fingerprint_data(data)
                        if fingerprint_config:
                            self._fingerprint_cache[fingerprint_name] = fingerprint_config
                except Exception as e:
                    print(f"警告：无法加载指纹文件 {json_file}: {e}")
            
            self._initialized = True
    
    def _generate_fingerprint_name(self, json_file: Path) -> str:
        """根据文件路径生成指纹名称"""
        # 移除扩展名
        name_parts = []
        
        # 获取相对于tls_datas的路径
        relative_path = json_file.relative_to(self.data_dir)
        
        # 添加浏览器类型
        browser_type = relative_path.parts[0]  # chrome, firefox, safari等
        name_parts.append(browser_type)
        
        # 添加操作系统信息
        if len(relative_path.parts) > 1:
            os_type = relative_path.parts[1]  # windows, macos, ios等
            name_parts.append(os_type)
        
        # 添加文件名（去除扩展名）
        filename = json_file.stem
        name_parts.append(filename)
        
        return "_".join(name_parts)
    
    def _parse_fingerprint_data(self, data: Dict) -> Optional[Dict[str, Any]]:
        """解析指纹数据并转换为xtls_client参数格式"""
        try:
            tls_data = data.get("tls", {})
            http2_data = data.get("http2", {})
            
            config = {}
            
            # 提取JA3字符串
            if "ja3" in tls_data:
                config["ja3_string"] = tls_data["ja3"]
            
            # 提取User-Agent
            if "user_agent" in data:
                config["user_agent"] = data["user_agent"]
            
            # 解析签名算法
            signature_algorithms = self._extract_signature_algorithms(tls_data)
            if signature_algorithms:
                config["supported_signature_algorithms"] = signature_algorithms
            
            # 解析支持的版本
            supported_versions = self._extract_supported_versions(tls_data)
            if supported_versions:
                config["supported_versions"] = supported_versions
            
            # 解析密钥共享曲线
            key_share_curves = self._extract_key_share_curves(tls_data)
            if key_share_curves:
                config["key_share_curves"] = key_share_curves
            
            # 解析证书压缩算法
            cert_compression = self._extract_cert_compression(tls_data)
            if cert_compression:
                config["cert_compression_algo"] = cert_compression
            
            # 解析HTTP/2设置
            h2_settings = self._extract_h2_settings(http2_data)
            if h2_settings:
                config["h2_settings"] = h2_settings["settings"]
                config["h2_settings_order"] = h2_settings["order"]
            
            # 解析连接流控制
            connection_flow = self._extract_connection_flow(http2_data)
            if connection_flow:
                config["connection_flow"] = connection_flow
            
            # 解析伪头部顺序
            pseudo_header_order = self._extract_pseudo_header_order(http2_data)
            if pseudo_header_order:
                config["pseudo_header_order"] = pseudo_header_order
            
            # 解析头部顺序
            header_order = self._extract_header_order(http2_data)
            if header_order:
                config["header_order"] = header_order
            
            return config if config else None
            
        except Exception as e:
            print(f"解析指纹数据时出错: {e}")
            return None
    
    def _extract_signature_algorithms(self, tls_data: Dict) -> Optional[List[str]]:
        """提取签名算法列表"""
        extensions = tls_data.get("extensions", [])
        for ext in extensions:
            if ext.get("name") == "signature_algorithms (13)":
                algorithms = ext.get("signature_algorithms", [])
                # 转换为xtls_client格式
                converted = []
                for algo in algorithms:
                    if "ecdsa_secp256r1_sha256" in algo:
                        converted.append("ECDSAWithP256AndSHA256")
                    elif "rsa_pss_rsae_sha256" in algo:
                        converted.append("PSSWithSHA256")
                    elif "rsa_pkcs1_sha256" in algo:
                        converted.append("PKCS1WithSHA256")
                    elif "ecdsa_secp384r1_sha384" in algo:
                        converted.append("ECDSAWithP384AndSHA384")
                    elif "rsa_pss_rsae_sha384" in algo:
                        converted.append("PSSWithSHA384")
                    elif "rsa_pkcs1_sha384" in algo:
                        converted.append("PKCS1WithSHA384")
                    elif "rsa_pss_rsae_sha512" in algo:
                        converted.append("PSSWithSHA512")
                    elif "rsa_pkcs1_sha512" in algo:
                        converted.append("PKCS1WithSHA512")
                return converted if converted else None
        return None
    
    def _extract_supported_versions(self, tls_data: Dict) -> Optional[List[str]]:
        """提取支持的TLS版本"""
        extensions = tls_data.get("extensions", [])
        for ext in extensions:
            if ext.get("name") == "supported_versions (43)":
                versions = ext.get("versions", [])
                converted = []
                for version in versions:
                    if "GREASE" in version:
                        converted.append("GREASE")
                    elif "TLS 1.3" in version:
                        converted.append("1.3")
                    elif "TLS 1.2" in version:
                        converted.append("1.2")
                    elif "TLS 1.1" in version:
                        converted.append("1.1")
                    elif "TLS 1.0" in version:
                        converted.append("1.0")
                return converted if converted else None
        return None
    
    def _extract_key_share_curves(self, tls_data: Dict) -> Optional[List[str]]:
        """提取密钥共享曲线"""
        extensions = tls_data.get("extensions", [])
        for ext in extensions:
            if ext.get("name") == "supported_groups (10)":
                groups = ext.get("supported_groups", [])
                converted = []
                for group in groups:
                    if "GREASE" in group:
                        converted.append("GREASE")
                    elif "X25519" in group and "MLKEM768" not in group:
                        converted.append("X25519")
                    elif "P-256" in group:
                        converted.append("P256")
                    elif "P-384" in group:
                        converted.append("P384")
                    elif "P-521" in group:
                        converted.append("P521")
                return converted if converted else None
        return None
    
    def _extract_cert_compression(self, tls_data: Dict) -> Optional[str]:
        """提取证书压缩算法"""
        extensions = tls_data.get("extensions", [])
        for ext in extensions:
            if ext.get("name") == "compress_certificate (27)":
                algorithms = ext.get("algorithms", [])
                if algorithms:
                    algo = algorithms[0]
                    if "brotli" in algo:
                        return "brotli"
                    elif "zlib" in algo:
                        return "zlib"
                    elif "zstd" in algo:
                        return "zstd"
        return None
    
    def _extract_h2_settings(self, http2_data: Dict) -> Optional[Dict]:
        """提取HTTP/2设置"""
        frames = http2_data.get("sent_frames", [])
        for frame in frames:
            if frame.get("frame_type") == "SETTINGS":
                settings = frame.get("settings", [])
                h2_settings = {}
                order = []
                
                for setting in settings:
                    if "HEADER_TABLE_SIZE" in setting:
                        value = int(setting.split("=")[1].strip())
                        h2_settings["HEADER_TABLE_SIZE"] = value
                        order.append("HEADER_TABLE_SIZE")
                    elif "ENABLE_PUSH" in setting:
                        value = int(setting.split("=")[1].strip())
                        h2_settings["ENABLE_PUSH"] = value
                        order.append("ENABLE_PUSH")
                    elif "MAX_CONCURRENT_STREAMS" in setting:
                        value = int(setting.split("=")[1].strip())
                        h2_settings["MAX_CONCURRENT_STREAMS"] = value
                        order.append("MAX_CONCURRENT_STREAMS")
                    elif "INITIAL_WINDOW_SIZE" in setting:
                        value = int(setting.split("=")[1].strip())
                        h2_settings["INITIAL_WINDOW_SIZE"] = value
                        order.append("INITIAL_WINDOW_SIZE")
                    elif "MAX_FRAME_SIZE" in setting:
                        value = int(setting.split("=")[1].strip())
                        h2_settings["MAX_FRAME_SIZE"] = value
                        order.append("MAX_FRAME_SIZE")
                    elif "MAX_HEADER_LIST_SIZE" in setting:
                        value = int(setting.split("=")[1].strip())
                        h2_settings["MAX_HEADER_LIST_SIZE"] = value
                        order.append("MAX_HEADER_LIST_SIZE")
                
                return {"settings": h2_settings, "order": order} if h2_settings else None
        return None
    
    def _extract_connection_flow(self, http2_data: Dict) -> Optional[int]:
        """提取连接流控制值"""
        frames = http2_data.get("sent_frames", [])
        for frame in frames:
            if frame.get("frame_type") == "WINDOW_UPDATE":
                return frame.get("increment")
        return None
    
    def _extract_pseudo_header_order(self, http2_data: Dict) -> Optional[List[str]]:
        """提取伪头部顺序"""
        frames = http2_data.get("sent_frames", [])
        for frame in frames:
            if frame.get("frame_type") == "HEADERS":
                headers = frame.get("headers", [])
                pseudo_headers = []
                for header in headers:
                    if header.startswith(":"):
                        key = header.split(":")[1].strip()
                        if " " in key:
                            key = key.split(" ")[0]
                        pseudo_header = f":{key}"
                        if pseudo_header not in pseudo_headers:
                            pseudo_headers.append(pseudo_header)
                return pseudo_headers if pseudo_headers else None
        return None
    
    def _extract_header_order(self, http2_data: Dict) -> Optional[List[str]]:
        """提取普通头部顺序"""
        frames = http2_data.get("sent_frames", [])
        for frame in frames:
            if frame.get("frame_type") == "HEADERS":
                headers = frame.get("headers", [])
                normal_headers = []
                for header in headers:
                    if not header.startswith(":"):
                        key = header.split(":")[0].strip().lower()
                        if key not in normal_headers:
                            normal_headers.append(key)
                return normal_headers if normal_headers else None
        return None
    
    def get_fingerprint_config(self, fingerprint_name: str) -> Optional[Dict[str, Any]]:
        """获取指定指纹的配置（线程安全）"""
        with self._lock:
            # 确保已初始化
            if not self._initialized:
                self._load_all_fingerprints()
            return self._fingerprint_cache.get(fingerprint_name)
    
    def list_available_fingerprints(self) -> List[str]:
        """列出所有可用的指纹名称（线程安全）"""
        with self._lock:
            # 确保已初始化
            if not self._initialized:
                self._load_all_fingerprints()
            return list(self._fingerprint_cache.keys())
    
    def get_fingerprints_by_browser(self, browser: str) -> List[str]:
        """根据浏览器类型筛选指纹（线程安全）"""
        with self._lock:
            # 确保已初始化
            if not self._initialized:
                self._load_all_fingerprints()
            return [name for name in self._fingerprint_cache.keys() if name.startswith(browser.lower())]
    
    def randomize_fingerprint_config(self, fingerprint_config: Dict[str, Any]) -> Dict[str, Any]:
        """随机化指纹配置参数，使其更难被检测"""
        if not fingerprint_config:
            return fingerprint_config
        
        # 创建配置的深拷贝，避免修改原始数据
        randomized_config = fingerprint_config.copy()
        
        # 随机化支持的签名算法顺序
        if "supported_signature_algorithms" in randomized_config:
            algorithms = randomized_config["supported_signature_algorithms"].copy()
            random.shuffle(algorithms)
            randomized_config["supported_signature_algorithms"] = algorithms
        
        # 随机化密钥共享曲线顺序
        if "key_share_curves" in randomized_config:
            curves = randomized_config["key_share_curves"].copy()
            # 保持GREASE在第一位（如果存在），其他的随机排序
            non_grease = [c for c in curves if c != "GREASE"]
            grease = [c for c in curves if c == "GREASE"]
            random.shuffle(non_grease)
            randomized_config["key_share_curves"] = grease + non_grease
        
        # 随机化支持的版本顺序
        if "supported_versions" in randomized_config:
            versions = randomized_config["supported_versions"].copy()
            # 保持GREASE在第一位（如果存在），其他的随机排序
            non_grease = [v for v in versions if v != "GREASE"]
            grease = [v for v in versions if v == "GREASE"]
            random.shuffle(non_grease)
            randomized_config["supported_versions"] = grease + non_grease
        
        # 随机化HTTP/2设置顺序
        if "h2_settings_order" in randomized_config:
            order = randomized_config["h2_settings_order"].copy()
            random.shuffle(order)
            randomized_config["h2_settings_order"] = order
        
        # 随机化头部顺序（保持伪头部在前面）
        if "header_order" in randomized_config:
            headers = randomized_config["header_order"].copy()
            random.shuffle(headers)
            randomized_config["header_order"] = headers
        
        # 随机化伪头部顺序
        if "pseudo_header_order" in randomized_config:
            pseudo_headers = randomized_config["pseudo_header_order"].copy()
            random.shuffle(pseudo_headers)
            randomized_config["pseudo_header_order"] = pseudo_headers
        
        # 轻微随机化连接流控制值（±10%范围内）
        if "connection_flow" in randomized_config:
            flow = randomized_config["connection_flow"]
            if isinstance(flow, int) and flow > 0:
                variation = int(flow * 0.1)  # 10%的变化范围
                randomized_flow = flow + random.randint(-variation, variation)
                # 确保值为正数
                randomized_config["connection_flow"] = max(1024, randomized_flow)
        
        # 随机化HTTP/2设置的值（在合理范围内）
        if "h2_settings" in randomized_config:
            settings = randomized_config["h2_settings"].copy()
            
            # 对部分设置进行轻微随机化
            if "HEADER_TABLE_SIZE" in settings:
                base_value = settings["HEADER_TABLE_SIZE"]
                variation = int(base_value * 0.05)  # 5%的变化
                settings["HEADER_TABLE_SIZE"] = base_value + random.randint(-variation, variation)
            
            if "INITIAL_WINDOW_SIZE" in settings:
                base_value = settings["INITIAL_WINDOW_SIZE"]
                variation = int(base_value * 0.05)  # 5%的变化
                settings["INITIAL_WINDOW_SIZE"] = base_value + random.randint(-variation, variation)
            
            if "MAX_HEADER_LIST_SIZE" in settings:
                base_value = settings["MAX_HEADER_LIST_SIZE"]
                variation = int(base_value * 0.05)  # 5%的变化
                settings["MAX_HEADER_LIST_SIZE"] = base_value + random.randint(-variation, variation)
            
            randomized_config["h2_settings"] = settings
        
        return randomized_config

# 线程安全的单例实现
_fingerprint_loader = None
_global_lock = threading.Lock()

def _get_fingerprint_loader() -> FingerprintLoader:
    """获取线程安全的全局实例"""
    global _fingerprint_loader
    if _fingerprint_loader is None:
        with _global_lock:
            # 双重检查锁定模式
            if _fingerprint_loader is None:
                _fingerprint_loader = FingerprintLoader()
    return _fingerprint_loader

def get_fingerprint_config(fingerprint_name: str) -> Optional[Dict[str, Any]]:
    """获取指定指纹的配置（全局函数，线程安全）"""
    loader = _get_fingerprint_loader()
    return loader.get_fingerprint_config(fingerprint_name)

def list_available_fingerprints() -> List[str]:
    """列出所有可用的指纹名称（全局函数，线程安全）"""
    loader = _get_fingerprint_loader()
    return loader.list_available_fingerprints()

def get_fingerprints_by_browser(browser: str) -> List[str]:
    """根据浏览器类型筛选指纹（全局函数，线程安全）"""
    loader = _get_fingerprint_loader()
    return loader.get_fingerprints_by_browser(browser)

def get_randomized_fingerprint_config(fingerprint_name: str) -> Optional[Dict[str, Any]]:
    """获取随机化的指纹配置（全局函数，线程安全）"""
    loader = _get_fingerprint_loader()
    config = loader.get_fingerprint_config(fingerprint_name)
    if config:
        return loader.randomize_fingerprint_config(config)
    return None
