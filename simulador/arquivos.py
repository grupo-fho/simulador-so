"""Sistema de arquivos virtual. Nenhuma operação acessa o disco hospedeiro."""

from dataclasses import dataclass, field

from .eventos import RegistroEventos
from .modelo import ErroSimulacao, PCB


@dataclass
class FCB:
    identificador: int
    nome: str
    tipo: str
    permissoes: str
    criacao: int
    modificacao: int
    tamanho: int = 0
    primeiro_bloco: int | None = None


@dataclass
class Arquivo:
    fcb: FCB


@dataclass
class Diretorio:
    fcb: FCB
    filhos: dict[str, "Arquivo | Diretorio"] = field(default_factory=dict)


@dataclass
class Bloco:
    dados: bytes
    proximo: int | None = None


@dataclass
class ArquivoAberto:
    identificador: int
    processo_id: str
    arquivo: Arquivo
    modo: str
    posicao: int = 0


class SistemaArquivos:
    def __init__(self, tamanho_bloco: int, numero_blocos: int,
                 log: RegistroEventos) -> None:
        self.tamanho_bloco = tamanho_bloco
        self.numero_blocos = numero_blocos
        self.log = log
        self.raiz = Diretorio(FCB(0, "/", "diretorio", "rw", 0, 0))
        self.blocos: dict[int, Bloco] = {}
        self.tabela_global: dict[int, ArquivoAberto] = {}
        self._proximo_fcb = 1
        self._proxima_abertura = 1

    def _partes(self, caminho: str) -> list[str]:
        if not isinstance(caminho, str) or not caminho.startswith("/"):
            raise ErroSimulacao("Caminho deve ser absoluto, por exemplo /aula/notas.")
        partes = caminho.split("/")[1:]
        if caminho == "/":
            return []
        if any(not parte or parte in {".", ".."} or "\x00" in parte for parte in partes):
            raise ErroSimulacao(f"Caminho inválido: {caminho!r}.")
        return partes

    @staticmethod
    def _exigir_permissao(no: Arquivo | Diretorio, permissao: str) -> None:
        if permissao not in no.fcb.permissoes:
            raise ErroSimulacao(f"Permissão '{permissao}' negada para {no.fcb.nome}.")

    def localizar(self, caminho: str) -> Arquivo | Diretorio:
        no = self.raiz
        for parte in self._partes(caminho):
            if not isinstance(no, Diretorio):
                raise ErroSimulacao(f"Um componente de {caminho} não é diretório.")
            self._exigir_permissao(no, "r")
            if parte not in no.filhos:
                raise ErroSimulacao(f"Caminho inexistente: {caminho}.")
            no = no.filhos[parte]
        return no

    def _pai(self, caminho: str) -> tuple[Diretorio, str]:
        partes = self._partes(caminho)
        if not partes:
            raise ErroSimulacao("Não é permitido criar ou remover a raiz.")
        pai = self.localizar("/" + "/".join(partes[:-1]))
        if not isinstance(pai, Diretorio):
            raise ErroSimulacao("O pai deve ser um diretório.")
        self._exigir_permissao(pai, "w")
        return pai, partes[-1]

    def criar(self, caminho: str, diretorio: bool, permissoes: str, clock: int) -> None:
        if not isinstance(permissoes, str) or permissoes not in {"r", "w", "rw", ""}:
            raise ErroSimulacao("Permissões devem ser '', r, w ou rw.")
        pai, nome = self._pai(caminho)
        if nome in pai.filhos:
            raise ErroSimulacao(f"O caminho já existe: {caminho}.")
        fcb = FCB(self._proximo_fcb, nome, "diretorio" if diretorio else "arquivo",
                  permissoes, clock, clock)
        self._proximo_fcb += 1
        pai.filhos[nome] = Diretorio(fcb) if diretorio else Arquivo(fcb)
        pai.fcb.modificacao = clock
        self.log.registrar(clock, "CRIACAO_ARQUIVO", caminho, f"tipo={fcb.tipo}; permissões={permissoes!r}")

    def abrir(self, pcb: PCB, caminho: str, modo: str, clock: int) -> int:
        if modo not in {"r", "w", "rw", "a"}:
            raise ErroSimulacao("Modo de abertura deve ser r, w, rw ou a.")
        arquivo = self.localizar(caminho)
        if not isinstance(arquivo, Arquivo):
            raise ErroSimulacao("Não é possível abrir diretório como arquivo.")
        if "r" in modo:
            self._exigir_permissao(arquivo, "r")
        if "w" in modo or modo == "a":
            self._exigir_permissao(arquivo, "w")
        if modo == "w":
            self._substituir_conteudo(arquivo, b"", clock)
        descritor = 0
        while descritor in pcb.arquivos_abertos:
            descritor += 1
        global_id = self._proxima_abertura
        self._proxima_abertura += 1
        self.tabela_global[global_id] = ArquivoAberto(
            global_id, pcb.identificador, arquivo, modo,
            arquivo.fcb.tamanho if modo == "a" else 0)
        pcb.arquivos_abertos[descritor] = global_id
        self.log.registrar(clock, "ABERTURA_ARQUIVO", pcb.identificador,
                           f"{caminho}; fd={descritor}; global={global_id}; modo={modo}")
        return descritor

    def _abertura(self, pcb: PCB, descritor: int) -> ArquivoAberto:
        if type(descritor) is not int or descritor not in pcb.arquivos_abertos:
            raise ErroSimulacao(f"Descritor {descritor!r} fechado ou inexistente em {pcb.identificador}.")
        return self.tabela_global[pcb.arquivos_abertos[descritor]]

    def _indices_blocos(self, arquivo: Arquivo) -> list[int]:
        indices = []
        indice = arquivo.fcb.primeiro_bloco
        while indice is not None:
            indices.append(indice)
            indice = self.blocos[indice].proximo
        return indices

    def conteudo(self, arquivo: Arquivo) -> bytes:
        return b"".join(self.blocos[i].dados for i in self._indices_blocos(arquivo))

    def _substituir_conteudo(self, arquivo: Arquivo, dados: bytes, clock: int) -> None:
        antigos = self._indices_blocos(arquivo)
        necessarios = (len(dados) + self.tamanho_bloco - 1) // self.tamanho_bloco
        livres = [i for i in range(self.numero_blocos) if i not in self.blocos]
        if necessarios > len(antigos) + len(livres):
            raise ErroSimulacao("Disco virtual cheio. A escrita foi cancelada sem alterar o arquivo.")
        escolhidos = (antigos + livres)[:necessarios]
        for indice in antigos:
            del self.blocos[indice]
        for posicao, indice in enumerate(escolhidos):
            inicio = posicao * self.tamanho_bloco
            proximo = escolhidos[posicao + 1] if posicao + 1 < necessarios else None
            self.blocos[indice] = Bloco(dados[inicio:inicio + self.tamanho_bloco], proximo)
        arquivo.fcb.primeiro_bloco = escolhidos[0] if escolhidos else None
        arquivo.fcb.tamanho = len(dados)
        arquivo.fcb.modificacao = clock

    def ler(self, pcb: PCB, descritor: int, quantidade: int | None, clock: int) -> bytes:
        abertura = self._abertura(pcb, descritor)
        if "r" not in abertura.modo:
            raise ErroSimulacao("Descritor não foi aberto para leitura.")
        self._exigir_permissao(abertura.arquivo, "r")
        if quantidade is not None and (type(quantidade) is not int or quantidade < 0):
            raise ErroSimulacao("Quantidade de leitura deve ser inteira e não negativa.")
        dados = self.conteudo(abertura.arquivo)
        fim = len(dados) if quantidade is None else abertura.posicao + quantidade
        resultado = dados[abertura.posicao:fim]
        abertura.posicao += len(resultado)
        self.log.registrar(clock, "LEITURA_ARQUIVO", pcb.identificador,
                           f"fd={descritor}; dados={resultado!r}; posição={abertura.posicao}")
        return resultado

    def escrever(self, pcb: PCB, descritor: int, texto: str, clock: int) -> None:
        abertura = self._abertura(pcb, descritor)
        if abertura.modo not in {"w", "rw", "a"}:
            raise ErroSimulacao("Descritor não foi aberto para escrita.")
        self._exigir_permissao(abertura.arquivo, "w")
        dados = texto.encode("utf-8")
        anteriores = self.conteudo(abertura.arquivo)
        posicao = len(anteriores) if abertura.modo == "a" else abertura.posicao
        # Outros descritores podem ter truncado o mesmo arquivo: preenche o intervalo.
        anteriores = anteriores.ljust(posicao, b"\x00")
        novos = anteriores[:posicao] + dados + anteriores[posicao + len(dados):]
        self._substituir_conteudo(abertura.arquivo, novos, clock)
        abertura.posicao = posicao + len(dados)
        self.log.registrar(clock, "ESCRITA_ARQUIVO", pcb.identificador,
                           f"fd={descritor}; bytes={len(dados)}; tamanho={len(novos)}")

    def fechar(self, pcb: PCB, descritor: int, clock: int) -> None:
        abertura = self._abertura(pcb, descritor)
        del self.tabela_global[abertura.identificador]
        del pcb.arquivos_abertos[descritor]
        self.log.registrar(clock, "FECHAMENTO_ARQUIVO", pcb.identificador, f"fd={descritor}")

    def fechar_todos(self, pcb: PCB, clock: int) -> None:
        for descritor in list(pcb.arquivos_abertos):
            self.fechar(pcb, descritor, clock)

    def remover(self, caminho: str, clock: int) -> None:
        pai, nome = self._pai(caminho)
        if nome not in pai.filhos:
            raise ErroSimulacao(f"Caminho inexistente: {caminho}.")
        no = pai.filhos[nome]
        if isinstance(no, Diretorio) and no.filhos:
            raise ErroSimulacao("Diretório não vazio.")
        if any(abertura.arquivo is no for abertura in self.tabela_global.values()):
            raise ErroSimulacao("Não é permitido remover um arquivo aberto.")
        if isinstance(no, Arquivo):
            for indice in self._indices_blocos(no):
                del self.blocos[indice]
        del pai.filhos[nome]
        pai.fcb.modificacao = clock
        self.log.registrar(clock, "REMOCAO_ARQUIVO", caminho, "Objeto removido; blocos liberados.")

    def listar(self, caminho: str, clock: int) -> list[dict]:
        no = self.localizar(caminho)
        if not isinstance(no, Diretorio):
            raise ErroSimulacao("Listagem exige diretório.")
        self._exigir_permissao(no, "r")
        resultado = [vars(filho.fcb).copy() for _, filho in sorted(no.filhos.items())]
        self.log.registrar(clock, "LISTAGEM", caminho, repr(resultado))
        return resultado
