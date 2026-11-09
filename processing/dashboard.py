
import logging
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

logger = logging.getLogger(__name__)


def bar_chart(ax, data, title, color, top=15):
    # horizontal bars, the biggest at the top, with the number written at the end of each bar
    rows = sorted(data.items(), key=lambda item: item[1], reverse=True)[:top]

    if not rows:
        ax.set_title(title)
        ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)
        logger.warning('Graph "%s" is empty', title)
        return

    labels = [label for label, count in rows][::-1]
    values = [count for label, count in rows][::-1]

    # thin bars when there are only a few, so 1 bar does not fill the whole graph
    bars = ax.barh(labels, values, color=color, height=0.6 if len(rows) > 3 else 0.3)
    if len(rows) <= 3:
        ax.set_ylim(-1.5, len(rows) + 0.5)
    ax.bar_label(bars, padding=3, fontsize=9)
    ax.set_title(title, fontweight="bold")
    ax.set_xlabel("attempts")
    ax.set_xlim(0, max(values) * 1.15)
    # attempts are whole numbers, no 0.2 / 0.4 ticks
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)


def show_dashboard(successful_users, failed_countries, invalid_users):
    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.suptitle("SSH auth.log analysis", fontsize=16, fontweight="bold")

    # 1. failed attempts by country ("Unknown" is not a country, it is only shown in the title)
    countries = {country: count for country, count in failed_countries.items() if country != "Unknown"}
    unknown = failed_countries.get("Unknown", 0)
    bar_chart(axes[0], countries, "Failed attempts by country (top 15, %d unknown)" % unknown, "#DC2626")

    # 2. successful attempts by user
    bar_chart(axes[1], successful_users, "Successful attempts by user", "#16A34A")

    # 3. failed attempts with an invalid user
    bar_chart(axes[2], invalid_users,
              "Failed attempts with invalid user (top 15, total %d)" % sum(invalid_users.values()),
              "#F59E0B")

    plt.tight_layout()
    plt.show()
