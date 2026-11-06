-- ==============================================================================
-- PROJETO: Healthcare Operations & Clinical Data Warehouse
-- COMPONENTE: 02_dw_star_schema.sql
-- DESCRIÇÃO: Esquema Dimensional Estrela (Star Schema - Kimball OLAP)
-- AUTORA: Luanna Oliveira
-- ==============================================================================

-- Dimensão Tempo / Calendário
CREATE TABLE IF NOT EXISTS dim_tempo (
    sk_tempo INTEGER PRIMARY KEY, -- Formato YYYYMMDD
    data_completa DATE NOT NULL UNIQUE,
    ano INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    nome_mes VARCHAR(15) NOT NULL,
    trimestre INTEGER NOT NULL,
    dia INTEGER NOT NULL,
    dia_semana_num INTEGER NOT NULL,
    nome_dia_semana VARCHAR(15) NOT NULL,
    flag_fim_de_semana BOOLEAN NOT NULL
);

-- Dimensão Paciente
CREATE TABLE IF NOT EXISTS dim_paciente (
    sk_paciente INTEGER PRIMARY KEY,
    paciente_id_origem INTEGER NOT NULL,
    faixa_etaria VARCHAR(20) NOT NULL,
    genero CHAR(1) NOT NULL,
    cidade VARCHAR(60) NOT NULL,
    uf CHAR(2) NOT NULL,
    tempo_como_cliente_meses INTEGER NOT NULL,
    status_ativo BOOLEAN NOT NULL
);

-- Dimensão Profissional de Saúde
CREATE TABLE IF NOT EXISTS dim_profissional (
    sk_profissional INTEGER PRIMARY KEY,
    profissional_id_origem INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    especialidade VARCHAR(60) NOT NULL,
    tempo_casa_anos DECIMAL(4,1) NOT NULL,
    status_ativo BOOLEAN NOT NULL
);

-- Dimensão Serviço / Procedimento
CREATE TABLE IF NOT EXISTS dim_servico (
    sk_servico INTEGER PRIMARY KEY,
    servico_id_origem INTEGER NOT NULL,
    nome_servico VARCHAR(80) NOT NULL,
    categoria VARCHAR(40) NOT NULL,
    duracao_padrao_minutos INTEGER NOT NULL,
    faixa_preco VARCHAR(20) NOT NULL
);

-- Tabela Fato: Atendimentos e Procedimentos Clínicos
CREATE TABLE IF NOT EXISTS fact_atendimentos (
    id_atendimento_origem INTEGER PRIMARY KEY,
    sk_tempo INTEGER NOT NULL REFERENCES dim_tempo(sk_tempo),
    sk_paciente INTEGER NOT NULL REFERENCES dim_paciente(sk_paciente),
    sk_profissional INTEGER NOT NULL REFERENCES dim_profissional(sk_profissional),
    sk_servico INTEGER NOT NULL REFERENCES dim_servico(sk_servico),
    
    -- Métricas e Fatos Quantitativos
    duracao_efetiva_minutos INTEGER NOT NULL,
    tempo_espera_minutos INTEGER NOT NULL,
    receita_bruta DECIMAL(10,2) NOT NULL,
    desconto_concedido DECIMAL(10,2) NOT NULL,
    receita_liquida DECIMAL(10,2) NOT NULL,
    custo_estimado DECIMAL(10,2) NOT NULL,
    margem_contribuicao DECIMAL(10,2) NOT NULL,
    
    -- Flags Analíticas de Desempenho
    flag_realizado BOOLEAN NOT NULL,
    flag_no_show BOOLEAN NOT NULL,
    flag_cancelado BOOLEAN NOT NULL,
    score_nps INTEGER
);
