import json
import os
import re
import xml.etree.ElementTree as ET
from configparser import ConfigParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import tomllib  # type: ignore
except ImportError:
    import tomli as tomllib


# ===== Python =====
def parse_python_config(dir_path: Path) -> Optional[Tuple[str, str]]:
    pyproject = dir_path / "pyproject.toml"
    if pyproject.is_file():
        try:
            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            if "project" in data:
                name = data["project"].get("name")
                version = data["project"].get("version")
                if name and version:
                    return name, version
            if "tool" in data and "poetry" in data["tool"]:
                name = data["tool"]["poetry"].get("name")
                version = data["tool"]["poetry"].get("version")
                if name and version:
                    return name, version
        except Exception:
            pass

    setup_cfg = dir_path / "setup.cfg"
    if setup_cfg.is_file():
        try:
            config = ConfigParser()
            config.read(setup_cfg)
            if config.has_section("metadata"):
                name = config.get("metadata", "name", fallback=None)
                version = config.get("metadata", "version", fallback=None)
                if name and version:
                    return name, version
        except Exception:
            pass

    setup_py = dir_path / "setup.py"
    if setup_py.is_file():
        try:
            content = setup_py.read_text(encoding="utf-8", errors="ignore")
            name_match = re.search(r"name\s*=\s*['\"]([A-Za-z0-9_.\-]+)['\"]", content)
            ver_match = re.search(
                r"version\s*=\s*['\"]([A-Za-z0-9_.\-]+)['\"]", content
            )
            if name_match and ver_match:
                return name_match.group(1), ver_match.group(1)
        except Exception:
            pass
    return None


# ===== Node.js =====
def parse_node_config(dir_path: Path) -> Optional[Tuple[str, str]]:
    package_json = dir_path / "package.json"
    if package_json.is_file():
        try:
            with package_json.open(encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("name")
            version = data.get("version")
            if name and version:
                return name, version
        except Exception:
            pass
    return None


# ===== Maven =====
def parse_maven_config(dir_path: Path) -> Optional[Tuple[str, str]]:
    pom_xml = dir_path / "pom.xml"
    if pom_xml.is_file():
        try:
            tree = ET.parse(pom_xml)
            root = tree.getroot()
            ns_match = re.match(r"\{.*\}", root.tag)
            nsmap = {"mvn": ns_match.group(0)[1:-1]} if ns_match else {}

            def find_tag(tag: str) -> Optional[str]:
                if nsmap:
                    el = root.find(f"mvn:{tag}", namespaces=nsmap)
                else:
                    el = root.find(tag)
                return el.text.strip() if el is not None and el.text else None

            artifact_id = find_tag("artifactId")
            version = find_tag("version")
            if artifact_id and version:
                return artifact_id, version
        except Exception:
            pass
    return None


# ===== Go =====
def parse_go_config(dir_path: Path) -> Optional[Tuple[str, str]]:
    go_mod = dir_path / "go.mod"
    if go_mod.is_file():
        try:
            with go_mod.open(encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("module "):
                        module_path = line.split()[1]
                        name = module_path.split("/")[-1]  # 模块名用最后一段
                        version = ""  # go.mod 通常不含自身版本
                        return name, version
        except Exception:
            pass
    return None


# ===== PHP =====
def parse_php_config(dir_path: Path) -> Optional[Tuple[str, str]]:
    composer_json = dir_path / "composer.json"
    if composer_json.is_file():
        try:
            with composer_json.open(encoding="utf-8") as f:
                data = json.load(f)
            name = data.get("name")
            version = data.get("version", "")
            if name:
                return name, version
        except Exception:
            pass
    return None


# ===== 主方法 =====
def get_all_build_artifacts(repo_path: str) -> List[Dict]:
    repo = Path(repo_path).resolve()
    results = []

    for root, dirs, files in os.walk(repo):
        dir_path = Path(root)
        rel_path = os.path.relpath(dir_path, repo)  # 相对于 repo_path 的路径
        if rel_path == ".":
            rel_path = "."  # 根目录

        for parser in (
            parse_python_config,
            parse_node_config,
            parse_maven_config,
            parse_go_config,
            parse_php_config,
        ):
            info = parser(dir_path)
            if info:
                results.append(
                    {"path": rel_path, "name": info[0], "version": info[1]}  # 相对路径
                )
    return results


# ==== 测试 ====
if __name__ == "__main__":
    repo_dir = "/path/to/your/repo"
    artifacts = get_all_build_artifacts(repo_dir)
    for art in artifacts:
        print(f"[{art['path']}] 产物名: {art['name']}, 版本号: {art['version']}")
