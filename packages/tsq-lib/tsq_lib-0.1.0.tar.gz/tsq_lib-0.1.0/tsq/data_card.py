import pandas as pd
import json
import html
from typing import Dict, Any

def generate_data_card(df: pd.DataFrame, dataset_name: str = "Unnamed Dataset") -> Dict[str, Any]:
    """
    Build a finance data card from tidy data: ['timestamp', 'entity', 'variable', 'value'].
    """
    required = {'timestamp', 'entity', 'variable', 'value'}
    if not required.issubset(df.columns):
        raise ValueError(f"Data must contain columns {required}, found {df.columns.tolist()}")

    df = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    n_obs = len(df)
    n_entities = df['entity'].nunique()
    n_variables = df['variable'].nunique()
    time_min, time_max = df['timestamp'].min(), df['timestamp'].max()
    try:
        freq = pd.infer_freq(df['timestamp'].dropna().sort_values().unique())
    except Exception:
        freq = None

    missing_values = int(df['value'].isna().sum())
    duplicates = int(df.duplicated().sum())
    monotonicity = bool(all(df.sort_values(['entity', 'timestamp']).groupby('entity')['timestamp']
                              .apply(lambda x: x.is_monotonic_increasing or x.is_monotonic_non_decreasing)))

    variables = {}
    for var, g in df.groupby('variable'):
        g_val = g['value']
        variables[var] = {
            "n_observations": int(g.shape[0]),
            "n_missing": int(g_val.isna().sum()),
            "min": None if g_val.dropna().empty else float(g_val.min(skipna=True)),
            "max": None if g_val.dropna().empty else float(g_val.max(skipna=True))
        }

    return {
        "dataset_name": dataset_name,
        "overview": {
            "n_observations": int(n_obs),
            "n_entities": int(n_entities),
            "n_variables": int(n_variables),
            "time_range": [None if pd.isna(time_min) else str(time_min),
                           None if pd.isna(time_max) else str(time_max)],
            "inferred_frequency": freq
        },
        "data_quality": {
            "missing_values": missing_values,
            "duplicates": duplicates,
            "timestamps_monotonic": monotonicity
        },
        "variables": variables
    }

def save_data_card_json(df: pd.DataFrame, dataset_name: str, path: str) -> None:
    """
    Generate and save a JSON data card.
    """
    card = generate_data_card(df, dataset_name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)

def save_data_card_html(df: pd.DataFrame, dataset_name: str, path: str) -> None:
    """
    Generate and save an HTML data card.
    """
    card = generate_data_card(df, dataset_name)

    def b(val): return "✅" if val else "❌"
    title = html.escape(card.get("dataset_name", "Dataset"))
    ov = card["overview"]
    dq = card["data_quality"]
    vars_ = card["variables"]

    html_content = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title} — Data Card</title>
<style>
body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 24px; color:#222; }}
h1 {{ margin-bottom: 0.25rem; }}
h2 {{ margin-top: 2rem; }}
.small {{ color:#666; font-size:0.9rem; }}
.card {{ border:1px solid #e5e7eb; border-radius:12px; padding:16px; margin:12px 0; background:#fafafa; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #eee; text-align: left; padding: 8px 6px; }}
th {{ background:#f3f4f6; }}
.kv {{ display:grid; grid-template-columns: 240px 1fr; gap:8px 16px; }}
.badge {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#eef2ff; font-size:0.85rem; }}
</style></head>
<body>

<h1>Data Card</h1>
<div class="small">{title}</div>

<div class="card">
  <h2>Overview</h2>
  <div class="kv">
    <div>Observations</div><div>{ov['n_observations']}</div>
    <div>Entities</div><div>{ov['n_entities']}</div>
    <div>Variables</div><div>{ov['n_variables']}</div>
    <div>Time range</div><div>{ov['time_range'][0]} — {ov['time_range'][1]}</div>
    <div>Inferred frequency</div><div><span class="badge">{ov['inferred_frequency'] or '—'}</span></div>
  </div>
</div>

<div class="card">
  <h2>Data Quality</h2>
  <div class="kv">
    <div>Missing values</div><div>{dq['missing_values']}</div>
    <div>Duplicates</div><div>{dq['duplicates']}</div>
    <div>Timestamps monotonic per entity</div><div>{b(dq['timestamps_monotonic'])}</div>
  </div>
</div>

<div class="card">
  <h2>Variables</h2>
  <table>
    <thead><tr><th>Variable</th><th>Obs</th><th>Missing</th><th>Min</th><th>Max</th></tr></thead>
    <tbody>
"""
    for var_name, stats in vars_.items():
        html_content += f"<tr><td>{html.escape(str(var_name))}</td>" \
                        f"<td>{stats['n_observations']}</td>" \
                        f"<td>{stats['n_missing']}</td>" \
                        f"<td>{'' if stats['min'] is None else stats['min']}</td>" \
                        f"<td>{'' if stats['max'] is None else stats['max']}</td></tr>\n"

    html_content += """    </tbody>
  </table>
</div>

<div class="small">Generated by TSQ (Time Series Quality) • Extend with finance-specific checks.</div>
</body></html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html_content)

def save_data_card_latex(df, dataset_name: str, path: str) -> None:
    card = generate_data_card(df, dataset_name)
    ov = card["overview"]
    dq = card["data_quality"]
    vars_ = card["variables"]

    latex_content = f"""\\section*{{Data Card: {dataset_name}}}
\\begin{{itemize}}
    \\item Observations: {ov['n_observations']}
    \\item Entities: {ov['n_entities']}
    \\item Variables: {ov['n_variables']}
    \\item Time range: {ov['time_range'][0]} -- {ov['time_range'][1]}
    \\item Inferred frequency: {ov['inferred_frequency'] or '---'}
    \\item Missing values: {dq['missing_values']}
    \\item Duplicates: {dq['duplicates']}
    \\item Timestamps monotonic: {"Yes" if dq['timestamps_monotonic'] else "No"}
\\end{{itemize}}

\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{lrrrr}}
\\hline
Variable & Obs & Missing & Min & Max \\\\
\\hline
"""
    for var_name, stats in vars_.items():
        latex_content += f"{var_name} & {stats['n_observations']} & {stats['n_missing']} & {stats['min'] or ''} & {stats['max'] or ''} \\\\\n"

    latex_content += """\\hline
\\end{tabular}
\\caption{Variable-level statistics for """ + dataset_name + """}
\\end{table}
"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(latex_content)
