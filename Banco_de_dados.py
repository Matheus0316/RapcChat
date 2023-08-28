from datetime import datetime
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
import urllib.parse

Base = declarative_base()

bd_dados = {
    'user': 'postgres',
    'password': urllib.parse.quote_plus('230006004'),
    'host': 'localhost',
    'port': '5432',
    'database': 'RapcChat'
}

url = f"postgresql://{bd_dados['user']}:{bd_dados['password']}@{bd_dados['host']}:{bd_dados['port']}/{bd_dados['database']}"

class Cliente_bd(Base):
    """
    Representação do cliente no banco de dados
    """
    __tablename__ = 'CLIENTE'
    id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    nome = Column(String, nullable=False)
    login = Column(String, nullable=False, unique=True)


    def __repr__(self):
        return f"cliente: Id {self.id}, Nome {self.nome}"

class Mensagem_bd(Base):
    """
    Representação da mensagem no banco de dados
    """
    __tablename__ = 'MENSAGEM'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True, unique=True)
    id_emissor = Column(Integer, ForeignKey('CLIENTE.id'), nullable=False)
    id_destinatario = Column(Integer, ForeignKey('CLIENTE.id'), nullable=False)
    mensagem = Column(String(500), nullable=False)
    data = Column(DateTime)

    def __repr__(self):
        return f"Mensagem: Emissor {self.id_emissor}, Destinatário {self.id_destinatario}, Data de envio {self.data}"

engine = create_engine(url)

def conectar():
    try:
        connection = engine.connect()
        print('A conexão com o banco de dados foi bem sucedida')
        return engine

    except Exception as e:
        try:
            Base.metadata.create_all(engine)
            return conectar()
        except Exception as e:
            return f'Não foi possivel conectar ao banco de dados. Erro: {e}'

