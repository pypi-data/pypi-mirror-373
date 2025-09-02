import pandas as pd
from tsq.data_card import save_data_card_json, save_data_card_html, save_data_card_latex

# Example dataset in tidy format
data = {
    "timestamp": pd.date_range("2025-01-01", periods=5, freq="D").repeat(2),
    "entity": ["AAPL"]*5 + ["MSFT"]*5,
    "variable": ["close"]*10,
    "value": [170, 171, 169, 172, None, 310, 312, 309, 315, 318]
}
df = pd.DataFrame(data)

# Generate both JSON + HTML cards
save_data_card_json(df, "Example Equity Dataset", "data_card.json")
save_data_card_html(df, "Example Equity Dataset", "data_card.html")
save_data_card_latex(df, "Example Equity Dataset", "data_card.tex")

print("✅ Data card reports saved.")
