#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Lint para YAML do Copilot Studio.
Detecta:
- Tabs (\t)
- NBSP (\xa0)
- CRLF (\r\n)
- Espaços à direita
- Caracteres não ASCII (na primeira rodada)
- Inconsistência de tipos (String/string, Object/object)

Uso:
  python AberturaChamadoAI/scripts/lint_yaml_copilot.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT, 'config')

ASCII_ONLY = True  # primeira rodada sem emojis/pipes/acentos, pode ajustar depois

def scan_file(path):
    issues = []
    try:
        with open(path, 'rb') as f:
            raw = f.read()
        # Detectar BOM (UTF-8 BOM: EF BB BF)
        if raw.startswith(b'\xEF\xBB\xBF'):
            issues.append('BOM: arquivo possui UTF-8 BOM, remova')
        # Detectar CRLF
        if b'\r\n' in raw:
            issues.append('CRLF: quebras de linha Windows detectadas')
        text = raw.decode('utf-8', errors='replace')
    except Exception as e:
        return [f'Erro ao ler arquivo: {e}']

    lines = text.split('\n')
    for idx, line in enumerate(lines, start=1):
        if '\t' in line:
            issues.append(f'Linha {idx}: tab encontrado (\t)')
        if '\xa0' in line:
            issues.append(f'Linha {idx}: NBSP (\xa0) encontrado')
        if line.rstrip() != line:
            issues.append(f'Linha {idx}: espaço à direita')
        if ASCII_ONLY:
            for ch in line:
                if ord(ch) > 127:
                    issues.append(f'Linha {idx}: caractere não ASCII detectado (U+{ord(ch):04X})')
                    break

    # Checagens simples por padrões de tipos inconsistentes
    if 'outputType:' in text or 'variables:' in text:
        if ' type: string' in text:
            issues.append('Tipo minúsculo detectado: use "String"')
        if ' type: any' in text:
            issues.append('Tipo "any" não suportado: use "Object" ou "String"')
        if ' responseSchema: Any' in text:
            issues.append('responseSchema Any não suportado: use String (HTTP cru) ou Object')
        if ' responseSchema: string' in text:
            issues.append('responseSchema minúsculo: use "String"')
        if ' type: object' in text:
            issues.append('Tipo minúsculo detectado: use "Object"')
    return issues

def main():
    if not os.path.isdir(CONFIG_DIR):
        print(f'Config dir não encontrado: {CONFIG_DIR}')
        sys.exit(1)
    yaml_files = [
        os.path.join(CONFIG_DIR, f)
        for f in os.listdir(CONFIG_DIR)
        if f.endswith('.yaml') or f.endswith('.yml')
    ]
    any_issue = False
    for path in yaml_files:
        issues = scan_file(path)
        if issues:
            any_issue = True
            print(f'>> {os.path.relpath(path)}')
            for i in issues:
                print(f'  - {i}')
    if not any_issue:
        print('Sem problemas detectados.')

if __name__ == '__main__':
    main()