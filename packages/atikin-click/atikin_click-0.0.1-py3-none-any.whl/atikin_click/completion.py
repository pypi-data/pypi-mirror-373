# completion.py
"""
Generate shell completion scripts for Atikin CLI
Supports bash and zsh
"""

import sys

BASH_TEMPLATE = """
# Atikin CLI bash completion
_atikin_complete() {
    COMPREPLY=( $( COMP_WORDS="${{COMP_WORDS[*]}}" \
                   COMP_CWORD=$COMP_CWORD \
                   atikin complete-bash ) )
}
complete -F _atikin_complete atikin
"""

ZSH_TEMPLATE = """
# Atikin CLI zsh completion
_atikin_complete() {
    reply=( $( atikin complete-zsh ) )
}
compctl -K _atikin_complete atikin
"""

def generate_shell_script(shell: str) -> str:
    shell = shell.lower()
    if shell == "bash":
        return BASH_TEMPLATE.strip()
    elif shell == "zsh":
        return ZSH_TEMPLATE.strip()
    else:
        raise ValueError("Unsupported shell. Choose 'bash' or 'zsh'.")
