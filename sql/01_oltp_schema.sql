-- ==============================================================================
-- PROJETO: Healthcare Operations & Clinical Data Warehouse
-- COMPONENTE: 01_oltp_schema.sql
-- DESCRIÇÃO: Estrutura do Banco Transacional (OLTP - 3FN) para Gestão Clínica
-- AUTORA: Luanna Oliveira
-- ==============================================================================

-- Tabela de Pacientes
CREATE TABLE IF NOT EXISTS tb_pacientes (
    paciente_id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    genero CHAR(1) CHECK (genero IN ('M', 'F', 'O')),
    cidade VARCHAR(60) NOT NULL,
    uf CHAR(2) NOT NULL DEFAULT 'MG',
    data_cadastro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status_ativo BOOLEAN NOT NULL DEFAULT 1
);

-- Tabela de Profissionais de Saúde / Fisioterapeutas / Especialistas
CREATE TABLE IF NOT EXISTS tb_profissionais (
    profissional_id INTEGER PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    especialidade VARCHAR(60) NOT NULL,
    registro_conselho VARCHAR(30) UNIQUE NOT NULL,
    data_admissao DATE NOT NULL,
    status_ativo BOOLEAN NOT NULL DEFAULT 1
);

-- Tabela de Serviços e Procedimentos Clínicos
CREATE TABLE IF NOT EXISTS tb_servicos (
    servico_id INTEGER PRIMARY KEY,
    nome_servico VARCHAR(80) NOT NULL,
    categoria VARCHAR(40) NOT NULL, -- Ex: Fisioterapia, Pilates Clínico, Reabilitação, Avaliação
    valor_tabela DECIMAL(10,2) NOT NULL,
    custo_base DECIMAL(10,2) NOT NULL,
    duracao_padrao_minutos INTEGER NOT NULL
);

-- Tabela Transacional de Agendamentos e Atendimentos
CREATE TABLE IF NOT EXISTS tb_atendimentos (
    atendimento_id INTEGER PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES tb_pacientes(paciente_id),
    profissional_id INTEGER NOT NULL REFERENCES tb_profissionais(profissional_id),
    servico_id INTEGER NOT NULL REFERENCES tb_servicos(servico_id),
    data_hora_agendada TIMESTAMP NOT NULL,
    data_hora_inicio TIMESTAMP,
    data_hora_fim TIMESTAMP,
    status_atendimento VARCHAR(20) NOT NULL CHECK (status_atendimento IN ('Realizado', 'Cancelado', 'No-Show', 'Reagendado')),
    valor_final DECIMAL(10,2) NOT NULL,
    desconto_aplicado DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    avaliacao_paciente_nps INTEGER CHECK (avaliacao_paciente_nps BETWEEN 0 AND 10)
);
