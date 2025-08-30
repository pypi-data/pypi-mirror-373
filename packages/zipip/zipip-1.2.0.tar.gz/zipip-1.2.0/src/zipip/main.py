import os
import sys
import requests
import subprocess
import time
import socket
from packaging import tags
from packaging.version import parse as parse_version
from packaging.tags import Tag
from packaging.requirements import Requirement
from packaging.markers import default_environment
from importlib.metadata import distributions

def is_aria2_running():
    try:
        with socket.create_connection(("localhost", 6800), timeout=2):
            return True
    except:
        return False

def installed_list():
    installed = {}
    for dist in distributions():
        installed[dist.metadata['Name'].lower()] = dist.version
    return installed

def get_compatible_tags():
    return set(tags.sys_tags())

def parse_wheel_tags(filename):
    if filename.endswith('.whl'):
        filename = filename[:-4]
    parts = filename.split('-')
    if len(parts) < 4:
        return []
    python_tag, abi_tag, platform_tag = parts[-3:]
    pythons = python_tag.split('.')
    abis = abi_tag.split('.')
    platforms = platform_tag.split('.')
    return [Tag(p, a, pl) for p in pythons for a in abis for pl in platforms]

def get_best_wheel(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: Failed to get metadata for package '{package_name}'. {e}")
        return None, None, None

    data = response.json()
    releases = data.get('releases', {})
    if not releases:
        return None, None, None

    compatible_tags_set = get_compatible_tags()

    stable_versions = [v for v in releases.keys() if not parse_version(v).is_prerelease]
    sorted_versions = sorted(stable_versions, key=parse_version, reverse=True)

    for version in sorted_versions:
        files = releases[version]
        for file_info in files:
            if file_info.get('packagetype') == 'bdist_wheel':
                wheel_tags = set(parse_wheel_tags(file_info['filename']))
                if not wheel_tags.isdisjoint(compatible_tags_set):
                    return file_info['url'], file_info['filename'], version

    return None, None, None

def get_dependencies_for_version(package_name, version):
    url = f"https://pypi.org/pypi/{package_name}/{version}/json"
    try:
        print(f"   ℹ️ Fetching dependencies for {package_name} version {version}...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        dependencies = data.get('info', {}).get('requires_dist', []) or []
        return dependencies
    except requests.RequestException as e:
        print(f"   ⚠️ Could not fetch dependencies for {package_name}=={version}. {e}")
        return []

packages_in_progress = set()

def download_and_install(package_name):
    global packages_in_progress

    normalized_package_name = package_name.lower().replace("_", "-")

    installed_packages = installed_list()
    if normalized_package_name in installed_packages:
        print(f"✔️ {package_name} is already installed. Skipping.")
        return

    if normalized_package_name in packages_in_progress:
        print(f"☑️ {package_name} is already in the installation queue. Skipping.")
        return

    packages_in_progress.add(normalized_package_name)

    print(f"\n🔍 Searching for a compatible wheel for: {package_name}")
    url, file_name, version = get_best_wheel(package_name)

    if url and file_name and version:
        print("✅ Found compatible wheel.")
        print(f"   - Version: {version}")
        print(f"   - Filename: {file_name}")

        dependencies = get_dependencies_for_version(package_name, version)

        env = default_environment()
        if dependencies:
            print("📄 Checking dependencies...")
            for dep_string in dependencies:
                try:
                    req = Requirement(dep_string)
                    if req.marker and not req.marker.evaluate(environment=env):
                        print(f"   ⏩ Skipping conditional dependency: {dep_string}")
                        continue
                    download_and_install(req.name)
                except Exception as e:
                    print(f"⚠️ Could not parse dependency '{dep_string}': {e}. Skipping.")
        else:
            print("📄 No dependencies listed for this wheel.")

        print(f"\n⬇️ Downloading {file_name}...")
        try:
            if not is_aria2_running():
                print("❌ aria2c RPC server is not running. Start it with:")
                print("   aria2c --enable-rpc --rpc-listen-all")
                sys.exit(1)

            import aria2p
            aria2 = aria2p.API(
                aria2p.Client(host="http://localhost", port=6800, secret="")
            )

            download = aria2.add_uris([url], options={
                "max-connection-per-server": "16",
                "split": "16",
                "min-split-size": "1M",
                "enable-http-pipelining": "true",
                "user-agent": "Mozilla/5.0",
                "continue": "true",
                "out": file_name,
                "dir": os.getcwd()
            })

            while True:
                download.update()
                if download.is_complete:
                    print(f"   ✅ Download complete: {file_name}")
                    break
                elif download.is_removed or download.has_failed:
                    print("   ❌ Download failed or removed.")
                    sys.exit(1)
                print(f"   ⏳ Downloading: {download.progress_string()} at {download.download_speed_string()}")
                time.sleep(1)

        except Exception as e:
            print(f"\n❌ aria2p download failed: {e}")
            sys.exit(1)

        print(f"\n🚀 Installing {file_name}...")
        try:
            wheel_path = os.path.join(download.dir, download.name)
            command = f'"{sys.executable}" -m pip install --no-deps "{wheel_path}"'
            print(f"   📿 Executing: {command}")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            print(result.stdout)
            print(f"✅ Successfully installed {package_name}.")

        except subprocess.CalledProcessError as e:
            print(f"\n❌ Pip failed to install '{package_name}'.")
            print(f"   - Exit Code: {e.returncode}")
            print(f"   - Stderr: {e.stderr}")
            sys.exit(1)
        finally:
            if os.path.exists(wheel_path):
                print(f"🩹 Cleaning up: {wheel_path}")
                os.remove(wheel_path)

    else:
        print(f"❌ No compatible wheel found for '{package_name}' on your system.")

def cli():
    if len(sys.argv) == 1 or sys.argv[1] == '--help':
        print("Usage:\n  zipp [--help]\n  zipp list\n  zipp install <package-name> [package-name...]")
        sys.exit(0)

    command = sys.argv[1]

    if command == 'list':
        installed = installed_list()
        if not installed:
            print("No packages installed or could not read list.")
        else:
            print(f"{'Package':<30} Version")
            print("-" * 40)
            for name, version in sorted(installed.items()):
                print(f"{name:<30} {version}")

    elif command == 'install':
        if len(sys.argv) < 3:
            print("Error: 'install' command requires at least one package name.")
            print("Usage: zipp install <package-name> [package-name...]")
            sys.exit(1)

        for pkg in sys.argv[2:]:
            download_and_install(pkg)

        print("\nAll installations complete.")

if __name__ == '__main__':
    cli()
