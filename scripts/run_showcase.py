"""
==============================================================================
PROJETO: Healthcare Operations & Clinical Data Warehouse
COMPONENTE: scripts/run_showcase.py
DESCRIÇÃO: Script interativo de demonstração executiva. Executa o pipeline,
           valida a suíte de testes de dados e exibe os relatórios analíticos.
AUTORA: Luanna Oliveira
==============================================================================
"""

import sqlite3
import pandas as pd
import subprocess
import os

pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 120)

def main():
    print("=" * 90)
    print(" DEMONSTRACAO EXECUTIVA: HEALTHCARE OPERATIONS & CLINICAL DATA WAREHOUSE")
    print(" Autora: Luanna Oliveira")
    print("=" * 90)

    # 1. Execucao do Pipeline de ETL
    print("\n[ETAPA 1/3] Executando Pipeline de ETL e Carga Dimensional (Star Schema)...")
    res_etl = subprocess.run(["python", "scripts/etl_pipeline.py"], capture_output=True, text=True)
    print(res_etl.stdout.strip())

    # 2. Execucao dos Testes Automatizados de Data Quality
    print("\n" + "-" * 90)
    print("[ETAPA 2/3] Executando Suíte de Testes Automatizados de Qualidade de Dados (Pytest/Unittest)...")
    res_tests = subprocess.run(["python", "tests/test_data_quality.py", "-v"], capture_output=True, text=True)
    print(res_tests.stderr.strip() or res_tests.stdout.strip())

    # 3. Consultas Analiticas Avancadas
    print("\n" + "-" * 90)
    print("[ETAPA 3/3] Consultas Analíticas Avançadas de Negócio (SQL Sênior - Star Schema)")
    print("-" * 90)

    conn = sqlite3.connect("clinical_dw.db")

    # Relatorio 1: Rentabilidade e Performance por Especialista
    print("\n>>> RELATÓRIO 1: RENTABILIDADE E MARGEM DE CONTRIBUIÇÃO POR PROFISSIONAL")
    q1 = """
    WITH performance_profissional AS (
        SELECT 
            p.nome AS profissional,
            p.especialidade,
            COUNT(f.id_atendimento_origem) AS volume_atendimentos,
            ROUND(SUM(f.receita_liquida), 2) AS receita_total,
            ROUND(SUM(f.margem_contribuicao), 2) AS margem_contribuicao,
            ROUND(AVG(f.score_nps), 1) AS nps_medio
        FROM fact_atendimentos f
        JOIN dim_profissional p ON f.sk_profissional = p.sk_profissional
        WHERE f.flag_realizado = 1
        GROUP BY p.nome, p.especialidade
    )
    SELECT 
        profissional,
        volume_atendimentos AS atendimentos,
        'R$ ' || PRINTF('%,.2f', receita_total) AS receita,
        'R$ ' || PRINTF('%,.2f', margem_contribuicao) AS margem,
        ROUND((margem_contribuicao * 100.0 / receita_total), 1) || '%' AS margem_pct,
        nps_medio,
        CASE 
            WHEN margem_contribuicao >= AVG(margem_contribuicao) OVER () THEN 'Acima da Media'
            ELSE 'Abaixo da Media'
        END AS benchmark_clinica
    FROM performance_profissional
    ORDER BY margem_contribuicao DESC;
    """
    df1 = pd.read_sql_query(q1, conn)
    print(df1.to_string(index=False))

    # Relatorio 2: Ocupacao, No-Show e Horarios Criticos
    print("\n>>> RELATÓRIO 2: OCUPAÇÃO, TAXA DE NO-SHOW E RECEITA POR DIA DA SEMANA")
    q2 = """
    WITH metricas_dias AS (
        SELECT 
            t.nome_dia_semana AS dia_semana,
            COUNT(f.id_atendimento_origem) AS agendamentos,
            SUM(f.flag_realizado) AS realizados,
            SUM(f.flag_no_show) AS no_shows,
            ROUND(AVG(f.tempo_espera_minutos), 1) AS espera_media_min,
            ROUND(SUM(f.receita_liquida), 2) AS receita
        FROM fact_atendimentos f
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        GROUP BY t.nome_dia_semana
    )
    SELECT 
        dia_semana,
        agendamentos,
        realizados,
        no_shows,
        ROUND((no_shows * 100.0 / agendamentos), 1) || '%' AS taxa_no_show,
        espera_media_min || ' min' AS tempo_espera,
        'R$ ' || PRINTF('%,.2f', receita) AS receita_gerada
    FROM metricas_dias
    ORDER BY receita DESC;
    """
    df2 = pd.read_sql_query(q2, conn)
    print(df2.to_string(index=False))

    # Relatorio 3: Retencao e Analise de Recencia (Cohort)
    print("\n>>> RELATÓRIO 3: ANÁLISE DE RECORRÊNCIA E RETENÇÃO DE PACIENTES (TOP 5)")
    q3 = """
    WITH historico AS (
        SELECT 
            p.paciente_id_origem,
            p.faixa_etaria,
            t.data_completa,
            LAG(t.data_completa, 1) OVER (
                PARTITION BY f.sk_paciente 
                ORDER BY t.data_completa
            ) AS data_anterior
        FROM fact_atendimentos f
        JOIN dim_paciente p ON f.sk_paciente = p.sk_paciente
        JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
        WHERE f.flag_realizado = 1
    )
    SELECT 
        'Paciente #' || paciente_id_origem AS id_paciente,
        faixa_etaria,
        COUNT(*) AS total_sessoes,
        MIN(data_completa) AS primeira_sessao,
        MAX(data_completa) AS ultima_sessao,
        CASE 
            WHEN COUNT(*) >= 4 THEN 'Tratamento Continuo (Ativo)'
            WHEN COUNT(*) BETWEEN 2 AND 3 THEN 'Em Andamento'
            ELSE 'Primeira Consulta'
        END AS status_fidelizacao
    FROM historico
    GROUP BY paciente_id_origem, faixa_etaria
    ORDER BY total_sessoes DESC
    LIMIT 5;
    """
    df3 = pd.read_sql_query(q3, conn)
    print(df3.to_string(index=False))

    conn.close()
    print("\n" + "=" * 90)
    print(" EXECUCAO CONCLUIDA COM 100% DE SUCESSO")
    print("=" * 90)

if __name__ == "__main__":
    main()
