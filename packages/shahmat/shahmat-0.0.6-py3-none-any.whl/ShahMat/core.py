import time
import numpy as np
import pandas as pd
import requests
from datetime import datetime

from tqdm import tqdm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def chesscom(username: str, *, start_year: int = 2025):
    print('\nWelcome to ShahMat – Review your Chess Performance')

    URL = f"https://api.chess.com/pub/player/{username}/games"
    this_year, this_month = datetime.now().year, datetime.now().month

    sess = requests.Session()
    sess.headers.update({
        "User-Agent": "AG Algo Lab (website: https://ag-algolab.github.io/)",
        "Accept": "application/json",
    })

    data = []
    for year in range(start_year, this_year + 1):
        max_month = this_month + 1 if year == this_year else 13
        for month in tqdm(
            range(1, max_month),
            desc=f"Extract {year}",
            ascii='-#',
            colour='green',
            leave=False,
            bar_format='{l_bar}{bar}| Remaining: {remaining}'
        ):
            infos = f"{URL}/{year}/{month:02d}"
            res = sess.get(infos)
            if res.status_code == 200:
                games = res.json().get('games', [])
                if games:
                    data.append(pd.json_normalize(games))
            else:
                print(res.status_code)
            time.sleep(.5)

    df = pd.concat(data, ignore_index=True)
    df['date'] = pd.to_datetime(df['end_time'], unit='s')
    df.set_index('date', inplace=True)
    df = df[['time_control', 'time_class', 'rated', 'rules', 'url',
             'white.rating', 'black.rating', 'white.result', 'black.result',
             'white.username', 'black.username']]

    df["user_color"] = np.where(df["white.username"].str.lower() == username.lower(), "white", "black")
    df["user_elo"] = np.where(df["user_color"] == "white", df["white.rating"], df["black.rating"])
    df["opponent_elo"] = np.where(df["user_color"] == "white", df["black.rating"], df["white.rating"])
    df["elo_diff"] = df["user_elo"] - df["opponent_elo"]
    df["opponent_name"] = np.where(df["user_color"] == "white", df["black.username"], df["white.username"])

    draws = ["stalemate", "agreed", "repetition", "insufficient", "timevsinsufficient", "draw"]
    df["result"] = np.where(df["user_color"] == "white", df["white.result"], df["black.result"])
    df['result'] = np.where(df['result'] == 'win', 1, np.where(df['result'].isin(draws), .5, 0))
    df['result_type'] = np.where(df['white.result'] == 'win', df['black.result'], df['white.result'])
    df = df[(df["rated"] == True) & (df["rules"] == "chess")]
    df = df.drop(columns=[
        "white.username", "black.username",
        "white.rating", "black.rating",
        "white.result", "black.result",
        "rated", "rules"
    ])

    # -------------------- State shared by analysis functions --------------------
    df_current = df.copy()
    dfw_current = df_current[df_current['user_color'] == 'white']
    dfb_current = df_current[df_current['user_color'] == 'black']

    def _set_time_class(time_class: str = 'all'):
        nonlocal df_current, dfw_current, dfb_current
        if time_class == 'all':
            df_current = df.copy()
        else:
            df_current = df[df['time_class'] == time_class].copy()
        dfw_current = df_current[df_current['user_color'] == 'white']
        dfb_current = df_current[df_current['user_color'] == 'black']

    def _hour_analysis():
        if len(df_current) == 0:
            raise KeyError("No data extracted")

        data_per_hour = {}
        n_per_hour = []
        sr_per_hour = []

        for hour in range(24):
            df_hour = df_current[df_current.index.hour == hour]
            data_per_hour[hour] = df_hour
            n_per_hour.append(len(df_hour))
            sr_per_hour.append(round(df_hour["result"].mean(), 3) if len(df_hour) else np.nan)

        hours = list(range(24))
        sr_plot = np.nan_to_num(np.array(sr_per_hour, dtype=float), nan=0.0)
        sr_mean = df_current['result'].mean()
        sr_max = max(sr_plot) if len(sr_plot) else np.nan

        top3 = np.argsort(sr_plot)[-3:][::-1]
        print("==== Top 3 Best Hours (UTC) ====")
        for i, h in enumerate(top3, start=1):
            print(f"{i} -> {h}h  (score={sr_plot[h]:.3f})")

        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.plot(hours, sr_plot, marker="o", color="tab:blue", label="Score rate")
        ax1.set_xlabel("Hour of day (UTC)")
        ax1.set_ylabel("Score rate (0=loss, 0.5=draw, 1=win)", color="tab:blue")
        ax1.tick_params(axis='y', labelcolor="tab:blue")
        ax1.set_xticks(range(24))
        ax1.set_ylim(0, 1)
        ax1.axhline(sr_mean, color="tab:grey", linestyle=":", linewidth=1.5, label="Average Score Rate")
        if not np.isnan(sr_max):
            ax1.axhline(sr_max, color="tab:green", linestyle=":", linewidth=1.5, label="Max Score Rate")

        ax2 = ax1.twinx()
        ax2.bar(hours, n_per_hour, alpha=0.3, color="tab:purple", label="Number of games")
        ax2.set_ylabel("Number of games", color="tab:purple")
        ax2.tick_params(axis='y', labelcolor="tab:purple")

        plt.title("Score rate & number of games per hour")
        fig.tight_layout()
        plt.show()


    def _elo_diff(bin_size=5, min_n=5, relativelohi=False):
        if "elo_diff" not in df_current.columns or "result" not in df_current.columns or "user_color" not in df_current.columns:
            raise KeyError("Columns missing: 'elo_diff', 'result', 'user_color'.")

        if len(dfw_current) == 0 and len(dfb_current) == 0:
            raise KeyError("No data extracted")

        if relativelohi:
            lo = np.floor(df_current["elo_diff"].min() / bin_size) * bin_size
            hi = np.ceil(df_current["elo_diff"].max() / bin_size) * bin_size
            if lo == hi:
                lo -= bin_size
                hi += bin_size
        else:
            lo = -75
            hi =  75

        edges = np.arange(lo, hi + bin_size, bin_size)

        def make_curve(dfc):
            if len(dfc) == 0:
                return np.array([]), np.array([]), np.array([])
            cats = pd.cut(dfc["elo_diff"], bins=edges, include_lowest=True)
            stats = dfc.groupby(cats, observed=True).agg(sr=("result", "mean"), n=("result", "size"))
            stats = stats[stats["n"] > min_n]
            if len(stats) == 0:
                return np.array([]), np.array([]), np.array([])
            x = np.array([(iv.left + iv.right) / 2 for iv in stats.index])
            y = stats["sr"].values.astype(float)
            n = stats["n"].values.astype(int)
            return x, y, n

        x_w, y_w, n_w = make_curve(dfw_current)
        x_b, y_b, n_b = make_curve(dfb_current)

        cats_all = pd.cut(df_current["elo_diff"], bins=edges, include_lowest=True)
        vol_series = df_current.groupby(cats_all, observed=True).size()
        x_vol = np.array([(iv.left + iv.right) / 2 for iv in vol_series.index])
        vol_vals = vol_series.values.astype(int)
        bar_width = bin_size * 0.9

        fig, ax = plt.subplots(figsize=(10, 5))
        ax2 = ax.twinx()
        ax2.bar(x_vol, vol_vals, width=bar_width, alpha=0.25, color="gray", edgecolor="none", label="Games (volume)", zorder=0)

        handles, labels = [], []
        if x_w.size:
            l_w, = ax.plot(x_w, y_w, marker="o", linestyle="-", color="gray", label="White", zorder=3)
            handles.append(l_w); labels.append("White")
        else:
            print("[Info] Not enough data for White (<= 5).")
        if x_b.size:
            l_b, = ax.plot(x_b, y_b, marker="o", linestyle="-", color="black", label="Black", zorder=3)
            handles.append(l_b); labels.append("Black")
        else:
            print("[Info] Not enough data for Black (<= 5).")

        ax.axvline(0, linestyle="--", linewidth=.5, color="black", alpha=0.6, zorder=1)
        ax.axhline(0.5, linestyle=":", linewidth=.5, color="black", alpha=0.6, zorder=1)

        ax.set_ylim(0, 1)
        ax.set_xlabel("Elo diff (reference: you)")
        ax.set_ylabel("Score rate (0=loss, 0.5=draw, 1=win)")
        ax2.set_ylabel("Number of games (volume)")

        h2, l2 = ax2.get_legend_handles_labels()
        handles += h2; labels += l2
        ax.legend(handles, labels, loc="best")

        ax.set_title(f"Score rate vs Elo diff (bin={bin_size}, min n={min_n} per bin)")
        fig.tight_layout()
        plt.show()


    def _result(min_pct=.03):
        if "result" not in df_current.columns or "result_type" not in df_current.columns:
            raise KeyError("Colonnes requises manquantes: 'result' et 'result_type'.")

        plt.rcParams.update({
            "figure.facecolor": "#f5f6f7",
            "axes.facecolor": "#f5f6f7",
            "axes.edgecolor": "#e6e6e9",
            "text.color": "#2a2a2a"
        })

        def _normalize_label(x: str) -> str:
            if not isinstance(x, str): return "unknown"
            s = x.strip().lower()
            aliases = {
                "checkmated": "checkmate",
                "mate": "checkmate",
                "resigned": "resign",
                "resign": "resign",
                "timeout": "timeout",
                "time forfeit": "timeout",
                "time": "timeout",
                "stalemate": "stalemate",
                "abandoned": "abandoned",
                "agreed": "agreed draw",
                "draw agreed": "agreed draw",
                "insufficient material": "insufficient material",
                "insufficient": "insufficient material",
            }
            return aliases.get(s, s)

        df_ = df_current.copy()
        df_["result_type"] = df_["result_type"].astype(str).map(_normalize_label)

        wins = df_[df_["result"] == 1]
        losses = df_[df_["result"] == 0]

        COLOR_MAP = {
            "checkmate": "#b3d9ff",
            "resign": "#ffd59e",
            "timeout": "#c9e4c5",
            "stalemate": "#e6ccff",
            "abandoned": "#f6c1c1",
            "agreed draw": "#ffe8b6",
            "insufficient material": "#d7e3fc",
            "unknown": "#dcdcdc",
            "other": "#d0d0d0"
        }
        ORDER = ["checkmate", "resign", "timeout", "stalemate", "agreed draw",
                 "insufficient material", "abandoned", "unknown", "Other"]

        def prep(series, min_pct):
            if series.empty: return {}, 0
            s = series.fillna("unknown").astype(str)
            counts = s.value_counts()
            total = int(counts.sum())
            if total == 0: return {}, 0
            pct = counts / total
            small = pct[pct < min_pct].index
            if len(small):
                counts.loc["Other"] = counts.loc[small].sum()
                counts = counts.drop(small)
            counts.index = [str(i) for i in counts.index]
            return counts.to_dict(), total

        counts_w, _ = prep(wins["result_type"], min_pct)
        counts_l, _ = prep(losses["result_type"], min_pct)

        all_keys = [k for k in ORDER if (k in counts_w or k in counts_l)]
        if not all_keys:
            fig = plt.figure(figsize=(10, 4))
            plt.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12)
            plt.axis("off")
            plt.show()
            return

        sizes_w = [counts_w.get(k, 0) for k in all_keys]
        sizes_l = [counts_l.get(k, 0) for k in all_keys]
        colors = [COLOR_MAP.get(k.lower(), COLOR_MAP["unknown"]) for k in all_keys]

        fig, axes = plt.subplots(1, 2, figsize=(14, 7), constrained_layout=True)
        titles = ["When YOU win – opponent's result types", "When YOU lose – your result types"]
        data = [sizes_w, sizes_l]

        for ax, arr, ttl in zip(axes, data, titles):
            if sum(arr) > 0:
                wedges, _texts, autotexts = ax.pie(
                    arr,
                    labels=None,
                    autopct=lambda p: f"{p:.1f}%" if p >= 2 else "",
                    startangle=90,
                    wedgeprops={"linewidth": 1, "edgecolor": "white"},
                    colors=colors,
                    pctdistance=0.7
                )
                for t in autotexts:
                    t.set_color("#333333")
                    t.set_fontsize(10)
                ax.axis("equal")
                ax.set_title(ttl, pad=16, fontsize=12)
            else:
                ax.text(0.5, 0.5, "No data", ha="center", va="center", fontsize=12)
                ax.axis("off")

        handles = [mpatches.Patch(color=COLOR_MAP.get(k.lower(), COLOR_MAP["unknown"]), label=k) for k in all_keys]
        axes[1].legend(
            handles=handles,
            title="Result types",
            loc="upper left",
            bbox_to_anchor=(1.02, 1.0),
            frameon=True,
            facecolor="#ffffff",
            edgecolor="#e6e6e9"
        )
        fig.suptitle("Result type breakdown (wins vs losses)", fontsize=14)
        plt.show()


    def _daily_sessions():
        if "result" not in df.columns:
            raise KeyError("Missing 'result' column in dataframe")


        df_shifted = df.copy()
        df_shifted.index = df_shifted.index - pd.Timedelta(hours=3)

        grouped = df_shifted.groupby(df_shifted.index.date)


        daily_counts = []
        daily_scores = []
        for day, dfg in grouped:
            daily_counts.append(len(dfg))
            daily_scores.append(dfg["result"].mean())


        daily_df = pd.DataFrame({
            "games": daily_counts,
            "score_rate": daily_scores
        })

        daily_df["games"] = daily_df["games"].clip(upper=20)

        agg = daily_df.groupby("games").agg(sr_mean=("score_rate", "mean"),
                                            n_days=("score_rate", "size"))


        # --- Plot ---
        fig, ax1 = plt.subplots(figsize=(10, 5))

        # si index numérique (1..15)
        ax1.set_xticks(agg.index)
        ax1.set_xticklabels([str(i) if i < 20 else "20+" for i in agg.index])


        # Score rate moyen en fonction du nombre de parties
        ax1.plot(agg.index, agg["sr_mean"], marker="o", color="tab:blue", label="Score rate (mean)")
        ax1.set_xlabel("Number of games in a day (3h→3h UTC)")
        ax1.set_ylabel("Score rate", color="tab:blue")
        ax1.set_ylim(0, 1)
        ax1.tick_params(axis='y', labelcolor="tab:blue")

        # Deuxième axe : combien de jours observés avec ce volume de parties
        ax2 = ax1.twinx()
        ax2.bar(agg.index, agg["n_days"], alpha=0.3, color="tab:grey", label="Days observed")
        ax2.set_ylabel("Number of days", color="tab:grey")
        ax2.tick_params(axis='y', labelcolor="tab:grey")

        plt.title("Score rate vs Number of games per day (day = 3h→3h UTC)")
        fig.tight_layout()
        plt.show()
        plt.close(fig)


    def _all_def():
        _hour_analysis()
        _elo_diff()
        _result()
        _daily_sessions()

    def _download():
        export = df_current[['user_color', 'time_class', 'user_elo', 'opponent_elo', 'result', 'result_type', 'url']]
        export.to_csv(f"chesscom_data_{username}.csv", index=True)
        print(f"Saved: chesscom_data_{username}.csv")

    # ====================== Interactive Menus ======================
    quit_all = False

    def timecontrol_menu():
        print("\nPick a Time Control to analyze:")
        print("  1. Bullet")
        print("  2. Blitz")
        print("  3. Rapid")
        print("  4. All")
        print("  0. Quit")

    def analysis_menu():
        print("\nPick the angle to explore your games:")
        print("  1. Hours of play")
        print("  2. Games per Day")
        print("  3. Elo Difference")
        print("  4. Result Types Breakdown")
        print("  5. Complete Analysis")
        print("  6. Download Data (filtered)")
        print("  9. Change TimeControl")
        print("  0. Quit")


    while True:
        timecontrol_menu()
        choice = input("> ").strip()
        if choice == "0":
            quit_all = True
            break
        if choice not in {"1", "2", "3", "4"}:
            print("Invalid choice.")
            continue

        if choice == "1":
            _set_time_class('bullet')
        elif choice == "2":
            _set_time_class('blitz')
        elif choice == "3":
            _set_time_class('rapid')
        elif choice == "4":
            _set_time_class('all')


        while True:
            analysis_menu()
            c2 = input("> ").strip()
            if c2 == "0":
                quit_all = True
                break
            if c2 == "9":
                break
            actions = {
                "1": _hour_analysis,
                "2": _daily_sessions,
                "3": _elo_diff,
                "4": _result,
                "5": _all_def,
                "6": _download,
            }
            if c2 in actions:
                try:
                    actions[c2]()
                except Exception as e:
                    print(f"[Error] {e}")
            else:
                print("Invalid choice.")

        if quit_all:
            break

    print('Made by AG Algo Lab: https://ag-algolab.github.io/')


