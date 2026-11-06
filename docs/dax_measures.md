# Medidas DAX: Healthcare Operations & Clinical Data Warehouse

Guia completo de medidas DAX prontas para copiar e colar no Power BI Desktop.

---

## 1. Tabela de Medidas Sugerida
Crie uma tabela vazia no Power BI chamada `_Medidas` para centralizar todos os cálculos.

---

## 2. Métricas de Volume & Atendimentos

### Total de Agendamentos
```dax
Total Agendamentos = COUNTROWS(fact_atendimentos)
```

### Atendimentos Realizados
```dax
Atendimentos Realizados = 
CALCULATE(
    COUNTROWS(fact_atendimentos),
    fact_atendimentos[flag_realizado] = 1
)
```

### Total de No-Shows (Faltas sem aviso)
```dax
Total No-Shows = 
CALCULATE(
    COUNTROWS(fact_atendimentos),
    fact_atendimentos[flag_no_show] = 1
)
```

### Taxa de No-Show (%)
```dax
Taxa No-Show % = 
DIVIDE(
    [Total No-Shows],
    [Total Agendamentos],
    0
)
```

---

## 3. Métricas Financeiras & Margem de Contribuição

### Receita Total Bruta
```dax
Receita Total = 
CALCULATE(
    SUM(fact_atendimentos[receita_liquida]),
    fact_atendimentos[flag_realizado] = 1
)
```

### Custo Operacional Total
```dax
Custo Total = 
CALCULATE(
    SUM(fact_atendimentos[custo_estimado]),
    fact_atendimentos[flag_realizado] = 1
)
```

### Margem de Contribuição Líquida (R$)
```dax
Margem de Contribuicao = 
[Receita Total] - [Custo Total]
```

### Margem de Lucro / Contribuição (%)
```dax
Margem % = 
DIVIDE(
    [Margem de Contribuicao],
    [Receita Total],
    0
)
```

### Ticket Médio por Atendimento
```dax
Ticket Medio = 
DIVIDE(
    [Receita Total],
    [Atendimentos Realizados],
    0
)
```

---

## 4. Métricas de Qualidade & Satisfação

### NPS Médio (Satisfação do Paciente)
```dax
NPS Medio = 
CALCULATE(
    AVERAGE(fact_atendimentos[score_nps]),
    fact_atendimentos[flag_realizado] = 1
)
```

### Tempo Médio de Espera (minutos)
```dax
Tempo Medio Espera = 
CALCULATE(
    AVERAGE(fact_atendimentos[tempo_espera_minutos]),
    fact_atendimentos[flag_realizado] = 1
)
```

---

## 5. Medidas Avançadas de Benchmark & Contexto

### Média Geral de Faturamento da Clínica
```dax
Receita Media Geral = 
CALCULATE(
    [Receita Total],
    ALL(dim_profissional)
)
```

### Ranking de Especialistas por Faturamento
```dax
Rank Profissional = 
RANKX(
    ALL(dim_profissional[nome]),
    [Receita Total],
    ,
    DESC,
    Dense
)
```

### Status de Desempenho vs. Média da Clínica
```dax
Status Desempenho = 
IF(
    [Margem de Contribuicao] >= CALCULATE(AVERAGE(fact_atendimentos[margem_contribuicao]), ALL(dim_profissional)),
    "Acima da Média",
    "Abaixo da Média"
)
```
