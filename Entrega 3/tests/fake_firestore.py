"""Firestore falso, em memória, para testar a API sem internet e sem firebase.json.

Imita só o que o código da API usa:
  db.collection(nome)               -> coleção
  coleção.document(id)              -> referência (.get .set .update .delete .id)
  coleção.add(dict)                 -> (None, referência)   (igual ao Firestore real)
  coleção.where(campo, "==", valor) -> consulta (.where .limit .get .stream)
  coleção.stream()                  -> todos os documentos
"""
import copy
import itertools


class FakeSnapshot:
    def __init__(self, id, dados):
        self.id = id
        self._dados = dados

    @property
    def exists(self):
        return self._dados is not None

    def to_dict(self):
        # Cópia: quem altera o dicionário (ex.: pop("senha")) não mexe no "banco"
        return copy.deepcopy(self._dados) if self._dados is not None else None


class FakeDocumentRef:
    def __init__(self, colecao, id):
        self._colecao = colecao
        self.id = id

    def get(self):
        return FakeSnapshot(self.id, self._colecao._docs.get(self.id))

    def set(self, dados):
        self._colecao._docs[self.id] = copy.deepcopy(dados)

    def update(self, dados):
        if self.id not in self._colecao._docs:
            raise KeyError(f"Documento {self.id} não existe")
        self._colecao._docs[self.id].update(copy.deepcopy(dados))

    def delete(self):
        self._colecao._docs.pop(self.id, None)


class FakeQuery:
    def __init__(self, colecao, filtros=None, limite=None):
        self._colecao = colecao
        self._filtros = filtros or []
        self._limite = limite

    def where(self, campo=None, operador=None, valor=None, filter=None):
        if filter is not None:  # suporte ao FieldFilter(...)
            campo, operador, valor = filter.field_path, filter.op_string, filter.value
        if operador != "==":
            raise NotImplementedError("O Firestore falso só suporta o operador '=='")
        return FakeQuery(self._colecao, self._filtros + [(campo, valor)], self._limite)

    def limit(self, n):
        return FakeQuery(self._colecao, self._filtros, n)

    def stream(self):
        encontrados = []
        for id, dados in list(self._colecao._docs.items()):
            if all(dados.get(campo) == valor for campo, valor in self._filtros):
                encontrados.append(FakeSnapshot(id, dados))
                if self._limite is not None and len(encontrados) >= self._limite:
                    break
        return iter(encontrados)

    def get(self):
        return list(self.stream())


class FakeCollection(FakeQuery):
    def __init__(self, nome, gerador_id):
        self.nome = nome
        self._docs = {}
        self._gerador_id = gerador_id
        super().__init__(self)

    def document(self, id):
        return FakeDocumentRef(self, id)

    def add(self, dados):
        id = f"doc{next(self._gerador_id)}"
        self._docs[id] = copy.deepcopy(dados)
        return None, FakeDocumentRef(self, id)


class FakeFirestore:
    def __init__(self):
        self._colecoes = {}
        self._gerador_id = itertools.count(1)

    def collection(self, nome):
        if nome not in self._colecoes:
            self._colecoes[nome] = FakeCollection(nome, self._gerador_id)
        return self._colecoes[nome]

    def limpar(self):
        """Apaga tudo (usado entre um teste e outro)."""
        self._colecoes.clear()
