#!/usr/bin/python3
# -*- coding: utf-8 -*-

from collections import OrderedDict
import sys
import os
import time
import shutil
import tempfile
import subprocess
import logging
import re
from pathlib import Path
import zipfile
import hashlib
import lzma
from typing import List
import concurrent.futures
import requests
import pyaxml
from apkpatcher.zipalign import zipalign

try:
    from lxml import etree
except ImportError:
    import xml.etree.ElementTree as etree


def new_logger(level: "logging._Level") -> logging.Logger:
    """Instanciate Logger

    Args:
        level (logging._Level): level of logger

    Returns:
        logging.Logger: new logger
    """
    logger = logging.getLogger("apkpatcher")

    class CustomFormatter(logging.Formatter):
        """Apkpatcher formatter
        """

        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        tmp_format = (
            "%(asctime)s - %(name)s [ %(levelname)s ] - %(message)s (%(filename)s:%(lineno)d)"
        )

        FORMATS = {
            logging.DEBUG: grey + tmp_format + reset,
            logging.INFO: grey + tmp_format + reset,
            logging.WARNING: yellow + tmp_format + reset,
            logging.ERROR: red + tmp_format + reset,
            logging.CRITICAL: bold_red + tmp_format + reset,
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter())
    logger.addHandler(ch)
    logger.setLevel(level)
    return logger


def plba(filename: str | Path, arch : str) -> str:
    """Filename with architecture

    Args:
        filename (str | Path): base filename
        arch (str): architecture

    Returns:
        str: return filename with architecture
    """
    p = Path(filename)
    return f"{p.parent}/{p.stem}_{arch}.so"


def download_smali(output_file: Path):
    """Download smali

    Args:
        output_file (Path): output location
    """
    version = "3.0.9"
    r = requests.get(
        f"https://github.com/baksmali/smali/releases/download/{version}/smali-{version}-fat-release.jar",
        timeout=30
    )
    with open(output_file, "wb") as f:
        f.write(r.content)


def download_baksmali(output_file: Path):
    """Download baksmali

    Args:
        output_file (Path): output location
    """
    version = "3.0.9"
    r = requests.get(
        f"https://github.com/baksmali/smali/releases/download/{version}/baksmali-{version}-fat-release.jar",
        timeout=30
    )
    with open(output_file, "wb") as f:
        f.write(r.content)


def get_latest_version_directory(base_path: Path) -> str | None:
    """Get latest version directory

    Args:
        base_path (Path): base path

    Returns:
        str | None: the latest version directory
    """
    try:
        from packaging.version import Version

        dirs = [d for d in base_path.iterdir() if d.is_dir()]
        version_dirs = [
            d.name for d in dirs if re.match(r"^[0-9]+\.[0-9]+\.[0-9]+(-rc[0-9]+)?$", d.name)
        ]
        latest_version = max(version_dirs, key=Version, default=None)
        return latest_version if latest_version else None
    except Exception:
        return None

class Manifest:
    
    def __init__(self, file: Path):
        self.__file : Path = file
        self.__xml = None
        self.__update : bool = False

    def read(self):
        if self.__xml is None:
            with open(self.__file, "rb") as f:
                # Read AXML and get XML object
                axml, _ = pyaxml.AXML.from_axml(f.read())
                self.__xml = axml.to_xml()
        return self.__xml
    
    def update(self, xml):
        self.__xml = xml
        self.__update = True

    def write(self):
        if self.__update:
            res_aml = pyaxml.axml.AXML()
            res_aml.from_xml(self.__xml)

            with open(self.__file, "wb") as fp_out:
                fp_out.write(res_aml.pack())
            self.__update = False


class Patcher:
    """Patcher

    Raises:
        ValueError: _description_
        ValueError: _description_
        ValueError: _description_
        when: _description_
        FileNotFoundError: _description_
        FileNotFoundError: _description_
        ValueError: _description_
        FileNotFoundError: _description_
        ValueError: _description_
    """

    ARCH_ARM = "arm"
    ARCH_ARM64 = "arm64"
    ARCH_X86 = "x86"
    ARCH_X64 = "x64"
    ARCH_X86_64 = "x86_64"

    DEFAULT_HOOKFILE_NAME = "libhook.js.so"
    DEFAULT_CONFIG_NAME = "generatedConfigFile.config"

    CONFIG_BIT = 1 << 0
    AUTOLOAD_BIT = 1 << 1

    INTERNET_PERMISSION = "android.permission.INTERNET"

    def __init__(
        self,
        apk: str | Path,
        version_buildtools: str = None,
        sdktools: str | Path = None,
        logger: logging.Logger | None = None,
        nb_jobs: int = 4,
    ):
        """
        Initialisation of patcher

        Parameters:
                    apk (str): path of the apk
                    sdktools (str): path of the sdktools for zipalign
                    version_buildtools (str): version_buildtools to choose the correct path of
                    logger (logging.Logger) logger

        """
        self.nb_jobs = nb_jobs
        self.logger: logging.Logger = None
        if logger is None:
            self.logger = new_logger(logging.INFO)
        else:
            self.logger = logger
        self.apk: Path = Path(apk)
        self.arch: str | None = None
        if sdktools is None:
            if "ANDROID_SDK_ROOT" in os.environ:
                sdktools = os.environ["ANDROID_SDK_ROOT"]
        if not sdktools is None:
            self.sdktools: Path = Path(sdktools)
        else:
            self.sdktools = None
        self.version: str = version_buildtools
        self.final_dir: OrderedDict[Path, Path] = OrderedDict()
        self._pause: bool = False
        self.plugin: Path | None = None
        self.entrypoint_smali_path: Path | None = None
        self.entrypoint_class: str | None = None

        self.debug_mode: bool = False

        self.keycertificate = Path("./apkpatcherkeystore").absolute()
        self.keyalias = "apkpatcheralias1"
        self.keypass = "password"

        self._keep_keycertificate = False

        self.v4_signature_file = None
        self.frida_downloaded: List[Path] = []
        self.use_download_frida = None

        self._need_full_extraction: bool = False

        self.hash_dict = {}

        jnius_lib_path = []
        if self.sdktools:
            if self.version is None:
                self.version = get_latest_version_directory(Path(f"{self.sdktools}/build-tools/"))
                if self.version is None:
                    self.logger.error("\nArgument version_buildtools is missing, you should add it")
                    self.logger.error("To know buildtools installed you can use: sdkmanager --list")
                    raise ValueError("version_buildtools is not set or incorrect")

            self.path_build_tools = Path(
                f"{self.sdktools}/build-tools/{self.version}/"
                if (self.sdktools and self.version)
                else ""
            )
            if not self.path_build_tools.exists():
                self.logger.error("\nArgument version_buildtools is missing, you should add it")
                self.logger.error("To know buildtools installed you can use: sdkmanager --list")
                raise ValueError("version_buildtools is not set or incorrect")
            jnius_lib_path.append(f"{self.path_build_tools}/lib/apksigner.jar")

        self.network_certificates: list[Path] = []
        import jnius_config

        smali_jar = Path(__file__).parent / "smali.jar"
        if not smali_jar.exists():
            download_smali(smali_jar)

        baksmali_jar = Path(__file__).parent / "baksmali.jar"
        if not baksmali_jar.exists():
            download_baksmali(baksmali_jar)

        jnius_lib_path.append(smali_jar.as_posix())
        jnius_lib_path.append(baksmali_jar.as_posix())

        jnius_config.set_classpath(*jnius_lib_path)
        if not "JAVA_HOME" in os.environ:
            try:
                # Run the command to get the properties
                result = subprocess.run(
                    ["java", "-XshowSettings:properties", "-version"],
                    stderr=subprocess.PIPE,
                    stdout=subprocess.DEVNULL,  # Redirect stdout to /dev/null
                    text=True,
                )
                # Filter the output to find the 'java.home' property
                for line in result.stderr.splitlines():
                    if "java.home" in line:
                        # Extract the value after the '='
                        java_home = line.split("=", 1)[1].strip()
                        os.environ["JAVA_HOME"] = java_home
                        break
            except FileNotFoundError:
                self.logger.error("Java is not installed or not found in PATH.")
        from jnius import autoclass, cast

        self.cast = cast
        self.smali = autoclass("com.android.tools.smali.smali.Main")
        self.baksmali = autoclass("com.android.tools.smali.baksmali.Main")

        self.File = autoclass("java.io.File")
        self.ArrayList = autoclass("java.util.ArrayList")
        self.Collections = autoclass("java.util.Collections")
        self.KeyStore = autoclass("java.security.KeyStore")
        self.FileInputStream = autoclass("java.io.FileInputStream")
        self.PrivateKey = autoclass("java.security.PrivateKey")

        if self.sdktools is None:
            self.ApkSigner_Builder = None
            self.SignerConfig_Builder = None
        else:
            self.ApkSigner_Builder = autoclass("com.android.apksig.ApkSigner$Builder")
            self.SignerConfig_Builder = autoclass(
                "com.android.apksig.ApkSigner$SignerConfig$Builder"
            )
        
        self.compression_level = 9
        self.compression_method = zipfile.ZIP_DEFLATED
        self.manifest = None

    def __del__(self):
        self.__finish_with_certificate()
        self.__remove_frida_downloaded()


    def set_compression(self, method : int, level : int):
        """set compression method for zip level


        Args:
            method (int): one of these method ( zipfile.ZIP_STORED,  zipfile.ZIP_DEFLATED, zipfile.ZIP_BZIP2, zipfile.ZIP_LZMA)
            level (int): The compresslevel parameter controls the compression level to use when writing files to the archive. When using ZIP_STORED or ZIP_LZMA it has no effect. When using ZIP_DEFLATED integers 0 through 9 are accepted (see zlib for more information). When using ZIP_BZIP2 integers 1 through 9 are accepted (see bz2 for more information).
        """
        self.compression_method = method
        self.compression_level = level

    @property
    def need_full_extraction(self) -> bool:
        """need full extraction

        Returns:
            bool: return true if needed full extraction
        """
        if self._need_full_extraction or not self.plugin is None or self.pause:
            return True
        return False

    @need_full_extraction.setter
    def need_full_extraction(self, value: bool):
        """force need full extraction

        Args:
            value (bool): value True or False
        """
        self._need_full_extraction = value

    def missing_sdktools(self):
        """raise an error when sdktools is missing

        Raises:
            ValueError: The error
        """
        self.logger.error(
            "\nArgument sdktools is missing, you should add '-s /usr/lib/android-sdk' or ANDROID_SDK_ROOT environment variable is not set"
        )
        self.logger.error(
            "If you didn't have installed sdktools follow this tutorial: https://asthook.ci-yow.com/how.install.html#setup-sdktools"
        )
        raise ValueError("sdktools is not set is not set or incorrect")

    ################################################################################
    #                                                                              #
    #            CERTIFICATES                                                      #
    #                                                                              #
    ################################################################################

    def add_network_certificate(self, cert: Path):
        """add network certificate

        Args:
            cert (Path): the certificate to inject
        """
        self.network_certificates.append(cert)

    def set_use_download_frida(self, frida_version: str):
        """Specify frida version to download

        Args:
            frida_version (str): frida version
        """
        self.use_download_frida = frida_version

    def __remove_frida_downloaded(self):
        """_summary_
        """
        for f in self.frida_downloaded:
            if f.exists():
                f.unlink()

    def download_frida(self) -> str | None:
        """Download frida binary

        Returns:
            str | None: return the name of lib
        """
        base_url = "https://github.com/frida/frida/releases/download/"
        if not self.arch:
            architectures = [
                self.ARCH_ARM,
                self.ARCH_ARM64,
                self.ARCH_X86,
                self.ARCH_X86_64,
            ]
        else:
            if self.arch == self.ARCH_X64:
                architectures = [self.ARCH_X86_64]
            else:
                architectures = [self.arch]
        self.frida_downloaded: List[Path] = []

        for arch in architectures:
            filename = f"frida-gadget-{self.use_download_frida}-android-{arch}.so.xz"
            url = f"{base_url}{self.use_download_frida}/{filename}"
            output_file = Path(f"libfrida-gadget_{arch}.so").absolute()

            try:
                # Download the file
                self.logger.info("Downloading %s...", url)
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Save the compressed file
                compressed_path = Path(filename)
                with open(compressed_path, "wb") as f:
                    f.write(response.content)

                # Uncompress the file
                self.logger.info("Uncompressing %s...", compressed_path)
                with lzma.open(compressed_path, "rb") as xz_file:
                    with open(output_file, "wb") as out_file:
                        out_file.write(xz_file.read())

                # Remove the compressed file
                compressed_path.unlink()
                self.frida_downloaded.append(output_file)

            except requests.HTTPError as e:
                self.logger.error("Failed to download %s : %s", url, e)
            except lzma.LZMAError as e:
                self.logger.error("Failed to uncompress %s: %s", filename, e)

        if len(self.frida_downloaded) == 1:
            return self.frida_downloaded[0]
        if self.frida_downloaded:
            return self.frida_downloaded[0].parent / "libfrida-gadget"
        return None

    def inject_custom_network_certificate(self, rsc, path_network: str) -> bool:
        """Inject custom network certificate
        """
        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))
        netsec_path = main_dir / path_network
        ca_path = main_dir / "res/my_ca"

        # create directory if didn't exist 
        netsec_path.parent.mkdir(parents=True, exist_ok=True)
        ca_path.parent.mkdir(parents=True, exist_ok=True)

        _id = rsc.add_id_public(
            rsc.get_packages()[0], "raw", "network_security_config_ca", "res/my_ca"
        )

        buf = f"""
        <network-security-config>
            <base-config cleartextTrafficPermitted="true">
                <trust-anchors>
                    <certificates src="system"/>
                    <certificates src="user"/>
                    <certificates src="@{hex(_id)[2:]}"/>
                </trust-anchors>
            </base-config>
        </network-security-config>
        """

        root = etree.fromstring(buf)
        res_aml = pyaxml.axml.AXML()
        res_aml.from_xml(root)
        with open(netsec_path, "wb") as f:
            f.write(res_aml.pack())

        for cert in self.network_certificates:
            shutil.copyfile(cert, ca_path)
        self.logger.info("Custom certificate was injected inside the apk")
        return True

    def create_security_config_xml(self, path_network: str) -> bool:
        """Create security config file for add certificate

        Args:
            path_network (str): path network
        """
        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))
        netsec_path = main_dir / path_network

        # create directory if didn't exist 
        netsec_path.parent.mkdir(parents=True, exist_ok=True)

        buf = """
        <network-security-config>
            <base-config cleartextTrafficPermitted="true">
                <trust-anchors>
                    <certificates src="system"/>
                    <certificates src="user"/>
                </trust-anchors>
            </base-config>
        </network-security-config>
        """
        root = etree.fromstring(buf)
        res_aml = pyaxml.axml.AXML()
        res_aml.from_xml(root)
        with open(netsec_path, "wb") as f:
            f.write(res_aml.pack())

        self.logger.info("The network_security_config.xml file was created!")
        return True

    def enable_user_certificates(self, rsc: pyaxml.ARSC):
        """Enable user certificate

        Args:
            rsc (pyaxml.ARSC): return ARSC file
            return 2 if rsc modified
            return 1 if success
            return 0 if failed
        """
        path_network, ret = self.inject_user_certificates_label(rsc)
        if path_network:
            if self.network_certificates:
                if self.inject_custom_network_certificate(rsc, path_network):
                    return 2
                return 0
            if self.create_security_config_xml(path_network):
                return ret
        return 0

    def inject_user_certificates_label(self, rsc: pyaxml.ARSC) -> (str, int):
        """Inject a proxy certificate directly inside the application

        Args:
            rsc (pyaxml.ARSC): ARSC file (resource file of Android)

        Raises:
            FileNotFoundError: raise when manifest is not found

        Returns:
            str: return the path of network file
        """
        ret = 1
        self.logger.info("Injecting Network Security label to accept user certificates...")
        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))
        manifest_path = main_dir / "AndroidManifest.xml"

        if not manifest_path.is_file():
            self.logger.error("Couldn't find the Manifest file. Something is wrong with the apk!")
            raise FileNotFoundError("manifest not found")

        _id = rsc.get_id_public(rsc.get_packages()[0], "xml", "network_security_config")
        if not _id:
            path_network: str = "res/network_security_config.xml"
            _id = rsc.add_id_public(
                rsc.get_packages()[0],
                "xml",
                "network_security_config",
                path_network,
            )
            ret = 2
        else:
            _id, path_network = _id
            path_network = pyaxml.StringBlocks(proto=rsc.proto.stringblocks).decode_str(
                path_network
            )

        xml = self.manifest.read()
        application = xml.findall("./application")[0]
        application.attrib[
            "{http://schemas.android.com/apk/res/android}networkSecurityConfig"
        ] = f"@{hex(_id)[2:]}"
        self.manifest.update(xml)

        self.logger.info("The Network Security label was added!")

        return (path_network, ret)

    ################################################################################
    #                                                                              #
    #                        PERMISSIONS                                           #
    #                                                                              #
    ################################################################################

    def has_permission(self, permission_name: str) -> bool:
        """
        Check if the apk have 'permission_name' as permission

        Parameters:
                    permission_name (str): name of the permission with format:
                    android.permission.XXX

        Returns:
                has_permission (bool): permission is present
        """
        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))
        manifest_path = main_dir / "AndroidManifest.xml"

        if not manifest_path.is_file():
            self.logger.error("Couldn't find the Manifest file. Something is wrong with the apk!")
            raise FileNotFoundError("manifest not found")
        
        xml = self.manifest.read()
        # Search over all the application permissions
        android_name = "{http://schemas.android.com/apk/res/android}name"
        for permission in xml.findall("./uses-permission"):
            if permission.attrib[android_name] == permission_name:
                self.logger.info(
                    "The app %s has the permission '%s'", self.apk, permission_name
                )
                return True

        self.logger.info("The app %s doesn't have the permission '%s'", self.apk, permission_name)
        return False

    def inject_permission_manifest(self, permission: str):
        """
        Inject permission on the Manifest
        """
        self.logger.info("Injecting permission %s in Manifest...", permission)

        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))
        manifest_path = main_dir / "AndroidManifest.xml"

        if not manifest_path.is_file():
            self.logger.error("Couldn't find the Manifest file. Something is wrong with the apk!")
            return False

        xml = self.manifest.read()
        
        for i, elt in enumerate(xml):  # range(len(xml)):
            if elt.tag in ("application", "uses-permission"):
                newperm = etree.Element("uses-permission")
                newperm.attrib["{http://schemas.android.com/apk/res/android}name"] = permission
                xml.insert(i, newperm)
                self.manifest.update(xml)
                return True
            
        self.logger.error("resource file could not be found")
        return False

    ################################################################################
    #                                                                              #
    #                EXTRACT REPACK APK                                            #
    #                                                                              #
    ################################################################################

    def extract_dex(self, dex_file : Path):
        """Extract Dex

        Args:
            dex_file (Path): the dexfile to extract
        """
        # Define the output directory
        output_dir = dex_file.parent / ("smali_" + dex_file.stem)

        self.logger.info("Processing %s...", dex_file)

        self.baksmali.main(
            [
                "d",
                dex_file.as_posix(),
                "-o",
                output_dir.as_posix(),
            ]
        )
        self.compute_directory_hashes(output_dir)

    def extract_apk(self, apk: Path, final_dir: Path):
        """
        Extract the apk on the temporary folder
        """

        self.logger.info("Extracting %s (without resources) to %s", apk, final_dir)
        # Ensure the extraction directory exists
        final_dir.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(apk.absolute().as_posix(), "r") as zip_ref:
                zip_ref.extractall(final_dir.absolute().as_posix())
                self.logger.info("Extraction complete.")
        except zipfile.BadZipFile as e:
            self.logger.error("Error: The file is not a valid zip file: %s", e)
        except Exception as e:
            self.logger.error("Unexpected error during extraction: %s", e)

        # Iterate over files in the directory
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.nb_jobs) as executor:
            futures = list(
                map(
                    lambda x: executor.submit(self.extract_dex, x),
                    [dex_file for dex_file in final_dir.rglob("*.dex") if not dex_file.is_dir()],
                )
            )
            concurrent.futures.wait(futures)

    def add_certificate(self, keycertificate: Path | str, keyalias: str, keypass: str):
        """Add signature certificate

        Args:
            keycertificate (Path | str): certificate path
            keyalias (str): aliasname
            keypass (str): password
        """
        self.keycertificate = Path(keycertificate)
        self.keyalias = keyalias
        self.keypass = keypass
        self.keep_certificate()

    def keep_certificate(self):
        """keep certificate after use it"""
        self._keep_keycertificate = True

    def enable_v4_signature(self, file: Path | str):
        """enable v4 signature

        Args:
            file (Path | str): v4_signature file
        """
        self.v4_signature_file = Path(file)

    def sign_and_zipalign(self, apk_path: Path, splits_apk: List[Path]):
        """
        sign and zipalign file
        """

        if self.ApkSigner_Builder is None or self.SignerConfig_Builder is None:
            self.missing_sdktools()
            return 1

        self.logger.info("Optimizing with zipalign... %s", apk_path)

        tmp_target_file: Path = apk_path.rename(
            apk_path.with_name(apk_path.stem.replace(".apk", "_tmp.apk"))
        )

        zipalign(tmp_target_file, apk_path)

        tmp_target_file.unlink()

        if not self.keycertificate.exists():
            self.logger.info("Generating a random key...")
            subprocess.call(
                f"keytool -genkey -keyalg RSA -keysize 2048 -validity 700 -noprompt -alias {self.keyalias} -dname "
                f'"CN=apk.patcher.com, OU=ID, O=APK, L=Patcher, S=Patch, C=BR" -keystore {self.keycertificate} '
                f"-storepass {self.keypass} -keypass {self.keypass} 2> /dev/null",
                shell=True,
            )

        self.logger.info("Signing the patched apk... %s", apk_path)

        keyStore = self.KeyStore.getInstance("JKS")
        fis = self.FileInputStream(self.keycertificate.as_posix())
        keyStore.load(fis, self.keypass)

        privateKey = keyStore.getKey(self.keyalias, self.keypass)
        cert = keyStore.getCertificate(self.keyalias)

        l = self.ArrayList()
        l.add(self.cast("java.security.cert.X509Certificate", cert))
        signerConfig = self.SignerConfig_Builder(
            "signer", self.cast("java.security.PrivateKey", privateKey), l
        )
        signerconfig = signerConfig.build()

        tmp_target_file: Path = apk_path.rename(
            apk_path.with_name(apk_path.stem.replace(".apk", "_tmp.apk"))
        )

        signerBuilder = self.ApkSigner_Builder(self.Collections.singletonList(signerconfig))
        signerBuilder.setInputApk(self.File(tmp_target_file.as_posix()))
        signerBuilder.setOutputApk(self.File(apk_path.as_posix()))
        signerBuilder.setV1SigningEnabled(True)
        signerBuilder.setV2SigningEnabled(True)
        signerBuilder.setV3SigningEnabled(True)
        if self.debug_mode:
            signerBuilder.setDebuggableApkPermitted(True)
        if self.v4_signature_file:
            signerBuilder.setV4SigningEnabled(True)
            signerBuilder.setV4SignatureOutputFile(self.v4_signature_file.as_posix())

        apkSigner = signerBuilder.build()
        apkSigner.sign()

        tmp_target_file.unlink()

        for split in splits_apk:
            tmp_split_file: Path = split.with_name(split.name.replace(".apk", "_new_signed.apk"))
            split_new_name = tmp_split_file.absolute().as_posix()
            signerBuilder = self.ApkSigner_Builder(self.Collections.singletonList(signerconfig))
            signerBuilder.setInputApk(self.File(split.absolute().as_posix()))
            signerBuilder.setOutputApk(self.File(split_new_name))
            signerBuilder.setV1SigningEnabled(True)
            signerBuilder.setV2SigningEnabled(True)
            signerBuilder.setV2SigningEnabled(True)
            signerBuilder.setV3SigningEnabled(True)
            if self.debug_mode:
                signerBuilder.setDebuggableApkPermitted(True)
            if self.v4_signature_file:
                signerBuilder.setV4SigningEnabled(True)
                signerBuilder.setV4SignatureOutputFile(self.v4_signature_file.as_posix())

            apkSigner = signerBuilder.build()
            apkSigner.sign()

        self.logger.info("The apk %s was signed!", apk_path)
        self.logger.info("The file was optimized!")

    def __finish_with_certificate(self):
        if not self._keep_keycertificate:
            if self.keycertificate.exists():
                self.keycertificate.unlink()

    @property
    def pause(self) -> bool:
        """get Pause status

        Returns:
            bool: pause
        """
        return self._pause

    @pause.setter
    def pause(self, pause: bool) -> None:
        """enable a pause during the process to edit the application

        Args:
            pause (bool): pause parameter
        """
        self._pause = pause

    def set_plugin(self, plugin: str | Path) -> None:
        """set a plugin

        Args:
            plugin (str | Path): _description_
        """
        self.plugin = Path(plugin).absolute()

    def calculate_sha256(self, file_path: Path):
        """
        Calculate the SHA-256 hash of a file.

        :param file_path: Path to the file.
        :return: SHA-256 hash as a hexadecimal string.
        """
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def compute_directory_hashes(self, base_directory, hash_dict: dict | None = None) -> None:
        """
        Compute SHA-256 hashes for all files in a directory and store them in a nested dictionary.

        :param base_directory: Path to the base directory.
        """
        base_path = Path(base_directory)
        if not base_path.is_dir():
            raise ValueError(f"Provided path is not a directory: {base_directory}")

        if hash_dict is None:
            hash_dict = self.hash_dict

        class_name = base_path.name  # Use the base directory name as the class_name

        for file_path in base_path.rglob("*"):  # Recursively iterate through all files
            if file_path.is_file():
                relative_path = file_path.relative_to(base_path).as_posix()
                file_hash = self.calculate_sha256(file_path)

                # Add to the dictionary
                if class_name not in hash_dict:
                    hash_dict[class_name] = {}
                hash_dict[class_name][relative_path] = file_hash

    def __check_if_dex_is_modified(self, class_dir: Path) -> bool:

        old_files = set()
        new_files = set()

        if not class_dir.name in self.hash_dict:
            return True

        for path, hash_value in self.hash_dict[class_dir.name].items():
            old_files.add((path, hash_value))

        new_files_dict = {}
        self.compute_directory_hashes(class_dir, new_files_dict)

        for path, hash_value in new_files_dict[class_dir.name].items():
            new_files.add((path, hash_value))

        if len(new_files - old_files) != 0 or len(old_files - new_files) != 0:
            self.logger.info("Some change has been detected in %s", class_dir)
            return True
        return False

    def repackage_dex(self, classes_dir: Path) -> bool:
        """Repackage Dex

        Args:
            classes_dir (Path): classes directory

        Returns:
            bool: _description_
        """
        dex_file_name = f"{classes_dir.name[6:]}.dex"
        dex_file_path: Path = classes_dir.parent / dex_file_name

        self.logger.info("Processing %s...", classes_dir)
        if self.__check_if_dex_is_modified(classes_dir):
            dex_file_path.unlink()
            self.smali.main(
                [
                    "a",
                    classes_dir.as_posix(),
                    "-o",
                    dex_file_path.as_posix(),
                ]
            )
            if not dex_file_path.exists():
                self.logger.error("Some error has been detected in smali code")
                return False
        shutil.rmtree(classes_dir)
        return True

    def repackage_apk(self, target_file: Path | None = None) -> Path | None:
        """
        repackage the apk

        Parameters:
                    - target_file (str) : the path of the new apk created if
                      none, a new apk will be created with suffix "_patched.apk"
        """
        if self.plugin:
            args = [self.plugin.as_posix()]
            args.extend([dir.as_posix() for dir in self.final_dir.values()])
            result = subprocess.run(args, capture_output=True, text=True)
            self.logger.info("NORMAL output")
            self.logger.info(result.stdout)
            if result.returncode != 0:
                self.logger.error("ERROR output")
                self.logger.error(result.stderr)
                sys.exit(1)
        if self.pause:
            self.logger.info(
                "You can modify the apk here: %s",
                next(iter(self.final_dir.values())).parent
            )
            input()
        if target_file is None:
            target_file = self.apk.with_name(self.apk.name.replace(".apk", "_patched.apk"))

            if target_file.is_file():
                timestamp = str(time.time()).replace(".", "")
                new_file_name = target_file.with_name(f"{target_file.stem}_{timestamp}.apk")
                target_file = new_file_name

        self.logger.info("Repackaging apk to %s", target_file)
        self.logger.info("This may take some time...")

        # Iterate over directories starting with "classes"
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.nb_jobs) as executor:
            futures = list(
                map(
                    lambda x: executor.submit(self.repackage_dex, x),
                    (
                        sub_d
                        for d in self.final_dir.values()
                        if d.exists()
                        for sub_d in d.iterdir()
                        if sub_d.is_dir() and sub_d.name.startswith("smali_")
                    ),
                )
            )
            concurrent.futures.wait(futures)
            for future in futures:
                if not future.result():
                    return None

        # Zip the contents of the parent directory

        main_app: bool = True
        new_final_dir: OrderedDict[Path, Path] = OrderedDict()
        for apk_path, directory in self.final_dir.items():
            if main_app:
                zip_file_path = target_file.absolute()
                main_app = False
            else:
                zip_file_path: Path = apk_path.with_name(
                    apk_path.name.replace(".apk", "_new_signed.apk")
                )
            if not directory.exists():
                shutil.copyfile(apk_path, zip_file_path)
                continue
            self.logger.info("Creating zip archive: %s", zip_file_path)
            new_final_dir[zip_file_path] = directory
            try:
                with zipfile.ZipFile(zip_file_path, "w", compression=self.compression_method, compresslevel=self.compression_level) as zipf:
                    for file in directory.rglob("*"):
                        if file.relative_to(directory).name == "resources.arsc":
                            zipf.write(file, arcname=file.relative_to(directory), compress_type=zipfile.ZIP_STORED)
                        else:
                            zipf.write(file, arcname=file.relative_to(directory))
                self.logger.info("Successfully created zip archive: %s", zip_file_path)
            except Exception as e:
                self.logger.error("Error creating zip archive: %s", e)
                return None
            self.final_dir = new_final_dir

        return target_file

    ################################################################################
    #                                                                              #
    #                INJECT NATIVE CODE                                            #
    #                                                                              #
    ################################################################################

    def get_entrypoint_class_name(self) -> str | None:
        """
        get the class name of the entrypoint
        """
        entrypoint_class = None
        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))
        manifest_path = main_dir / "AndroidManifest.xml"

        if not manifest_path.is_file():
            self.logger.error("Couldn't find the Manifest file. Something is wrong with the apk!")
            raise FileNotFoundError("manifest not found")

        xml = self.manifest.read()

        android_name = "{http://schemas.android.com/apk/res/android}name"
        # Look over the application wrapper
        for application in xml.findall("./application"):
            if android_name in application.attrib:
                entrypoint_class = application.attrib[android_name]
            

        # Look over all the activities and try to find either one with MAIN as action
        if not entrypoint_class:
            for activity in xml.findall("./application/activity"):
                is_main = False
                for action in activity.findall("intent-filter/action"):
                    if action.attrib[android_name] == "android.intent.action.MAIN":
                        is_main = True
                        break
                if is_main:
                    for category in activity.findall("intent-filter/category"):
                        if category.attrib[android_name] == "android.intent.category.LAUNCHER":
                            entrypoint_class = activity.attrib[android_name]
                            break

        # Do the same for activities alias in case we did not find the main activity
        if not entrypoint_class:
            android_target_activity = (
                "{http://schemas.android.com/apk/res/android}targetActivity"
            )
            for alias in xml.findall("./application/activity-alias"):
                is_main = False
                for action in alias.findall("intent-filter/action"):
                    if action.attrib[android_name] == "android.intent.action.MAIN":
                        is_main = True
                        break
                if is_main:
                    for category in alias.findall("intent-filter/category"):
                        if category.attrib[android_name] == "android.intent.category.LAUNCHER":
                            entrypoint_class = alias.attrib[android_target_activity]
                            break

        # Check if entry point is relative, if so search in the Manifest package
        if entrypoint_class is None:
            self.logger.error("Fail to find entrypoint class")
            return entrypoint_class
        if entrypoint_class.startswith("."):
            entrypoint_class = xml.attrib["package"] + entrypoint_class

        if entrypoint_class is None:
            self.logger.error("Fail to find entrypoint class")

        return entrypoint_class

    def get_package(self) -> str:
        xml = self.manifest.read()
        return xml.attrib["package"]

    def get_entrypoint_smali_path(self) -> Path | None:
        """
        get the path of apk entrypoint on the smali files
        """
        entrypoint_final_path = None
        if self.entrypoint_class is None:
            raise ValueError("entrypoint class is None")

        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))

        for file in main_dir.iterdir():
            if file.name.startswith("smali"):
                entrypoint_tmp = (
                    main_dir / file / (self.entrypoint_class.replace(".", "/") + ".smali")
                )
                if entrypoint_tmp.is_file():
                    entrypoint_final_path = entrypoint_tmp
                    break
        
        if entrypoint_final_path is None:
            for file in main_dir.iterdir():
                if file.name.startswith("smali"):
                    entrypoint_tmp = (
                        main_dir / file / ((self.package + "." + self.entrypoint_class).replace(".", "/") + ".smali")
                    )
                    if entrypoint_tmp.is_file():
                        entrypoint_final_path = entrypoint_tmp
                        break

        if entrypoint_final_path is None:
            self.logger.error("Couldn't find the application entrypoint")
            sys.exit(1)
        else:
            self.logger.info("Found application entrypoint at %s", entrypoint_final_path)

        return entrypoint_final_path

    def insert_lib_loader(self, lib_name="libfrida-gadget"):
        """
        inject snippet to load lib in smali code
        """
        if not lib_name.startswith("lib"):
            self.logger.error(f"Library {lib_name} didn't begin with \"lib\"")
            return False
        lib_name = lib_name[3:]
        partial_injection_code = """
    const-string v0, "<LIBINJECTED>"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

        """.replace(
            "<LIBINJECTED>", lib_name
        )

        full_injection_code = """
.method static constructor <clinit>()V
    .locals 1

    .prologue
    const-string v0, "<LIBINJECTED>"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    return-void
.end method
        """.replace(
            "<LIBINJECTED>", lib_name
        )

        with open(self.entrypoint_smali_path, "r", encoding="utf-8") as smali_file:
            content = smali_file.read()

            if lib_name in content:
                self.logger.info("The lib is already in the entrypoint. Skipping...")
                return False

            direct_methods_start_index = content.find("# direct methods")
            direct_methods_end_index = content.find("# virtual methods")

            if direct_methods_start_index == -1 and direct_methods_end_index == -1:
                self.logger.error("Could not find direct methods.")
                return False

            class_constructor_start_index = content.find(
                ".method static constructor <clinit>()V",
                direct_methods_start_index,
                direct_methods_end_index,
            )

            if class_constructor_start_index == -1:
                has_class_constructor = False
            else:
                has_class_constructor = True

            class_constructor_end_index = -1
            if has_class_constructor:
                class_constructor_end_index = content.find(
                    ".end method",
                    class_constructor_start_index,
                    direct_methods_end_index,
                )

                if has_class_constructor and class_constructor_end_index == -1:
                    self.logger.error("Could not find the end of class constructor.")
                    return False

            prologue_start_index = -1
            if has_class_constructor:
                prologue_start_index = content.find(
                    ".prologue",
                    class_constructor_start_index,
                    class_constructor_end_index,
                )

            no_prologue_case = False
            locals_start_index = -1

            # check for locals
            if has_class_constructor and prologue_start_index == -1:
                no_prologue_case = True

                locals_start_index = content.find(
                    ".locals ",
                    class_constructor_start_index,
                    class_constructor_end_index,
                )

            if not no_prologue_case or locals_start_index != -1:
                locals_end_index = -1
                if no_prologue_case:
                    locals_end_index = locals_start_index + len("locals ")  # X')
                    x = re.search(r"^ *\d+", content[locals_end_index + 1 :])
                    locals_end_index += x.span()[1]
            else:

                # check for registers
                if has_class_constructor and prologue_start_index == -1:
                    no_prologue_case = True

                    locals_start_index = content.find(
                        ".registers ",
                        class_constructor_start_index,
                        class_constructor_end_index,
                    )

                    if no_prologue_case and locals_start_index == -1:
                        self.logger.error(
                            'Has class constructor. No prologue case, but no "locals 0" found.'
                        )
                        return False

                if not no_prologue_case or locals_start_index != -1:
                    locals_end_index = -1
                    if no_prologue_case:
                        locals_end_index = locals_start_index + len("registers ")  # X')
                        x = re.search(r"^ *\d+", content[locals_end_index + 1 :])
                        locals_end_index += x.span()[1]

            prologue_end_index = -1
            if has_class_constructor and prologue_start_index > -1:
                prologue_end_index = prologue_start_index + len(".prologue") + 1

            if has_class_constructor:
                if no_prologue_case:
                    new_content = content[0:locals_end_index]

                    if content[locals_end_index] == "0":
                        new_content += "1"
                    else:
                        new_content += content[locals_end_index]

                    new_content += "\n\n    .prologue"
                    new_content += partial_injection_code
                    new_content += content[locals_end_index + 1 :]
                else:
                    new_content = content[0:prologue_end_index]
                    new_content += partial_injection_code
                    new_content += content[prologue_end_index:]
            else:
                tmp_index = direct_methods_start_index + len("# direct methods") + 1
                new_content = content[0:tmp_index]
                new_content += full_injection_code
                new_content += content[tmp_index:]

        # The newContent is ready to be saved

        self.entrypoint_smali_path.write_text(new_content)

        self.logger.info("Lib loader was injected in the entrypoint smali file!")

        return True

    def create_lib_arch_folders(self, arch):
        """
        make lib folder in the apk to put native lib
        """
        # noinspection PyUnusedLocal
        sub_dir = None
        sub_dir_2 = None

        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))

        libs_path = main_dir / "lib"

        if not libs_path.is_dir():
            self.logger.info('There is no "lib" folder. Creating...')
            libs_path.mkdir(parents=True, exist_ok=True)

        if arch == self.ARCH_ARM:
            sub_dir = libs_path / "armeabi"
            sub_dir_2 = libs_path / "armeabi-v7a"

        elif arch == self.ARCH_ARM64:
            sub_dir = libs_path / "arm64-v8a"

        elif arch == self.ARCH_X86:
            sub_dir = libs_path / "x86"

        elif arch == self.ARCH_X64:
            sub_dir = libs_path / "x86_64"

        else:
            self.logger.error("Couldn't create the appropriate folder with the given arch.")
            return []

        if not sub_dir.is_dir():
            self.logger.info("Creating folder %s", sub_dir)
            sub_dir.mkdir(parents=True, exist_ok=True)

        if arch == self.ARCH_ARM:
            if not sub_dir_2.is_dir():
                self.logger.info("Creating folder %s", sub_dir_2)
                sub_dir_2.mkdir(parents=True, exist_ok=True)

        if arch == self.ARCH_ARM:
            return [sub_dir, sub_dir_2]
        return [sub_dir]

    def check_libextract(self) -> bool:
        """check if extractNativeLibs is enable and active it

        Returns:
            bool: return False if we didn't find manifest
        """
        self.logger.info("check if lib is extractable")

        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))

        manifest_path = main_dir / "AndroidManifest.xml"

        if not manifest_path.is_file():
            self.logger.error("Couldn't find the Manifest file. Something is wrong with the apk!")
            return False

        etree_xml = self.manifest.read()
        extract_native = etree_xml.findall(
            "./application/[@{http://schemas.android.com/apk/res/android}extractNativeLibs='false']"
        )
        if len(extract_native) > 0:
            extract_native[0].attrib[
                "{http://schemas.android.com/apk/res/android}extractNativeLibs"
            ] = "true"
            self.manifest.update(etree_xml)
        return True

    def insert_lib(
        self,
        gadget_path: str | Path,
        arch: str,
        dst : str | Path,
        config_file_path=None,
        auto_load_script_path=None,
    ):
        """
        Insert native lib inside the apk

        Parameters:
                    - gadget_path (str): the path of the gadget to insert
        """
        if isinstance(gadget_path, str):
            gadget_path = Path(gadget_path)
        if isinstance(dst, str):
            dst = Path(dst)
        arch_folders = self.create_lib_arch_folders(arch)

        if not arch_folders:
            self.logger.error("Some error occurred while creating the libs folders")
            return False

        for folder in arch_folders:
            if config_file_path and auto_load_script_path:
                self.delete_existing_gadget(
                    folder, gadget_path.name, delete_custom_files=self.CONFIG_BIT | self.AUTOLOAD_BIT
                )

            elif config_file_path and not auto_load_script_path:
                self.delete_existing_gadget(folder, gadget_path.name, delete_custom_files=self.CONFIG_BIT)

            elif auto_load_script_path and not config_file_path:
                self.delete_existing_gadget(folder, gadget_path.name, delete_custom_files=self.AUTOLOAD_BIT)

            else:
                self.delete_existing_gadget(folder, gadget_path.name, delete_custom_files=0)

            target_gadget_path = folder /  dst.name

            self.logger.info("Copying gadget to %s", target_gadget_path)

            shutil.copyfile(gadget_path, target_gadget_path)

            if config_file_path:
                target_config_path = target_gadget_path.replace(".so", ".config.so")

                self.logger.info("Copying config file to %s", target_config_path)
                shutil.copyfile(config_file_path, target_config_path)

            if auto_load_script_path:
                target_autoload_path = target_gadget_path.replace(
                    gadget_path.name, self.DEFAULT_HOOKFILE_NAME
                )

                self.logger.info("Copying auto load script file to %s", target_autoload_path)
                shutil.copyfile(auto_load_script_path, target_autoload_path)

        return True

    def delete_existing_gadget(self, arch_folder: Path, lib_name : str, delete_custom_files: int = 0):
        """
        delete existing gadget inside the apk
        """
        gadget_path = arch_folder / lib_name

        if gadget_path.is_file():
            gadget_path.unlink()

        if delete_custom_files & self.CONFIG_BIT:
            config_file_path: Path = arch_folder / self.DEFAULT_CONFIG_NAME

            if config_file_path.is_file():
                config_file_path.unlink()

        if delete_custom_files & self.AUTOLOAD_BIT:
            hookfile_path: Path = arch_folder / self.DEFAULT_HOOKFILE_NAME

            if hookfile_path.is_file():
                hookfile_path.unlink()

    ################################################################################
    #                                                                              #
    #                PATCHING                                                      #
    #                                                                              #
    ################################################################################

    def set_arch(self, arch: str):
        """set architecture of target phone where apk would be installed

        Args:
            arch (str): architecture
        """
        self.arch = arch

    def set_debug(self):
        """set debug mode"""
        self.debug_mode = True

    def enable_debug_mode(self) -> bool:
        """Enable debug mode

        Returns:
            bool: success to enable debug mode
        """
        self.logger.info("Injecting debuggable in Manifest...")

        if not bool(self.final_dir):
            self.logger.error("self.final_dir is empty")
            return False
        main_dir = next(iter(self.final_dir.values()))

        manifest_path = main_dir / "AndroidManifest.xml"

        if not manifest_path.is_file():
            self.logger.error("Couldn't find the Manifest file. Something is wrong with the apk!")
            return False

        xml = self.manifest.read()

        debuggable = "{http://schemas.android.com/apk/res/android}debuggable"
        application = xml.find("./application")

        # keep the order
        ordered_attrib = OrderedDict(application.attrib)

        # create the attribute and set a temporary position
        new_attrib = (debuggable, "true")
        position = -1

        # element that should be before debuggable
        element_should_before = [
            "{http://schemas.android.com/apk/res/android}theme",
            "{http://schemas.android.com/apk/res/android}label",
            "{http://schemas.android.com/apk/res/android}icon",
        ]

        i = 0
        for k in ordered_attrib.keys():
            i += 1
            if k in element_should_before:
                position = i  # update position

        # insert debuggable
        items = list(ordered_attrib.items())
        if position != -1:
            items.insert(position, new_attrib)
        else:
            items.append(new_attrib)

        # update attributes
        application.attrib.clear()
        application.attrib.update(OrderedDict(items))
        self.manifest.update(xml)
    
        return True

    def __init_final_dir(self, directory: Path, main_apk: Path, splits_apk: List[Path]):
        """Initialise final_dir

        Args:
            directory (Path): directory base
            main_apk (Path): main APK
            splits_apk (List[Path]): splits APK
        """
        self.final_dir.clear()
        self.final_dir[main_apk] = Path(f"{directory.absolute()}/{main_apk.stem}")
        for split in splits_apk:
            self.final_dir[split] = Path(f"{directory.absolute()}/{split.stem}")

    def patching(
        self,
        gadget_to_use: str | Path | None = None,
        output_file: Path | None = None,
        user_certificate: bool = False,
        splits_apk: list[Path] | None = None,
        entrypoint=None,
        permissions: list[str] = None,
    ) -> bool:
        """
        patch the apk with gadget 'gadget_to_use'
        """
        if isinstance(gadget_to_use, str):
            gadget_to_use = Path(gadget_to_use)
        if splits_apk is None:
            splits_apk = []
        if len(self.network_certificates) > 0:
            user_certificate = True
        if not self.apk.is_file():
            self.logger.error("The file %s couldn't be found!", self.apk)
            return False

        # Create tempory file
        with tempfile.TemporaryDirectory() as tmp_dir:
            apk_name = Path(self.apk).stem
            self.__init_final_dir(Path(tmp_dir), self.apk, splits_apk)

            main_dir = next(iter(self.final_dir.values()))
            manifest_path = main_dir / "AndroidManifest.xml"
            self.manifest = Manifest(manifest_path)

            # download frida-gadget if needed
            if gadget_to_use is None and self.use_download_frida:
                gadget_to_use = self.download_frida()

            # extract the apk on temporary folder
            if not self.need_full_extraction:
                self.extract_apk(self.apk, next(iter(self.final_dir.values())))
            else:
                for apk_name, directory in self.final_dir.items():
                    self.extract_apk(apk_name, directory)

            if permissions:
                for permission in permissions:
                    has_permission = self.has_permission(permission)
                    if not has_permission:
                        if not self.inject_permission_manifest(permission):
                            sys.exit(1)

            if self.debug_mode:
                self.enable_debug_mode()

            if gadget_to_use:
                # add Internet permission
                has_internet_permission = self.has_permission(self.INTERNET_PERMISSION)
                if not has_internet_permission:
                    if not self.inject_permission_manifest(self.INTERNET_PERMISSION):
                        sys.exit(1)

                # inject frida library
                # get entrypoint
                self.package = self.get_package()
                if entrypoint is None:
                    self.entrypoint_class = self.get_entrypoint_class_name()
                    if self.entrypoint_class is None:
                        return
                else:
                    self.entrypoint_class = entrypoint
                if not self.entrypoint_class:
                    return
                self.entrypoint_smali_path = self.get_entrypoint_smali_path()

                # inject loader frida
                if not self.insert_lib_loader(gadget_to_use.stem):
                    return False
                if not self.check_libextract():
                    return False

                # add target library in lib
                if not self.arch:
                    archs = [
                        (plba(gadget_to_use, self.ARCH_ARM), self.ARCH_ARM, gadget_to_use.with_suffix(".so")),
                        (plba(gadget_to_use, self.ARCH_ARM64), self.ARCH_ARM64, gadget_to_use.with_suffix(".so")),
                        (plba(gadget_to_use, self.ARCH_X86), self.ARCH_X86, gadget_to_use.with_suffix(".so")),
                        (plba(gadget_to_use, self.ARCH_X86_64), self.ARCH_X64, gadget_to_use.with_suffix(".so")),
                    ]
                else:
                    archs = [(gadget_to_use, self.arch, gadget_to_use)]
                for gadget, arch, out in archs:
                    self.insert_lib(gadget, arch, out)

            # add users certificate
            if user_certificate:
                with open(next(iter(self.final_dir.values())) / "resources.arsc", "r+b") as fp:
                    rsc, _ = pyaxml.ARSC.from_axml(fp.read())
                    ret = self.enable_user_certificates(rsc)
                    if ret == 2:
                        rsc.compute(recursive=False)
                        fp.seek(0)
                        fp.write(rsc.pack())
                    elif ret == 0:
                        return False
            
            if self.compression_method == zipfile.ZIP_DEFLATED:
                if not self.check_libextract():
                    return False
                
            self.manifest.write()

            # repackage the apk and sign + align it
            if output_file:
                output_file_path = self.repackage_apk(target_file=output_file)
            else:
                output_file_path = self.repackage_apk()

            if output_file_path is None:
                return False

            if self.need_full_extraction:
                for apk_path in self.final_dir:
                    self.sign_and_zipalign(apk_path, [])
            else:
                self.sign_and_zipalign(output_file_path, splits_apk)
            return True
