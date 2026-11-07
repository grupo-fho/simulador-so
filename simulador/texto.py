"""Formato de texto do SO: assinatura, tamanho UTF-8 e conteúdo no disco virtual."""

from .modelo import ErroSimulacao


class TextoSO:
    extensao = ".sotxt"

    @staticmethod
    def codificar(texto: str) -> str:
        return f"SOTXT/1\n{len(texto.encode('utf-8'))}\n{texto}"

    @staticmethod
    def decodificar(dados: bytes) -> str:
        if not dados:  # Um arquivo recém-criado representa texto vazio.
            return ""
        try:
            assinatura, tamanho, texto = dados.decode("utf-8").split("\n", 2)
            if assinatura == "SOTXT/1" and int(tamanho) == len(texto.encode("utf-8")):
                return texto
        except (ValueError, UnicodeError):
            pass
        raise ErroSimulacao("Arquivo .sotxt inválido: assinatura, tamanho ou texto corrompido.")
