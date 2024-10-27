from typing import Annotated
import datetime
import pandas as pd

from fastapi import Depends, FastAPI, HTTPException, Query, File, UploadFile
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Company(SQLModel, table=True):
    cnpj: str = Field(primary_key=True, nullable=False)
    denom_social: str = Field(nullable=False)
    sit: str = Field(nullable=False)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow, nullable=False)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "API está funcionando"}

@app.post("/companies/")
def create_company(company: Company, session: SessionDep) -> Company:
    company.updated_at = datetime.datetime.utcnow()
    session.add(company)
    session.commit()
    session.refresh(company)
    return company

@app.get("/companies/")
def read_companies(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100
) -> list[Company]:
    companies = session.exec(select(Company).offset(offset).limit(limit)).all()
    return companies

@app.post("/companies/upload/")
async def upload_companies(session: SessionDep, file: UploadFile = File(...)) -> list[dict]:
    try:
        # Tente ler o conteúdo do arquivo CSV
        df = pd.read_csv(file.file, sep=";", encoding='latin1', on_bad_lines='skip')  # Ignora linhas com erro
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="O arquivo está vazio.")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Erro de parsing do arquivo CSV: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler o arquivo CSV: {str(e)}")
    
    # Selecionar apenas as colunas necessárias
    required_columns = ['CNPJ_CIA', 'DENOM_SOCIAL', 'SIT']
    if not all(col in df.columns for col in required_columns):
        raise HTTPException(status_code=400, detail="Colunas obrigatórias não encontradas no CSV.")
    
    # Filtra apenas as colunas desejadas
    filtered_df = df[required_columns].rename(columns={
        'CNPJ_CIA': 'cnpj',
        'DENOM_SOCIAL': 'denom_social',
        'SIT': 'sit'
    })

    # Adiciona a data de consumo e insere os dados no banco
    for _, row in filtered_df.iterrows():
        company = Company(
            cnpj=row['cnpj'],
            denom_social=row['denom_social'],
            sit=row['sit'],
            updated_at=datetime.datetime.utcnow()
        )
        
        # Verifica se o CNPJ já existe
        existing_company = session.exec(select(Company).where(Company.cnpj == company.cnpj)).first()
        if existing_company is None:
            session.add(company)

    session.commit()

    return filtered_df.to_dict(orient='records')
