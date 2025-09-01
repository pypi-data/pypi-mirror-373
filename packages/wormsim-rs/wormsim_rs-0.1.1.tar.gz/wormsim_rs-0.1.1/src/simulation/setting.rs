use dict_derive::FromPyObject;

// 固定されたシミュレーション設定を表す構造体Const
#[derive(FromPyObject)]
pub struct Const {
    pub alpha: f64,           // 線形濃度の勾配
    pub c_0: f64,             // ガウス濃度の設定
    pub lambda: f64,          // ガウス濃度の設定
    pub x_peak: f64,          // 勾配のピークのx座標 /cm
    pub y_peak: f64,          // 勾配のピークのy座標 /cm
    pub dt: f64,              // 時間刻みの幅 /s
    pub periodic_time: f64,   // 移動の1サイクルの継続時間 /s
    pub frequency: f64,       // 方向の平均周波数 /Hz
    pub mu_0: f64,            //初期角度 /rad
    pub velocity: f64,        // 線虫の速度 /cm/s
    pub simulation_time: f64, // シミュレーション時間 /s
    pub time_constant: f64,   // 時定数 /s
}
