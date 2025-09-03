"""Helpers that print instructions for argcomplete activation."""
def print_autocomplete_instructions(cmd_name: str = "atikin"):
    print("Autocomplete setup instructions:")
    print()
    print("1) Install argcomplete:")
    print("   pip install argcomplete")
    print()
    print("2) For one-time activation in current shell:")
    print(f"   eval \"$(register-python-argcomplete {cmd_name})\"")
    print()
    print("3) For permanent (bash) registration:")
    print(f"   register-python-argcomplete {cmd_name} >> ~/.bashrc")
    print()
    print("See argcomplete docs for zsh / fish / other shells.")
