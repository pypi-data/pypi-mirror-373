import datetime
import uuid

def serialize_value(value):
    if isinstance(value, (uuid.UUID, datetime.datetime)):
        return str(value)
    elif isinstance(value, list):
        return [serialize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    return value

def set_nested(d, keys, value):
    """Define o valor em dicionário aninhado baseado nos `keys`"""
    current = d
    for key in keys[:-1]:
        if isinstance(current, list):
            # Neste caso, aplicamos a lógica em cada item da lista
            for item in current:
                set_nested(item, keys[keys.index(key):], value)
            return
        current = current.setdefault(key, {})
    if isinstance(current, list):
        # Aplica valor em todos os itens da lista
        for item in current:
            item[keys[-1]] = serialize_value(value)
    else:
        current[keys[-1]] = serialize_value(value)


def construir_objeto(campos, valores):
    resultado = {}
    campos_base_completos = set()

    # Primeiro, identificar campos que já têm uma lista inteira (ex: itensfaixas)
    for campo, valor in zip(campos, valores):
        if '.' not in campo and isinstance(valor, list):
            resultado[campo] = serialize_value(value=valor)
            campos_base_completos.add(campo)

    # Agora processar os campos normais e subcampos
    for campo, valor in zip(campos, valores):
        if '.' in campo:
            partes = campo.split('.')
            base = partes[0]
            if base in campos_base_completos:
                continue  # ignora subcampos de listas já preenchidas
            if base not in resultado:
                resultado[base] = []
            set_nested(resultado, partes, valor)
        elif campo not in resultado:
            resultado[campo] = serialize_value(valor)

    return resultado


def color(text, code):
    return f"\033[{code}m{text}\033[0m"

def comparar(v1, v2, caminho=''):
    if isinstance(v1, dict) and isinstance(v2, dict):
        for k in set(v1.keys()).union(v2.keys()):
            comparar(v1.get(k), v2.get(k), f"{caminho}.{k}" if caminho else k)
    elif isinstance(v1, list) and isinstance(v2, list):
        max_len = max(len(v1), len(v2))
        for i in range(max_len):
            item1 = v1[i] if i < len(v1) else None
            item2 = v2[i] if i < len(v2) else None
            comparar(item1, item2, f"{caminho}[{v1[i]['id'][:8]}]")
    else:
        s1 = str(v1)
        s2 = str(v2)
        if s1 != s2:
            s1_pad = s1.ljust(25)
            s2_pad = s2.ljust(25)
            print(f"{caminho:<40} {color(s1_pad, '31')} {color(s2_pad, '32')} {color('≠', '33')}")

def mostrar_diferencas(entidade, id, linha1, linha2):
    print(f"ID: {color(id,'36')}")
    print(f"Entidade: {color(entidade,'36')}")
    print(f"{'Campo':<40} {'Local':<25} {'Nuvem':<25} {'Status'}")
    print("-" * 100)

    comparar(linha1, linha2)