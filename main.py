from fastapi import FastAPI
from fastapi.responses import JSONResponse
import fdb
import time
import threading
import uvicorn

app = FastAPI()

# Configurações do banco de dados Firebird
db_config = {
    'host': 'localhost',
    'database': 'path_to_your_database.fdb',
    'user': 'your_username',
    'password': 'your_password',
    'port': 3050  # Porta padrão do Firebird
}

event_port = 3051  # Porta do RemoteEvent

def setup_remote_event():
    """Configura o evento remoto."""
    conn = fdb.connect(**db_config)
    event_con = conn.event_conduit(['new_record_event'])
    event_con.begin()
    return event_con

def wait_for_event(event_con):
    """Aguarda o evento remoto."""
    while True:
        event_con.wait()
        print("Novo registro inserido ou atualizado na tabela PAINEL_ATENDIMENTO")
        time.sleep(1)

def fetch_records():
    """Busca registros da tabela PAINEL_ATENDIMENTO."""
    conn = fdb.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PAINEL_ATENDIMENTO")
    records = cursor.fetchall()
    conn.close()
    return records

@app.get('/api/records')
def get_records():
    """Endpoint para obter registros da tabela PAINEL_ATENDIMENTO."""
    records = fetch_records()
    return JSONResponse(content=records)

if __name__ == '__main__':
    # Configura o evento remoto
    event_con = setup_remote_event()

    # Inicia a thread para aguardar o evento remoto
    event_thread = threading.Thread(target=wait_for_event, args=(event_con,))
    event_thread.daemon = True
    event_thread.start()

    # Inicia o servidor FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000, debug=True)