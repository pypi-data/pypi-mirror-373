pub mod simulation;
use pyo3::prelude::*;
use rand::{rng, Rng};
use simulation::*;
use std::collections::VecDeque;

#[pyfunction]
pub fn klinotaxis(gene: Gene, constant: Const, mode: usize) -> PyResult<(Vec<f64>, Vec<f64>)> {
    // 遺伝子の受け渡し
    let weight: GeneConst = gene.scaling();
    // 時間に関する定数をステップ数に変換
    let time: Time = time_new(&weight, &constant);

    // 配列の宣言
    let mut y: [[f64; 8]; 2] = [[0.0; 8]; 2];
    let mut mu: [f64; 2] = [0.0; 2];
    let mut phi: [f64; 2] = [0.0; 2];
    let mut r: [[f64; 2]; 2] = [[0.0; 2]; 2];

    // 位置座標の配列を用意
    let mut x_vec: Vec<f64> = vec![0.0];
    let mut y_vec: Vec<f64> = vec![0.0];

    // concentration関数の選択
    let concentration_fn: fn(&Const, f64, f64) -> f64 = match mode {
        0 => concentration,
        1 => gauss_concentration,
        2 => two_gauss_concentration,
        _ => {
            return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                "Invalid mode selected",
            ))
        }
    };

    // 初期濃度の履歴生成
    let mut c_vec: VecDeque<f64> = VecDeque::new();
    for _ in 0..time.n_time + time.m_time {
        c_vec.push_back(concentration_fn(&constant, 0.0, 0.0));
    }

    // 運動ニューロンの初期活性を0～1の範囲でランダム化
    let mut rng_init = rng();
    rng_init.fill(&mut y[0][4..]);

    // 初期角度で配置
    mu[0] = constant.mu_0;

    // オイラー法
    for k in 0..time.simulation_time - 1 {
        // 濃度の更新
        c_vec.pop_front();
        c_vec.push_back(concentration_fn(&constant, r[0][0], r[0][1]));

        let y_on_off: [f64; 2] = y_on_off(&constant, &weight, &time, &c_vec);
        let y_osc: f64 = y_osc(&constant, k as f64 * constant.dt);

        for i in 0..8 {
            let mut synapse = 0.0;
            let mut gap = 0.0;
            for j in 0..8 {
                synapse += weight.w[j][i] * sigmoid(y[0][j] + weight.theta[j]);
                gap += weight.g[j][i] * (y[0][j] - y[0][i]);
            }
            let input = weight.w_on[i] * y_on_off[0]
                + weight.w_off[i] * y_on_off[1]
                + weight.w_osc[i] * y_osc;

            // ニューロンの膜電位の更新
            y[1][i] =
                y[0][i] + (-y[0][i] + synapse + gap + input) / constant.time_constant * constant.dt;
        }

        // 方向の更新
        let d = sigmoid(y[0][5] + weight.theta[5]) + sigmoid(y[0][6] + weight.theta[6]);
        let v = sigmoid(y[0][4] + weight.theta[4]) + sigmoid(y[0][7] + weight.theta[7]);
        phi[1] = phi[0];
        phi[0] = weight.w_nmj * (d - v);
        mu[1] = mu[0] + phi[0] * constant.dt;

        // 位置の更新
        r[1][0] = r[0][0] + constant.velocity * (mu[0]).cos() * constant.dt;
        r[1][1] = r[0][1] + constant.velocity * (mu[0]).sin() * constant.dt;

        // r_arrへの追加
        x_vec.push(r[1][0]);
        y_vec.push(r[1][1]);

        // 更新
        y[0] = y[1];
        mu[0] = mu[1];
        r[0] = r[1];
    }

    // r_arrをPyArrayとして返す
    Ok((x_vec, y_vec))
}

/// A Python module implemented in Rust.
#[pymodule]
fn _internal(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(klinotaxis, m)?)?;
    Ok(())
}
