-- ==============================================================================
-- PROJETO: Healthcare Operations & Clinical Data Warehouse
-- COMPONENTE: 03_analytical_queries.sql
-- DESCRIÇÃO: Consultas Analíticas Avançadas de Negócio (SQL Sênior)
-- AUTORA: Luanna Oliveira
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUERY 1: Análise de Ocupação e Horários de Pico por Dia da Semana e Especialidade
-- Técnica: Window Functions (RANK, AVG acumulado) e agregações condicionais
-- Objetivo: Identificar subutilização de salas e capacidade operacional ociosa
-- ------------------------------------------------------------------------------
WITH metricas_operacionais AS (
    SELECT 
        t.nome_dia_semana,
        s.categoria AS especialidade,
        COUNT(f.id_atendimento_origem) AS total_agendamentos,
        SUM(CASE WHEN f.flag_realizado = 1 THEN 1 ELSE 0 END) AS total_atendimentos_realizados,
        SUM(CASE WHEN f.flag_no_show = 1 THEN 1 ELSE 0 END) AS total_no_shows,
        ROUND(AVG(f.tempo_espera_minutos), 2) AS media_espera_minutos,
        ROUND(SUM(f.receita_liquida), 2) AS receita_total
    FROM fact_atendimentos f
    JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
    JOIN dim_servico s ON f.sk_servico = s.sk_servico
    GROUP BY t.nome_dia_semana, s.categoria
)
SELECT 
    nome_dia_semana,
    especialidade,
    total_agendamentos,
    total_atendimentos_realizados,
    total_no_shows,
    ROUND((total_no_shows * 100.0 / NULLIF(total_agendamentos, 0)), 2) AS taxa_no_show_pct,
    media_espera_minutos,
    receita_total,
    RANK() OVER (PARTITION BY especialidade ORDER BY receita_total DESC) AS ranking_receita_por_especialidade
FROM metricas_operacionais
ORDER BY especialidade, ranking_receita_por_especialidade;

-- ------------------------------------------------------------------------------
-- QUERY 2: Rentabilidade e Margem de Contribuição por Profissional
-- Técnica: Cálculo de margem percentual, comparação com a média global da clínica
-- Objetivo: Subsidiar decisões de remuneração, comissionamento e expansão de grade
-- ------------------------------------------------------------------------------
WITH performance_profissional AS (
    SELECT 
        p.nome AS profissional,
        p.especialidade,
        COUNT(f.id_atendimento_origem) AS volume_atendimentos,
        ROUND(SUM(f.receita_liquida), 2) AS receita_liquida_total,
        ROUND(SUM(f.custo_estimado), 2) AS custo_total,
        ROUND(SUM(f.margem_contribuicao), 2) AS margem_contribuicao_total,
        ROUND(AVG(f.score_nps), 1) AS media_satisfacao_nps
    FROM fact_atendimentos f
    JOIN dim_profissional p ON f.sk_profissional = p.sk_profissional
    WHERE f.flag_realizado = 1
    GROUP BY p.nome, p.especialidade
)
SELECT 
    profissional,
    especialidade,
    volume_atendimentos,
    receita_liquida_total,
    margem_contribuicao_total,
    ROUND((margem_contribuicao_total * 100.0 / NULLIF(receita_liquida_total, 0)), 2) AS margem_lucro_pct,
    media_satisfacao_nps,
    ROUND(AVG(margem_contribuicao_total) OVER (), 2) AS media_margem_clinica,
    CASE 
        WHEN margem_contribuicao_total >= AVG(margem_contribuicao_total) OVER () THEN 'Acima da Média'
        ELSE 'Abaixo da Média'
    END AS status_desempenho
FROM performance_profissional
ORDER BY margem_contribuicao_total DESC;

-- ------------------------------------------------------------------------------
-- QUERY 3: Análise de Retenção e Frequência do Paciente (Cohort / Recência)
-- Técnica: Window Functions (LAG, ROW_NUMBER) para calcular intervalo entre visitas
-- Objetivo: Identificar risco de evasão/abandono de tratamento clínico
-- ------------------------------------------------------------------------------
WITH historico_consultas AS (
    SELECT 
        f.sk_paciente,
        p.paciente_id_origem,
        p.faixa_etaria,
        t.data_completa,
        LAG(t.data_completa, 1) OVER (
            PARTITION BY f.sk_paciente 
            ORDER BY t.data_completa
        ) AS data_consulta_anterior
    FROM fact_atendimentos f
    JOIN dim_paciente p ON f.sk_paciente = p.sk_paciente
    JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
    WHERE f.flag_realizado = 1
)
SELECT 
    sk_paciente,
    paciente_id_origem,
    faixa_etaria,
    COUNT(*) AS total_sessoes_realizadas,
    MIN(data_completa) AS primeira_sessao,
    MAX(data_completa) AS ultima_sessao
FROM historico_consultas
GROUP BY sk_paciente, paciente_id_origem, faixa_etaria
HAVING COUNT(*) >= 2
ORDER BY total_sessoes_realizadas DESC;
