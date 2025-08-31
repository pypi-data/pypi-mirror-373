from src.code_splitter import CodeSplitter
from src.command import get_args


def main():
    args = get_args()

    CodeSplitter(original_file_path=args.file_path, git_commit=args.git, target_block_types=args.targets).execute()


if __name__ == "__main__":
    main()
