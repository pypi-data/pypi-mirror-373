from .cli import default_cli

def main():
    import sys
    rc = default_cli.run(sys.argv[1:])
    sys.exit(rc)

if __name__ == "__main__":
    main()
