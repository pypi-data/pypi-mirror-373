from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Tuple

# Rustでビルドされた低レベルモジュールをインポート
# maturinが `wormsim_rs` パッケージ内に `_internal` モジュールとして配置してくれます。
from . import _internal as rs

# --- ここからが高レベルAPI ---

# デフォルトの遺伝子データを定義
DEFAULT_GENE = [
    -0.8094022576319283,
    -0.6771492613425638,
    0.05892807075993428,
    -0.4894407617977082,
    0.1593721867510597,
    0.3576592038271041,
    -0.5664294232926526,
    -0.7853343958692636,
    0.6552003805912084,
    -0.6492992485125678,
    -0.5482223848375227,
    -0.956542705465967,
    -1.0,
    -0.7386107983898611,
    0.02074396537515929,
    0.7150315462816783,
    -0.9243504880454858,
    0.1353396882729762,
    0.9494528443702027,
    0.7727883271643218,
    -0.6046043758402895,
    0.7969062294208619,
]


@dataclass
class Gene:
    """線虫の遺伝情報を表現するデータクラス。

    生の遺伝子ベクトル（浮動小数点数のリスト）を保持します。このベクトルは、
    線虫の神経回路のパラメータ（シナプス結合強度やニューロンの閾値など）を定義するために、
    内部で特定範囲の値にスケーリングされます。

    Attributes:
        `gene` (List[float]):
            遺伝子パラメータのベクトル。**ちょうど22個の要素**を持つ必要があり、
            **各要素は-1.0から1.0の範囲内**でなければなりません。
            各インデックスは、以下のように特定の生物学的パラメータにマッピングされます。

            - **時間スケール:**
                - `gene[0]`: 感覚ニューロンの時間スケール (`n`)。 [0.1, 4.2] にスケーリング。
                - `gene[1]`: 感覚ニューロンの時間スケール (`m`)。 [0.1, 4.2] にスケーリング。
            - **ニューロンの閾値 (`theta`):** [-15, 15] にスケーリング。
                - `gene[2]`: `theta[0]`
                - `gene[3]`: `theta[1]`
                - `gene[4]`: `theta[2]`
                - `gene[5]`: `theta[3]`
                - `gene[6]`: `theta[4]` 及び `theta[5]`
                - `gene[7]`: `theta[6]` 及び `theta[7]`
            - **感覚ニューロンからのシナプス結合重み (`w_on`, `w_off`):** [-15, 15] にスケーリング。
                - `gene[8]`: `w_on[0]`
                - `gene[9]`: `w_on[1]`
                - `gene[10]`: `w_off[0]`
                - `gene[11]`: `w_off[1]`
            - **介在/運動ニューロン間のシナプス結合重み (`w`):** [-15, 15] にスケーリング。
                - `gene[12]`: `w[0][2]`
                - `gene[13]`: `w[1][3]`
                - `gene[14]`: `w[2][4]` 及び `w[2][5]`
                - `gene[15]`: `w[3][6]` 及び `w[3][7]`
                - `gene[16]`: `w[4][4]` 及び `w[5][5]`
                - `gene[17]`: `w[6][6]` 及び `w[7][7]`
            - **ギャップ結合の重み (`g`):** [0, 2.5] にスケーリング。
                - `gene[18]`: `g[0][1]` 及び `g[1][0]`
                - `gene[19]`: `g[2][3]` 及び `g[3][2]`
            - **振動成分の重み (`w_osc`):** [0, 15] にスケーリング。
                - `gene[20]`: `w_osc[4]`, `w_osc[7]` (及び `w_osc[5]`, `w_osc[6]` はその負の値)
            - **神経筋接合部の重み (`w_nmj`):**
                - `gene[21]`: 回転角度の重み。 [1, 3] にスケーリング。

    Raises:
        ValueError: `gene`リストの要素数が22でない場合、または
                    リスト内のいずれかの値が-1.0から1.0の範囲外の場合に送出されます。
    """

    gene: List[float] = field(default_factory=lambda: DEFAULT_GENE)

    def __post_init__(self):
        """インスタンス化後に遺伝子ベクトルの妥当性を検証します。"""
        # 1. 要素数の検証
        expected_length = 22
        if len(self.gene) != expected_length:
            raise ValueError(
                f"遺伝子リストはちょうど {expected_length} 個の要素を持つ必要がありますが、"
                f"現在 {len(self.gene)} 個です。"
            )

        # 2. 各値の範囲の検証
        for i, value in enumerate(self.gene):
            if not (-1.0 <= value <= 1.0):
                raise ValueError(
                    f"遺伝子リストの値が不正です。インデックス {i} の値 ({value}) が "
                    f"-1.0 から 1.0 の範囲外です。"
                )


@dataclass
class Const:
    """シミュレーションのための物理的および環境的な固定設定を表現します。

    このクラスは、線虫の遺伝子によらない全ての定数パラメータを保持します。
    これには、化学的環境の特性、運動の物理法則、シミュレーションの時間解像度などが含まれます。

    Attributes:
        `alpha` (float): NaClの線形濃度勾配。
        `c_0` (float): ガウス分布型の濃度設定における基準濃度。
        `lambda_` (float): ガウス分布型の濃度設定における分布の広がり。
        `x_peak` (float): 濃度勾配のピーク（中心）のx座標 (cm)。
        `y_peak` (float): 濃度勾配のピーク（中心）のy座標 (cm)。
        `dt` (float): シミュレーションにおける時間刻みの幅 (s)。
        `periodic_time` (float): 線虫の移動における1サイクルの継続時間 (s)。
        `frequency` (float): 移動方向の平均的な変化頻度 (Hz)。
                         **注: このパラメータは定義されていますが、現在のシミュレーションでは使用されていません。**
        `mu_0` (float): 線虫の初期の進行角度 (rad)。
        `velocity` (float): 線虫の一定の移動速度 (cm/s)。
        `simulation_time` (float): シミュレーション全体の実行時間 (s)。
        `time_constant` (float): システムの応答時定数 (s)。
    """

    alpha: float = -0.01
    c_0: float = 1.0
    lambda_: float = 1.61  # Pythonの予約語 'lambda' との衝突を避けるため '_' を付加
    x_peak: float = 4.5
    y_peak: float = 0.0
    dt: float = 0.01
    periodic_time: float = 4.2
    frequency: float = 0.033
    mu_0: float = 0.0
    velocity: float = 0.022
    simulation_time: float = 300.0
    time_constant: float = 0.1


def klinotaxis(
    gene: Gene, constant: Const, mode: int = 1
) -> Tuple[List[float], List[float]]:
    """C. elegansの化学走性（クリノタキシス）をシミュレートします。

    この関数は、線虫の神経回路モデルと環境情報を用いて、NaClの濃度勾配に
    対する移動軌跡を計算します。クリノタキシスは、生物が時間的な濃度変化を
    感知し、進行方向を修正することで勾配を移動する行動戦略です。

    Args:
        `gene` (Gene):
            線虫の神経回路パラメータ（シナプス強度、閾値など）を定義する
            遺伝子ベクトルを含むオブジェクト。
        `constant` (Const):
            シミュレーションの物理的・環境的条件（濃度勾配の形状、線虫の速度、
            シミュレーション時間など）を定義する固定パラメータのオブジェクト。
        `mode` (int, optional):
            NaClの濃度勾配のタイプを選択します。デフォルトは1です。
            * 0: 線形勾配
            * 1: 単一のガウス分布ピーク
            * 2: 2つのガウス分布ピーク

    Returns:
        Tuple[List[float], List[float]]:
            線虫の軌跡を表すタプル。最初のリストがX座標群、その次のリストが
            Y座標群です。単位はcmです。

    Raises:
        ValueError:
            `mode`に0, 1, 2以外の無効な値が指定された場合に送出されます。
        RuntimeError:
            シミュレーションを実行するRustバックエンドで予期せぬエラーが
            発生した場合に送出されます。
    """
    # --- 入力値の検証 ---
    if mode not in [0, 1, 2]:
        raise ValueError(
            f"無効なモード値です: {mode}。0, 1, または 2 を指定してください。"
        )

    # --- データ変換 ---
    gene_dict = asdict(gene)
    const_dict = asdict(constant)
    const_dict["lambda"] = const_dict.pop("lambda_")

    # --- Rustバックエンドの呼び出しとエラーハンドリング ---
    try:
        return rs.klinotaxis(gene_dict, const_dict, mode)
    except Exception as e:
        # Rust側からの例外を捕捉し、より有益な情報を持つ例外に変換して再送出します。
        raise RuntimeError("シミュレーションの内部計算でエラーが発生しました。") from e
