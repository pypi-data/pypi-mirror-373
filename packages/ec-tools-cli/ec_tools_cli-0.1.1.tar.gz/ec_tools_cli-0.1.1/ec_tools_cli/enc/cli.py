DETAILED_DOC = """
Support file encryption and decryption using AES.
ec-enc -e <input-file> -o <output-file> -p <password>
ec-enc -d <input-file> -o <output-file> -p <password>
"""
import argparse
import logging

from ec_tools.tools.cipher import AesMode, file_encryption_utils


def get_args():
    parser = argparse.ArgumentParser(
        description="Encryption CLI Tool",
        epilog=DETAILED_DOC,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-e", "--encrypting-file", type=str, help="File to encrypt")
    parser.add_argument("-d", "--decrypting-file", type=str, help="File to decrypt")
    parser.add_argument("-o", "--output-file", type=str, required=True, help="Output file path")
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        required=True,
        help="Password for encryption/decryption",
    )
    return parser.parse_args()


def main():
    args = get_args()
    logger = logging.getLogger("Encryption CLI")
    if args.encrypting_file and args.decrypting_file:
        logger.error("Error: You cannot specify both an encrypting file and a decrypting file.")
        exit(-1)
    if args.encrypting_file:
        file_encryption_utils.encrypt_file(
            args.encrypting_file,
            args.output_file,
            args.password,
            aes_mode=AesMode.AES_256_CBC,
            iterations=10000,
            chunk_size=1024 * 1024,
        )
    elif args.decrypting_file:
        file_encryption_utils.decrypt_file(args.decrypting_file, args.output_file, args.password)
    else:
        logger.error("Error: You must specify either an encrypting file or a decrypting file.")
        exit(-1)
