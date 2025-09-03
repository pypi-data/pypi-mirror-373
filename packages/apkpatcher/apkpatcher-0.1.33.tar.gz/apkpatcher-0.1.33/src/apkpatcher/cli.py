import os
import argparse
import logging
import sys
from pathlib import Path
import tempfile
import shutil
import zipfile
from apkpatcher import Patcher, conf, new_logger, download_baksmali, download_smali


def main() -> int:
    """cli function"""

    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--apk", help="Specify the apk you want to patch")
    parser.add_argument("-m", "--multiple_split", nargs="*", help="provided multiple split apks")
    parser.add_argument(
        "-g",
        "--gadget",
        help="Specify the frida-gadget file \
                        file.so or file with no architecture specified will be \
                        autocomplete with file_<arch>.so",
    )
    parser.add_argument(
        "--download_frida_version",
        help="Specify the frida version you want to inject. it should be use \
        only if you didn't download .so file. for instance: --download_frida_version 16.3.3",
    )
    parser.add_argument(
        "--download_frida",
        help="Automatic guess the version of frida to download one installed on the current environmen",
        action="store_true")
    parser.add_argument("-s", "--sdktools", help="Path of the sdktools")
    parser.add_argument("-b", "--version_buildtools", help="version for buildtools")
    parser.add_argument(
        "-r",
        "--arch",
        choices=[
            Patcher.ARCH_ARM,
            Patcher.ARCH_ARM64,
            Patcher.ARCH_X86,
            Patcher.ARCH_X64,
        ],
        help="architecture targeted",
    )
    parser.add_argument(
        "-v", "--verbosity", help="Verbosity level (0 to 3). Default is 3", type=int
    )

    parser.add_argument(
        "-e",
        "--enable-user-certificates",
        help="Add some configs in apk to accept user certificates",
        action="store_true",
    )
    parser.add_argument(
        "--enable-debug",
        help="enable debuggable",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--custom-certificate",
        help="Install a custom network certificate inside the apk",
    )

    parser.add_argument(
        "--keycertificate",
        help="use a specific certificate to generate the apk",
    )

    parser.add_argument(
        "--keyalias",
        help="alias name to use a specific certificate to generate the apk",
    )

    parser.add_argument(
        "--keypass",
        help="password to use a specific certificate to generate the apk",
    )

    parser.add_argument(
        "--keep-keycertificate",
        help="generate a certificate to sign apk and keep it at the end",
        action="store_true",
    )

    parser.add_argument(
        "--v4",
        help="use a v4 signature file to sign APK",
    )

    parser.add_argument("-o", "--output-file", help="Specify the output file (patched)")

    parser.add_argument("-p", "--pause", help="pause before repackage the apk", action="store_true")
    parser.add_argument(
        "--plugin",
        help="execute load plugin (a python file with as argument the folder before the packaging)",
    )
    parser.add_argument("-V", "--version", help="version of apkpatcher", action="store_true")
    parser.add_argument(
        "--entrypoint",
        help="specify the class name where you want to inject your library",
    )
    parser.add_argument(
        "--download-jars",
        help="download jars files",
        action="store_true",
    )

    parser.add_argument(
        "--only-unpack",
        help="unpack without repack and save all content in target directory",
    )

    parser.add_argument(
        "--only-repack",
        help="repack from target directory",
    )

    parser.add_argument("--compression-level", type=int, default=9)
    parser.add_argument("--compression-method", choices=
                        [
                            "STORED",  
                            "DEFLATED", 
                           # "BZIP2", not supported by apksigner 
                           # "LZMA"
                        ])

    parser.add_argument("-j", "--nb-jobs", help="nomber of jobs", type=int, default=4)

    parser.add_argument("--add-permissions", nargs="+", help="Add permissions in android app")

    args = parser.parse_args()

    if args.version:
        print(f"version {conf.VERSION}")
        return 0

    if args.download_jars:
        smali_jar = Path(__file__).parent / "smali.jar"
        if not smali_jar.exists():
            download_smali(smali_jar)

        baksmali_jar = Path(__file__).parent / "baksmali.jar"
        if not baksmali_jar.exists():
            download_baksmali(baksmali_jar)
        return 0

    if not args.sdktools:
        if "ANDROID_SDK_ROOT" in os.environ:
            args.sdktools = os.environ["ANDROID_SDK_ROOT"]

    if len(sys.argv) == 1 or (
        not (args.apk and args.only_unpack) and not (args.apk and args.sdktools)
    ):
        print("apkpatcher -a <apk> -s <sdktools> -b <version> [options]")
        if not args.apk:
            print("\nArgument apk is missing, you should add '-a myapk.apk'")
        if not args.sdktools:
            print(
                "\nArgument sdktools is missing, you should add '-s /usr/lib/android-sdk' or ANDROID_SDK_ROOT environment variable is not set"
            )
            print(
                "If you didn't have installed sdktools follow this tutorial: https://asthook.ci-yow.com/how.install.html#setup-sdktools"
            )
        parser.print_help()
        return 1

    logger = None
    if args.verbosity:
        if args.verbosity == 3:
            logger = new_logger(logging.DEBUG)
        elif args.verbosity == 2:
            logger = new_logger(logging.INFO)
        else:
            logger = new_logger(logging.ERROR)
    else:
        logger = new_logger(logging.INFO)
    patcher = Patcher(args.apk, args.version_buildtools, args.sdktools, logger, args.nb_jobs)
    if args.only_unpack:
        patcher.extract_apk(patcher.apk, Path(args.only_unpack + "/base"))
        return 0
    if args.multiple_split:
        splits_apk = list(Path(p) for p in args.multiple_split)
    else:
        splits_apk = []
    if args.only_repack:
        with tempfile.TemporaryDirectory() as tmp_dir:
            shutil.copytree(Path(args.only_repack), tmp_dir, dirs_exist_ok=True)
            patcher.final_dir.clear()
            patcher.final_dir[args.apk] = Path(tmp_dir) / "base"
            if not patcher.repackage_apk(Path(args.apk)):
                return 1
            patcher.sign_and_zipalign(Path(args.apk), splits_apk)
        return 0
    if args.custom_certificate:
        patcher.add_network_certificate(Path(args.custom_certificate))
    if args.arch:
        patcher.set_arch(args.arch)
    patcher.pause = args.pause
    if args.keycertificate and args.keyalias and args.keypass:
        patcher.add_certificate(args.keycertificate, args.keyalias, args.keypass)
    if args.keep_keycertificate:
        patcher.keep_certificate()
    if args.v4:
        patcher.enable_v4_signature(args.v4)
    if args.enable_debug:
        patcher.set_debug()
    if args.plugin:
        patcher.set_plugin(args.plugin)
    if args.download_frida:
        import frida
        version = frida.__version__
        patcher.set_use_download_frida(version)
    if args.download_frida_version:
        patcher.set_use_download_frida(args.download_frida_version)
    if args.entrypoint:
        entrypoint = args.entrypoint
    else:
        entrypoint = None

    if args.compression_method:
        comp_meth = zipfile.ZIP_STORED
        if args.compression_method == "STORED":
            comp_meth = zipfile.ZIP_STORED
        elif args.compression_method == "DEFLATED":
            comp_meth = zipfile.ZIP_DEFLATED
        elif args.compression_method == "BZIP2":
            comp_meth = zipfile.ZIP_BZIP2 
        elif args.compression_method == "LZMA":
            comp_meth = zipfile.ZIP_LZMA
        patcher.set_compression(comp_meth, args.compression_level)
    
    if args.output_file:
        if not patcher.patching(
            args.gadget,
            output_file=Path(args.output_file),
            user_certificate=args.enable_user_certificates,
            splits_apk=splits_apk,
            entrypoint=entrypoint,
            permissions=args.add_permissions,
        ):
            return 1
    else:
        if not patcher.patching(
            args.gadget,
            user_certificate=args.enable_user_certificates,
            splits_apk=splits_apk,
            entrypoint=entrypoint,
            permissions=args.add_permissions,
        ):
            return 1
    return 0
