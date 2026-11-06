"""
==============================================================================
PROJETO: Healthcare Operations & Clinical Data Warehouse
COMPONENTE: tests/test_data_quality.py
DESCRIÇÃO: Suíte de testes automatizados de qualidade e integridade de dados.
           Compatível nativamente com unittest (Python Standard Library) e pytest.
           Atua como o Juiz Externo Objetivo comprovando a conformidade do DW.
AUTORA: Luanna Oliveira
==============================================================================
"""

import sqlite3
import unittest
import os

DB_PATH = "clinical_dw.db"

class TestDataWarehouseQuality(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Banco de dados {DB_PATH} não encontrado. Execute scripts/etl_pipeline.py antes.")
        cls.conn = sqlite3.connect(DB_PATH)
        cls.cursor = cls.conn.cursor()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_01_tables_exist(self):
        """Garante que todas as tabelas do Star Schema e do OLTP foram devidamente criadas."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in self.cursor.fetchall()]
        
        expected_tables = [
            "tb_pacientes", "tb_profissionais", "tb_servicos", "tb_atendimentos",
            "dim_tempo", "dim_paciente", "dim_profissional", "dim_servico", "fact_atendimentos"
        ]
        for tbl in expected_tables:
            self.assertIn(tbl, tables, f"Tabela obrigatória ausente: {tbl}")

    def test_02_surrogate_key_uniqueness(self):
        """Verifica unicidade absoluta das chaves primárias e substitutas em dimensões e fatos."""
        tables_keys = [
            ("dim_tempo", "sk_tempo"),
            ("dim_paciente", "sk_paciente"),
            ("dim_profissional", "sk_profissional"),
            ("dim_servico", "sk_servico"),
            ("fact_atendimentos", "id_atendimento_origem"),
        ]
        for table, pk in tables_keys:
            self.cursor.execute(f"SELECT COUNT({pk}), COUNT(DISTINCT {pk}) FROM {table}")
            total, distinct = self.cursor.fetchone()
            self.assertEqual(total, distinct, f"Violação de unicidade na chave {pk} da tabela {table}: {total} != {distinct}")

    def test_03_referential_integrity(self):
        """Valida ausência de registros órfãos entre a tabela fato e as dimensões conectadas."""
        # Dim Tempo
        self.cursor.execute("""
            SELECT COUNT(*) FROM fact_atendimentos f
            LEFT JOIN dim_tempo t ON f.sk_tempo = t.sk_tempo
            WHERE t.sk_tempo IS NULL
        """)
        self.assertEqual(self.cursor.fetchone()[0], 0, "Registros órfãos encontrados para dim_tempo")

        # Dim Paciente
        self.cursor.execute("""
            SELECT COUNT(*) FROM fact_atendimentos f
            LEFT JOIN dim_paciente p ON f.sk_paciente = p.sk_paciente
            WHERE p.sk_paciente IS NULL
        """)
        self.assertEqual(self.cursor.fetchone()[0], 0, "Registros órfãos encontrados para dim_paciente")

        # Dim Profissional
        self.cursor.execute("""
            SELECT COUNT(*) FROM fact_atendimentos f
            LEFT JOIN dim_profissional pr ON f.sk_profissional = pr.sk_profissional
            WHERE pr.sk_profissional IS NULL
        """)
        self.assertEqual(self.cursor.fetchone()[0], 0, "Registros órfãos encontrados para dim_profissional")

        # Dim Servico
        self.cursor.execute("""
            SELECT COUNT(*) FROM fact_atendimentos f
            LEFT JOIN dim_servico s ON f.sk_servico = s.sk_servico
            WHERE s.sk_servico IS NULL
        """)
        self.assertEqual(self.cursor.fetchone()[0], 0, "Registros órfãos encontrados para dim_servico")

    def test_04_measures_arithmetic_consistency(self):
        """Garante que a aritmética das métricas do DW esteja consistente (receita, margem, custo)."""
        self.cursor.execute("""
            SELECT COUNT(*) FROM fact_atendimentos
            WHERE ROUND(margem_contribuicao, 2) != ROUND(receita_liquida - custo_estimado, 2)
        """)
        inconsistencias = self.cursor.fetchone()[0]
        self.assertEqual(inconsistencias, 0, f"Encontradas {inconsistencias} linhas com cálculo incorreto de margem")

    def test_05_flags_mutual_exclusivity(self):
        """Assegura que um mesmo atendimento não pode ter status conflitantes simultaneamente."""
        self.cursor.execute("""
            SELECT COUNT(*) FROM fact_atendimentos
            WHERE (flag_realizado + flag_no_show + flag_cancelado) > 1
        """)
        conflitos = self.cursor.fetchone()[0]
        self.assertEqual(conflitos, 0, f"Encontradas {conflitos} linhas com flags conflitantes")

    def test_06_analytical_queries_execution(self):
        """Garante que as consultas analíticas de negócio rodam com sucesso e retornam dados."""
        with open("sql/03_analytical_queries.sql", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Filtra queries SQL reais
        queries = [q.strip() for q in content.split(";") if q.strip() and not q.strip().startswith("--")]
        
        for idx, q in enumerate(queries, start=1):
            try:
                self.cursor.execute(q)
                results = self.cursor.fetchall()
                self.assertGreater(len(results), 0, f"Query analítica {idx} retornou 0 resultados.")
            except Exception as e:
                self.fail(f"Falha na execução da query analítica {idx}: {str(e)}")

if __name__ == "__main__":
    unittest.main(verbosity=2)
