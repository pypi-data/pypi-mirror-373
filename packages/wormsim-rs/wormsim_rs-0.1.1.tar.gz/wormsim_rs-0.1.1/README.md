# wormsim_rs

Rust製の高速シミュレーションエンジンによって、線虫（*Caenorhabditis elegans*）の塩濃度依存的な走性行動を再現します。Pythonバインディングを通して、Pythonから簡単に利用できます。

本シミュレータは以下の論文に基づいています：

> Hironaka, M., & Sumi, T. (2025). *A neural network model that generates salt concentration memory-dependent chemotaxis in Caenorhabditis elegans*. eLife, 14, RP104456. [https://elifesciences.org/articles/104456](https://elifesciences.org/articles/104456)

---

## 🚀 特徴（Features）

- Rustによる高速なシミュレーション
- [PyO3](https://github.com/PyO3/pyo3) と [maturin](https://github.com/PyO3/maturin) によるPythonバインディング
- `Gene`および`Const`構造体による柔軟なパラメータ指定
- 濃度場の切り替え（線形・ガウス分布-1ピーク・ガウス分布-2ピーク）

---

## 📦 インストール方法（Installation）

### Python（PyPI）

```bash
pip install wormsim-rs
```

---

## 🧪 クイックスタート（Python）

```python
import matplotlib.pyplot as plt
import wormsim_rs as ws

# パラメータを定義
gene = ws.Gene()     # デフォルトの遺伝子パラメータ（22次元ベクトル）
const = ws.Const()   # デフォルトの環境パラメータ

# シミュレーション実行（mode=1: ガウス分布-1ピークの濃度場）
x, y = ws.klinotaxis(gene, const, mode=1)

plt.plot(x, y, label="Trajectory")
plt.scatter(0, 0, label="Starting Point")
plt.scatter(const.x_peak, const.y_peak, label="Gradient Peak")
plt.axis("equal")
plt.legend()
plt.show()
```

---

## 🧬 API仕様

### `klinotaxis(gene: Gene, constant: Const, mode: int = 1) -> tuple[list[float], list[float]]`

線虫1個体の移動軌跡をシミュレーションします。

- **`gene`**: ニューロンモデルのパラメータを格納する [`Gene`](#gene) オブジェクト
- **`constant`**: シミュレーション環境の定数を格納する [`Const`](#const) オブジェクト
- **`mode`**: 濃度マップのモードを指定

  - `0`: 線形勾配
  - `1`: ガウス分布 - 1ピーク（デフォルト）
  - `2`: ガウス分布 - 2ピーク

戻り値は `(x: list[float], y: list[float])` のタプルで、移動経路を表します。

---

### `Gene`

神経モデルに関連するパラメータをまとめたデータクラス。

- **フィールド**

  - `gene` (`list[float]`):
    22次元の遺伝子ベクトル。

    - 要素数は **22個**
    - 各値は **-1.0 〜 1.0** の範囲
    - 内部的に以下の生理学的パラメータへスケーリングされます:

      - **時間スケール**: `n`, `m`
      - **ニューロン閾値**: `theta`
      - **シナプス結合重み**: `w_on`, `w_off`, `w`
      - **ギャップ結合重み**: `g`
      - **振動成分重み**: `w_osc`
      - **神経筋接合部重み**: `w_nmj`

- **使用例**

```python
# デフォルトの遺伝子を使用
gene = ws.Gene()

# 独自の遺伝子を設定（22次元、-1.0〜1.0の範囲）
gene = ws.Gene(gene=[0.1] * 22)
```

---

### `Const`

シミュレーションにおける環境定数をまとめたデータクラス。

- **フィールド**

  - `alpha` (`float`): 線形濃度の勾配
  - `c_0` (`float`): ガウス分布の基準濃度
  - `lambda_` (`float`): ガウス分布の広がり（`lambda` は予約語のため末尾に `_`）
  - `x_peak`, `y_peak` (`float`): 濃度ピークの座標 (cm)
  - `dt` (`float`): 時間刻み幅 (s)
  - `periodic_time` (`float`): 1サイクルの移動時間 (s)
  - `frequency` (`float`): 方向変化の平均周波数 (Hz) ※現在未使用
  - `mu_0` (`float`): 初期角度 (rad)
  - `velocity` (`float`): 線虫の移動速度 (cm/s)
  - `simulation_time` (`float`): シミュレーション総時間 (s)
  - `time_constant` (`float`): 応答の時定数 (s)

- **使用例**

```python
# デフォルト値
const = ws.Const()

# 一部を上書き
const = ws.Const(
    x_peak=4.5,
    y_peak=0.0,
    velocity=0.03,
    simulation_time=600.0,
)
```

---

## 🧭 濃度マップモード（Concentration Modes）

- `mode = 0`: 線形勾配（遺伝的アルゴリズムでの学習用）
- `mode = 1`: ガウス分布 - 1ピーク（基本形）
- `mode = 2`: ガウス分布 - 2ピーク

---

## 📚 参考文献（References）

Hironaka, M., & Sumi, T. (2025). *A neural network model that generates salt concentration memory-dependent chemotaxis in Caenorhabditis elegans*. eLife, 14, RP104456. [https://elifesciences.org/articles/104456](https://elifesciences.org/articles/104456)

---
