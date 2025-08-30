import argparse
from datetime import datetime

from .processor import process_pdf


def cli():
    parser = argparse.ArgumentParser(
        description="Convert PDF pages to images and transcribe them using Ollama."
    )
    parser.add_argument(
        "pdf_path",
        help="Path to the input PDF file",
    )
    parser.add_argument(
        "--custom-instructions",
        "-c",
        help="Path to a text file containing additional instructions for the transcription prompt",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        help="Output directory (default: output_YYYYMMDD_HHMMSS)",
    )
    parser.add_argument(
        "--model",
        "-m",
        default="qwen2.5vl:latest",
        help="Ollama model to use (default: qwen2.5vl:latest)",
    )
    parser.add_argument(
        "--keep-images",
        "-k",
        action="store_true",
        default=False,
        help="Keep the intermediate image files (default: False)",
    )
    parser.add_argument(
        "--width",
        "-w",
        type=int,
        default=0,
        help="Width of the resized images. Set to 0 to skip resizing (default: 0)",
    )
    parser.add_argument(
        "--start",
        "-s",
        type=int,
        default=0,
        help="Start page number (default: 0)",
    )
    parser.add_argument(
        "--end",
        "-e",
        type=int,
        default=0,
        help="End page number (default: 0)",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        default=False,
        help="Write merged output to stdout (default: False)",
    )

    args = parser.parse_args()

    process_pdf(
        pdf_path=args.pdf_path,
        custom_instructions=args.custom_instructions,
        output_dir=args.output,
        model=args.model,
        keep_images=args.keep_images,
        width=args.width,
        start=args.start,
        end=args.end,
        stdout=args.stdout,
    )


if __name__ == "__main__":
    cli()
