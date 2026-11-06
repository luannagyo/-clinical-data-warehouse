"""
Gera imagens de fundo em alta definicao (1920x1080) para o Power BI Desktop.
Cria duas opcoes:
1. fundo_modern_dark.png (Tema Dark Slate / Tecnologia & Saude)
2. fundo_clean_light.png (Tema Executivo Clean / Navy & White)
"""

from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os

os.makedirs("portfolio/clinical-data-warehouse/powerbi_assets", exist_ok=True)

WIDTH = 1920
HEIGHT = 1080

def create_dark_background():
    img = Image.new("RGBA", (WIDTH, HEIGHT), "#0F172A") # Slate 900
    draw = ImageDraw.Draw(img)

    # Top Header Container
    draw.rounded_rectangle([30, 25, 1890, 115], radius=16, fill="#1E293B", outline="#334155", width=2)

    # 4 KPI Card Containers
    card_w = 445
    card_gap = 25
    start_x = 30
    kpi_y0 = 135
    kpi_y1 = 295
    for i in range(4):
        x0 = start_x + i * (card_w + card_gap)
        x1 = x0 + card_w
        # Subtle accent border on top
        draw.rounded_rectangle([x0, kpi_y0, x1, kpi_y1], radius=16, fill="#1E293B", outline="#334155", width=2)
        # Top colored accent bar
        colors = ["#38BDF8", "#34D399", "#A78BFA", "#FBBF24"] # Cyan, Emerald, Purple, Amber
        draw.rounded_rectangle([x0, kpi_y0, x1, kpi_y0 + 8], radius=4, fill=colors[i])

    # 3 Main Chart Containers
    chart_w = 600
    chart_gap = 30
    chart_start_x = 30
    chart_y0 = 315
    chart_y1 = 1055
    for i in range(3):
        x0 = chart_start_x + i * (chart_w + chart_gap)
        x1 = x0 + chart_w
        draw.rounded_rectangle([x0, chart_y0, x1, chart_y1], radius=16, fill="#1E293B", outline="#334155", width=2)

    out_path = "portfolio/clinical-data-warehouse/powerbi_assets/fundo_modern_dark.png"
    img.convert("RGB").save(out_path, quality=95)
    print(f"Salvo: {out_path}")

def create_light_background():
    img = Image.new("RGBA", (WIDTH, HEIGHT), "#F8FAFC") # Slate 50
    draw = ImageDraw.Draw(img)

    # Top Header Container (Dark Navy banner)
    draw.rounded_rectangle([30, 25, 1890, 115], radius=16, fill="#0F172A", outline="#1E293B", width=1)

    # 4 KPI Card Containers
    card_w = 445
    card_gap = 25
    start_x = 30
    kpi_y0 = 135
    kpi_y1 = 295
    for i in range(4):
        x0 = start_x + i * (card_w + card_gap)
        x1 = x0 + card_w
        # White card with soft border
        draw.rounded_rectangle([x0, kpi_y0, x1, kpi_y1], radius=16, fill="#FFFFFF", outline="#E2E8F0", width=2)
        # Top colored accent bar
        colors = ["#0284C7", "#059669", "#7C3AED", "#D97706"] # Vibrant Blue, Green, Purple, Warm Gold
        draw.rounded_rectangle([x0, kpi_y0, x1, kpi_y0 + 8], radius=4, fill=colors[i])

    # 3 Main Chart Containers
    chart_w = 600
    chart_gap = 30
    chart_start_x = 30
    chart_y0 = 315
    chart_y1 = 1055
    for i in range(3):
        x0 = chart_start_x + i * (chart_w + chart_gap)
        x1 = x0 + chart_w
        draw.rounded_rectangle([x0, chart_y0, x1, chart_y1], radius=16, fill="#FFFFFF", outline="#E2E8F0", width=2)

    out_path = "portfolio/clinical-data-warehouse/powerbi_assets/fundo_clean_light.png"
    img.convert("RGB").save(out_path, quality=95)
    print(f"Salvo: {out_path}")

if __name__ == "__main__":
    create_dark_background()
    create_light_background()
