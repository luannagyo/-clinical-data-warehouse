"""
==============================================================================
PROJETO: Healthcare Operations & Clinical Data Warehouse
COMPONENTE: scripts/etl_pipeline.py
DESCRIÇÃO: Pipeline ETL em Python para extração de dados transacionais,
           transformação dimensional (Star Schema) e carga no Data Warehouse.
AUTORA: Luanna Oliveira
==============================================================================
"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = "clinical_dw.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_schemas(cursor):
    # Executa scripts DDL
    with open("sql/01_oltp_schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    with open("sql/02_dw_star_schema.sql", "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

def seed_oltp_data(cursor):
    """Gera dados transacionais simulados representativos de um ambiente clínico real."""
    print("-> Semeando dados transacionais (OLTP)...")
    
    # 1. Profissionais
    profissionais = [
        (1, "Dra. Camila Vasconcelos", "Fisioterapia Traumato-Ortopédica", "CREFITO-4/12345", "2022-01-15", 1),
        (2, "Dr. Rodrigo Guimarães", "Pilates Clínico e Reabilitação Postural", "CREFITO-4/23456", "2021-06-10", 1),
        (3, "Dra. Mariana Duarte", "Fisioterapia Respiratória e Pediátrica", "CREFITO-4/34567", "2023-03-01", 1),
        (4, "Dr. Lucas Meireles", "Osteopatia e Terapia Manual", "CREFITO-4/45678", "2020-08-20", 1),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO tb_profissionais VALUES (?, ?, ?, ?, ?, ?)
    """, profissionais)

    # 2. Serviços
    servicos = [
        (1, "Sessão de Pilates Clínico", "Pilates Clínico", 120.00, 45.00, 50),
        (2, "Avaliação Fisioterapêutica e Biomecânica", "Avaliação", 180.00, 60.00, 60),
        (3, "Fisioterapia Ortopédica e Funcional", "Fisioterapia", 140.00, 50.00, 50),
        (4, "Sessão de Osteopatia e Liberação Miofascial", "Osteopatia", 220.00, 80.00, 60),
        (5, "Reeducação Postural Global (RPG)", "Fisioterapia", 160.00, 55.00, 50),
    ]
    cursor.executemany("""
        INSERT OR REPLACE INTO tb_servicos VALUES (?, ?, ?, ?, ?, ?)
    """, servicos)

    # 3. Pacientes
    cidades = ["Contagem", "Belo Horizonte", "Betim", "Nova Lima"]
    generos = ["F", "M"]
    pacientes = []
    nomes_base = [
        "Beatriz Lima", "Lucas Silveira", "Juliana Mendes", "Rafael Carvalho", 
        "Fernanda Rocha", "Gustavo Pires", "Patrícia Alves", "Thiago Moura",
        "Aline Fonseca", "Marcos Nogueira", "Letícia Castro", "Diego Furtado",
        "Sofia Azevedo", "Gabriel Ribeiro", "Larissa Peixoto", "Bruno Antunes"
    ]
    for pid, nome in enumerate(nomes_base, start=1):
        ano_nasc = random.randint(1965, 2002)
        nasc = f"{ano_nasc}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        gen = random.choice(generos)
        cid = random.choice(cidades)
        pacientes.append((pid, nome, nasc, gen, cid, "MG", "2024-01-10 08:00:00", 1))

    cursor.executemany("""
        INSERT OR REPLACE INTO tb_pacientes VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, pacientes)

    # 4. Atendimentos transacionais (últimos 90 dias)
    base_date = datetime(2026, 8, 1)
    status_choices = ["Realizado", "Realizado", "Realizado", "Realizado", "No-Show", "Cancelado"]
    atendimentos = []
    
    for aid in range(1, 151):
        pid = random.randint(1, len(pacientes))
        prof = random.choice(profissionais)
        srv = random.choice(servicos)
        
        dias_offset = random.randint(0, 90)
        dt_agendada = base_date + timedelta(days=dias_offset, hours=random.randint(8, 18))
        status = random.choice(status_choices)
        
        valor = srv[3]
        desconto = 20.00 if random.random() < 0.25 else 0.00
        valor_final = valor - desconto
        
        if status == "Realizado":
            dt_inicio = dt_agendada + timedelta(minutes=random.randint(0, 15))
            dt_fim = dt_inicio + timedelta(minutes=srv[5])
            nps = random.choice([8, 9, 10, 10, 10, 7])
        else:
            dt_inicio = None
            dt_fim = None
            nps = None
            if status == "Cancelado":
                valor_final = 0.00
            elif status == "No-Show":
                valor_final = valor * 0.5 # Taxa de retenção

        atendimentos.append((
            aid, pid, prof[0], srv[0], 
            dt_agendada.strftime("%Y-%m-%d %H:%M:%S"),
            dt_inicio.strftime("%Y-%m-%d %H:%M:%S") if dt_inicio else None,
            dt_fim.strftime("%Y-%m-%d %H:%M:%S") if dt_fim else None,
            status, valor_final, desconto, nps
        ))

    cursor.executemany("""
        INSERT OR REPLACE INTO tb_atendimentos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, atendimentos)
    print(f"-> 150 atendimentos transacionais inseridos.")

def run_etl(cursor):
    """Transforma os dados de OLTP e popula as tabelas do Star Schema (OLAP)."""
    print("\n-> Executando transformação dimensional (ETL Star Schema)...")
    
    # 1. Carga da dim_tempo
    cursor.execute("""
        SELECT DISTINCT substr(data_hora_agendada, 1, 10) FROM tb_atendimentos
    """)
    datas = [row[0] for row in cursor.fetchall()]
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
    
    for dt_str in datas:
        dt = datetime.strptime(dt_str, "%Y-%m-%d")
        sk_tempo = int(dt.strftime("%Y%m%d"))
        dia_sem = dt.weekday()
        flag_fds = 1 if dia_sem >= 5 else 0
        trimestre = (dt.month - 1) // 3 + 1
        
        cursor.execute("""
            INSERT OR REPLACE INTO dim_tempo VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sk_tempo, dt_str, dt.year, dt.month, meses[dt.month], trimestre, dt.day, dia_sem + 1, dias_semana[dia_sem], flag_fds))

    # 2. Carga da dim_paciente
    cursor.execute("SELECT paciente_id, data_nascimento, genero, cidade, uf, status_ativo FROM tb_pacientes")
    for row in cursor.fetchall():
        pid, dnasc, gen, cid, uf, stat = row
        idade = 2026 - int(dnasc.split("-")[0])
        if idade < 25:
            faixa = "Até 24 anos"
        elif idade < 40:
            faixa = "25 a 39 anos"
        elif idade < 60:
            faixa = "40 a 59 anos"
        else:
            faixa = "60+ anos"
            
        cursor.execute("""
            INSERT OR REPLACE INTO dim_paciente VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (pid, pid, faixa, gen, cid, uf, 12, stat))

    # 3. Carga da dim_profissional
    cursor.execute("SELECT profissional_id, nome, especialidade, status_ativo FROM tb_profissionais")
    for row in cursor.fetchall():
        prid, nome, esp, stat = row
        cursor.execute("""
            INSERT OR REPLACE INTO dim_profissional VALUES (?, ?, ?, ?, ?, ?)
        """, (prid, prid, nome, esp, 3.5, stat))

    # 4. Carga da dim_servico
    cursor.execute("SELECT servico_id, nome_servico, categoria, duracao_padrao_minutos, valor_tabela FROM tb_servicos")
    for row in cursor.fetchall():
        sid, nome, cat, dur, val = row
        faixa_preco = "Premium" if val >= 200 else ("Padrão" if val >= 140 else "Econômico")
        cursor.execute("""
            INSERT OR REPLACE INTO dim_servico VALUES (?, ?, ?, ?, ?, ?)
        """, (sid, sid, nome, cat, dur, faixa_preco))

    # 5. Carga da fact_atendimentos
    cursor.execute("""
        SELECT 
            a.atendimento_id,
            a.paciente_id,
            a.profissional_id,
            a.servico_id,
            substr(a.data_hora_agendada, 1, 10) as data_agendada,
            a.data_hora_agendada,
            a.data_hora_inicio,
            a.data_hora_fim,
            a.status_atendimento,
            a.valor_final,
            a.desconto_aplicado,
            s.custo_base,
            a.avaliacao_paciente_nps
        FROM tb_atendimentos a
        JOIN tb_servicos s ON a.servico_id = s.servico_id
    """)
    
    rows = cursor.fetchall()
    for row in rows:
        aid, pid, prof_id, serv_id, dt_str, dt_agend, dt_ini, dt_fim, status, vlr_final, desc, custo_base, nps = row
        sk_tempo = int(dt_str.replace("-", ""))
        
        flag_realizado = 1 if status == "Realizado" else 0
        flag_no_show = 1 if status == "No-Show" else 0
        flag_cancelado = 1 if status == "Cancelado" else 0
        
        if flag_realizado and dt_ini and dt_agend:
            t_agend = datetime.strptime(dt_agend, "%Y-%m-%d %H:%M:%S")
            t_ini = datetime.strptime(dt_ini, "%Y-%m-%d %H:%M:%S")
            t_fim = datetime.strptime(dt_fim, "%Y-%m-%d %H:%M:%S")
            espera = max(0, int((t_ini - t_agend).total_seconds() / 60))
            duracao = max(0, int((t_fim - t_ini).total_seconds() / 60))
        else:
            espera = 0
            duracao = 0
            
        receita_bruta = vlr_final + desc
        receita_liq = vlr_final
        custo = custo_base if flag_realizado else (custo_base * 0.2 if flag_no_show else 0.0)
        margem = receita_liq - custo

        cursor.execute("""
            INSERT OR REPLACE INTO fact_atendimentos VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            aid, sk_tempo, pid, prof_id, serv_id,
            duracao, espera, receita_bruta, desc, receita_liq,
            custo, margem, flag_realizado, flag_no_show, flag_cancelado, nps
        ))

    print(f"-> Fact_atendimentos populada com {len(rows)} registros.")

def main():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        init_schemas(cursor)
        seed_oltp_data(cursor)
        run_etl(cursor)
        conn.commit()
        print("\n[OK] Pipeline ETL concluída com sucesso no banco: clinical_dw.db")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
